# sources/distributed-fs/ceph-client/drivers/scsi/bnx2i/bnx2i_hwi.c

## Purpose

`bnx2i_hwi.c` implements the hardware interface for bnx2i. It sizes and allocates queue pairs, builds firmware KWQEs and SQ WQEs, rings doorbells, processes CQEs and KCQEs, handles TCP/iSCSI error notifications, and provides the CNIC ULP callback table.

## Important APIs, Types, and Functions

Externally used functions include `bnx2i_arm_cq_event_coalescing()`, `bnx2i_get_rq_buf()`, `bnx2i_put_rq_buf()`, `bnx2i_send_iscsi_login()`, `bnx2i_send_iscsi_tmf()`, `bnx2i_send_iscsi_text()`, `bnx2i_send_iscsi_scsicmd()`, `bnx2i_send_iscsi_nopout()`, `bnx2i_send_iscsi_logout()`, `bnx2i_update_iscsi_conn()`, `bnx2i_ep_ofld_timer()`, `bnx2i_send_cmd_cleanup_req()`, `bnx2i_send_conn_destroy()`, `bnx2i_send_conn_ofld_req()`, `bnx2i_alloc_qp_resc()`, `bnx2i_free_qp_resc()`, `bnx2i_send_fw_iscsi_init_msg()`, `bnx2i_process_scsi_cmd_resp()`, `bnx2i_percpu_io_thread()`, and `bnx2i_map_ep_dbell_regs()`.

Important internal handlers include CQE processors for login, text, TMF, logout, NOP-In, async, reject, cleanup, fast-path notifications, connection update, TCP/iSCSI errors, offload completion, and destroy completion. The global `bnx2i_cnic_cb` exports callbacks to CNIC.

## Control Flow

Firmware init is started by `bnx2i_send_fw_iscsi_init_msg()`, which adjusts QP sizes, builds INIT1/INIT2 KWQEs, sets tolerated protocol error masks, and submits them through CNIC. Connection offload uses either 570x or 5771x KWQE layout, with different page-table offsets and additional 5771x WQE data. After login negotiation, `bnx2i_update_iscsi_conn()` sends negotiated digest, burst, PDU length, R2T, and ERL parameters.

Outbound iSCSI PDUs are written into the current SQ entry by `bnx2i_send_iscsi_*()` routines and posted by `bnx2i_ring_dbell_update_sq_params()`. The doorbell path updates SQ producer pointers, increments active command count, flushes WQE memory with `wmb()`, and either writes 570x doorbell registers or 577xx host-memory doorbell structures plus MMIO trigger.

Incoming KCQ notifications are dispatched by `bnx2i_indicate_kcqe()`. Fast-path notifications call `bnx2i_process_new_cqes()`, which walks CQEs by expected sequence number, dispatches by iSCSI opcode, queues SCSI command responses to per-CPU threads, handles middle-path responses inline, replenishes RQ entries, advances CQ pointers, and re-arms CQ event coalescing.

## State and Persistence Behavior

No durable storage is used. Runtime state includes QP DMA memory/page tables, CQ expected sequence number, SQ/RQ/CQ producer and consumer pointers, 577xx doorbell host-memory areas, endpoint state bits, active command counters, generic PDU response buffers, per-connection violation notification masks, per-CPU work queues, and HBA protocol error masks/statistics.

## Dependencies and Integration Points

The file depends on `bnx2i.h`, HSI structures, libiscsi task lookup and completion APIs, SCSI command/request CPU affinity, CNIC KWQE/KCQE callbacks, netdev events, PCI MMIO mapping, DMA allocation, timers, kthreads, and iSCSI offload netlink messaging.

## Risks and Edge Cases

Queue memory is shared with firmware; ordering before doorbell writes is critical. CQ processing relies on monotonically advancing `cq_req_sn`; missed or stale CQEs stall completions. SCSI completions are offloaded to per-CPU kthreads, but allocation failure falls back to inline processing. RQ accounting must match firmware behavior for zero-length unsolicited PDUs. Error masks can turn protocol violations into warnings, affecting recovery. 570x and 577xx page-table and doorbell formats differ substantially. Endpoint state transitions are woken by timers, CNIC callbacks, network events, and KCQEs, so missed wakeups can hang connect or teardown.

## Test Signals

Validate firmware init, queue-size adjustment, 570x and 577xx offload, doorbell mapping, login/text/logout/NOP/TMF/SCSI PDUs, SCSI sense data through RQ, CQ sequence wrap, per-CPU completion path and CPU offline fallback, event coalescing behavior, protocol warning/recovery masks, TCP FIN/RST/error recovery, netdev up/down/change events, and QP allocation/free failure injection.
