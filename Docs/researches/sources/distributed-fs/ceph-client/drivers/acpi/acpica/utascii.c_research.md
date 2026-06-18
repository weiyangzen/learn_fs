# sources/distributed-fs/ceph-client/drivers/acpi/acpica/utascii.c

Purpose: `utascii.c` validates ACPI nameseg/table-signature characters and repairs printable ASCII strings for diagnostics.

Important APIs/types/functions: `acpi_ut_valid_nameseg()` validates four characters. `acpi_ut_valid_name_char()` accepts uppercase letters, digits, underscore, and `!` only in position 3 for tables such as `ASF!`. `acpi_ut_check_and_repair_ascii()` copies bytes into a repaired string until NUL or `count`, replacing non-printable bytes with spaces.

Control flow: Nameseg validation is a fixed four-byte loop and does not require a NUL-terminated string. ASCII repair stops early on NUL after copying it, otherwise transforms only non-printable bytes.

State and persistence behavior: No global state is modified. The only mutation is writing to caller-provided `repaired_name`.

Dependencies and integration points: It is used by table lookup/printing, namespace name repair/validation, and any ACPICA component that needs fixed-size ACPI identifier validation.

Risks and test signals: Risks include signed-char `isprint` behavior if callers pass non-ASCII values, accidentally permitting lowercase names, and callers expecting full padding after early NUL. Tests should cover exactly four-byte non-NUL signatures, `ASF!`, lowercase rejection, underscore/digits, embedded NUL repair, and non-printable bytes.
