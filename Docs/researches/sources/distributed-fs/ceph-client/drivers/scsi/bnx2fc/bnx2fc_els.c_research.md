# sources/distributed-fs/ceph-client/drivers/scsi/bnx2fc/bnx2fc_els.c

## Purpose

`bnx2fc_els.c` implements ELS and middle-path recovery helpers for offloaded FCoE sessions. It sends selected ELS requests through firmware, converts firmware responses back into libfc frames, handles RRQ/REC/SRR recovery, and hooks FLOGI/FDISC/LOGO responses to maintain FCoE source MAC state.

## Important APIs, Types, and Functions

Externally used functions include `bnx2fc_send_rrq()`, `bnx2fc_send_adisc()`, `bnx2fc_send_logo()`, `bnx2fc_send_rls()`, `bnx2fc_send_rec()`, `bnx2fc_send_srr()`, `bnx2fc_process_els_compl()`, and `bnx2fc_elsct_send()`. The central internal routine is `bnx2fc_initiate_els()`, which allocates an ELS command, initializes middle-path buffers and firmware task context, starts optional timers, posts the SQE, links the command to `tgt->els_queue`, and rings the doorbell.

## Control Flow

ADISC, LOGO, and RLS intercepted from libfc are sent as firmware middle-path ELS commands. Completion builds an FC frame from firmware response header/payload, restores the original L2 OXID, and passes it to `bnx2fc_process_l2_frame_compl()`. RRQ retires resources for aborted exchanges. REC probes target exchange state for tape recovery and can trigger command repost, sequence cleanup, SRR, or ABTS. SRR completion accepts LS_ACC and falls back to ABTS on LS_RJT or retry exhaustion.

`bnx2fc_process_els_compl()` cancels timers, removes active-list linkage, copies response metadata from task context, invokes the callback, and drops the command reference. `bnx2fc_elsct_send()` wraps libfc so FLOGI/FDISC update data MAC selection and fabric LOGO clears it.

## State and Persistence Behavior

State is transient per ELS command and per original I/O reference. `bnx2fc_els_cb_arg` links firmware ELS commands to original I/O, L2 OXID, offsets, and callbacks. Flags such as `BNX2FC_FLAG_ELS_TIMEOUT`, `BNX2FC_FLAG_SRR_SENT`, `BNX2FC_FLAG_CMD_LOST`, `BNX2FC_FLAG_ISSUE_ABTS`, and `BNX2FC_FLAG_IO_COMPL` coordinate recovery. FLOGI/LOGO hooks update persistent `fcoe_port->data_src_addr`.

## Dependencies and Integration Points

The file integrates with libfc ELS structures and exchange callbacks, libfcoe FIP MAC selection, firmware task setup in `bnx2fc_hwi.c`, command allocation, cleanup/ABTS helpers, SCSI command state, and debug logging.

## Risks and Edge Cases

Timeout/completion races and reference ownership are high-risk. Atomic allocations can fail and drop responses. REC/SRR is tape-oriented and must avoid reposting after SCSI completion or ABTS. `bnx2fc_initiate_els()` validates opcode ranges but relies on callers for matching payloads. Lock drops around recursive REC/SRR sends allow state changes.

## Test Signals

Test offloaded ADISC/LOGO/RLS, FLOGI granted-MAC and FC-MAP handling, fabric LOGO MAC clearing, ELS timeout cleanup, RRQ after abort, tape REC/SRR for lost response/data, SRR rejection, allocation failures, link/session-not-ready rejection, and refcount leak checks.
