<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/eventlog/efi.c -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/eventlog/efi.c

## Purpose
Reads TPM2 event logs from EFI configuration tables, including optional final-events log append data.

## Important APIs, Types, And Functions
The exported function is `tpm_read_log_efi()`. It uses global EFI table addresses `efi.tpm_log` and `efi.tpm_final_log`, `efi_tpm_final_log_size`, `struct linux_efi_tpm_eventlog`, `struct efi_tcg2_final_events_table`, `devm_kmemdup()`, and `devm_krealloc()`.

## Control Flow
The reader only handles TPM2 chips and rejects invalid EFI TPM log table addresses. It maps the fixed log header to obtain size, remaps the full payload, copies the main log into devm memory, and records its version. If a valid TPM2 final-events table exists, it maps that table, subtracts the portion already present in the preboot log, grows the log buffer, appends the remaining final events, and updates the end pointer.

## State And Persistence
The combined log persists as device-managed memory in `chip->log`. EFI table mappings are temporary and are unmapped before return. On allocation failure, copied log memory is freed and the reader returns an error.

## Dependencies And Integration Points
Used as the second backend in `tpm_read_log()` after ACPI fallback. It depends on EFI boot services handoff tables populated by architecture EFI code and on TPM2 event-log format constants.

## Risks And Edge Cases
Final-events size arithmetic is sensitive because the global final size excludes the preboot prefix after adjustment. Empty logs are errors. Partial allocation failure must avoid leaving stale `chip->log` pointers. The backend intentionally rejects TPM1.

## Test Signals
Boot EFI TPM2 systems with only the main log, with final-events data, with invalid table addresses, and with zero-sized logs. Compare securityfs binary output length against main plus final-events expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/eventlog/efi.c -->
