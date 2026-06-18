# sources/distributed-fs/ceph-client/drivers/acpi/acpica/tbutils.c

Purpose: `tbutils.c` supplies core table utilities for FACS initialization, DSDT corruption detection/copying, RSDT/XSDT parsing, root entry address decoding, and descriptor validation reference counting.

Important APIs/types/functions: `acpi_tb_initialize_facs()` maps the preferred FACS/XFACS table into `acpi_gbl_FACS`. `acpi_tb_check_dsdt_header()` detects DSDT replacement/corruption by comparing saved length/checksum. `acpi_tb_copy_dsdt()` copies the DSDT into owned memory and replaces the descriptor. `acpi_tb_parse_root_table()` maps the RSDP and RSDT/XSDT, validates checksum/length, installs child tables, and triggers FADT parsing. `acpi_tb_get_table()` and `acpi_tb_put_table()` maintain descriptor validation counts and map/unmap lifetime. Static `acpi_tb_get_root_table_entry()` handles unaligned 32/64-bit root entries.

Control flow: Root parsing maps a small RSDP, selects XSDT unless disabled or unavailable, unmaps RSDP before mapping the root table, validates root length and checksum, then iterates entries. Each nonzero entry is installed through `acpi_tb_install_standard_table()`. When a newly installed table is FADT, it records `acpi_gbl_fadt_index` and parses the FADT immediately to discover DSDT/FACS. Table get/put validates on first use, increments validation count up to `ACPI_MAX_TABLE_VALIDATIONS`, and invalidates when the count drops to zero.

State and persistence behavior: This file mutates `acpi_gbl_FACS`, `acpi_gbl_DSDT`, `acpi_gbl_original_dsdt_header`, descriptor pointers/validation counts, `acpi_gbl_fadt_index`, and DSDT descriptor ownership when copying. Root and table mappings are transient unless validation counts or permanent FACS handling keep them live.

Dependencies and integration points: It integrates OSL memory mapping, checksum utilities, table install/print/validation routines, FADT parsing, DSDT copy policy (`acpi_gbl_copy_dsdt_locally`), 32-bit/XSDT policy (`acpi_gbl_do_not_use_xsdt`), and public table APIs in `tbxface.c`.

Risks and test signals: Risks include mapping failures in early boot, invalid root lengths, 64-bit XSDT truncation on 32-bit builds, table validation count overflow/underflow, DSDT copy ownership mistakes, and FACS preference flag behavior. Tests should watch root table checksum errors, FADT-triggered DSDT/FACS installation, balanced `acpi_get_table()`/`acpi_put_table()` calls, `acpi=copy_dsdt`-style local copy behavior, and warnings from DSDT corruption detection.
