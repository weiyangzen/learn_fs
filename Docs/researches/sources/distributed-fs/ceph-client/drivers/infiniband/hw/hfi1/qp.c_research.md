# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/qp.c

## Purpose
`qp.c` supplies HFI1-specific Queue Pair behavior for the RDMAVT core: supported work-request metadata, QP private allocation, send scheduling, SDMA/PIO wait handling, path/MTU validation, migration, error cleanup, and debug iteration.

## Important APIs, Types, And Functions
`hfi1_post_parms` declares supported RDMA, atomic, send, local invalidate, OPFN, and TID RDMA operations by QP type and flags. `hfi1_check_modify_qp()` validates address-vector service class against SDMA engines and PIO send contexts. `hfi1_modify_qp()` updates cached service class, SDMA engine, send context, header type, and OPFN state. `hfi1_setup_wqe()` enforces PMTU/VL15/SL constraints and decides whether immediate send scheduling is needed. `_hfi1_schedule_send()`, `hfi1_schedule_send()`, `hfi1_qp_wakeup()`, and `hfi1_qp_unbusy()` coordinate iowait-driven send progress. `qp_to_sdma_engine()` and `qp_to_send_context()` map QPs to hardware resources. Lifecycle helpers include `qp_priv_alloc()`, `qp_priv_free()`, `flush_qp_waiters()`, `stop_send_queue()`, `quiesce_qp()`, `notify_qp_reset()`, `notify_error_qp()`, and `hfi1_error_port_qps()`.

## Control Flow
When QP attributes change, HFI1 validates the new path, computes SC/VL-backed resources, updates 16B/9B header state, and initializes OPFN as needed. Posting a WQE lets HFI1 enforce length/MTU policy and force direct scheduling for small PIO-threshold packets. Send progress runs through `iowait`; if SDMA descriptors are unavailable, `iowait_sleep()` queues the txreq on the SDMA engine wait list and marks QP wait flags. Credit or DMA availability wakeups clear flags and reschedule IB or TID work. Reset/error/quiesce paths remove waiters, drain SDMA/PIO, flush queued txreqs, clear AHG/TID/OPFN state, and transition matching QPs to error when port SL mappings change.

## State And Persistence
QP-specific HFI1 state lives in `struct hfi1_qp_priv`: owner, AHG state, service class, SDMA engine, send context, iowait work queues, TID state, running packet-size estimate, and header type. Wait flags are split between RDMAVT `s_flags` and HFI1 private high bits. State is runtime-only and rebuilt when QPs are created or modified.

## Dependencies And Integration Points
The file depends on RDMAVT QP APIs, RDMA core verbs types, HFI1 SDMA, PIO send contexts, TID RDMA, OPFN, AH/LID helpers, iowait infrastructure, workqueues, tracepoints, and seq_file diagnostics. It is a major integration point between generic RDMA QP semantics and HFI1 hardware resource selection.

## Risks
Wait-state handling is race-sensitive: QP references are taken when queued and released on wake/removal, and busy flags are mirrored for TID second-leg sends. Incorrect locking around `s_lock`, engine waitlocks, or send-context waitlocks can strand QPs or double-release references. MTU conversion clamps OPA 10K to 8K for verbs compatibility, which can surprise callers. `hfi1_migrate_qp()` updates `priv->s_sde` but relies on later paths for send-context consistency.

## Test Signals
Cover QP modify validation for AV and alternate path, SC 0xf rejection, no-SDMA and no-PIO-resource cases, WQE length checks by QP type, immediate scheduling threshold, SDMA descriptor exhaustion and wakeup, PIO drain wait, reset/error cleanup, path migration event delivery, MTU conversion/clamping, and SL-specific port QP error iteration.
