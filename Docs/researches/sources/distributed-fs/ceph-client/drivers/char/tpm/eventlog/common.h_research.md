<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/eventlog/common.h -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/eventlog/common.h

## Purpose
Declares event-log seq operation exports and firmware reader entry points, with configuration-dependent stubs for disabled firmware interfaces.

## Important APIs, Types, And Functions
Exports `tpm1_ascii_b_measurements_seqops`, `tpm1_binary_b_measurements_seqops`, `tpm2_binary_b_measurements_seqops`, and reader functions `tpm_read_log_acpi()`, `tpm_read_log_of()`, and `tpm_read_log_efi()`.

## Control Flow
When `CONFIG_ACPI`, `CONFIG_OF`, or `CONFIG_EFI` is disabled, inline stubs return `-ENODEV`, allowing `common.c` to continue fallback probing without conditional call-site logic.

## State And Persistence
The header has no runtime state. It defines the compile-time contract between the common event-log setup and backend readers/parsers.

## Dependencies And Integration Points
Includes `../tpm.h`, is included by ACPI/EFI/OF readers and TPM1/TPM2 seq parser implementations, and mirrors Makefile conditional object inclusion.

## Risks And Edge Cases
Stub return values are part of fallback semantics; changing them would alter probing. Prototype drift between enabled readers and stubs would cause build or link failures across config combinations.

## Test Signals
Compile TPM event-log support with ACPI, EFI, and OF independently enabled or disabled. Runtime fallback should skip missing backends cleanly and still expose logs when another backend succeeds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/eventlog/common.h -->
