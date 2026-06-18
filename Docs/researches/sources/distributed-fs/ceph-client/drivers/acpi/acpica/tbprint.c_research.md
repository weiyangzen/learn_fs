# sources/distributed-fs/ceph-client/drivers/acpi/acpica/tbprint.c

Purpose: `tbprint.c` emits sanitized, human-readable ACPI table headers for diagnostics, with special handling for FACS, RSDP, and CDAT tables that do not fully match the common ACPI table header layout.

Important APIs/types/functions: `acpi_tb_print_table_header()` is the public utility. Static `acpi_tb_fix_string()` replaces non-printable bytes with `?`; `acpi_tb_cleanup_table_header()` copies a header and sanitizes signature/OEM/compiler string fields.

Control flow: The print function first identifies FACS by signature and prints only signature/physical address/length. It identifies RSDP by RSDP signature, sanitizes OEM ID, and prints revision and length using the ACPI 2.0 length only when present. If CDAT support is active and the signature is not a valid nameseg, it prints CDAT-style length. Otherwise it prints the sanitized common header fields.

State and persistence behavior: It does not mutate global ACPI state except diagnostic output. It uses a local header copy so firmware table contents are not repaired in place.

Dependencies and integration points: It depends on ACPICA logging macros, table signatures, name validation from `utascii.c`, and is used by root parsing, install, DSDT corruption diagnostics, and FADT/root table discovery paths.

Risks and test signals: Risks are accidental overread of special table layouts, misleading output from corrupt strings, and compiler diagnostics around packed headers. Test signals include clean boot table logs with malformed OEM strings, FACS/RSDP/CDAT formatting, and no mutation of the original table header after printing.
