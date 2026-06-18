# sources/distributed-fs/ceph-client/drivers/acpi/acpica/tbxfroot.c

Purpose: `tbxfroot.c` finds and validates the Root System Description Pointer in low memory, supporting the early boot path that discovers the ACPI root table before the main table manager is initialized.

Important APIs/types/functions: `acpi_tb_get_rsdp_length()` returns either the ACPI 2.0+ RSDP length or the legacy checksum length after signature validation. `acpi_tb_validate_rsdp()` checks signature, legacy checksum, and extended checksum for revision 2+. `acpi_find_root_pointer()` searches EBDA and high BIOS memory windows for a valid RSDP. `acpi_tb_scan_memory_for_rsdp()` scans a mapped memory range in `ACPI_RSDP_SCAN_STEP` increments.

Control flow: Root search maps the EBDA pointer location, converts the segment to a physical address, checks that it is sane, maps up to the EBDA window bounded below VGA memory, scans for a valid RSDP, and returns the physical address if found. If EBDA search fails, it maps and scans the E0000h-FFFFFh window. Scanning validates each candidate by signature and checksum before returning.

State and persistence behavior: It has no persistent internal state; it returns the physical RSDP address through the caller's pointer. Mappings are always temporary and explicitly unmapped.

Dependencies and integration points: It depends on OSL low-memory mapping, checksum utility `acpi_ut_checksum()`, RSDP constants, and is called by OSL/root pointer discovery paths consumed by `acpi_initialize_tables()`.

Risks and test signals: Risks include mapping failures before memory services are mature, bogus EBDA pointers, scanning beyond the EBDA window, accepting duplicate invalid signatures, and revision/length inconsistencies. Tests should cover valid RSDP in EBDA and high BIOS windows, bad legacy or extended checksums, invalid signatures, absent ACPI, and EBDA pointer bounds at 0x400 and 0xA0000.
