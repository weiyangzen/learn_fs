<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/eventlog/acpi.c -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/eventlog/acpi.c

## Purpose
Reads the firmware TPM event log from ACPI TCPA or TPM2 tables and stores it in `chip->log` for securityfs export.

## Important APIs, Types, And Functions
Defines `struct acpi_tcpa`, `tpm_is_tpm2_log()`, `tpm_bios_log_free()`, and exported reader `tpm_read_log_acpi()`. It consumes `struct acpi_table_tpm2`, `struct acpi_tpm2_phy`, `struct tpm_bios_log`, `TCG_SPECID_SIG`, `EFI_TCG2_EVENT_LOG_FORMAT_TCG_1_2`, and `EFI_TCG2_EVENT_LOG_FORMAT_TCG_2`.

## Control Flow
The reader rejects chips without an ACPI device handle. TPM2 chips read the ACPI `TPM2` table and its physical log area fields; TPM1 chips read the `TCPA` table and select client/server length/address layout by platform class. It maps firmware memory, copies the log into kernel memory, verifies TPM2 logs have an EFI Spec ID event signature, registers a devm cleanup action, and returns the detected log format.

## State And Persistence
The copied log persists in `chip->log.bios_event_log` until device-managed cleanup or explicit failure cleanup. The ACPI table references are temporary and are released with `acpi_put_table()`.

## Dependencies And Integration Points
Called from `eventlog/common.c` before EFI and OF fallbacks. It depends on ACPI table discovery, ACPI I/O memory mapping, TPM chip flags, and TCG event-log structures from `linux/tpm_eventlog.h`.

## Risks And Edge Cases
ACPI does not bind event logs to a specific TPM, so multiple ACPI TPMs can expose the same log. Bad firmware lengths, zero addresses, unmappable memory, or TPM2 logs without the expected Spec ID event return errors so EFI can be tried. Pointer arithmetic over firmware-provided lengths is boundary-sensitive.

## Test Signals
Boot TPM1 and TPM2 ACPI systems with valid and missing TCPA/TPM2 tables, malformed zero-length log areas, invalid TPM2 Spec ID signatures, and securityfs reads of `binary_bios_measurements`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/eventlog/acpi.c -->
