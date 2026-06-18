<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_smic_sm.c -->
# sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_smic_sm.c

## Purpose
Implements the SMIC low-level IPMI system-interface state machine. It serializes request bytes through SMIC control/data/flag registers, reads response bytes, handles timeout/error recovery, and exposes a `si_sm_handlers` table.

## Important APIs, Types, and Functions
- `struct si_sm_data` stores SMIC state, `si_sm_io`, write/read buffers, positions, retry count, truncation state, and timeout.
- `init_smic_data()`, `start_smic_transaction()`, `smic_get_result()`, `smic_event()`, `smic_detect()`, `smic_cleanup()`, and `smic_size()` implement the `si_sm_handlers` contract.
- Register helpers read/write SMIC data, status, control, and flags offsets.
- `start_error_recovery()` retries the original write up to `SMIC_MAX_ERROR_RETRIES` before marking `SMIC_HOSED`.

## Control Flow
Transactions begin in `SMIC_START_OP`, issue `GET_STATUS`, proceed through `WR_START`, repeated `WR_NEXT`, `WR_END`, wait for `RX_DATA_READY`, then issue `RD_START`, repeated `RD_NEXT`, and `RD_END`. `smic_event()` advances one or more steps depending on flags/status, returns delay guidance, and returns `SI_SM_TRANSACTION_COMPLETE` when the read end confirms ready with no error.

## State and Persistence
All per-transaction state lives in `si_sm_data`. `smic_timeout` is decremented by elapsed microseconds while non-idle, `error_retries` persists across restart attempts, and `truncated` causes `smic_get_result()` to report `IPMI_ERR_MSG_TRUNCATED`.

## Dependencies and Integration Points
Depends on `ipmi_si_sm.h`, IPMI completion codes, and `si_sm_io` accessor callbacks installed by memory or port setup. The handler table is selected by PCI/platform/ACPI discovery for SMIC interfaces.

## Risks
The state machine is sensitive to exact hardware status codes and `SMIC_FLAG_BSY`. Timeout accounting has a FIXME for calls with `time > SMIC_RETRY_TIMEOUT`, which can delay error recovery. Buffer limits are fixed at 80 bytes; overlong reads are drained but reported truncated.

## Test Signals
Tests should simulate normal write/read, busy flag delays, bad status at every phase, RX/TX readiness delays, timeout retry then hosed behavior, oversized responses, and `SMIC_SMS_DATA_AVAIL` returning `SI_SM_ATTN` while idle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_smic_sm.c -->
