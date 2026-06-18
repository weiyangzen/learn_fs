# sources/distributed-fs/ceph-client/drivers/acpi/acpica/exsystem.c

## Purpose
`exsystem.c` wraps host OS synchronization and timing services for AML `Acquire`, `Wait`, `Sleep`, `Stall`, `Signal`, and `Reset` behavior.

## Important APIs, Types, and Functions
Exports include `acpi_ex_system_wait_semaphore()`, `acpi_ex_system_wait_mutex()`, `acpi_ex_system_do_stall()`, `acpi_ex_system_do_sleep()`, `acpi_ex_system_signal_event()`, `acpi_ex_system_wait_event()`, and `acpi_ex_system_reset_event()`. Dependencies include `acpi_os_wait_semaphore()`, `acpi_os_acquire_mutex()`, `acpi_os_stall()`, `acpi_os_sleep()`, semaphore creation/deletion, and `acpi_ex_exit_interpreter()`/`acpi_ex_enter_interpreter()`.

## Control Flow, State, and Persistence
Semaphore and mutex waits first try a non-blocking acquire. If they would block, they release the interpreter and namespace mutexes, wait with the requested timeout, then reacquire interpreter state. `Stall` enforces a hard compatibility cap of 255 microseconds and warns once above the ACPI 100-microsecond guidance. `Sleep` releases the interpreter, caps the sleep duration to `ACPI_MAX_SLEEP`, sleeps, and reacquires the interpreter. Event signal/wait wrappers operate on the event object's OS semaphore. Event reset creates a fresh semaphore, deletes the old one, and swaps the object pointer.

## Dependencies and Integration Points
Opcode handlers in `exoparg1.c` and `exoparg2.c` call these wrappers. The file integrates AML synchronization semantics with OS primitives while preventing the AML interpreter lock from blocking unrelated AML progress during waits or sleeps.

## Risks and Test Signals
Risks include interpreter lock imbalance, timeout truncation to `u16` for event waits, reset races while other waiters use the old semaphore, oversized stall/sleep compatibility behavior, and OS error propagation. Tests should cover immediate and blocking semaphore/mutex paths, timeout returns, interpreter lock release/reacquire under contention, `Stall` boundary values, sleep cap behavior, signal/wait/reset event sequences, and error injection from OS primitives.
