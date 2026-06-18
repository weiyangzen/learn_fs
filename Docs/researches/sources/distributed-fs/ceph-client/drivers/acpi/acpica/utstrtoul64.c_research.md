## sources/distributed-fs/ceph-client/drivers/acpi/acpica/utstrtoul64.c

Purpose: `utstrtoul64.c` implements ACPICA's top-level string-to-integer conversion policies for full 64-bit parser/tool conversion, runtime implicit conversion, and runtime explicit `to_integer` conversion.

Important APIs and functions: `acpi_ut_strtoul64` supports decimal, hex with `0x`, and octal with leading `0`, forces a 64-bit conversion regardless of current DSDT integer width, and returns overflow status. `acpi_ut_implicit_strtoul64` implements ACPI implicit conversion rules: hex only, optional ACPICA-accepted `0x`, no errors, overflow truncation. `acpi_ut_explicit_strtoul64` implements explicit conversion rules: decimal by default, hex with `0x`, no octal, no errors, overflow truncation.

Control flow: all three paths trim leading whitespace and leading zeros. `acpi_ut_strtoul64` detects base, temporarily saves and changes `acpi_gbl_integer_bit_width` to 64, calls the base converter, then restores the original width. Runtime conversions ignore status from lower-level converters by design.

State and dependencies: the only mutable state interaction is temporary global integer-width override in `acpi_ut_strtoul64`. The file depends on prefix/removal and base conversion helpers from `utstrsuppt.c`.

Integration points: iASL parsers/preprocessor, data table compiler, AML interpreter conversions, debugger command parsing, `acpi_dump`, return-value repair, and acpi_exec namespace overrides use these conversion policies.

Risks: caller expectations must match the selected conversion policy; implicit hex-only behavior and explicit no-octal behavior are intentionally different from parser conversion. Temporary mutation of global integer width must always be restored.

Test signals: empty and whitespace strings, `0`, decimal, octal, hex, implicit `"BA98"` and `"0x1234"`, explicit `"012"` as decimal not octal, overflow truncation in runtime paths, and status-returning overflow in `acpi_ut_strtoul64` are key.
