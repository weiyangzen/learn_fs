<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/eventlog/tpm2.c -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/eventlog/tpm2.c

## Purpose
Parses TPM 2.0 crypto-agile event logs for binary securityfs export.

## Important APIs, Types, And Functions
Key functions are `calc_tpm2_event_size()`, `tpm2_bios_measurements_start()`, `tpm2_bios_measurements_next()`, `tpm2_bios_measurements_stop()`, and `tpm2_binary_bios_measurements_show()`. It exports `tpm2_binary_b_measurements_seqops` and delegates record sizing to `__calc_tpm2_event_size()`.

## Control Flow
Position zero returns `SEQ_START_TOKEN` for the initial Spec ID event when it fits and is not an empty terminator. Later positions skip the first event header and walk agile `struct tcg_pcr_event2_head` entries by computing each event size against the first header. Show writes either the initial event header block or the current agile event block directly to the seq_file.

## State And Persistence
Parser state is derived from `*pos` and `chip->log` on each seq callback. No data is modified or persisted by this file.

## Dependencies And Integration Points
Used by `eventlog/common.c` when the reader reports `EFI_TCG2_EVENT_LOG_FORMAT_TCG_2`. It depends on TPM2 event-log helpers from `linux/tpm_eventlog.h` and on firmware logs beginning with a valid Spec ID event.

## Risks And Edge Cases
The iterator uses strict boundary checks and treats zero-size or past-end events as end of sequence. Off-by-one choices around `>= limit` can suppress exactly-ending entries, so event-size helper behavior matters. No ascii TPM2 view is provided.

## Test Signals
Use TPM2 logs with multiple digest banks, final-events appended records, truncated agile records, invalid digest counts, empty terminators, and exact-end boundary cases. Validate securityfs binary output can be parsed by userspace event-log tools.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/eventlog/tpm2.c -->
