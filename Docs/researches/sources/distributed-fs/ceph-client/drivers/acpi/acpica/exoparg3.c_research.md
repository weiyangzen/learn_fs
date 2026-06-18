# sources/distributed-fs/ceph-client/drivers/acpi/acpica/exoparg3.c

## Purpose
`exoparg3.c` handles triadic AML opcode execution, specifically `Fatal`, `External`, and `Mid`.

## Important APIs, Types, and Functions
The exported functions are `acpi_ex_opcode_3A_0T_0R()` and `acpi_ex_opcode_3A_1T_1R()`. Important types include `struct acpi_signal_fatal_info`, `struct acpi_walk_state`, and internal string/buffer operand objects. Dependencies include `acpi_os_signal()`, `acpi_ut_create_internal_object()`, `ACPI_ALLOCATE_ZEROED`, `acpi_ex_store()`, and debug/error macros.

## Control Flow, State, and Persistence
`Fatal` constructs a fatal signal payload from three integer operands, reports a BIOS error, calls the OS fatal signal hook, and returns either `AE_ERROR` or `AE_OK` depending on `ACPI_CONTINUE_ON_FATAL`. `External` is ignored at runtime after logging because it should only aid disassembly. `Mid` creates a new string or buffer object with the source type, clamps the requested slice to source length, allocates storage for non-empty output, copies the selected bytes, marks buffers data-valid, stores the result to the target, and exposes it as `walk_state->result_obj`.

## Dependencies and Integration Points
This file integrates AML fatal signaling with the host OS and implements `Mid` in the same store/result convention used by other executor opcode files. It relies on operand resolution to guarantee source type and integer arguments before execution.

## Risks and Test Signals
Risks include host-specific fatal signal behavior, configuration-dependent fatal return status, slice length overflow/truncation around large indices, zero-length buffer ownership, and result cleanup when target storage fails. Tests should cover `Fatal` signal payloads, `External` no-op execution, `Mid` for strings and buffers, index beyond end, zero requested length, truncation at source end, and allocation/store failure paths.
