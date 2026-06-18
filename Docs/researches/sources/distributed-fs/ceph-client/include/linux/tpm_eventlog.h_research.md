# sources/distributed-fs/ceph-client/include/linux/tpm_eventlog.h

## Purpose
Defines TPM BIOS/EFI event log record layouts and helper logic for calculating TPM2 event sizes. It gives parsers the packed structures and validation needed to walk variable-length TCG event logs containing multiple digest algorithms.

## Important APIs, Types, And Functions
Important definitions include `struct tcpa_event`, `struct tcpa_pc_event`, `struct tcg_efi_specid_event_head`, `struct tcg_pcr_event`, `struct tcg_event_field`, `struct tcg_pcr_event2_head`, `struct tcg_algorithm_size`, and `struct tcg_algorithm_info`. Enums define BIOS platform classes, TPM 1.2 event types, and PC event IDs. The key function is `__calc_tpm2_event_size()`, which validates a TPM2 event against the initial Spec ID event and returns the computed byte length or zero on malformed input.

## Control Flow
`__calc_tpm2_event_size()` starts at a TPM2 event header, optionally maps only the bytes it needs through `TPM_MEMREMAP`, validates that `event_header` is PCR 0, `NO_ACTION`, and has a zero SHA1 digest, then checks the Spec ID signature and algorithm count. It walks each digest by reading its algorithm ID, matching it to the digest-size table from the Spec ID event, skips the digest bytes, then reads the event data length and computes total size. Unknown algorithms, mapping failure, mismatched counts, or empty event type/data return zero.

## State, Persistence, And Dependencies
The header stores no persistent state. It depends on `linux/tpm.h`, endian conversion on PPC64, and arch/platform-provided `TPM_MEMREMAP`/`TPM_MEMUNMAP` hooks when parsing physical log memory. Structures are packed where wire layout requires it.

## Integration Points
Used by TPM event-log readers under firmware/ACPI/EFI paths and seq_file exports for binary or ASCII event logs. It must agree with PCR bank metadata from TPM2 capabilities and TCG EFI Spec ID event layout.

## Risks And Test Signals
Risks include parsing attacker-controlled or firmware-corrupt logs, incorrect pointer arithmetic across pages, endianness mismatches, trusting unbounded algorithm counts, and accepting unknown digest algorithms. Test signals include malformed-log fuzzing, cross-page mapping tests, PPC64 endian coverage, Spec ID signature/count validation, and regression logs from TPM 1.2 and TPM2 firmware.
