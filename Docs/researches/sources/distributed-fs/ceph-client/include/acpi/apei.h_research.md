# sources/distributed-fs/ceph-client/include/acpi/apei.h

Purpose: Declares the Linux ACPI Platform Error Interface entry points and ERST ioctl ABI used for firmware error record storage and hardware error source setup.

Important APIs, types, and functions: Defines `APEI_ERST_INVALID_RECORD_ID`, `APEI_ERST_CLEAR_RECORD`, `APEI_ERST_GET_RECORD_COUNT`, `enum hest_status`, globals `hest_disable`, `erst_disable`, and conditionally `ghes_disable`. Declares `acpi_hest_init()`, `acpi_ghes_init()`, ERST operations `erst_write()`, `erst_get_record_count()`, record-id iteration, `erst_read()`, `erst_read_record()`, `erst_clear()`, and arch hooks `arch_apei_enable_cmcff()` and `arch_apei_report_mem_error()`.

Control flow: Initialization stubs collapse to no-ops when APEI/GHES configs are disabled. Enabled users initialize HEST/GHES, iterate or read ERST records, and clear/write records through firmware-backed storage.

State and persistence: ERST records are persistent firmware error records with CPER payloads. The header exposes disable flags and record IDs but stores no records itself.

Dependencies and integration points: Depends on `linux/acpi.h`, CPER definitions, and ioctl encoding. Integrates with GHES, HEST parsing, EDAC/RAS reporting, persistent error logs, and arch-specific corrected-machine-check or memory-error reporting.

Risks and test signals: Risks include ioctl ABI breakage, ERST iteration races, invalid CPER length handling, and config-disabled callers assuming real support. Test APEI enabled/disabled builds, ERST read/write/clear through user ABI, malformed CPER injection, GHES boot paths, and arch hook coverage.
