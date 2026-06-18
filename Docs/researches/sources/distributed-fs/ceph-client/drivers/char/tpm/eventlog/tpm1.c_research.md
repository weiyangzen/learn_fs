<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/eventlog/tpm1.c -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/eventlog/tpm1.c

## Purpose
Parses TPM 1.1/1.2 BIOS event logs and exposes both binary and human-readable securityfs seq_file views.

## Important APIs, Types, And Functions
Defines TPM1 seq callbacks `tpm1_bios_measurements_start()`, `tpm1_bios_measurements_next()`, `tpm1_bios_measurements_stop()`, `tpm1_binary_bios_measurements_show()`, `tpm1_ascii_bios_measurements_show()`, and helper `get_event_name()`. Exports `tpm1_ascii_b_measurements_seqops` and `tpm1_binary_b_measurements_seqops`.

## Control Flow
The iterator walks variable-sized `struct tcpa_event` records by repeatedly validating header fit, endian-converted event size/type, terminator records, and end-of-log bounds. Binary output emits a temporary header with endian-normalized numeric fields, followed by original event payload bytes. ASCII output prints PCR index, SHA1 digest, event type, and a decoded event-name string for known TCPA/PC event IDs.

## State And Persistence
No parser state persists beyond the seq_file position. The parser reads immutable `chip->log` memory and allocates a temporary event-name buffer per ascii record.

## Dependencies And Integration Points
Used by `eventlog/common.c` for TPM1 securityfs files. It depends on TCPA event definitions, `do_endian_conversion()`, `MAX_TEXT_EVENT`, seq_file, and TPM event type constants.

## Risks And Edge Cases
Firmware logs are untrusted; every record length must be bounded before dereference. The ascii decoder only recognizes selected event IDs and truncates free-form separator/action strings to `MAX_TEXT_EVENT`. Binary output intentionally normalizes header endianness, which differs from a raw memory dump.

## Test Signals
Read logs with valid records, terminators, truncated headers, oversized event payloads, unknown event types, `EVENT_TAG` records with hash payloads, and long text events. Compare ascii and binary seq iteration counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/eventlog/tpm1.c -->
