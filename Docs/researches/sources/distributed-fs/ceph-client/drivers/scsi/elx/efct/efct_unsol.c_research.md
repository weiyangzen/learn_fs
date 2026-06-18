# sources/distributed-fs/ceph-client/drivers/scsi/elx/efct/efct_unsol.c

## Purpose
`efct_unsol.c` handles unsolicited FC frames received from RQ processing. It routes FCP command frames to the SCSI target path, routes BLS ABTS frames to abort handling, rejects unsupported TMFs when necessary, sends task-set-full/busy responses with send-frame when IO allocation fails, and forwards non-local frames to the EFC discovery library.

## Important APIs, Types, and Functions
The public entry points are `efct_unsolicited_cb`, `efct_dispatch_fcp_cmd`, and `efct_node_recv_abts_frame`. Internal helpers include `efct_node_find`, `efct_dispatch_frame`, `efct_dispatch_unsol_tmf`, `efct_validate_fcp_cmd`, `efct_populate_io_fcp_cmd`, `efct_get_flags_fcp_cmd`, send-frame response helpers, `efct_process_abts`, and rejection callbacks.

## Control Flow
HW RQ completion passes a sequence to `efct_unsolicited_cb`. `efct_dispatch_frame` inspects the FC header. FCP frames look up an `efct_node` by destination FCID and source FCID in `efct->lookup`; if found, `efct_dispatch_fcp_cmd` validates payload length, extracts LUN/CDB/task flags, allocates a SCSI IO, populates FC exchange metadata, and calls either `efct_scsi_recv_tmf` or `efct_scsi_recv_cmd`. If IO allocation fails, it constructs an FCP response with BUSY or TASK_SET_FULL and sends it via `efct_hw_send_frame`.

BLS frames are treated as ABTS. The code looks up the node, allocates a manufactured SCSI IO, finds the target IO by OX_ID/RX_ID, and if found submits an abort-task TMF. If not found, it sends BA_RJT. Frames not handled as FCP/BLS are forwarded to `efc_dispatch_frame`.

## State and Persistence Behavior
No persistent state is stored here. It consumes one RQ sequence at a time and uses `efct->lookup` to map FCID pairs to active target nodes. It increments `node->abort_cnt` for ABTS frames. Send-frame response context is carved out of the received payload buffer and freed when the send-frame callback reposts the original sequence.

## Dependencies and Integration Points
This file depends on HW sequence/RQ free APIs, SCSI IO/TMF/response APIs, EFC discovery dispatch, xarray node lookup, FC/FCP frame structures, and send-frame WQE support. It is invoked by `efct_hw_rqpair_process_rq`.

## Risks
Node lookup failures for ABTS return `-EIO` without freeing the sequence in the BLS not-found path handled by `efct_dispatch_frame`, which should be checked against caller free behavior. Unsupported additional CDB length returns `-EIO` after IO allocation without clearly freeing the IO. Send-frame response context reuses the payload DMA buffer as heap; insufficient buffer size errors must ensure the original sequence is eventually reposted. Direction flag naming can be confusing and should be tested against real FCP read/write commands.

## Test Signals
Test valid FCP read/write/no-data commands, invalid short payloads, invalid LUN conversion, additional CDB rejection, IO allocation failure busy/task-set-full response, TMF flag mapping/rejection, ABTS found/not-found paths, node lookup races during shutdown, and fallback to EFC discovery for non-FCP/BLS frames.
