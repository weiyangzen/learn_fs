# `sources/distributed-fs/ceph-client/drivers/s390/scsi/zfcp_fc.h`

## Purpose

`zfcp_fc.h` declares Fibre Channel helper structures and inline FCP command/response conversion routines for zfcp. It defines CT/ELS request containers, GPN_FT sizing constants, WKA port state, FC event queue infrastructure, and the logic that maps Linux SCSI commands to FCP command IUs and FCP responses back to SCSI result/sense/residual state.

## Important APIs, Types, And Data

- GPN_FT constants compute CT response capacity:
  - `ZFCP_FC_CT_SIZE_PAGE`, `ZFCP_FC_GPN_FT_ENT_PAGE`, `ZFCP_FC_GPN_FT_NUM_BUFS`, `ZFCP_FC_GPN_FT_MAX_SIZE`, and `ZFCP_FC_GPN_FT_MAX_ENT`.
- `ZFCP_FC_CTELS_TMO` defines default CT/ELS timeout from FC R_A_TOV.
- `struct zfcp_fc_event` and `struct zfcp_fc_events` queue FC HBAAPI events from IRQ context to workqueue context.
- CT request/response containers: `zfcp_fc_gid_pn_req/rsp`, `zfcp_fc_gpn_ft_req`, `zfcp_fc_gspn_req/rsp`, and `zfcp_fc_rspn_req`.
- `struct zfcp_fc_req` is the internal FC request envelope containing `struct zfcp_fsf_ct_els`, request/response SG entries, and a union of embedded payloads for ADISC, GID_PN, GPN_FT, GSPN, and RSPN.
- `enum zfcp_fc_wka_status` and `struct zfcp_fc_wka_port` model WKA generic-service ports with open/close wait queues, state, refcount, D_ID, FSF handle, mutex, and delayed close work.
- `struct zfcp_fc_wka_ports` groups management, time, directory, and alias service WKA ports.
- Inline helpers:
  - `zfcp_fc_scsi_to_fcp()` fills an FCP command IU from `struct scsi_cmnd`, including LUN, task attribute, data direction, CDB, transfer length, and DIF Type 1 protection overhead.
  - `zfcp_fc_fcp_tm()` creates an FCP task-management command for a SCSI device and TM flag.
  - `zfcp_fc_eval_fcp_rsp()` evaluates an FCP response IU into SCSI result, sense buffer, residual count, and host-byte errors.

## Control Flow And Integration

FSF SCSI command setup calls `zfcp_fc_scsi_to_fcp()` before queueing an FSF FCP command. FSF task-management setup calls `zfcp_fc_fcp_tm()`. FSF FCP completion calls `zfcp_fc_eval_fcp_rsp()` after basic FSF status handling to translate remote SCSI/FCP response semantics into the Linux SCSI command. `struct zfcp_fc_req` is used by `zfcp_fc.c` when sending internal CT/ELS commands through `zfcp_fsf_send_ct()` and `zfcp_fsf_send_els()`.

## State And Persistence

Most structures are short-lived request or event containers. WKA port objects persist per adapter in `adapter->gs`. The inline FCP response evaluator mutates the live `struct scsi_cmnd`: `result`, sense buffer, and residual.

## Dependencies

The header depends on FC ELS/FCP/NS definitions, SCSI command and tagged command headers, and zfcp FSF CT/ELS structures. It also assumes SCSI protection helpers such as `scsi_get_prot_type()`, `scsi_bufflen()`, and `scsi_set_resid()`.

## Risks And Edge Cases

- `zfcp_fc_scsi_to_fcp()` copies `scsi->cmd_len` bytes into `fc_cdb`; callers must ensure the CDB length fits the FCP command IU.
- DIF Type 1 length adjustment assumes 8 protection bytes per logical block and uses `sector_size`; invalid sector size would corrupt FCP_DL.
- `zfcp_fc_eval_fcp_rsp()` treats non-`FCP_TMF_CMPL` response-info codes as `DID_ERROR` and returns before sense/residual evaluation.
- Sense data pointer arithmetic depends on whether response-info length is present and on big-endian length fields.
- Residual-under with good SCSI status is promoted to `DID_ERROR` when transferred bytes are below `underflow` and no sense data is present.

## Test Signals

Coverage should verify:

- FCP command IUs contain correct LUN encoding, read/write flags, CDB, FCP_DL, and protection-adjusted length.
- Task-management IUs set only LUN and TM flags needed by FSF.
- FCP response evaluation copies bounded sense data, handles TMF completion/failure, sets residual underflow, and flags residual overrun errors.
- GPN_FT sizing constants match page-sized SG response allocation and parsing in `zfcp_fc.c`.
