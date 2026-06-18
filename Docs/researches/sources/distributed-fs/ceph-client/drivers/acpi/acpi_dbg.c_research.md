# sources/distributed-fs/ceph-client/drivers/acpi/acpi_dbg.c

## Purpose
`acpi_dbg.c` provides the userspace I/O bridge for the in-kernel ACPICA AML debugger. It exposes `debugfs/acpi/acpidbg`, connects user reads and writes to ACPICA debugger callbacks, and manages a debugger kthread plus circular input/output buffers.

## Important APIs, Types, And Functions
The central type is `struct acpi_aml_io`, containing wait queue, flags, user count, lock, debugger thread, aligned input/output buffers, circular-buffer cursors, callback, context, and usage count. Important flags include `ACPI_AML_OPENED`, `ACPI_AML_CLOSED`, `ACPI_AML_IN_USER`, `ACPI_AML_IN_KERN`, `ACPI_AML_OUT_USER`, and `ACPI_AML_OUT_KERN`. Important functions are buffer access predicates, `acpi_aml_lock_write()`, `acpi_aml_lock_read()`, `acpi_aml_write_kern()`, `acpi_aml_readb_kern()`, `acpi_aml_write_log()`, `acpi_aml_read_cmd()`, `acpi_aml_thread()`, `acpi_aml_create_thread()`, file operations `open/read/write/poll/release`, and the registered `struct acpi_debugger_ops`.

## Control Flow
Init creates the debugfs file and registers debugger operations with ACPICA. The first non-write-only opener becomes the active reader, initializes the ACPICA debugger, marks the interface opened, and resets circular buffers. ACPICA creates the debugger thread through `acpi_aml_create_thread()`. Kernel debugger output goes to `out_crc` via `write_log`; userspace reads it from the debugfs file. Userspace writes commands into `in_crc`; the debugger thread consumes bytes via `read_cmd()` until newline. Release of the active reader marks the interface closed, wakes blocked readers/writers, waits for busy operations to drain, terminates the ACPICA debugger, waits for the thread usage count to drop, and clears opened/closed flags when all users are gone.

## State And Persistence
All state is in memory and scoped to module lifetime. User-visible state is the debugfs file. The circular buffers hold transient debugger input/output. `acpi_aml_active_reader` enforces a single controlling reader.

## Dependencies And Integration Points
It depends on debugfs, wait queues, kthreads, circular-buffer helpers, user copy APIs, ACPICA debugger registration (`acpi_register_debugger()`), ACPICA callbacks (`acpi_os_printf`, `acpi_os_get_line`), and `acpi_debugfs_dir`.

## Risks
The code is highly stateful: open/close races, blocking reads/writes, and thread termination depend on `flags`, `users`, `usages`, and wait queues being updated in the right order. Memory barriers around circular-buffer head/tail updates are essential. Only the debugger thread may perform kernel-side buffer access; violating that assumption causes `-EFAULT`. A stuck userspace peer can block debugger command/log flow unless nonblocking I/O is used.

## Test Signals
Test debugfs open exclusivity, writer-before-reader rejection, nonblocking read/write `-EAGAIN`, poll readiness, command echo/log output, active-reader close while operations block, module unload, and ACPICA debugger init failure paths.
