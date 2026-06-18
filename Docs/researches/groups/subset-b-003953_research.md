# subset-b-003953 research

Grouped research for rdmavt and RXE software RDMA transport files under `sources/distributed-fs/ceph-client/drivers/infiniband/sw`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/qp.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/qp.c

## Purpose
`qp.c` is the central rdmavt queue-pair implementation shared by software verbs transports such as hfi1/qib-style providers. It owns QP number allocation, QP hash-table membership, QP create/modify/query/destroy verbs, send and receive posting, shared receive queue posting, RC retry/RNR timers, receive-WQE extraction, send completion advancement, SGE copy heuristics, and connected loopback for local RC/UC traffic.

## Important APIs, types, and functions
The exported surface includes `ib_rvt_state_ops`, `rvt_driver_qp_init()`, `rvt_qp_exit()`, `rvt_create_qp()`, `rvt_modify_qp()`, `rvt_destroy_qp()`, `rvt_query_qp()`, `rvt_post_recv()`, `rvt_post_send()`, `rvt_post_srq_recv()`, `rvt_get_rwqe()`, `rvt_comm_est()`, `rvt_rc_error()`, timer helpers, `rvt_qp_iter*()`, `rvt_send_complete()`, `rvt_copy_sge()`, and `rvt_ruc_loopback()`. Internal helpers manage QPN bitmap pages, driver-private QP allocation hooks, MR reference cleanup, UD address-handle attribute caching, and send queue reservation accounting. `struct rvt_qp`, `struct rvt_swqe`, `struct rvt_rq`, `struct rvt_krwq`, `struct rvt_rwq`, `struct rvt_sge_state`, and `struct rvt_wss` are the dominant state carriers.

## Control flow
Driver registration calls `rvt_driver_qp_init()` to allocate a QP hash table and initialize the QPN bitmap, including provider-reserved QPN ranges. `rvt_create_qp()` validates core capabilities, allocates send/receive queues, creates mmap metadata for user receive queues, initializes timers and locks, calls provider QP-private hooks, allocates a QPN, and returns mmap offsets to userspace when applicable. QPs enter the lookup table when transitioning from RESET to INIT in `rvt_modify_qp()`.

Send posting takes `s_hlock`, validates opcode support through `rdi->post_parms`, validates SGEs and lkeys, executes or queues local operations, computes PSN ranges, lets the provider finish WQE setup, updates queue head with a write barrier, and schedules or directly invokes the send engine. Receive posting writes RWQEs into a kernel or user-mapped ring. Receive consumption validates user-controlled head/tail values before using them, initializes SGEs, emits local protection errors for bad lkeys, and triggers SRQ limit events. Error/reset paths stop timers, notify providers, drain queues, drop MR refs, remove QPs from RCU lookup tables, and emit last-WQE events when needed.

## State and persistence
All persistent runtime state is in memory: QPN bitmaps, QP hash buckets, queue indices, MR references, timers, retry counters, PSNs/MSNs, pending mmap records, and port counters. User-mapped receive queues make ring indices user-visible, so the code repeatedly sanitizes head/tail values and uses RDMA UAPI atomic accessors. The working-set-size heuristic tracks destination pages atomically to choose cacheless copy behavior for large SGE copies. QPNs and object counts are released only after QP reset, RCU removal, and refcount drain.

## Dependencies and integration points
The file integrates with the RDMA core verbs ABI, rdmavt provider hooks in `rvt_dev_info.driver_f`, CQ/MR/AH/mmap/mcast helpers, RCU lookup, timers/hrtimers, tracepoints, OPA address validation, and user copy helpers. Providers supply send scheduling, PMTU translation, QP private allocation, reset/error notifications, and optional QPN allocation.

## Risks
The highest-risk areas are lock ordering across `r_lock`, `s_hlock`, and `s_lock`; user-writable queue indices; MR reference lifetime while deregistration races active QPs; reset/error paths that temporarily drop locks; and timer callbacks running while QPs are being destroyed. `rvt_ruc_loopback()` combines requester and responder state, remote-key validation, atomics, local invalidation, receive completions, RNR retry handling, and RC error transition in one path, making regression tests important. QPN bitmap allocation depends on provider QPN increments, reserved ranges, AIP prefixes, and QoS bit assumptions.

## Test signals
Useful signals include QP lifecycle tests for all supported QP types, QPN reuse and reserved ranges, post-send/post-recv validation, user mmap receive queues with corrupt head/tail values, MR deregistration while WQEs reference lkeys, RC timeout/RNR retry behavior, SRQ limit events, loopback SEND/RDMA/atomic/local-invalidate flows, SQ drain and last-WQE events, and build coverage with lockdep, KASAN, and tracepoint compilation enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/qp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/qp.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/qp.h

## Purpose
`qp.h` is the local rdmavt QP interface used by `vt.c`, `srq.c`, provider-facing code, and other rdmavt modules. It exposes QP lifecycle verbs, send/receive posting entry points, receive-queue allocation, and working-set-size initialization.

## Important APIs, types, and functions
The header includes `<rdma/rdmavt_qp.h>` and declares `rvt_driver_qp_init()`, `rvt_qp_exit()`, `rvt_create_qp()`, `rvt_modify_qp()`, `rvt_destroy_qp()`, `rvt_query_qp()`, `rvt_post_recv()`, `rvt_post_send()`, `rvt_post_srq_recv()`, `rvt_wss_init()`, `rvt_wss_exit()`, and `rvt_alloc_rq()`.

## Control flow
This header does not execute control flow. It defines the compilation contract that lets `vt.c` install QP operations into `ib_device_ops`, lets `srq.c` reuse receive-queue allocation, and lets the module registration path initialize and tear down QP-related global device state.

## State and persistence
No state is stored in the header. Its declarations govern in-memory state owned by `qp.c`, especially QP hash tables, QPN maps, per-QP rings, and WSS tables.

## Dependencies and integration points
The header is an internal bridge between rdmavt's public RDMA structures and local implementation files. It depends on RDMA core QP type definitions and is included by modules that need the QP verbs to be available without including `qp.c` internals.

## Risks
Prototype drift here breaks `ib_device_ops` initialization and provider builds. Since the header exports functions used from multiple rdmavt compilation units, signature changes must be coordinated with `vt.c`, `srq.c`, and all provider references.

## Test signals
Build coverage of `CONFIG_INFINIBAND_RDMAVT` consumers is the primary signal. Compile failures in `vt.c`, `srq.c`, or provider drivers catch most contract mismatches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/qp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/rc.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/rc.c

## Purpose
`rc.c` contains small but critical Reliable Connection helpers shared by rdmavt providers: AETH credit encoding/decoding and send SGE rewind. It supports RC flow control and retransmission recovery.

## Important APIs, types, and functions
`rvt_compute_aeth()` builds an Acknowledge Extended Transport Header value using `qp->r_msn` and receive queue credit information. `rvt_get_credit()` consumes AETH credits on the requester side, updating `qp->s_lsn`, unlimited-credit state, and wait flags. `rvt_restart_sge()` resets an SGE state to the beginning of a WQE and skips a requested byte length. The file uses a 31-entry credit table and `IB_AETH_*` bit definitions.

## Control flow
Responder ACK generation calls `rvt_compute_aeth()`. For SRQ-backed QPs, credit is marked invalid because SRQs do not advertise per-QP credits. For per-QP receive queues, it reads cached `kwq->count`, and if empty computes credits from sanitized head/tail ring indices. It then binary-searches the credit table to choose the largest encoded credit not exceeding the available RWQE count.

Requester ACK handling calls `rvt_get_credit()` with `s_lock` held. Invalid credit enables unlimited sending and wakes send processing when waiting on SSN credit. Valid credit extends `s_lsn` only if it advances beyond the previous value. `rvt_restart_sge()` is used by retry paths to rebuild the current SGE cursor from a WQE.

## State and persistence
State is entirely in the QP: `r_msn`, receive-queue counts, user or kernel ring indices, `s_lsn`, `s_flags`, and SGE cursor fields. The helper deliberately tolerates fuzzy concurrent reads of head/tail because subsequent ACKs correct credit approximation.

## Dependencies and integration points
The file depends on `rdmavt_qp.h`, `ib_hdrs.h`, RDMA UAPI atomic accessors, and provider send scheduling through `rdi->driver_f.schedule_send()`. It is used by RC responder/requester code in provider drivers and by rdmavt retry logic.

## Risks
Credit encoding mistakes can deadlock senders or overrun receive queues. User-mapped queue indices must remain sanitized before credit calculations. `rvt_get_credit()` assumes `s_lock` is held; callers that violate this can race wait flags and send scheduling.

## Test signals
RC tests should cover SRQ vs non-SRQ AETH generation, empty and partially filled receive queues, corrupt user head/tail values, invalid/unlimited credits, credit wrap via MSN masking, and retry paths that call `rvt_restart_sge()` at packet boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/rc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/srq.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/srq.c

## Purpose
`srq.c` implements rdmavt shared receive queue lifecycle verbs: driver initialization, create, modify/resize, query, and destroy. It shares receive queue allocation and mmap mechanisms with QP receive queues.

## Important APIs, types, and functions
The exported functions are `rvt_driver_srq_init()`, `rvt_create_srq()`, `rvt_modify_srq()`, `rvt_query_srq()`, and `rvt_destroy_srq()`. Core state lives in `struct rvt_srq`, `struct rvt_rq`, `struct rvt_rwq`, `struct rvt_krwq`, and `struct rvt_mmap_info`.

## Control flow
Device registration initializes `n_srqs_lock` and the allocated count. Create accepts only `IB_SRQT_BASIC`, validates max WR/SGE against device limits, allocates a one-extra-entry circular queue via `rvt_alloc_rq()`, creates mmap metadata for user SRQs, initializes the SRQ limit, enforces `max_srq`, and appends mmap info to the pending list. Modify can resize the queue by allocating a temporary ring, verifying the requested size and current head/tail values, copying outstanding RWQEs from old tail to head, swapping in the new ring under `c_lock`, updating mmap metadata, and freeing the old ring. Limit-only modification just updates `srq->limit` under the queue lock.

## State and persistence
SRQ state is in memory: queue size, max SGE, head/tail/count, limit threshold, user mmap metadata, and the device SRQ allocation count. Resize preserves outstanding WR IDs and SGEs. User queues expose head/tail through mmap and therefore require validation before resize.

## Dependencies and integration points
The file depends on `rvt_alloc_rq()`, `rvt_create_mmap_info()`, `rvt_update_mmap_info()`, `rvt_release_mmap_info()`, RDMA udata copying, and QP receive consumption in `rvt_get_rwqe()`, which emits SRQ limit events.

## Risks
Resize is the sensitive path: it copies live queue entries while userspace may own ring indices, swaps pointers under lock, and updates mmap state after old mappings may exist. The limit-only branch lacks braces around the `else` body but assigns the same value once; this should be kept clear if edited. Cleanup must preserve kref semantics for user mappings.

## Test signals
Test SRQ create limits, unsupported SRQ types, posting and consuming from QPs sharing an SRQ, resize larger/smaller with queued WRs, invalid user head/tail values, mmap offset updates after resize, SRQ limit events, and allocation count under repeated create/destroy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/srq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/srq.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/srq.h

## Purpose
`srq.h` is the local interface for rdmavt shared receive queue lifecycle support.

## Important APIs, types, and functions
It includes `<rdma/rdma_vt.h>` and declares `rvt_driver_srq_init()`, `rvt_create_srq()`, `rvt_modify_srq()`, `rvt_query_srq()`, and `rvt_destroy_srq()`.

## Control flow
The header has no runtime control flow. Its declarations are consumed by `vt.c` when installing SRQ verbs and by `qp.c` when posting to and consuming from shared receive queues.

## State and persistence
No state is stored here. It exposes operations over `struct rvt_srq` state allocated and managed by the RDMA core object model.

## Dependencies and integration points
The header binds rdmavt SRQ support to RDMA core objects and internal implementation files. It should stay in sync with `srq.c` and `vt.c`.

## Risks
Prototype drift causes build failures or incorrect `ib_device_ops` wiring. Since SRQ objects interact with user mmap state, changes to signatures carrying `ib_udata` or attributes require careful ABI review.

## Test signals
Compile coverage for rdmavt and provider drivers catches header/implementation mismatch. Runtime SRQ verbs tests validate that the functions exposed through this header are correctly installed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/srq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/trace.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/trace.c

## Purpose
`trace.c` is the tracepoint instantiation unit for rdmavt. It defines `CREATE_TRACE_POINTS` once and includes the aggregate trace header so the trace events declared in the individual `trace_*.h` files get generated.

## Important APIs, types, and functions
There are no functions. The important mechanism is `#define CREATE_TRACE_POINTS` followed by `#include "trace.h"`, which pulls in `trace_rvt.h`, `trace_qp.h`, `trace_tx.h`, `trace_mr.h`, `trace_cq.h`, and `trace_rc.h`.

## Control flow
No runtime control flow is implemented directly. At build time, the Linux tracepoint framework emits event descriptors and callsites for all rdmavt trace events.

## State and persistence
No driver state is owned here. Tracepoint enablement state is owned by the kernel tracing subsystem.

## Dependencies and integration points
This file depends on every included trace header being tracepoint-safe and using `TRACE_INCLUDE_FILE` correctly. It integrates with ftrace/perf trace events and rdmavt callsites such as QP insertion/removal, send posting, CQ events, MR mapping, and RC timeout/RNR handling.

## Risks
Adding `CREATE_TRACE_POINTS` in more than one compilation unit would cause duplicate definitions. Broken include guards or mismatched `TRACE_INCLUDE_FILE` values in individual trace headers can break module builds.

## Test signals
Build `rdmavt` with tracing enabled, verify trace event files appear under tracing for `rvt`, `rvt_qp`, `rvt_tx`, `rvt_mr`, `rvt_cq`, and `rvt_rc`, and enable events while exercising QP/CQ/MR paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/trace.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/trace.h

## Purpose
`trace.h` aggregates all rdmavt tracepoint headers and defines common device-name helper macros for trace records.

## Important APIs, types, and functions
`RDI_DEV_ENTRY(rdi)` creates a trace string field named `dev` from `rvt_get_ibdev_name(rdi)`. `RDI_DEV_ASSIGN(rdi)` assigns that string in tracepoint fast paths. The header includes the trace systems for rvt core, QP, TX, MR, CQ, and RC.

## Control flow
There is no direct runtime flow. The macros are expanded by individual trace events so every event can include the rdmavt device name consistently.

## State and persistence
No persistent state. Trace event payloads include transient device strings copied at event time.

## Dependencies and integration points
It depends on `rvt_get_ibdev_name()` being available through included RDMA headers. It is included by `trace.c` for instantiation and by implementation files for tracepoint call declarations.

## Risks
Macro changes affect every trace event payload. If the common string field name changes, existing tracing scripts and debug workflows may break.

## Test signals
Tracepoint build coverage and runtime checks that emitted events include the expected `dev` field across all rdmavt trace systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/trace_cq.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/trace_cq.h

## Purpose
`trace_cq.h` declares rdmavt completion queue trace events for CQ creation and CQ entry polling/posting.

## Important APIs, types, and functions
The `rvt_cq_template` event class records whether a CQ is user mapped, requested CQE count, completion vector, CPU, and flags. `rvt_cq_entry_template` records work completion fields including `wr_id`, status, opcode, byte length, QPN, CQ index, flags, and immediate data. Events include `rvt_create_cq`, `rvt_cq_enter`, and `rvt_cq_poll`. `show_wc_opcode()` maps selected `IB_WC_*` opcodes to names.

## Control flow
No driver control flow is implemented. CQ code emits these tracepoints around CQ allocation and completion enqueue/poll paths, allowing correlation of CQ sizing, work completion production, and consumers.

## State and persistence
Trace events snapshot CQ and WC fields; they do not retain driver state. They expose transient queue indices and completion metadata through the tracing subsystem.

## Dependencies and integration points
The header depends on Linux tracepoint infrastructure, `rdmavt_cq.h`, `ib_verbs.h`, and the common `RDI_DEV_ENTRY` macros from `trace.h`. It is instantiated through `trace.c`.

## Risks
The trace fast assignment assumes `wc->qp` is valid. Tracepoints added around error or synthetic completions must preserve that invariant. Opcode maps can become stale if new work completion opcodes are used but not added to `show_wc_opcode()`.

## Test signals
Enable CQ trace events during CQ create, completion enqueue, poll, overflow/error tests, and user vs kernel CQ creation. Build with new RDMA opcodes catches enum-name drift only if the symbolic map is updated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/trace_cq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/trace_mr.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/trace_mr.h

## Purpose
`trace_mr.h` declares memory-region and SGE trace events for rdmavt memory mapping and lkey validation/debugging paths.

## Important APIs, types, and functions
`rvt_mr_template` records MR identity, IOVA, user base, lkey, segment indexes, virtual address, page, length, and offset for page/FMR/user segment events. `rvt_sge_template` records an SGE, incoming `ib_sge`, MR pointer, virtual and requested addresses, lkey, lengths, indexes, and whether the PD is user-owned. `rvt_map_mr_sg` records fast-reg scatterlist mapping arguments.

## Control flow
The header only defines tracepoint schemas. MR implementation code emits these events while building MR page segments, joining SGEs, and mapping scatterlists for memory registration.

## State and persistence
Trace payloads snapshot MR/SGE fields and can expose kernel virtual addresses and page pointers to privileged tracing consumers. Driver state is unchanged by tracing.

## Dependencies and integration points
It depends on `ib_verbs.h`, `rdma_vt.h`, `rdmavt_mr.h`, local `mr.h`, and tracepoint macros. It integrates with rdmavt MR registration, fast registration, and SGE validation paths.

## Risks
Pointer and address-heavy trace payloads are useful for debugging but must remain limited to kernel tracing contexts. The fast assignment currently sets `__entry->n = sge->m`, which looks suspicious because both `m` and `n` become the same value; changes should verify intended SGE index reporting. Type or layout changes in MR/SGE structures require trace field updates.

## Test signals
Enable MR trace events during user MR registration, FMR/fast-reg mapping, lkey validation, and SG list coalescing. Validate emitted `m`/`n`, lkey, and length fields against expected MR layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/trace_mr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/trace_qp.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/trace_qp.h

## Purpose
`trace_qp.h` declares QP hash-table and RNR NAK timer trace events for rdmavt.

## Important APIs, types, and functions
The `rvt_qphash_template` event class records QPN and hash bucket for `rvt_qpinsert` and `rvt_qpremove`. The `rvt_rnrnak_template` event class records QPN, hrtimer address, send flags, and timeout for `rvt_rnrnak_add`, `rvt_rnrnak_timeout`, and `rvt_rnrnak_stop`.

## Control flow
No control flow lives here. `qp.c` emits hash events when non-special QPs are inserted into or removed from the RCU hash table and emits RNR timer events when RNR retry timers are armed, fired, or stopped.

## State and persistence
Events snapshot QP fields and timer pointers. The tracing subsystem stores emitted records when enabled; QP state is not mutated by tracepoints.

## Dependencies and integration points
It depends on `rdmavt_qp.h`, `ib_verbs.h`, and common trace macros. It helps debug QP lookup lifetime and RNR retry behavior in `qp.c`.

## Risks
Tracepoints assume QP device pointers are live at emit time. They should remain inside sections where QP references or locks guarantee lifetime. Hash trace coverage excludes special QP0/QP1 insertion, so users should not expect complete QP lifecycle visibility from only these events.

## Test signals
Enable QP events while creating/destroying RC/UC/UD QPs and forcing RNR NAKs. Check that insert/remove bucket values match QPN hash behavior and timer events pair with retry scheduling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/trace_qp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/trace_rc.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/trace_rc.h

## Purpose
`trace_rc.h` declares Reliable Connection trace events for timeout-driven RC restart debugging.

## Important APIs, types, and functions
The `rvt_rc_template` event class records device name, QPN, send flags, a supplied PSN, send PSN trackers (`s_psn`, `s_next_psn`, `s_sending_psn`, `s_sending_hpsn`), and receive PSN. The concrete event is `rvt_rc_timeout`.

## Control flow
The tracepoint is emitted by the RC retry timer path in `qp.c` when a response is missing and provider restart scheduling is requested.

## State and persistence
Only trace records persist in the tracing subsystem. The fields are a snapshot of QP transport sequence state at timeout time.

## Dependencies and integration points
It depends on Linux tracepoint infrastructure and `rdmavt_qp.h`. It is useful with provider send/retry traces to explain retransmission windows and PSN divergence.

## Risks
If QP PSN fields are renamed or semantics shift, this trace schema must be updated together with timeout logic. The event is timeout-specific, so it does not cover all RC retry reasons.

## Test signals
Force RC packet loss or delayed ACKs, enable `rvt_rc_timeout`, and verify PSN fields identify the restart point used by provider `notify_restart_rc()` and send scheduling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/trace_rc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/trace_rvt.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/trace_rvt.h

## Purpose
`trace_rvt.h` declares a generic rdmavt debug trace event.

## Important APIs, types, and functions
`TRACE_EVENT(rvt_dbg)` records the rdmavt device name and a string message supplied by the caller. It uses `RDI_DEV_ENTRY` and `RDI_DEV_ASSIGN` from the aggregate trace header.

## Control flow
The header does not implement driver flow. Callers such as registration/unregistration paths emit `trace_rvt_dbg()` to mark high-level lifecycle transitions.

## State and persistence
It records transient debug messages into the tracing subsystem. No rdmavt state is changed.

## Dependencies and integration points
It depends on tracepoint infrastructure, `ib_verbs.h`, and `rdma_vt.h`. It complements more structured QP/CQ/MR trace systems with low-volume lifecycle messages.

## Risks
The event stores caller-provided strings, so callsites should pass stable string data rather than short-lived buffers. Overuse would reduce the usefulness of structured tracepoints.

## Test signals
Enable `rvt:rvt_dbg` while registering and unregistering an rdmavt provider and verify device names and messages are emitted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/trace_rvt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/trace_tx.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/trace_tx.h

## Purpose
`trace_tx.h` declares send-queue trace events for rdmavt post-send and send-completion paths.

## Important APIs, types, and functions
`rvt_post_one_wr` records WQE pointer, WR ID, send flags, QPN, QP type, PSN/lPSN, SSN, length, opcode, queue size/availability/head/last, PID, and SGE counts. `rvt_qp_send_completion` records WQE pointer, WR ID, QPN/QP type, length, completed index, SSN, opcode, and send flags. `show_wr_opcode()` maps common `IB_WR_*` opcodes to names.

## Control flow
`qp.c` emits `rvt_post_one_wr` after validating and filling a send WQE but before advancing the head. It emits `rvt_qp_send_completion` while completing a WQE and updating send queue cursors.

## State and persistence
Events snapshot send queue state. They can expose kernel pointers and user WR IDs through tracing but do not mutate queues.

## Dependencies and integration points
It depends on RDMA core work request enums, `rdmavt_qp.h`, and tracepoint infrastructure. It is a key diagnostic companion for provider send engines and CQ completion traces.

## Risks
Opcode maps must track RDMA core additions. Tracepoints should remain inside regions where the WQE and QP are stable. Since `rvt_post_one_wr` emits before `s_head` advances, trace consumers must interpret `head` as the pre-advance slot.

## Test signals
Enable TX events while posting SEND, RDMA, atomic, local invalidate, and fast-reg WRs. Verify PSN ranges, queue availability, reserve usage, completion index advancement, and matching CQ completion records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/trace_tx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/vt.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/vt.c

## Purpose
`vt.c` is the rdmavt library registration and RDMA core operations file. It allocates/deallocates rdmavt-backed IB devices, installs common `ib_device_ops`, validates provider hook coverage, initializes common rdmavt subsystems, registers/unregisters devices with the IB core, and initializes per-port state.

## Important APIs, types, and functions
Module init/exit call `rvt_driver_cq_init()` and `rvt_cq_exit()`. Exported APIs include `rvt_alloc_device()`, `rvt_dealloc_device()`, `rvt_register_device()`, `rvt_unregister_device()`, and `rvt_init_port()`. Static verbs handlers cover query/modify device/port, pkey/gid queries, ucontext allocation/deallocation, immutable port data, and `rvt_dev_ops` binding for AH, CQ, PD, MR, QP, SRQ, mmap, and multicast operations.

## Control flow
Provider drivers allocate an rdmavt device, fill `rdi->dparms`, ports, and `driver_f` hooks, then call `rvt_register_device()`. Registration first validates hook support for each rdmavt-managed verb through `check_support()`, installs common IB ops, initializes mmap, QP, AH count, SRQ, multicast, MR, WSS, CQ and PD state, updates user verbs command masks and device defaults, registers the IB device, and creates MAD agents. Failure unwinds WSS, MR, and QP state. Unregistration frees MAD agents, unregisters the IB device, and tears down WSS, MR, and QP state.

## State and persistence
State is per `struct rvt_dev_info`: port pointer array, device attributes, operation tables, counters, subsystem allocation tables, pkey tables, capability flags, and provider callbacks. It is in-memory only and persists until provider unregister.

## Dependencies and integration points
The file integrates rdmavt with RDMA core `ib_device_ops`, provider-specific `driver_f` hooks, MAD agent support, mmap/CQ/MR/QP/SRQ/AH/mcast modules, PCI-backed logging macros, and optional provider ucontext hooks.

## Risks
`check_support()` is the guardrail that prevents rdmavt from installing verbs without provider support; incomplete checks can produce runtime null calls. Registration unwind must match initialization order. `rvt_modify_device()` returns unsupported unless a provider overrides it, so feature additions must decide where responsibility belongs. Query functions assume provider-maintained port and pkey data are current.

## Test signals
Build and load an rdmavt provider, verify registration failure for missing hooks, exercise every installed verbs op, confirm uverbs ABI version and command masks, test port query/modify/pkey/gid behavior, and run unload tests under active object teardown to catch subsystem leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/vt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/vt.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/vt.h

## Purpose
`vt.h` is the central internal rdmavt include. It gathers subsystem headers and defines device-scoped logging macros used across rdmavt implementation files.

## Important APIs, types, and functions
It includes PD, QP, AH, MR, SRQ, multicast, mmap, CQ, and MAD headers. It defines `rvt_pr_info()`, `rvt_pr_warn()`, `rvt_pr_err()`, and `rvt_pr_err_ratelimited()` wrappers that log through `rdi->driver_f.get_pci_dev(rdi)` with the IB device name. It also defines `ibport_num_to_idx()` to convert one-based IB port numbers to zero-based arrays.

## Control flow
No direct flow is implemented. The inline port-index helper is used wherever RDMA core port numbers address `rdi->ports[]`.

## State and persistence
No state is stored here. The macros rely on provider `rvt_dev_info` state and a valid PCI device callback.

## Dependencies and integration points
The header depends on `<rdma/rdma_vt.h>`, `<linux/pci.h>`, and all local rdmavt subsystem headers. It is the common include point for files that need broad access to internal rdmavt APIs.

## Risks
Logging macros assume `get_pci_dev` is present and returns a valid device, which `vt.c` enforces during registration. `ibport_num_to_idx()` does no validation; callers must validate port numbers before indexing.

## Test signals
Build coverage across rdmavt and providers catches include-order problems. Runtime port query/modify tests with invalid port numbers should validate callers rather than this helper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/vt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/Kconfig

## Purpose
`Kconfig` defines the `RDMA_RXE` soft-RoCE driver option and its kernel configuration dependencies.

## Important APIs, types, and functions
The option is `config RDMA_RXE`, a tristate named "Software RDMA over Ethernet (RoCE) driver". It depends on `INET`, `PCI`, `INFINIBAND`, `64BIT`, and `INFINIBAND_VIRT_DMA`, and selects `NET_UDP_TUNNEL` and `CRC32`.

## Control flow
No runtime flow. Kconfig controls whether `rdma_rxe.o` is built into the kernel, built as a module, or omitted.

## State and persistence
Configuration state persists in the kernel `.config`. It determines module availability and optional build integration.

## Dependencies and integration points
The help text documents RXE as a software RDMA transport over the Linux network stack, interoperable with RoCE adapters or other RXE systems, and points users to rdma-core RXE configuration documentation. The selected symbols match runtime use of UDP tunnel networking and CRC32 ICRC support.

## Risks
Dependency changes can allow unsupported architectures or missing network/RDMA features to build RXE. The `64BIT` dependency matters because the uverbs ABI note in `rxe.h` distinguishes 32-bit layouts.

## Test signals
Kconfig tests should verify `RDMA_RXE=m/y` builds only when dependencies are met, that selecting RXE pulls required CRC and UDP tunnel support, and that module load works with rdma-core tooling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/Makefile -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/Makefile

## Purpose
`Makefile` declares the RXE module object composition.

## Important APIs, types, and functions
`obj-$(CONFIG_RDMA_RXE) += rdma_rxe.o` builds the driver. `rdma_rxe-y` links core RXE files for device setup, requester/completer/responder/receiver paths, pools, queues, verbs, address vectors, SRQ/QP/CQ/MR/MW, opcode tables, mmap, ICRC, multicast, tasks, net, hardware counters, and namespaces. `rdma_rxe-$(CONFIG_INFINIBAND_ON_DEMAND_PAGING) += rxe_odp.o` conditionally includes ODP support.

## Control flow
No runtime flow. The build system uses the object list to produce the `rdma_rxe` module or built-in object.

## State and persistence
Build state is determined by Kconfig and object dependencies. Runtime state is owned by the linked files.

## Dependencies and integration points
The file integrates RXE with the kernel kbuild system and optional ODP compilation. Object order matters for module linkage but not high-level behavior.

## Risks
Omitting a file from `rdma_rxe-y` creates unresolved symbols or missing feature paths. Adding new source files requires updating this list. ODP declarations in `rxe_loc.h` must stay compatible with the conditional `rxe_odp.o` inclusion.

## Test signals
Run kernel builds with `CONFIG_RDMA_RXE=m`, built-in, and with/without `CONFIG_INFINIBAND_ON_DEMAND_PAGING` to catch object-list and symbol regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe.c

## Purpose
`rxe.c` is the RXE module/device lifecycle file. It initializes soft-RoCE device attributes, port attributes, object pools, multicast/mmap state, RDMA link operations, module-level namespace/net notifiers, and registration with the RDMA core.

## Important APIs, types, and functions
Key functions are `rxe_dealloc()`, `rxe_init_device_param()`, `rxe_init_port_param()`, `rxe_init_ports()`, `rxe_init_pools()`, `rxe_init()`, `rxe_set_mtu()`, `rxe_add()`, `rxe_newlink()`, `rxe_dellink()`, `rxe_module_init()`, and `rxe_module_exit()`. It defines RDMA link ops of type `"rxe"` and optional ODP device ops for `advise_mr`.

## Control flow
Module init creates the RXE workqueue, initializes namespace support, registers net notifiers, and registers RDMA link ops. `rdma link add ... type rxe netdev ...` enters `rxe_newlink()`, which rejects VLAN devices, prevents duplicate RXE devices on the same netdev, initializes networking, and delegates to `rxe_net_add()`. `rxe_add()` initializes attributes/pools/locks/multicast state, sets MTU from the parent netdev, attaches link ops, and registers the IB device. Module exit unregisters link ops, unregisters the RXE driver, tears down networking/workqueue/namespace state, and logs unload.

## State and persistence
Per-device state includes RDMA device attributes, raw GID derived from the parent MAC or random address, one port's attributes, object pools for all RXE object types, mmap offsets and pending maps, multicast RB tree, counters, and locks. State is in-memory and tied to the RDMA link/device lifetime.

## Dependencies and integration points
RXE integrates with RDMA netlink link ops, the network device layer, address configuration helpers, RXE net/namespace modules, RDMA core registration, object pools, multicast, mmap, and optional ODP capability advertisement.

## Risks
Device lifetime spans netdev notifiers, RDMA link deletion, object pool cleanup, and module unload. Duplicate device detection must balance the `ib_device_get_by_netdev()` reference with `ib_device_put()`. Random GID fallback for devices without hardware addresses can affect connection identity. ODP capability bits must match actual compiled support.

## Test signals
Test module load/unload, `rdma link add/delete`, duplicate and VLAN rejection, netdev down/up/MTU changes, ODP capability advertisement with and without ODP config, object leak warnings in `rxe_dealloc()`, and namespace cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe.h

## Purpose
`rxe.h` is the top-level RXE internal header. It centralizes RDMA/network includes, debug/error logging macros, ABI constants, common prototypes, and the helper that maps a netdev to an RXE device.

## Important APIs, types, and functions
It defines `RXE_UVERBS_ABI_VERSION`, `RXE_ROCE_V2_SPORT`, logging macros for device/object types, `rxe_set_mtu()`, `rxe_add()`, `rxe_rcv()`, `rxe_get_dev_from_net()`, port state helpers, and the external workqueue `rxe_wq`. It includes RXE network, opcode, header, parameter, verbs, and local declarations.

## Control flow
The inline `rxe_get_dev_from_net()` calls `ib_device_get_by_netdev(ndev, RDMA_DRIVER_RXE)` and converts the returned IB device to `struct rxe_dev`; callers must release the reference. Other declarations are implemented in RXE source files.

## State and persistence
No state is owned in the header. Constants affect user ABI and default packet behavior; logging macros shape diagnostic output.

## Dependencies and integration points
The header integrates RXE with RDMA core headers, user verbs structures, address/GID helpers, sk_buffs, and internal RXE modules. It is included by most RXE implementation files.

## Risks
ABI version changes affect userspace providers. Logging macros dereference object/device pointers, so callsites must ensure object lifetime. `rxe_get_dev_from_net()` reference ownership must be followed exactly to avoid leaks or use-after-put.

## Test signals
Build all RXE objects after header changes, run uverbs compatibility tests, and use refcount/debug builds around duplicate-device and netdev-delete paths that call `rxe_get_dev_from_net()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_av.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_av.c

## Purpose
`rxe_av.c` converts RDMA address-handle attributes into RXE address vectors, validates address attributes, fills IP addressing metadata, and resolves the address vector used for outgoing packets.

## Important APIs, types, and functions
Functions include `rxe_init_av()`, `rxe_av_chk_attr()`, `rxe_ah_chk_attr()`, `rxe_av_from_attr()`, `rxe_av_to_attr()`, `rxe_av_fill_ip_info()`, and `rxe_get_av()`. Core state is `struct rxe_av`, `struct rdma_ah_attr`, `struct ib_global_route`, `struct rxe_ah`, `struct rxe_qp`, and `struct rxe_pkt_info`.

## Control flow
AH/QP attribute validation calls `chk_attr()`, which verifies GRH SGID index and network type for RXE when GRH is set. Initialization copies GRH fields, port number, source/destination IP addresses, network type, and destination MAC. Connected QPs use `qp->pri_av`. UD sends use either a new-provider AH number looked up from the AH pool with PD validation, or an embedded legacy AV in the WQE.

## State and persistence
Address vectors persist inside AH objects, QP primary AVs, or WQEs. `rxe_get_av()` may return a referenced AH through `ahp`; callers must drop that reference. It also populates transient packet routing data used by the network transmit path.

## Dependencies and integration points
The file depends on RDMA AH/GID helpers, RXE object pools, QP/PD/AH state, and network address type definitions. It feeds `rxe_req.c` and `rxe_net.c` transmit paths.

## Risks
SGID index validation uses `>` rather than `>=` against `gid_tbl_len`, so boundary expectations should be checked against RDMA core conventions. AH pool lookup and PD matching are critical to avoid using another PD's AH. Legacy embedded AV support must remain compatible with older userspace providers.

## Test signals
Test AH creation and QP modify with IPv4/IPv6 GIDs, invalid SGID indexes and network types, connected QP sends, UD sends with AH numbers, legacy UD embedded AVs, PD mismatch rejection, and AH reference release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_av.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_comp.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_comp.c

## Purpose
`rxe_comp.c` implements the requester-side completer state machine for RXE RC traffic. It processes ACK/NAK/read/atomic responses, completes send WQEs, manages retry/RNR timers, flushes queues on error/reset, and posts send CQEs.

## Important APIs, types, and functions
External entry points are `retransmit_timer()`, `rxe_comp_queue_pkt()`, and `rxe_completer()`. Important helpers include `get_wqe()`, `check_psn()`, `check_ack()`, `do_read()`, `do_atomic()`, `make_send_cqe()`, `do_complete()`, `complete_ack()`, `complete_wqe()`, `flush_send_queue()`, `free_pkt()`, and `reset_retry_timer()`. The `enum comp_state` names the state-machine stages.

## Control flow
Incoming response packets are queued on `qp->resp_pkts` and schedule the QP send task. `rxe_completer()` first handles invalid, ERR, or RESET QPs by draining response packets and flushing send WQEs. Otherwise it consumes an ACK packet, finds the oldest send WQE, validates PSN ordering, checks opcode/ACK/NAK semantics, copies read or atomic response data into local memory, advances completion PSNs, and posts CQEs when signaled or on error. Timeout and NAK paths trigger retry state by setting requester flags, decrementing retry counters, arming RNR timers, or transitioning the QP to error.

## State and persistence
State is in `qp->comp`, `qp->req`, send queue WQE states, response skb queue, retry timers, CQ queues, and hardware-style stats counters. Packet SKBs hold QP and device references until `free_pkt()` drops them. CQEs persist in user or kernel completion queues until polled.

## Dependencies and integration points
The completer depends on RXE queues, tasks, CQ posting, MR copy helpers, packet header helpers, timers, QP state locking, requester flags, and counters from `rxe_hw_counters.h`. It works in tandem with `rxe_req.c`, `rxe_resp.c`, and `rxe_task.c`.

## Risks
The retry/RNR state machine is high risk: spurious retransmit timer expirations are expected, and fields like `started_retry`, `timeout_retry`, `need_retry`, and `again` coordinate with requester scheduling. There is a source TODO about protection from QP destruction around `mod_timer(&qp->rnr_nak_timer)`. CQ full handling during flush stops notifications for remaining WQEs. Error handling must always generate completions required by the IB spec.

## Test signals
Run RC send/write/read/atomic/flush tests with ACKs, duplicate ACKs, out-of-order PSNs, RNR NAKs, sequence NAKs, remote invalid/access/op errors, retry exhaustion, RNR retry exhaustion, SQ drain, CQ overflow, QP ERR/RESET flushing, and packet loss with retransmit timers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_comp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_cq.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_cq.c

## Purpose
`rxe_cq.c` implements RXE completion queue backing storage creation, resize, posting, notification, overflow event generation, and cleanup.

## Important APIs, types, and functions
Functions are `rxe_cq_from_init()`, `rxe_cq_resize_queue()`, `rxe_cq_post()`, and `rxe_cq_cleanup()`. It uses `struct rxe_cq`, `struct rxe_cqe`, `struct rxe_queue`, `struct ib_wc`, and `struct ib_event`.

## Control flow
Creation allocates a `QUEUE_TYPE_TO_CLIENT` queue sized for `struct rxe_cqe`, creates mmap metadata for userspace when requested, marks user/kernel mode, initializes `cq_lock`, and stores the actual CQE capacity. Resize delegates to `rxe_queue_resize()` under the CQ lock and updates `ibcq.cqe` on success. Posting takes `cq_lock`, checks whether the queue is full, copies the CQE into the producer slot, advances the producer, and invokes the completion handler if notification mode matches. Overflow emits `IB_EVENT_CQ_ERR`.

## State and persistence
CQ state is the queue buffer, producer/consumer indices, user mmap info, notification flags, and CQE capacity. Completion records persist in the queue until userspace or kernel consumers poll them.

## Dependencies and integration points
The file depends on RXE queue/mmap helpers, RDMA CQ event handlers, QP completer/responder paths that post CQEs, and user mmap ABI structures.

## Risks
CQ overflow is fatal at the CQ level and must signal the event handler outside the lock. `rxe_cq_from_init()` returns immediately on mmap-info failure without cleaning the queue in this function, so callers must unwind through pool cleanup. Notification flags are cleared while holding the CQ lock before calling `comp_handler`.

## Test signals
Test user and kernel CQ creation, mmap setup failures, resize smaller/larger, posting solicited and non-solicited completions under `IB_CQ_NEXT_COMP` and `IB_CQ_SOLICITED`, CQ full event delivery, and cleanup after partial creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_cq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_hdr.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_hdr.h

## Purpose
`rxe_hdr.h` defines RXE packet metadata and inline accessors for InfiniBand/RoCE transport headers stored in SKBs or send buffers.

## Important APIs, types, and functions
`struct rxe_pkt_info` fits in `skb->cb` and carries device, QP, WQE, BTH pointer, opcode, mask, PSN, pkey index, payload length, and port. The header defines BTH, RDETH, DETH, RETH, FETH, ATMETH, AETH, ATMACK, immediate, and invalidate header structs plus field masks and inline getters/setters. Helpers include `SKB_TO_PKT()`, `PKT_TO_SKB()`, `bth_init()`, `feth_init()`, `header_size()`, `payload_addr()`, and `payload_size()`.

## Control flow
There is no standalone control flow, but every packet path uses these accessors to parse received headers, build outgoing headers, compute payload ranges, and interpret ACK/NAK syndromes and atomic/read/write parameters.

## State and persistence
Packet state is transient in skb control blocks and packet header buffers. `BUILD_BUG_ON(sizeof(struct rxe_pkt_info) > sizeof(skb->cb))` protects the skb control-block ABI.

## Dependencies and integration points
The header depends on `rxe_opcode[]` offset metadata and Linux networking SKB layout. It is used by requester, responder, receiver, network transmit/receive, ICRC, and completer code.

## Risks
Offset calculations rely on `rxe_opcode[pkt->opcode]` matching the actual packet opcode and header layout. `payload_size()` subtracts header offset, BTH padding, and ICRC; malformed `paylen` or opcode metadata can underflow. Inline byte-order and reserved-bit setters must match IB/RoCE specifications exactly.

## Test signals
Packet encode/decode tests should cover all supported opcodes, BTH reserved bits, PSN and QPN masking, immediate/invalidate fields, AETH syndromes, FLUSH headers, payload size with padding and ICRC, and receive rejection of too-short packets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_hdr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_hw_counters.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_hw_counters.c

## Purpose
`rxe_hw_counters.c` exposes RXE software counters through the RDMA hardware-stats interface.

## Important APIs, types, and functions
`rxe_counter_descs[]` maps `enum rxe_counters` indexes to stat names such as sent/received packets, duplicate/out-of-sequence requests, RNR/sequence/retry errors, send errors, link-down events, and RDMA send/recv counts. `rxe_ib_get_hw_stats()` copies atomic64 counter values into `struct rdma_hw_stats`. `rxe_ib_alloc_hw_port_stats()` allocates the stats descriptor structure and asserts descriptor count matches `RXE_NUM_OF_COUNTERS`.

## Control flow
RDMA core stats allocation calls `rxe_ib_alloc_hw_port_stats()`. Stats reads call `rxe_ib_get_hw_stats()`, which validates port/stats arguments and snapshots every counter.

## State and persistence
Counter values live in `rxe_dev.stats_counters[]` and are incremented by RXE packet, requester, responder, completer, and net paths. Stats persist for the life of the RXE device.

## Dependencies and integration points
The file depends on RDMA core hw stats APIs and `rxe_hw_counters.h`. It is wired into RXE device ops elsewhere and consumed by userspace RDMA stats tooling.

## Risks
The descriptor array and enum must remain in exact order and length. Adding counters requires updating both files and all counter increments. The port validation rejects port 0; callers must pass the RXE port number.

## Test signals
Read RDMA hw stats after traffic, duplicate/out-of-order packet tests, retry/RNR failures, link down events, and module reload. Build should catch descriptor/enum length mismatch via `BUILD_BUG_ON`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_hw_counters.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_hw_counters.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_hw_counters.h

## Purpose
`rxe_hw_counters.h` defines RXE counter indexes and declares RDMA hw-stats callbacks.

## Important APIs, types, and functions
`enum rxe_counters` lists all counter slots and terminates with `RXE_NUM_OF_COUNTERS`. Declarations include `rxe_ib_alloc_hw_port_stats()` and `rxe_ib_get_hw_stats()`.

## Control flow
No runtime flow. The enum indexes are used by `rxe_counter_inc()` and by `rxe_hw_counters.c` to expose stats.

## State and persistence
The header does not own state; it defines the index contract for `rxe_dev.stats_counters[]`.

## Dependencies and integration points
It integrates RXE internal counter increments with RDMA core hw stats. Every source file that increments counters depends on stable enum values.

## Risks
The comment says new enum entries must also be added to the descriptor vector. Reordering existing counters changes userspace-visible stat meanings.

## Test signals
Build with `BUILD_BUG_ON` in `rxe_hw_counters.c`, inspect stats names/order, and exercise each counter increment path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_hw_counters.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_icrc.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_icrc.c

## Purpose
`rxe_icrc.c` computes and verifies the RoCE invariant CRC (ICRC) for RXE packets.

## Important APIs, types, and functions
`rxe_icrc_check()` compares a received packet's ICRC with a locally computed value. `rxe_icrc_generate()` writes the ICRC for outgoing packets. Internal helpers `rxe_crc32()` and `rxe_icrc_hdr()` compute cumulative CRC across masked network/transport headers, BTH, remaining RXE headers, payload, and padding.

## Control flow
The receive path calls `rxe_icrc_check()` after packet metadata is initialized. It locates the delivered ICRC at the end of the packet, computes a header CRC using a masked LRH seed, masks mutable IPv4/IPv6/UDP/BTH fields per RoCE ICRC rules, adds payload and pad bytes, complements the result, and returns `-EINVAL` on mismatch. The transmit path calls `rxe_icrc_generate()` before xmit and stores the complemented CRC in the packet trailer.

## State and persistence
No persistent driver state. It reads SKB protocol/header contents and writes the outgoing packet's ICRC field.

## Dependencies and integration points
The file depends on Linux `crc32_le`, IP/IPv6/UDP header layouts, RXE header accessors, opcode header length metadata, and net receive/transmit paths.

## Risks
Header masking must exactly match RoCE requirements. `rxe_icrc_hdr()` assumes receive validation has guaranteed enough header length; related receive code comments note short packets could otherwise underflow. IPv4 vs IPv6 protocol detection must match SKB setup.

## Test signals
Test ICRC generation/check for IPv4 and IPv6, varied payload sizes and padding, corrupted payload/header/trailer, mutable header fields that should be masked, and too-short packet rejection in receive before ICRC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_icrc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_loc.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_loc.h

## Purpose
`rxe_loc.h` is the main RXE internal function declaration hub. It ties together AV, CQ, multicast, mmap, MR, MW, net, QP, SRQ, completer/requester/responder, ICRC, and ODP interfaces.

## Important APIs, types, and functions
The header declares most non-static RXE implementation functions. It also defines `struct rxe_mmap_info`, QP helper inlines `qp_num()`, `qp_type()`, `qp_state()`, `qp_mtu()`, `is_odp_mr()`, and `rxe_advance_resp_resource()`. It declares `atomic_ops_lock`, timer callbacks, packet queueing functions, and ODP functions or stubs depending on `CONFIG_INFINIBAND_ON_DEMAND_PAGING`.

## Control flow
No direct flow beyond small inline helpers. The ODP section selects real declarations when ODP is enabled and `-EOPNOTSUPP`/unsupported response stubs otherwise.

## State and persistence
The only defined structure here is mmap metadata, containing pending-list linkage, context, kref, mapped object pointer, and user-visible mmap info. Other state is declared and owned by implementation files.

## Dependencies and integration points
This header is included by RXE source files to avoid circular declarations. It binds object pools, workqueue tasks, memory access helpers, packet paths, and optional ODP support into one internal API.

## Risks
Because it is broad, changes here can trigger large rebuild impact. Stub return values must match callers' expectations when ODP is disabled. The `is_odp_mr()` inline checks `mr->umem` and `is_odp`; callers must still handle non-ODP and DMA MR paths correctly.

## Test signals
Build RXE with ODP enabled and disabled, run sparse-style checks for prototype drift, and exercise each declared subsystem path through verbs and packet tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_loc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_mcast.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_mcast.c

## Purpose
`rxe_mcast.c` implements RXE multicast group management. It maps multicast GIDs to netdev multicast MAC addresses, stores multicast groups in an RB tree, and tracks QPs attached to each group for packet replication in receive paths.

## Important APIs, types, and functions
External functions are `rxe_lookup_mcg()`, `rxe_attach_mcast()`, `rxe_detach_mcast()`, and `rxe_cleanup_mcg()`. Internal helpers manage netdev multicast add/delete, RB tree insert/remove/lookup, multicast group allocation/destruction, and multicast attachment (`struct rxe_mcg`) and membership (`struct rxe_mca`) lifetime.

## Control flow
Attach calls `rxe_get_mcg()` to find or allocate a group. Allocation enforces `max_mcast_grp`, speculatively allocates without holding the lock, rechecks under `mcg_lock`, inserts the group, and then adds the netdev multicast address outside the lock. Then `rxe_attach_mcg()` avoids duplicate QP membership, allocates an MCA, enforces per-group and total attach limits, takes a QP reference, and appends it to the group list. Detach finds the group, removes the matching MCA, drops references/counters, and destroys the group when the last QP detaches.

## State and persistence
Per-device multicast state includes `mcg_tree`, `mcg_lock`, group count, total attachment count, per-QP membership count, group krefs, QP refs, and netdev multicast filter state. It persists until detach or device cleanup.

## Dependencies and integration points
The file uses Linux RB trees, krefs, netdev multicast APIs, IPv6 multicast-to-Ethernet mapping, RXE object refs, and RDMA attach/detach multicast verbs. Receive multicast replication uses the group membership list.

## Risks
If `rxe_mcast_add()` fails after inserting the group into the tree, `rxe_get_mcg()` currently frees `mcg` directly rather than removing the tree entry and dropping the inserted kref; that path should be reviewed carefully. Attach/detach counters and krefs must remain balanced under lock. Netdev disappearance can make add/delete return `-ENODEV`.

## Test signals
Test first attach, duplicate attach, multi-QP attach limits, detach last member, netdev multicast add/delete failure, lookup while attach/detach races, device teardown with non-empty group tree, and receive replication to all members.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_mcast.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_mmap.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_mmap.c

## Purpose
`rxe_mmap.c` implements RXE userspace mmap support for queue buffers created by CQ, QP, and SRQ verbs.

## Important APIs, types, and functions
Functions are `rxe_mmap_release()`, `rxe_mmap()`, and `rxe_create_mmap_info()`. VMA operations `rxe_vma_open()` and `rxe_vma_close()` maintain krefs. State is held in `struct rxe_mmap_info` declared in `rxe_loc.h`.

## Control flow
Queue creation calls `rxe_create_mmap_info()` to allocate metadata, assign a SHMLBA-aligned offset under `mmap_offset_lock`, record the ucontext and object buffer, and initialize a kref. Higher-level queue code adds it to `pending_mmaps` and returns the offset to userspace. `rxe_mmap()` searches the pending list for matching context and offset, rejects mappings larger than the object, removes the metadata from the pending list, remaps the vmalloc buffer with `remap_vmalloc_range()`, sets VMA ops/private data, and takes a mapping reference. VMA close drops the reference, and final release removes pending linkage, frees the vmalloc buffer, and frees metadata.

## State and persistence
Mmap metadata persists between object creation and userspace mmap, then for as long as VMAs reference the buffer. The queue buffer is freed from mmap release, so object cleanup and VMA refs must coordinate through krefs.

## Dependencies and integration points
It depends on RDMA ucontext/udata bundling, RXE pending mmap lists, vmalloc remapping, SHMLBA alignment, and queue allocation code in `rxe_queue.c`.

## Risks
Failed `remap_vmalloc_range()` after removing from the pending list leaves the metadata not pending but still referenced only by the creator unless caller cleanup handles it. Offset growth is monotonic and could wrap only over very long lifetimes, but there is no explicit overflow check. Context/offset matching is the main isolation check.

## Test signals
Test successful mmap for CQ/QP/SRQ queues, wrong context, wrong offset, too-large VMA, remap failure injection, fork/VMA open-close kref behavior, object destroy while mapped, and repeated create/mmap/destroy cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_mmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_mr.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_mr.c

## Purpose
`rxe_mr.c` implements RXE memory region state, key generation, user memory pinning, fast registration, scatterlist mapping, MR copy, persistent-memory flush, atomic operations, DMA descriptor advancement, lookup/access validation, invalidation, and cleanup.

## Important APIs, types, and functions
Key functions include `rxe_get_next_key()`, `mr_check_range()`, `rxe_mr_init()`, `rxe_mr_init_dma()`, `rxe_mr_init_user()`, `rxe_mr_init_fast()`, `rxe_map_mr_sg()`, `rxe_mr_copy()`, `copy_data()`, `rxe_flush_pmem_iova()`, `rxe_mr_do_atomic_op()`, `rxe_mr_do_atomic_write()`, `advance_dma_data()`, `lookup_mr()`, `rxe_invalidate_mr()`, `rxe_reg_fast_mr()`, and `rxe_mr_cleanup()`. State includes `struct rxe_mr`, page-info arrays, `ib_umem`, access flags, keys, state enum, and `atomic_ops_lock`.

## Control flow
MR initialization assigns pool-index-based lkey/rkey values with random low key bytes and starts most MRs invalid until the specific type marks them valid/free. User MR registration pins umem pages, allocates page-info entries, validates persistent-memory access if requested, fills page mappings, and marks the MR valid. Fast MRs allocate page-info capacity and become FREE until a REG_MR WQE supplies iova/key/access and transitions them valid. Copy paths validate range and access, choose DMA, ODP, or page-info copy, and advance DMA descriptors across SGEs while holding/dropping MR references. Remote atomic paths validate state, range, and 8-byte alignment, then update mapped pages under a global spinlock.

## State and persistence
MRs persist in RXE object pools until deregistration. User pages are pinned through `ib_umem`; page-info arrays map IOVA to pages and offsets. Fast-registration state toggles between FREE and VALID. `num_mw` blocks invalidation while memory windows are bound. Persistent-memory flushes write back cache lines but do not otherwise persist metadata.

## Dependencies and integration points
The file integrates with RDMA umem, virtual DMA helpers, scatterlist-to-page mapping, ODP stubs/implementation, libnvdimm persistent-memory detection, RXE responder/requester/completer copy paths, MW binding, and pool reference management.

## Risks
Range arithmetic `iova + length` can overflow if not otherwise constrained. Page-size compatibility in fast registration is subtle, especially when MR page size is larger or smaller than PAGE_SIZE. Atomic operations use a global lock, which is simple but can bottleneck and must match memory ordering expectations. Invalidation must reject bound MRs and wrong key flavors. Persistent flush requires all pages to be pmem when access requests it.

## Test signals
Test user MR registration/deregistration, DMA MR access, fast-reg map sizes and page sizes, local and remote key lookup failures, copy across SGE/page boundaries, zero-length copy/flush, ODP enabled/disabled paths, persistent-memory access validation and flush, atomic compare-swap/fetch-add/write alignment errors, MW-bound invalidation rejection, and key rollover.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_mr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_mw.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_mw.c

## Purpose
`rxe_mw.c` implements RXE memory windows, including type 1 and type 2B allocation, bind, invalidate, lookup, and cleanup.

## Important APIs, types, and functions
External functions are `rxe_alloc_mw()`, `rxe_dealloc_mw()`, `rxe_bind_mw()`, `rxe_invalidate_mw()`, `rxe_lookup_mw()`, and `rxe_mw_cleanup()`. Internal helpers `rxe_check_bind_mw()`, `rxe_do_bind_mw()`, `rxe_check_invalidate_mw()`, and `rxe_do_invalidate_mw()` enforce IB access and state rules. State lives in `struct rxe_mw`, including rkey, state, access, bound MR, bound QP for type 2, address, length, and lock.

## Control flow
Allocation takes a PD reference, adds the MW to the pool, assigns an rkey using the pool index plus random key byte, initializes state to VALID for type 1 or FREE for type 2, and finalizes the object. Binding looks up the MW by rkey index, checks full rkey, optionally looks up the target MR by lkey, validates supported access flags, takes `mw->lock`, enforces type-specific state/PD/null-MR rules and MR access/range requirements, updates the low rkey byte, attaches MR/QP references, increments `mr->num_mw`, and marks the MW valid. Invalidation rejects type 1 and invalid MWs, then drops QP/MR refs and returns type 2 MWs to FREE. Cleanup drops PD/MR/QP references and marks the MW invalid.

## State and persistence
MW state is in-memory object-pool state. Bound type 2 MWs hold references to both QP and MR; bound MRs track `num_mw`, which blocks MR invalidation. Rkeys change on bind via the low key byte.

## Dependencies and integration points
MWs are used by requester bind/invalidate WQEs and responder remote access checks. The file depends on MR pools, PD/QP identity, RXE access masks, key generation from `rxe_mr.c`, and RXE object refcounting.

## Risks
Bind and invalidate correctness depends on state transitions under `mw->lock`. `rxe_do_invalidate_mw()` assumes valid type 2 MWs always have QP and MR pointers. Range checks must account for zero-based vs virtual-address MWs. Key mismatch handling must drop looked-up references on every error path.

## Test signals
Test type 1 and type 2 allocation, bind success/failure by state, PD mismatch, unsupported access, MR lacking bind/local-write access, zero-length/null MR behavior, zero-based range checks, remote lookup by rkey/access/QP, invalidate type 2, reject type 1 invalidate, cleanup while bound, and MR invalidation blocked by `num_mw`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_mw.c -->
