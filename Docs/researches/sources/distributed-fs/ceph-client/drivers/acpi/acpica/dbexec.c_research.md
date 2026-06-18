# sources/distributed-fs/ceph-client/drivers/acpi/acpica/dbexec.c

## Purpose
Implements debugger control-method/object evaluation, cleanup of converted arguments, execution setup, optional allocation-leak reporting, execution of all matching/predefined methods, and background/threaded method execution.

## Important APIs And Functions
`acpi_db_delete_objects` recursively frees debugger-created buffer and package external objects. `acpi_db_execute_method` converts command arguments, prepares a return buffer, sets `acpi_gbl_method_executing`, invokes `acpi_evaluate_object`, handles aborts/buffer overflow, and deletes arguments. `acpi_db_execute_setup` builds the fully qualified pathname from current debugger scope and configures output/single-step state. `acpi_db_execution_walk` evaluates zero-argument methods during wildcard execution. `acpi_db_execute` handles `*`, `PREDEF`, `ALL`, normal evaluate/debug modes, return-object dumping, `_PLD` special formatting, and allocation tracking. `acpi_db_create_execution_thread`, `acpi_db_single_execution_thread`, `acpi_db_create_execution_threads`, and `acpi_db_method_thread` run evaluations in one or more OS-layer debugger threads.

## Control Flow, State, And Persistence
The global `acpi_gbl_db_method_info` is reused as command context. Normal flow is parse/setup path, get handle, execute, sleep briefly for async handlers, report return object, restore console output. Threaded flow creates semaphores, initializes per-thread argument strings with thread count/id/index, launches OS execution callbacks, waits for completion, then destroys semaphores and thread ID storage. Single-step mode toggles `acpi_gbl_cm_single_step`.

## Dependencies And Integration Points
Integrates with `dbinput.c` command dispatch, `dbconvert.c` argument conversion, namespace handle lookup, ACPI object evaluation, debug output, allocation tracking caches, OS services for sleep/semaphores/thread execution, and `_PLD` display in `dbconvert.c`.

## Risks And Test Signals
Risks include global method-info reuse across background execution, races in threaded mode, semaphore cleanup on partial failures, return-buffer sizing (`ACPI_DEBUG_BUFFER_SIZE`), leaked external return buffers in some execution paths, and deadlock prevention through `acpi_gbl_method_executing`. Test signals include `Evaluate`, `Debug`, `All`, `Execute predefined`, `Background`, and `Threads` debugger commands, aborting a method, methods returning large objects, allocation tracking before/after execution, and AML tests that depend on thread argument conventions.
