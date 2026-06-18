# sources/distributed-fs/ceph-client/drivers/acpi/acpica/exoparg2.c

## Purpose
`exoparg2.c` implements executor entry points for AML opcodes with two input operands, covering `Notify`, `Divide`, arithmetic/logical operators, `Mod`, concatenation, `ToString`, `ConcatenateResTemplate`, `Index`, `Acquire`, and `Wait`.

## Important APIs, Types, and Functions
The exported handlers are `acpi_ex_opcode_2A_0T_0R()`, `acpi_ex_opcode_2A_2T_1R()`, `acpi_ex_opcode_2A_1T_1R()`, and `acpi_ex_opcode_2A_0T_1R()`. Key dependencies include `acpi_ev_is_notify_object()`, `acpi_ev_queue_notify_request()`, `acpi_ut_divide()`, `acpi_ex_do_math_op()`, `acpi_ex_do_concatenate()`, `acpi_ex_concat_template()`, `acpi_ex_store()`, `acpi_ex_do_logical_numeric_op()`, `acpi_ex_do_logical_op()`, `acpi_ex_acquire_mutex()`, and `acpi_ex_system_wait_event()`.

## Control Flow, State, and Persistence
`Notify` validates the target namespace node and queues asynchronous notify delivery after the current method completes. `Divide` allocates quotient and remainder objects, stores remainder and quotient into two targets, and returns the quotient. Math and `Mod` allocate integer results and store them into the target. `ToString` copies bytes from a buffer until the requested length, buffer length, or NUL byte. `Index` builds a `ACPI_TYPE_LOCAL_REFERENCE` object that points to a buffer/string byte or package element, stores that reference into the target, and returns it. `Acquire` and `Wait` convert `AE_TIME` into an AML logical true return while preserving other errors.

## Dependencies and Integration Points
This file bridges AML operators to event dispatch, resource-template concatenation, package/buffer/string indexing, mutex and event waits, and target storage. It relies on opcode metadata flags `AML_MATH`, `AML_LOGICAL_NUMERIC`, and `AML_LOGICAL` from the parser tables.

## Risks and Test Signals
Risks include swapped quotient/remainder semantics, index references outliving the parent buffer/package incorrectly, off-by-one range checks for strings/buffers/packages, asynchronous notify ordering, and timeout truth-value semantics for `Acquire`/`Wait`. Tests should include division by zero, divide target ordering, concatenation of supported types, `ToString` truncation and NUL handling, index into each supported container, out-of-range index errors, notify on invalid object types, and timed wait/acquire behavior.
