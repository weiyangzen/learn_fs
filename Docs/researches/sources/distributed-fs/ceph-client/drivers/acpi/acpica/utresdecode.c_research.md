## sources/distributed-fs/ceph-client/drivers/acpi/acpica/utresdecode.c

Purpose: `utresdecode.c` contains global constant string tables used to decode AML resource descriptor bitfields into readable names for ACPICA debug output, debugger resource dumps, and disassembly.

Important APIs and data: when `ACPI_DEBUG_OUTPUT`, `ACPI_DISASSEMBLER`, or `ACPI_DEBUGGER` is enabled, it exports arrays such as `acpi_gbl_bm_decode`, `acpi_gbl_config_decode`, `acpi_gbl_consume_decode`, `acpi_gbl_he_decode`, `acpi_gbl_ll_decode`, `acpi_gbl_mem_decode`, `acpi_gbl_shr_decode`, serial-bus arrays including `acpi_gbl_sbt_decode`, `acpi_gbl_am_decode`, `acpi_gbl_wm_decode`, `acpi_gbl_cph_decode`, `acpi_gbl_cpo_decode`, UART arrays, pin configuration names, and clock input names.

Control flow: there is no executable control flow beyond static initialization. Callers index these arrays with already-decoded descriptor field values.

State and dependencies: the arrays are immutable string-table state compiled only for diagnostic/tool configurations. The file depends on ACPI resource definitions from `acresrc.h` and the expectation that table order matches AML field encodings.

Integration points: resource descriptor dumping, ASL disassembly, and interactive debugger output use these names to convert compact numeric fields to ASL-like keywords.

Risks: the primary risk is table/index drift when ACPI adds resource encodings. Callers must bound-check indexes or choose arrays that include placeholder strings for reserved values, because this file does not validate indexes.

Test signals: descriptor dump tests should verify every legal bitfield value maps to the expected keyword, reserved values produce placeholder text where provided, and new descriptor fields added to `acresrc.h` have corresponding decode strings in diagnostic builds.
