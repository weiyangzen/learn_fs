# sources/distributed-fs/ceph-client/drivers/s390/block/dasd_3990_erp.c

## Purpose

`dasd_3990_erp.c` implements IBM 3990/ECKD DASD error recovery procedures for `struct dasd_ccw_req` requests. It is the discipline-specific recovery decision tree used after channel programs fail: it interprets 24-byte and 32-byte sense data, builds additional ERP requests, retries on alternate channel paths, blocks queues while waiting for state-change readiness, issues Diagnostic Control commands, handles PAV alias recovery, and finally marks the original request done or failed.

## Important APIs, Types, and Functions

- `struct DCTL_data` is the packed payload for Diagnostic Control (`CCW_CMD_DCTL`) requests, mainly used with Inhibit Write modifiers.
- `dasd_3990_erp_action()` is the exported/main entry point. It is called with the DASD queue lock held and returns either the original request or a new ERP-chain head.
- `dasd_3990_erp_add_erp()` creates a default ERP. In command mode it builds a NOOP/TIC chain to the failed CCW. In transport mode it clones the TCW and supplies a fresh TSB so original sense data is preserved.
- `dasd_3990_erp_inspect()` routes recovery through alias inspection, control-check handling, 24-byte sense handling, or 32-byte sense handling.
- `dasd_3990_erp_inspect_24()` dispatches classic sense bits such as command reject, intervention required, equipment check, data check, overrun, invalid track format, EOC, environmental data, no-record-found, and file-protected.
- `dasd_3990_erp_inspect_32()` handles SIM sense data, compound program action codes, and single program action codes such as fatal error, intervention required, logging required, action 1B write restart, state-change pending, and busy.
- `dasd_3990_erp_action_1()`, `dasd_3990_erp_action_4()`, and `dasd_3990_erp_action_5()` implement common recovery strategies: alternate path retry, queue blocking with timer, and retry-before-further-recovery.
- `dasd_3990_erp_action_1B_32()` and `dasd_3990_update_1B()` build/update a DE/LO/TIC ERP to resume an interrupted write from precise sense information.
- `dasd_3990_erp_further_erp()` chooses second-stage handling once retries are exhausted.
- `dasd_3990_erp_handle_sim()` logs SIM source reference codes and is callable outside the main ERP path.

## Control Flow

The main flow starts in `dasd_3990_erp_action(cqr)`. If the request actually completed with clean channel/device status, the request is marked `DASD_CQR_DONE`. Otherwise the code checks whether the same error already appears in the current ERP chain via `dasd_3990_erp_in_erp()`. A new error gets a default ERP through `dasd_3990_erp_additional_erp()`, followed by sense inspection. A repeated error reuses the matching ERP through `dasd_3990_erp_handle_match_erp()`, freeing successful leading ERP blocks and either retrying, updating special ERP data, or invoking `dasd_3990_erp_further_erp()` when retries reach zero.

The 24-byte sense path is a priority-ordered bit dispatch. Command rejects usually fail permanently unless environmental data suggests retry, writes are inhibited, or the request is invalid on a copy-pair secondary. Equipment and data checks select alternate-path, state-change wait, or action-5 retry depending on write-inhibited, environmental-data, permanent-error, and retry-exhausted bits. Some unrecoverable states, such as no-record-found, file-protected, invalid format without environmental data, or EOC, clean up the ERP and fail the original request. Correctable data checks with potentially incorrect data panic because the block layer cannot report "possibly wrong" data to the application.

The 32-byte path first logs SIM data when present. Compound action codes run in phases: set retry count from byte 25, optionally try alternate path, optionally issue DCTL or wait, then report configuration errors. Single action codes either retry, fail, run intervention-required handling, run logging-required handling, build action 1B restart ERP, or wait for state-change/busy.

Alias inspection runs before sense dispatch. If the failed request started on an alias device while its block base differs from `startdev`, the code may remove and reload a stale dynamic PAV alias, rewrites the CQR to base I/O with `dasd_eckd_reset_ccw_to_base_io()`, and restarts ERP on the base device.

## State and Persistence Behavior

The file mutates in-memory request and device state only; it has no persistent on-disk state. It changes `cqr->status`, `retries`, `function`, `refers`, `lpm`, `expires`, and ERP list membership. It manipulates device stop bits (`DASD_STOPPED_PENDING`), block/device timers, path masks, path error counters, and path error timestamps. Path autodisable state is reflected in `device->path[]` and operational path masks. ERP chains are explicit linked stacks through `refers`; successful intermediate ERP requests are removed from lists and freed.

## Dependencies and Integration Points

This code is tightly coupled to DASD core request handling (`dasd_alloc_erp_request`, `dasd_free_erp_request`, timers, queue status values), ECKD channel program data (`DEFINE_EXTENT`, `LOCATE_RECORD`, `PFX`, PSF, TIC), S/390 channel status and sense helpers (`scsw_*`, `dasd_get_sense`), path management (`dasd_path_get_opm`, `dasd_path_remove_opm`, `dasd_path_add_ifccpm`), extended error reporting (`dasd_eer_write`), and alias management (`dasd_alias_remove_device`, `dasd_reload_device`). It also respects user/devmap features such as `DASD_FEATURE_ERPLOG`, `DASD_FEATURE_PATH_AUTODISABLE`, and verification flags.

## Risks

The code is safety-critical and table-driven by hardware sense-byte conventions; small byte-index mistakes can cause wrong recovery, permanent I/O failure, or repeated retries. ERP chains require careful lifetime handling because requests are freed while list links and `refers` relationships are rewritten. Correctable-data cases intentionally panic, so regressions around sense classification can turn recoverable or reportable errors into system crashes. Path autodisable must avoid disabling the last path and must correctly account IFCC windows. Alias rerouting is race-sensitive because a dynamic PAV mapping can change while I/O and recovery are in progress.

## Test Signals

Useful test evidence would include fault-injection or hardware/z/VM tests for 24-byte and 32-byte sense classifications, action 1 alternate-path sequencing, action 4 timer/queue-block behavior, action 1B DE/LO restart construction, repeated-error chain matching, path threshold/autodisable behavior, and alias-to-base retry after PAV mapping changes. Logs from `DASD_FEATURE_ERPLOG`, DBF events, SIM messages, EER PPRC suspend events, and final CQR statuses are the primary observability signals.
