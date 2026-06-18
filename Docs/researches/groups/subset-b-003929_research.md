# Group Research: subset-b-003929

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/rc.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/rc.c

## Purpose
`rc.c` implements most of the HFI1 reliable connected (RC) verbs protocol engine. It constructs outbound RC requests and responses, consumes inbound RC packets, manages packet sequence number (PSN) retry and completion state, emits ACK/NAK packets, and bridges regular InfiniBand RC operations with HFI1 TID RDMA extensions. The file is on the hot path for SEND, RDMA WRITE, RDMA READ, atomics, OPFN, ACK processing, RNR retry, PSN retry, duplicate-request replay, and congestion notification.

## Important APIs, Types, and Functions
- `hfi1_make_rc_req()` is the transmit-side packet builder used by the RUC send loop. It selects 9B or 16B headers, prioritizes pending responder work via `make_rc_ack()`, handles QP error flushing, and builds packets for SEND, RDMA WRITE, RDMA READ, atomics, OPFN, and TID RDMA read/write requests.
- `make_rc_ack()` is the responder-side response builder. It drains `qp->s_ack_queue`, constructs ACK, atomic ACK, RDMA read response, TID RDMA read response, and TID RDMA write response packets, and manipulates `s_tail_ack_queue`, `s_acked_ack_queue`, `s_ack_state`, `s_ack_rdma_psn`, and responder flags.
- `hfi1_send_rc_ack()` builds a minimal inline ACK/NAK packet and sends it through PIO when possible. It falls back to queued send-engine ACKs when responder work is pending, RDMA ACK counters are nonzero, link state is inactive, or PIO buffers are unavailable.
- `hfi1_rc_rcv()` is the receive dispatcher for RC opcodes. It validates RUC headers, handles ECN/OPFN, dispatches responses to `rc_rcv_resp()`, checks PSN order and opcode sequencing, copies SEND/RDMA WRITE payloads, starts RDMA READ and atomic responses, and schedules ACK/NAK output.
- `rc_rcv_resp()` processes inbound response packets on the requester side, including ACKs, atomic ACKs, and RDMA READ response first/middle/last/only packets.
- `do_rc_ack()` advances completion and retry state for ACK, RNR NAK, and other NAK classes. It updates retry timers, credits, `s_last_psn`, `s_num_rd_atomic`, TID RDMA counters, and SWQE completion.
- `hfi1_restart_rc()`, `reset_psn()`, and `reset_sending_psn()` implement retry positioning and send-side PSN rollback.
- `do_rc_completion()` completes SWQEs once no in-flight SDMA descriptors still reference their SGEs.
- `rc_rcv_error()` handles out-of-order and duplicate request packets, including replay of prior RDMA read or atomic responses from the ACK queue.
- `process_becn()` and `log_cca_event()` update congestion-control state in response to backward ECN.

## Control Flow
The outbound path starts from `hfi1_do_send()` in `ruc.c`, which calls `hfi1_make_rc_req()` under `qp->s_lock`. If responder work is pending, `make_rc_ack()` takes precedence over requester sends. Otherwise the function checks QP send state, wait flags, PSN pacing, and the current SWQE. New SWQEs initialize SGE state, consume credits where applicable, set the opcode-specific BTH/extension headers, advance `s_cur`/`s_tail`, and update `s_psn`. Multi-packet SEND and RDMA WRITE work requests use `s_state` middle/last states and may enable SDMA AHG for repeated middle headers. RDMA READ, atomics, OPFN, and TID RDMA requests generate header-only or extension-specific packets and depend on ACK responses to complete.

The inbound request path enters `hfi1_rc_rcv()` with `r_lock` held. `hfi1_ruc_check_hdr()` validates addressing, P_Key, migration, and GRH constraints. Response opcodes are redirected to `rc_rcv_resp()`. Request opcodes are checked against `qp->r_psn` and `qp->r_state`; mismatches go through `rc_rcv_error()`. Valid SEND packets consume receive WQEs and produce receive completions. RDMA WRITE packets validate remote-write access and R_Key mapping before copying data. RDMA READ and atomic requests allocate or reuse ACK queue entries and schedule responder output through the send engine. ACKs are sent inline by `hfi1_send_rc_ack()` or deferred with `rc_defered_ack()`.

The ACK response path combines transport ACK semantics with local work completion. `do_rc_ack()` walks from `s_acked` while `ack_psn` covers SWQEs, completes normal WQEs, writes atomic return values, calls OPFN reply handling, manages read/atomic outstanding counters, and handles TID RDMA write exceptions. ACKs reset retry/RNR counters and refresh credits. RNR NAKs reset PSN, schedule RNR timers, and pause sends. Sequence-error NAKs call `hfi1_restart_rc()` and reschedule sends. Class B NAKs complete or error the QP when the failed SWQE is the last outstanding operation.

## State and Persistence Behavior
This file persists protocol state inside `struct rvt_qp`, `struct hfi1_qp_priv`, per-port counters, ACK queues, and TID RDMA request state. Important fields include `s_psn`, `s_next_psn`, `s_last_psn`, `s_sending_psn`, `s_sending_hpsn`, `r_psn`, `r_ack_psn`, `r_msn`, `s_ack_state`, `r_nak_state`, `s_nak_state`, `s_num_rd_atomic`, `s_rdma_ack_cnt`, and queue indices such as `s_cur`, `s_tail`, `s_acked`, `s_tail_ack_queue`, `s_acked_ack_queue`, and `r_head_ack_queue`. State is volatile kernel runtime state, not durable storage. Memory registrations held in ACK entries are reference-counted and released by `release_rdma_sge_mr()`.

Concurrency relies on `qp->s_lock` for send-side and ACK-queue state, `qp->r_lock` for receive-side state, interrupt-safe locking for mixed paths, and explicit memory barriers before clearing response-pending flags. Some copy operations deliberately drop locks while copying RDMA READ data into SGEs.

## Dependencies and Integration Points
The file depends heavily on RDMA core/RDMA VT (`rvt_*`, `ib_rvt_state_ops`, `rvt_get_rwqe()`, `rvt_copy_sge()`, `rvt_rkey_ok()`, timers, credits, and completions), HFI1 packet helpers (`hfi1_make_ruc_header()`, PIO send, ECN, P_Key, LID/SL/SC helpers), SDMA tx request state, TID RDMA helpers in `tid_rdma.c`, OPFN helpers, and tracepoints. `verbs.c` maps RC opcodes to `hfi1_rc_rcv()`. `driver.c` can call `hfi1_send_rc_ack()` for deferred ACK handling. The send loop in `ruc.c` invokes `hfi1_make_rc_req()`.

## Risks and Edge Cases
Risk is concentrated in retry and duplicate handling. Incorrect PSN rollback can resend the wrong bytes, complete a SWQE too early, or leak SGE/MR references. ACK queue wraparound has to preserve prior RDMA read and atomic responses for duplicate requests. TID RDMA adds special counters and states that do not always align with ordinary IB PSN semantics. Lock ordering between `r_lock` and `s_lock` must stay consistent in error and retry paths. Inline ACK fallback is sensitive to `s_rdma_ack_cnt`, PIO buffer availability, and link state. Length checks must account for 9B versus 16B padding, CRC, and LT bytes. Congestion BECN/FECN handling changes send headers and CCA timers and should not interact badly with ACK coalescing.

## Test Signals
Useful signals include RC SEND/RDMA READ/RDMA WRITE/atomic loopback and remote interoperability tests, induced packet loss or PSN sequence NAKs, RNR retry exhaustion, duplicate RDMA READ request replay, QP migration tests, OPFN negotiation tests, TID RDMA read/write stress, AHG-enabled multi-packet payload tests, and QP teardown while SDMA descriptors are still in flight. Runtime counters and tracepoints such as `rc_acks`, `rc_qacks`, `n_rc_resends`, `n_seq_naks`, `n_rnr_naks`, `n_rc_dupreq`, `n_rdma_seq`, and congestion log events are strong observability signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/rc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/rc.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/rc.h

## Purpose
`rc.h` is the small shared header for HFI1 RC helper routines. It shortens RC opcode macro usage, exposes selected ACK/completion helpers implemented in `rc.c`, and provides inline utilities for ACK queue maintenance, deferred ACK scheduling, SGE restart, and ACK-entry MR release.

## Important APIs, Types, and Functions
- `OP(x)` aliases `IB_OPCODE_RC_##x` for dense RC state-machine code.
- `update_ack_queue()` advances `s_tail_ack_queue` and `s_acked_ack_queue` past a completed ACK entry and resets `s_ack_state` to `ACKNOWLEDGE`.
- `rc_defered_ack()` puts a QP on the receive context `qp_wait_list`, sets `RVT_R_RSP_NAK`, and takes a QP reference so a later context drain can send the deferred ACK/NAK.
- `restart_sge()` converts a restart PSN into a byte offset relative to a SWQE and calls `rvt_restart_sge()`.
- `release_rdma_sge_mr()` drops the MR reference held by an ACK queue RDMA SGE and clears the pointer.
- `find_prev_entry()`, `do_rc_ack()`, and `do_rc_completion()` are exported from `rc.c` for internal HFI1 RC/TID RDMA use.

## Control Flow
The inline helpers are invoked by `rc.c` retry, receive-error, and ACK-response paths. `restart_sge()` is used when a requester has to restart in the middle of a SEND/RDMA operation or when an RDMA READ response is being copied after a retry. `rc_defered_ack()` is used by receive paths that want to delay NAK/ACK emission until the receive queue is drained. `update_ack_queue()` is used when an ACK queue entry can be skipped or reclaimed. `release_rdma_sge_mr()` is called before overwriting or retiring ACK entries that may own MR references.

## State and Persistence Behavior
The helpers mutate only QP runtime state: ACK queue indices, `s_ack_state`, `rspwait` list membership, `r_flags`, QP references, and MR references. There is no durable persistence. Correctness depends on callers holding the locks documented in `rc.c` and on the receive context wait list eventually dropping the QP reference with `rvt_put_qp()`.

## Dependencies and Integration Points
The header depends on RDMA VT QP structures, HFI1 receive context structures, Linux list handling, and RC opcode definitions from the RDMA headers. It is included by `rc.c` and indirectly supports TID RDMA code that needs RC ACK/completion helpers.

## Risks and Edge Cases
`update_ack_queue()` relies on `rvt_size_atomic()` wrap rules matching ACK queue allocation. `rc_defered_ack()` has to avoid double-enqueue by checking `list_empty(&qp->rspwait)`. `restart_sge()` assumes PSN deltas multiplied by PMTU correctly reflect byte offsets for the target work request. `release_rdma_sge_mr()` must be called on every overwrite/retire path to avoid MR reference leaks, but not while data is still needed for a response resend.

## Test Signals
Test signals come from RC retry and duplicate tests rather than this header directly: ACK queue wraparound, deferred NAK emission, RDMA READ resend from a middle PSN, and QP teardown with outstanding ACK entries should show no leaks, list corruption, or incorrect completions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/rc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/ruc.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/ruc.c

## Purpose
`ruc.c` contains shared reliable/unreliable connected transport helpers for HFI1 verbs. It validates inbound connected-transport headers, builds common 9B/16B LRH/OPA/BTH/GRH packet headers for RC and UC send paths, manages SDMA AHG header reuse, and implements the generic QP send loop used by RC, UC, and UD send builders.

## Important APIs, Types, and Functions
- `hfi1_ruc_check_hdr()` validates received packet addressing against the QP path or alternate path, including migration bit, GRH presence and GID matching, P_Key checks, SLID, port number, and migration state transitions.
- `hfi1_make_grh()` constructs an InfiniBand GRH from an RDMA global route.
- `build_ahg()` allocates or reuses an SDMA AHG entry for repeated middle packets and emits AHG update descriptors for PSN changes.
- `hfi1_make_ruc_header_9B()` and `hfi1_make_ruc_header_16B()` build local route headers and BTH fields for 9B and 16B packet formats.
- `hfi1_make_ruc_header()` resets per-packet AHG metadata and dispatches to the selected header builder.
- `hfi1_schedule_send_yield()` enforces a send-loop time slice and reschedules RC or TID send work when a QP has run too long.
- `hfi1_do_send()`, `_hfi1_do_send()`, and `hfi1_do_send_from_rvt()` are send engine entry points.

## Control Flow
Receive-side validation uses `hfi1_ruc_check_hdr()` before RC and UC packet processing. If a QP is armed for migration and the packet carries the migrated path bit, the function validates alternate path GRH/GID/P_Key/SLID data and then calls `hfi1_migrate_qp()` under `s_lock`. Otherwise it validates the primary remote path and rearms migration when appropriate.

Transmit header construction starts with the opcode-specific builder in `rc.c`, `uc.c`, `tid_rdma.c`, or `ud.c`, which fills BTH fields and payload length in `hfi1_pkt_state`. `hfi1_make_ruc_header()` clears stale AHG fields in the QP private AHG tx request and calls the 9B or 16B builder. The builder adds GRH when needed, applies migration and ECN/BECN bits, computes padding and length fields, applies the P_Key, optionally uses AHG for middle packets, and writes either IB LRH or OPA 16B headers.

The send loop in `hfi1_do_send()` chooses `hfi1_make_rc_req()`, `hfi1_make_uc_req()`, or `hfi1_make_ud_req()` by QP type. It handles local loopback, takes `s_lock`, checks `hfi1_send_ok()`, marks the QP busy, sends any waiting prebuilt txreq through `hfi1_verbs_send()`, calls the selected make-request function until it cannot build more, and uses `hfi1_schedule_send_yield()` to avoid monopolizing CPU/workqueue time.

## State and Persistence Behavior
The file manipulates runtime QP and QP-private state: migration state, AHG index/valid flags, AHG update counts, send busy flags, iowait pending flags, packet timeout bookkeeping, and selected SDMA engine CPU. It does not persist data beyond in-memory driver structures. AHG entries are allocated from and freed to the selected SDMA engine, so stale AHG flags must be cleared for packets that cannot safely use a copied header.

## Dependencies and Integration Points
`ruc.c` integrates with RDMA address handles, HFI1 P_Key/GID/LID/SL/SC helpers, SDMA AHG APIs from `sdma.h`, verbs tx request allocation and send, RC/UC/UD packet builders, TID RDMA send scheduling, and RDMA VT loopback support. It is a common layer for RC and UC receive validation and all connected transmit header formatting.

## Risks and Edge Cases
Header format differences are a major risk: 9B versus 16B padding, GRH placement, multicast GRH handling, BECN bit placement, path bits, permissive LID behavior, and P_Key placement must remain exact. AHG must be disabled when GRH, migration, or ECN changes make a copied header unsafe. Send-loop locking must keep one CPU from sending a QP out of order. Migration validation must not accept mismatched GIDs or SLIDs, and P_Key failures must update bad-P_Key reporting without advancing protocol state.

## Test Signals
Useful tests include RC and UC traffic over 9B and 16B headers, GRH and non-GRH paths, multicast 16B GRH behavior, path migration, bad P_Key and bad SLID rejection, ECN/BECN propagation, AHG-enabled large SEND/RDMA WRITE middle packet streams, loopback QPs, and send-loop fairness under heavy QP fan-out. Tracepoints for send scheduling and AHG allocation are useful diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/ruc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/sdma.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/sdma.c

## Purpose
`sdma.c` implements the HFI1 send DMA engine subsystem. It allocates and initializes per-engine descriptor rings, maps virtual lanes and CPUs to engines, submits `sdma_txreq` descriptors, processes interrupt-driven head progress, completes and cleans tx requests, recovers from SDMA errors, and drives an explicit engine state machine for startup, idle, halt, hardware cleanup, software cleanup, freeze, unfreeze, and running states.

## Important APIs, Types, and Functions
- Module parameters `sdma_descq_cnt`, `sdma_idle_cnt`, `num_sdma`, and `desct_intr` tune descriptor ring size, idle interrupt delay, engine count, and descriptor interrupt threshold.
- `sdma_init()`, `sdma_start()`, `sdma_all_running()`, `sdma_exit()`, and `sdma_clean()` manage subsystem lifetime.
- `sdma_map_init()`, `sdma_select_engine_vl()`, `sdma_select_engine_sc()`, and `sdma_select_user_engine()` maintain and consume RCU-protected engine maps.
- `sdma_set_cpu_to_sde_map()` and `sdma_get_cpu_to_sde_map()` maintain per-CPU user affinity using a resizable hash table.
- `sdma_send_txreq()` and `sdma_send_txlist()` submit one or many txreqs to an engine ring, or queue them for wait/flush when no descriptors or no running engine is available.
- `sdma_engine_interrupt()` and `sdma_make_progress()` retire descriptors, complete txreqs, unmap DMA mappings, wake waiters, and update counters.
- `sdma_engine_error()` and `__sdma_process_event()` drive recovery transitions for hardware errors and software-detected stalls.
- `ext_coal_sdma_tx_descs()`, `_pad_sdma_tx_descs()`, `_sdma_txreq_ahgadd()`, `sdma_ahg_alloc()`, and `sdma_ahg_free()` support descriptor overflow, packet padding, AHG edits, and AHG entry allocation.
- `sdma_freeze_notify()`, `sdma_freeze()`, and `sdma_unfreeze()` coordinate SDMA behavior across SPC freeze/unfreeze and link-down events.

## Control Flow
Initialization starts in `sdma_init()`. It checks SDMA capability, selects engine count, validates descriptor count, allocates `dd->per_sdma`, allocates coherent descriptor rings and tx rings per engine, allocates coherent head and padding memory, initializes CSRs with `init_sdma_regs()`, publishes the VL mapping with `sdma_map_init()`, and creates the per-device CPU affinity rhashtable. `sdma_start()` sends each engine an event to begin hardware startup. `sdma_all_running()` moves engines to running after link-up.

Submission enters `sdma_send_txreq()` or `sdma_send_txlist()` with a fully built txreq. Under `tail_lock`, the code rejects incomplete txreqs, checks `s99_running`, checks descriptor availability, copies descriptors into the coherent ring through `submit_tx()`, stores the txreq in `tx_ring`, increments iowait SDMA counts, and advances the hardware tail with a write memory barrier. If descriptors are unavailable, `sdma_check_progress()` may call an iowait sleep hook or return busy. If the engine is not running, txreqs go to `flushlist`, wait counts are incremented, and a high-priority flush worker completes them with communication error/abort semantics.

Progress enters through SDMA interrupts, forced progress interrupts, cleanup tasks, or recovery paths. `sdma_make_progress()` reads the hardware head from DMA memory or CSR, validates it when head checking is enabled, advances the software head, completes txreqs whose `next_descq_idx` has been reached, unmaps descriptors through `__sdma_txclean()`, invokes callbacks, decrements iowait counts, and wakes waiters when descriptors become available. Idle interrupts may force a one-time CSR head reread because host-memory head updates are not guaranteed to be ordered with idle interrupt delivery.

The state machine is centered in `__sdma_process_event()`. States include hardware down, startup halt wait, startup cleanup wait, idle, software cleanup wait, hardware cleanup wait, halt wait, idle halt wait, freeze states, and running. Events such as go-start, halt-done, cleanup-done, go-running, go-idle, link-down, hardware-freeze, unfreeze, and software-halted trigger CSR control changes, tasklets, workers, flushes, and wakeups. `sdma_set_state()` converts state actions into SendDmaCtrl enable/interrupt/halt/cleanup bits and flushes stale txreqs before entering running.

## State and Persistence Behavior
State is held in `struct sdma_engine`, `struct sdma_state`, descriptor rings, `tx_ring`, wait lists, flush lists, AHG bitmaps, rhashtable CPU mappings, RCU VL maps, coherent DMA memory, and hardware CSRs. It is runtime-only and is rebuilt on driver probe. Descriptor ownership is split between software tail/head indices and hardware head/tail CSRs. DMA mappings and optional pinning contexts are released only when txreqs complete or are cleaned. RCU protects VL map readers while updates replace the whole map and free old maps after a grace period.

Locking is split by ring side: `tail_lock` protects submission and state checks, `head_lock` protects progress and completion, `waitlock` protects `dmawait`, `flushlist_lock` protects flush list operations, `senddmactrl_lock` protects the shadow control register, and `process_to_sde_mutex` serializes CPU affinity changes.

## Dependencies and Integration Points
The SDMA subsystem depends on HFI1 chip CSR definitions, coherent DMA allocation, Linux tasklets/workqueues/timers/seqlocks/RCU/rhashtable, iowait, verbs and PSM/user SDMA callers, IPOIB transmit, QP engine selection, and sysfs/debugfs reporting. `verbs.c`, `user_sdma.c`, `ipoib_tx.c`, and `pin_system.c` build txreqs through `sdma_txinit*()`/`sdma_txadd_*()` and submit them here. `sysfs.c` exposes per-engine CPU affinity and VL data through APIs implemented here.

## Risks and Edge Cases
Correctness depends on strict descriptor ring accounting and memory ordering before tail updates. Generation bits must match ring wrap, with special AHG descriptors intentionally skipping generation insertion. If head reads are stale or insane, completion can stall or corrupt ordering. Descriptor coalescing must not accept caller-owned DMA addresses because it copies source bytes and owns the mapping. Freeze/error recovery must flush in-flight descriptors and waiters without double-completing txreqs. CPU affinity maps must preserve ordering guarantees for pinned user processes. AHG allocation is bitmap-based and can fail under pressure. Cleanup callbacks can run in interrupt/tasklet/workqueue context and must not sleep.

## Test Signals
High-value signals include descriptor ring wrap tests, multi-descriptor and over-64-iovec coalescing, non-dword packet padding, AHG copy/update traffic, `sdma_send_txlist()` batching, no-descriptor iowait sleep/wakeup, engine halt error injection, SDMA head-check failures, SPC freeze/unfreeze, link-down while descriptors are in flight, CPU-to-SDE sysfs updates, VL remapping, and unload with non-empty wait/flush lists. Counters `sdma_int_cnt`, `idle_int_cnt`, `progress_int_cnt`, `descq_full_count`, `err_cnt`, tracepoints, and debugfs `sdma_seqfile_dump_sde()` output are useful validation aids.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/sdma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/sdma.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/sdma.h

## Purpose
`sdma.h` defines the public and internal-facing contract for HFI1 send DMA. It provides descriptor format constants, SDMA state/event enums, core `struct sdma_engine` layout, VL mapping structures, tx request initialization and descriptor-building helpers, engine selection APIs, progress helpers, lifecycle APIs, AHG helpers, and debug/sysfs support declarations.

## Important APIs, Types, and Functions
- Descriptor constants define hardware descriptor fields for physical address, byte count, first/last flags, header update mode, AHG header index, generation bits, interrupt request, and head-to-host update.
- `enum sdma_states` and `enum sdma_events` enumerate the state machine implemented in `sdma.c`.
- `struct sdma_state` stores state-machine reference count, completion, current and previous state/op, running intent, and last event.
- `struct hw_sdma_desc` is the raw 128-bit ring descriptor.
- `struct sdma_engine` stores device/port links, CSR addresses, interrupt masks, coherent head and descriptor memory, tx ring, state machine, locks, head/tail indices, wait/flush lists, tasklets/workers/timers, AHG bitmap, CPU affinity mask, and sysfs kobject.
- `sdma_txinit()` and `sdma_txinit_ahg()` initialize `struct sdma_txreq` instances and optionally encode AHG copy/update metadata.
- `sdma_txadd_page()`, `sdma_txadd_kvaddr()`, and `sdma_txadd_daddr()` append DMA descriptors and close/pad a packet when the expected length is satisfied.
- `sdma_send_txreq()` and `sdma_send_txlist()` are submission APIs implemented in `sdma.c`.
- `sdma_select_engine_sc()`, `sdma_select_engine_vl()`, and `sdma_select_user_engine()` pick engines from SC/VL and user affinity maps.
- `sdma_progress()` lets iowait code detect whether descriptor progress occurred since a saved sequence.

## Control Flow
Callers allocate an enclosing object with `struct sdma_txreq` first, initialize it with `sdma_txinit()` or `sdma_txinit_ahg()`, add fragments using one of the `sdma_txadd_*()` helpers until `tx->tlen` reaches zero, and submit through `sdma_send_txreq()` or `sdma_send_txlist()`. The add helpers map pages or kernel virtual addresses for DMA, record mapping type and optional pinning context in each `sdma_desc`, decrement `tlen`, and mark the last descriptor when the packet is complete. If the built-in descriptor array is exhausted, `sdma.c` extends or coalesces descriptors.

Engine selection and lifecycle are declared here but implemented in `sdma.c`. Consumers use `sdma_running()` or submit APIs rather than directly changing engine state. Interrupt handlers call `sdma_engine_interrupt()` or `sdma_engine_error()`. Debug and sysfs code calls dump and mapping helpers.

## State and Persistence Behavior
The header describes in-memory runtime state only. `sdma_txreq` owns temporary descriptor arrays, DMA mappings, optional coalesce buffer, wait pointer, callback, AHG flags, and packet length counters until completion or cleanup. `sdma_engine` owns coherent DMA rings and state-machine data for the device lifetime. No state is persisted across module unload or device reset.

## Dependencies and Integration Points
`sdma.h` includes HFI1 core headers, verbs declarations, Linux list/workqueue/RCU types, and `sdma_txreq.h`. It is included by SDMA implementation and by packet producers in verbs, user SDMA, IPOIB, pinning, QP selection, sysfs, and RC/RUC code for AHG integration. The inline helpers depend on DMA mapping APIs and HFI1 device memory such as `dd->sdma_pad_phys` and `dd->default_desc1`.

## Risks and Edge Cases
The inline API assumes `tlen` is exact and all fragments sum to the initialized packet length. Calling submit with nonzero `tlen` is invalid. `sdma_txadd_daddr()` assumes the caller owns DMA mapping lifetime; `sdma_txadd_page()` and `sdma_txadd_kvaddr()` transfer unmap responsibility to SDMA cleanup. Last-descriptor padding uses a coherent pad buffer. AHG mode values are coupled to skip-count logic in `sdma.c`, so enum-like macro values must not change casually. `sdma_descq_freecnt()` relies on power-of-two descriptor counts and wrap semantics.

## Test Signals
Compile coverage is important because many helpers are inline. Runtime tests should build packets from page, kvaddr, and caller-DMA fragments; exercise exact-length, zero-length, oversize, and non-dword-sized packets; test AHG copy and update modes; force descriptor extension and coalescing; and validate cleanup after mapping failure. Engine selection tests should cover SC/VL maps and user CPU affinity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/sdma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/sdma_txreq.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/sdma_txreq.h

## Purpose
`sdma_txreq.h` defines the transport-neutral packet request container used by HFI1 SDMA producers. It provides the canonical fragment descriptor, request status codes, request flags, callback type, and `struct sdma_txreq` layout that verbs, user SDMA, IPOIB, and other callers embed at the start of their own request structures.

## Important APIs, Types, and Functions
- `NUM_DESC` sets the built-in descriptor capacity to 6, increased for AHG needs.
- `struct sdma_desc` stores two descriptor quadwords plus optional pinning context and a non-sleeping context release callback.
- Status constants `SDMA_TXREQ_S_OK`, `SDMA_TXREQ_S_SENDERROR`, `SDMA_TXREQ_S_ABORTED`, and `SDMA_TXREQ_S_SHUTDOWN` are passed to completion callbacks.
- Flags `SDMA_TXREQ_F_URGENT`, `SDMA_TXREQ_F_AHG_COPY`, `SDMA_TXREQ_F_USE_AHG`, and `SDMA_TXREQ_F_VIP` influence interrupt/head update behavior, AHG mode, and priority handling.
- `callback_t` is the completion callback signature.
- `struct sdma_txreq` tracks list linkage, descriptor storage, optional coalesce buffer, iowait owner, callback, packet and remaining length, descriptor counts/limits, next ring index, coalesce index, flags, and built-in descriptors.
- `sdma_txreq_built()` returns whether any descriptors have been built.

## Control Flow
Callers allocate a larger request object with `struct sdma_txreq` first, initialize it via helpers in `sdma.h`, add descriptors until `num_desc` is nonzero and `tlen` reaches zero, then submit it through `sdma.c`. During progress or abort, SDMA cleanup walks the descriptors, unmaps DMA mappings according to encoded mapping type, calls any pinning context release callback, frees coalesce/extended descriptor allocations, invokes the completion callback with one of the status values, and updates iowait state.

## State and Persistence Behavior
`struct sdma_txreq` is transient per-packet state. It can be queued on wait lists, flush lists, or the active tx ring. The descriptor pointer initially references the embedded `descs[]` array but may be replaced by an allocated larger array. `coalesce_buf` is allocated only for excessive fragment counts. `next_descq_idx` is set when submitted so progress can identify when the hardware head has passed the request. Nothing in this header is durable across request completion.

## Dependencies and Integration Points
The header depends on Linux list types and is included by `sdma.h`, which supplies initialization and descriptor manipulation helpers. Producers in verbs, user SDMA, IPOIB, and pinning code embed this type and attach subsystem-specific metadata after it. `sdma.c` is the primary consumer of private fields even though comments discourage direct external use.

## Risks and Edge Cases
The request structure is intentionally shared across multiple producers, so layout assumptions matter: the SDMA txreq must be first in enclosing structures when code casts between generic and producer-specific request types. Completion callbacks can run in interrupt, tasklet, or worker context and must not sleep. Pinning context release callbacks may also run in interrupt context. Mismanaging `tlen`, `num_desc`, or `desc_limit` can result in incomplete submission, descriptor overflow, or cleanup leaks. Flags must align with descriptor encoding logic in `sdma.h` and `sdma.c`.

## Test Signals
Tests should confirm callbacks receive correct status on success, abort, shutdown, and send error; descriptor extension preserves embedded descriptors; pinning context get/put balance is correct; `sdma_txreq_built()` distinguishes initialized-but-empty from built requests; and all producers can embed the struct without layout regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/sdma_txreq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/sysfs.c

## Purpose
`sysfs.c` exposes HFI1 verbs/device state through sysfs under the InfiniBand class device and per-port directories. It provides read-only port mapping data, congestion-control binary attributes, device identity and sensor attributes, a controlled diagnostic reset attribute, and per-SDMA-engine kobjects for CPU affinity and VL reporting.

## Important APIs, Types, and Functions
- `hfi1_get_pportdata_kobj()` maps an IB port sysfs kobject to `struct hfi1_pportdata`.
- `cc_table_bin_read()` and `cc_setting_bin_read()` expose congestion-control table and settings snapshots under the `CCMgtA` port group.
- `cc_prescan_show()` and `cc_prescan_store()` expose a simple on/off administrative congestion-control prescan toggle.
- Generated `sc2vl`, `sl2sc`, and `vl2mtu` attributes expose SC-to-VL, SL-to-SC, and VL-to-MTU mappings.
- Device attributes expose `hw_rev`, `board_id`, `boardversion`, `nctxts`, `nfreectxts`, `serial`, `tempsense`, and write-only `chip_reset`.
- `sde_show()`, `sde_store()`, `sde_sysfs_ops`, and `SDE_ATTR()` implement per-engine SDMA kobject attributes.
- `sde_show_cpu_to_sde_map()`, `sde_store_cpu_to_sde_map()`, and `sde_show_vl()` bridge sysfs to SDMA CPU affinity and VL APIs.
- `hfi1_verbs_register_sysfs()` and `hfi1_verbs_unregister_sysfs()` create and destroy per-engine `sdma%d` kobjects and files.

## Control Flow
The RDMA core consumes `ib_hfi1_attr_group` and `hfi1_attr_port_groups` to create device and port attributes. Attribute show functions derive HFI1 device or port structures from the passed `ib_device`, `device`, or `kobject`, format values with `sysfs_emit()`, and return byte counts or errors. Congestion-control binary reads validate `pos` and `count`, take RCU read lock, fetch `cc_state`, and copy the requested bytes from shadow structures.

SDMA sysfs registration iterates over `dd->num_sdma`, initializes each engine kobject as `sdma%d` under the IB class device kobject, then creates `cpu_list` and `vl` files. Store operations require `CAP_SYS_ADMIN`; `cpu_list` writes are parsed and applied by `sdma_set_cpu_to_sde_map()`. Unregistration drops each kobject reference, relying on kobject cleanup to remove files.

## State and Persistence Behavior
Most attributes expose live in-memory driver state. `cc_prescan_store()` mutates `ppd->cc_prescan`. `chip_reset_store()` triggers `hfi1_reset_device()` only when the write starts with `reset` and a diagnostic client is present. `cpu_list` writes update SDMA per-engine CPU masks and the per-device rhashtable mapping through SDMA code. No sysfs value is persisted by this file across unload or reset.

## Dependencies and Integration Points
The file integrates with RDMA sysfs helpers, HFI1 MAD/congestion structures, HFI1 device and port data, temperature sensing, reset handling, SDMA mapping APIs, Linux capabilities, kobjects, and sysfs attribute groups. It exposes data consumed by administrators, diagnostic tooling, and performance tuning scripts.

## Risks and Edge Cases
Binary read bounds must avoid overflow or out-of-range `pos` handling. RCU-protected congestion state can be absent, returning `-EINVAL`. The `cc_prescan_store()` parser accepts prefixes `"on"` and `"off"` without rejecting other strings, so writes like `"only"` enable it. `chip_reset` is intentionally gated by both string and diagnostic-client checks but remains a powerful side-effecting sysfs write. SDMA kobject registration bailout loops from the current index down to zero; correctness depends on kobject reference behavior for partially initialized entries. `sde_store()` enforces `CAP_SYS_ADMIN`, which is important because CPU affinity affects packet ordering and performance.

## Test Signals
Useful tests include sysfs presence/permissions for device and port groups, partial binary reads with varied offsets and counts, congestion state absent/present cases, `cc_prescan` toggling, valid and invalid `chip_reset` writes, temperature read errors, per-SDMA `vl` output, `cpu_list` parsing for valid/invalid/offline CPUs, and register/unregister failure injection to confirm kobject cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/sysfs.c -->
