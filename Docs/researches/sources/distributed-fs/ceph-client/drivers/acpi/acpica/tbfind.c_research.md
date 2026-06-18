# sources/distributed-fs/ceph-client/drivers/acpi/acpica/tbfind.c

Purpose: `tbfind.c` locates an installed ACPI table by signature, OEM ID, and OEM Table ID inside `acpi_gbl_root_table_list`, returning the descriptor index used by later table APIs.

Important APIs/types/functions: `acpi_tb_find_table()` is the sole exported function in this file. It validates the four-character signature with `acpi_ut_valid_nameseg()`, checks OEM string length bounds, normalizes the search fields into a local `struct acpi_table_header`, and scans `struct acpi_table_desc` entries.

Control flow: The function rejects invalid signatures or oversized OEM filters before locking `ACPI_MTX_TABLES`. It walks current root table descriptors, first comparing cached descriptor signatures, validating/mapping a table with `acpi_tb_validate_table()` if its pointer is absent, then comparing full header signature/OEM fields. Empty OEM filters act as wildcards. On match it writes `*table_index`; otherwise it returns `AE_NOT_FOUND`.

State and persistence behavior: It does not allocate lasting state, but may cause a descriptor to become validated/mapped as a side effect of `acpi_tb_validate_table()`. Table list access is serialized by the table mutex.

Dependencies and integration points: It integrates with table validation/mapping logic, ACPICA mutex helpers, name validation from `utascii.c`, and public table lookup paths that need a stable table index rather than a pointer.

Risks and test signals: Risks include pointer validation failures during lookup, caller-provided non-NUL or too-long OEM strings, and races if callers bypass the table mutex elsewhere. Tests should cover wildcard OEM IDs, duplicate signatures/instances, invalid signatures, absent table pointers that must be mapped, and failure propagation from validation.
