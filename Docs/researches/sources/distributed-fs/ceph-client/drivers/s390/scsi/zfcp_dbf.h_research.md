# `sources/distributed-fs/ceph-client/drivers/s390/scsi/zfcp_dbf.h`

## Purpose

`zfcp_dbf.h` declares the zfcp debug-feature record layouts and small inline tracing classifiers used across the zfcp driver. It is the common schema for recovery, SAN, HBA, SCSI, and payload debug areas, and it supplies convenience wrappers that choose debug tags and levels for FSF and SCSI events. The file is hardware-driver observability infrastructure rather than core I/O logic, but it is deeply integrated with ERP, FSF request handling, FC ELS/CT handling, and SCSI completion/error paths.

## Important APIs, Types, And Data

- `ZFCP_DBF_TAG_LEN` fixes trace tags at seven bytes. All call sites pass short stable identifiers such as `fs_rerr`, `rsl_err`, or `erardy1`, so tag length is a compatibility constraint for trace tooling.
- `ZFCP_DBF_INVALID_WWPN` and `ZFCP_DBF_INVALID_LUN` provide sentinel values for trace records where a port or LUN is not applicable.
- `enum zfcp_dbf_pseudo_erp_act_type` adds pseudo ERP action ids for rport add/delete trace records, distinct from real `enum zfcp_erp_act_type`.
- `struct zfcp_dbf_rec_trigger`, `struct zfcp_dbf_rec_running`, and `struct zfcp_dbf_rec` define recovery trace records: requested versus required ERP action, queue depths, current FSF request id, action status, step, and per-target adapter/port/LUN status.
- `struct zfcp_dbf_san` records CT/ELS/SAN request/response metadata with request id, destination id, payload length, and a compact payload prefix.
- `struct zfcp_dbf_hba_res`, `struct zfcp_dbf_hba_uss`, `struct zfcp_dbf_hba_fces`, and `struct zfcp_dbf_hba` cover FSF responses, unsolicited status, bit-error payloads, and FC Endpoint Security changes.
- `struct zfcp_dbf_scsi` captures SCSI id/LUN, result, retry counters, FCP response info, command opcode, FSF request id, host-scribble request id, optional response payload, and high LUN bits.
- `struct zfcp_dbf_pay` is the unformatted payload trace record, capped by `ZFCP_DBF_PAY_MAX_REC`.
- `struct zfcp_dbf` owns debug area handles (`pay`, `rec`, `hba`, `san`, `scsi`), per-area spinlocks, and reusable preallocated record buffers.
- Inline APIs:
  - `zfcp_dbf_hba_fsf_resp_suppress()` identifies benign FCP residual-under responses with good SCSI status so default HBA tracing can be less noisy.
  - `zfcp_dbf_hba_fsf_resp()` checks debug level before calling the out-of-line formatter.
  - `zfcp_dbf_hba_fsf_response()` classifies FSF completions into request errors, protocol errors, FSF errors, open completions, QTCB log-bearing completions, or normal completions.
  - `_zfcp_dbf_scsi()`, `zfcp_dbf_scsi_result()`, `zfcp_dbf_scsi_fail_send()`, `zfcp_dbf_scsi_abort()`, `zfcp_dbf_scsi_devreset()`, and `zfcp_dbf_scsi_nullcmnd()` centralize SCSI trace level/tag choices.

## Control Flow And Integration

This header is included by FSF and FC paths to trace request submission and completion decisions. `zfcp_dbf_hba_fsf_response()` is called from `zfcp_fsf_protstatus_eval()` before FSF protocol status is interpreted. Its branching means high-severity request/protocol/FSF errors are visible at low debug levels, while normal traffic is usually level 6. SCSI wrappers are invoked from FCP completion, abort, and reset paths in the SCSI/FSF code so that SCSI mid-layer outcomes can be correlated with FSF request ids and FCP response data.

The record structures are packed because they are written into debugfs/s390 debug feature buffers as binary records. They mirror fields from `zfcp_def.h`, `zfcp_fsf.h`, libfc, and SCSI structures, so layout and width changes in any of those domains can affect trace compatibility.

## State And Persistence

The file itself has no persistent runtime state beyond the `struct zfcp_dbf` fields embedded in each adapter. Debug data persists only in kernel debug buffers for the lifetime of the adapter/debug area. Reusable record buffers in `struct zfcp_dbf` are protected by per-area spinlocks in the implementation. The inline functions read live adapter, SCSI, and FSF request state but do not mutate driver state except indirectly through out-of-line trace calls.

## Dependencies

The header depends on:

- Linux s390 debug feature types (`debug_info_t`) through the driver definitions.
- SCSI FCP definitions such as `struct fcp_resp_with_ext`, `FCP_RESID_UNDER`, `FCP_TMF_TGT_RESET`, and SCSI status constants.
- `zfcp_ext.h` declarations for the out-of-line debug functions.
- `zfcp_fsf.h` for FSF status, QTCB, and qualifier constants.
- `zfcp_def.h` for `struct zfcp_fsf_req`, `struct zfcp_adapter`, and status bits.

## Risks And Edge Cases

- Trace tag strings must fit `ZFCP_DBF_TAG_LEN`; longer tags will be truncated or overflow if callers mishandle fixed-size buffers.
- Packed binary record layouts are ABI-like for diagnostics. Adding fields or changing widths without trace decoder updates can break tooling.
- `zfcp_dbf_hba_fsf_resp_suppress()` assumes an IO QTCB with a valid FCP response when `qtcb_type == FSF_IO_COMMAND`; bad or corrupted QTCBs could make the classifier misleading.
- `_zfcp_dbf_scsi()` obtains the adapter from `scmd->device->host->hostdata[0]`; callers must pass a valid SCSI command with attached host data.
- The file intentionally suppresses common benign residual-under FSF errors at default levels, so tests or support procedures must know when to raise debug levels for full visibility.

## Test Signals

Useful validation signals include:

- FSF completion cases produce expected tags: `fs_rerr`, `fs_perr`, `fs_ferr`, `fs_open`, `fs_qtcb`, and `fs_norm`.
- FCP residual-under with SAM good is suppressed to level 5 while other FSF errors remain level 1.
- SCSI completion paths emit `rsl_err`, `rsl_ret`, or `rsl_nor` according to result/retry state.
- Target and LUN reset traces prefix tags with `tr_` or `lr_`.
- Debug buffers remain parseable after record changes and do not race under concurrent FSF/SCSI completions.
