<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/hwxface.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/hwxface.c

## Purpose
Provides public ACPICA hardware interfaces for reset, generic GAS reads/writes, fixed bit register access, and sleep type discovery from namespace `_Sx` objects.

## Important APIs, Types, And Functions
Exports `acpi_reset`, `acpi_read`, `acpi_write`, `acpi_read_bit_register`, `acpi_write_bit_register`, and `acpi_get_sleep_type_data`. Important types are `struct acpi_generic_address`, `struct acpi_bit_register_info`, `struct acpi_evaluate_info`, and operand packages returned by AML evaluation.

## Control Flow
`acpi_reset` verifies the FADT reset flag and address, bypasses port validation for system-I/O reset registers with an 8-bit write, and otherwise uses `acpi_hw_write`. Generic read/write are direct public wrappers over GAS helpers. Bit-register reads locate metadata, read the parent register, mask and shift. Bit-register writes take the raw hardware lock, preserve unrelated bits for enable/control registers, and use write-one-to-clear semantics for PM1 status. Sleep type discovery allocates an evaluation block, evaluates the appropriate `_Sx` object, accepts either one encoded integer or at least two integer elements, fills type A/B, reports malformed returns, and releases references.

## State And Persistence
Mutates reset hardware, ACPI fixed registers, and caller-provided sleep type outputs. It temporarily allocates evaluation info and references returned AML objects.

## Dependencies And Integration Points
Integrates FADT data, GAS access, raw hardware lock, namespace evaluation, predefined-name validation, and sleep-state name globals. It is a public API surface exported to kernel ACPI code.

## Risks And Edge Cases
Reset deliberately bypasses I/O validation for compatibility. Bit-register writes must preserve status semantics or they may clear unrelated events. `_Sx` packages are firmware-controlled and may be absent, empty, wrongly typed, or encoded in vendor-compatible two-integer form.

## Test Signals
Check reset register variants, GAS memory/I/O read-write behavior, PM1 status write-one-to-clear behavior, locking under concurrent bit access, and `_S0`-`_S5` package shapes including missing, one-integer, two-integer, empty, and wrong-type returns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/hwxface.c -->
