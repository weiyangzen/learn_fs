# sources/distributed-fs/ceph-client/drivers/scsi/bnx2fc/bnx2fc_tgt.c

## Purpose

`bnx2fc_tgt.c` manages FCoE target sessions for the NetXtreme II offload driver. It reacts to libfc remote-port events, allocates connection IDs and queue-pair/session resources, sends offload/enable/disable/destroy requests to firmware, and flushes outstanding I/O during upload or failure.

## Important APIs, Types, and Functions

Primary entry points are `bnx2fc_rport_event_handler()`, `bnx2fc_tgt_lookup()`, and `bnx2fc_flush_active_ios()`. Internal helpers include `bnx2fc_offload_session()`, `bnx2fc_upload_session()`, `bnx2fc_init_tgt()`, `bnx2fc_alloc_conn_id()`, `bnx2fc_free_conn_id()`, `bnx2fc_alloc_session_resc()`, `bnx2fc_free_session_resc()`, and the offload/upload wait timers.

Important state is in `struct bnx2fc_rport`, `struct bnx2fc_hba`, `struct fcoe_port`, `struct fc_rport_priv`, firmware queues SQ/CQ/RQ/XFERQ/CONFQ/LCQ, page block lists, and connection DB memory.

## Control Flow

On `RPORT_EV_READY`, `bnx2fc_rport_event_handler()` filters out directory server, non-FCP, and non-target ports, then serializes with `hba_mutex`. It initializes the target, allocates DMA resources, sends a session offload request and waits for completion, maps doorbells, sends enable, and marks `BNX2FC_FLAG_SESSION_READY` on success. Context allocation failures are retried a few times.

On `RPORT_EV_LOGO`, `RPORT_EV_FAILED`, or `RPORT_EV_STOP`, the handler clears session-ready state and calls `bnx2fc_upload_session()`. Upload sends disable, waits for completion, flushes active I/O/TMF/ELS/retire queues, sends destroy if disable succeeded, waits for destroy, frees session resources, and releases the connection ID.

`bnx2fc_flush_active_ios()` marks `flush_in_prog`, removes commands from active queues, cancels timers, completes waiters where needed, either issues firmware cleanup or locally processes cleanup when disable failed, clears RRQ flags on retire queue entries, then waits for `num_active_ios` to drain.

## State and Persistence Behavior

The file maintains runtime-only target state: `hba->tgt_ofld_list`, `hba->next_conn_id`, `hba->num_ofld_sess`, target flags, queue indexes, DMA queue memory and PBLs, doorbell headers, wait queues, and timers. No data is persisted, but firmware-visible DMA allocations and connection IDs must be released on all failed offload and upload paths.

## Dependencies and Integration Points

It integrates with libfc remote-port events, the bnx2fc firmware request helpers in hardware-specific files, PCI DMA allocation, MMIO doorbell mapping, and SCSI I/O cleanup from `bnx2fc_io.c`. It also coordinates link-down shutdown through `hba->shutdown_wait`.

## Risks and Edge Cases

Offload and upload are blocking flows protected by `hba_mutex`; any missed wakeup on completion flags can stall remote-port processing until timer fallback. Upload timer deliberately fakes completion, so later paths must handle partially disabled firmware state. `bnx2fc_alloc_session_resc()` returns `-ENOMEM` without freeing partial allocations itself, relying on the caller's error path. Flush processing can race late firmware completions and SCSI aborts. Connection-ID allocation returns `-1` through an unsigned type, so callers must consistently compare against `(u32)-1` or assigned `-1`.

## Test Signals

Validate successful target login/offload/enable, context allocation retry, offload timeout, enable failure, rport logout/upload/destroy, disable failure, active I/O flush during link down, no leaked DMA queues after failed allocations, `tgt_lookup()` behavior for deleted rports, and shutdown wakeups when the last offloaded session disappears.
