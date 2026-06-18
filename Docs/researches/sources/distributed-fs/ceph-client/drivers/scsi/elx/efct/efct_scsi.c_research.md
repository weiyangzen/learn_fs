# sources/distributed-fs/ceph-client/drivers/scsi/elx/efct/efct_scsi.c

## Purpose
`efct_scsi.c` is the transport-independent SCSI target dispatch layer between LIO/unsolicited FCP parsing and the EFCT HW layer. It allocates active SCSI IOs, builds HW SGLs, manages pending IO dispatch when HW XRIs are exhausted, translates HW completion status to SCSI status, sends target read/write/status/TMF responses, and handles target abort/BLS responses.

## Important APIs, Types, and Functions
Public allocation/lifetime functions are `efct_scsi_io_alloc`, `efct_scsi_io_free`, `_efct_scsi_io_free`, and `efct_scsi_io_complete`. Dispatch functions are `efct_scsi_io_dispatch`, `efct_scsi_io_dispatch_abort`, and `efct_scsi_check_pending`. Data/status APIs are `efct_scsi_send_rd_data`, `efct_scsi_recv_wr_data`, `efct_scsi_send_resp`, `efct_scsi_send_tmf_resp`, and `efct_scsi_tgt_abort_io`. BLS helpers are `efct_bls_send_rjt` and internal BA_ACC/BA_RJT callbacks. Internal helpers map SGs to HW SGEs, perform pending-list dispatch, and translate completion status.

## Control Flow
`efct_scsi_io_alloc` pulls a software IO from the pool, initializes a kref and generic fields, grabs a node reference, marks target command mode, and links the IO onto the node active list. Data movement APIs set `hio_type`, callbacks, transfer lengths, residual/auto-response flags, WQ steering flags, and FCP target parameters before calling `efct_scsi_io_dispatch`.

Dispatch first reuses an existing HIO for continuation phases. If pending work exists, it queues the IO, honoring low-latency insertion for data IOs. Otherwise it tries to allocate a HW IO. If allocation fails, it queues the IO and returns success to the upper layer. `efct_scsi_check_pending` drains pending IOs without recursion; abort IOs do not need a new HIO but are ordered through the pending list. Dispatch failure is reported asynchronously through a NOP mailbox callback.

Completion enters `efct_target_io_cb`, updates transferred length, maps SLI WCQE status/ext status to `enum efct_scsi_io_status`, sets completion flags, invokes the target callback, and then tries pending work. Abort completion maps abort-specific statuses, calls the saved abort callback on the original IO, drops the original IO reference, frees the abort software IO, and drains pending work.

## State and Persistence Behavior
State is volatile and command scoped. Pending dispatch is held in `xport->io_pending_list` protected by `io_pending_lock` with counters and a recursion guard. Active IO lifetime is protected by `io->ref`, node refs, and pool ownership. `io->transferred`, `wire_len`, `xfer_req`, `auto_resp`, callbacks, and HW fields track multi-phase commands.

## Dependencies and Integration Points
This file calls the IO pool, HW IO/SGL/send/abort APIs, LIO callbacks through function pointers, xport pending counters/stats, and FC/FCP response structures. It is called by `efct_lio.c` for target-core operations and by `efct_unsol.c` for BA_RJT/TMF flows.

## Risks
Pending-list ordering is central: an IO queued because no HIO was available must later dispatch with the correct callback and stale fields cleared. The low-latency insertion uses `list_add(&xport->io_pending_list, &io->io_pending_link)`, whose argument order appears reversed relative to normal Linux list API usage and is a high-value review target. Residual trimming mutates the caller-provided SGL entries for overrun handling. Abort IO allocation bypasses `efct_scsi_io_alloc`, so it has different active-list/refcount behavior. Error paths in `efct_hw_bls_send` and `efct_els_hw_srrs_send` can leave allocated HIOs if WQE formatting fails unless caller cleanup handles it.

## Test Signals
Exercise HW IO exhaustion and pending-list drain, low-latency queue insertion, continuation data phases, read/write residual and auto-good-response behavior, sense/status response formatting, local reject/DIF/timeout/shutdown status mapping, abort before HW IO allocation, abort while HW IO active, ABTS BA_ACC/BA_RJT flows, and pool/refcount balance after errors.
