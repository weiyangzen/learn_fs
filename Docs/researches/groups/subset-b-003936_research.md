# subset-b-003936 research

Grouped research for Intel irdma shared-control source files under `sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/ctrl.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/ctrl.c

## Purpose
`ctrl.c` is the shared-control implementation for the Intel `irdma` RDMA device driver. It builds and posts control queue pair (CQP) work queue elements, initializes software-control objects, configures HMC/FPM resource layout, manages QPs/CQs/SRQs/CEQs/AEQs/statistics/work-scheduler nodes, decodes completion and async-event queues, and handles iWARP termination protocol details. It is the hardware-facing bridge between higher-level verbs/connection-management code and the device-specific WQE/context formats defined by `defs.h`, `type.h`, `hmc.h`, and the generation-specific hardware tables.

## Important APIs, types, and functions
- QoS and VSI helpers include `irdma_get_qp_from_list()`, `irdma_sc_suspend_resume_qps()`, `irdma_change_l2params()`, `irdma_qp_add_qos()`, `irdma_qp_rem_qos()`, `irdma_sc_vsi_init()`, and `irdma_get_encoded_wqe_size()`. They maintain per-user-priority QP lists, queue-set handles, DCB/TC state, and MTU/IEQ reinitialization.
- CQP WQE builders cover ARP/APBVT/qhash/local-MAC operations, QP create/modify/destroy/upload/flush/suspend/resume, CQ create/modify/destroy, SRQ create/modify/destroy, memory registration and STAG/MW management, push pages, work-scheduler nodes, stats operations, CEQ/AEQ creation, HMC/FPM query and commit, and static HMC-page notification.
- QP setup is split by protocol and hardware generation. `irdma_sc_qp_setctx()` fills iWARP/TCP host context, while `irdma_sc_qp_setctx_roce()` dispatches to Gen2 or Gen3 RoCE context writers with different IRD, SRQ, stats, local-ack-timeout, packet-limit, and remote-atomic fields.
- CQP lifecycle and completion functions include `irdma_sc_cqp_init()`, `irdma_sc_cqp_create()`, `irdma_sc_cqp_get_next_send_wqe_idx()`, `irdma_sc_cqp_post_sq()`, `irdma_sc_cqp_destroy()`, `irdma_sc_ccq_get_cqe_info()`, `irdma_sc_poll_for_cqp_op_done()`, `irdma_sc_cqp_def_cmpl_ae_handler()`, and `irdma_sc_cqp_cleanup_handler()`.
- Event queue functions include `irdma_sc_ceq_init()`, `irdma_sc_process_ceq()`, `irdma_sc_cleanup_ceqes()`, `irdma_sc_aeq_init()`, `irdma_sc_get_next_aeqe()`, `irdma_sc_repost_aeq_entries()`, and `irdma_cfg_aeq()`.
- HMC/FPM functions include `irdma_sc_init_iw_hmc()`, `irdma_sc_parse_fpm_query_buf()`, `irdma_sc_cfg_iw_fpm()`, `irdma_cfg_fpm_val()`, Gen1/Gen2/Gen3 resource calculators, and `irdma_update_sds_noccq()`.
- Generic dispatch is centralized in `irdma_process_cqp_cmd()`, `irdma_process_bh()`, and the large `irdma_exec_cqp_cmd()` switch over `enum irdma_cqp_op_type`.
- iWARP termination helpers include `irdma_bld_terminate_hdr()`, `irdma_terminate_connection()`, `irdma_terminate_received()`, `irdma_terminate_send_fin()`, `irdma_sc_send_lsmm()`, and `irdma_sc_send_rtt()`.
- Device bring-up and stats functions include `irdma_sc_dev_init()`, `irdma_wait_pe_ready()`, `irdma_sc_init_hw()`, `irdma_vsi_stats_init()`, `irdma_vsi_stats_free()`, `sc_vsi_update_stats()`, and `irdma_update_stats()`.

## Control flow
Device setup starts in `irdma_sc_dev_init()`. The function initializes locks/lists, stores BAR/register and FPM-buffer pointers, sets broad hardware limits, obtains virtual-channel data for unprivileged functions, calls the generation-specific hardware initializer, and for privileged functions waits until PE firmware CPUs report ready before verifying that the RDMA PE doorbell window is enabled.

CQP bring-up is staged. `irdma_sc_cqp_init()` validates the SQ size, encodes the hardware SQ size, records SQ/host-context DMA addresses, initializes CQP rings and out-of-order/deferred-completion lists, and clears CQP-related registers. `irdma_sc_cqp_create()` allocates the sideband update-SD buffer, writes the CQP host context with protocol, DCQCN, VF, packed-PDU, Gen3 block-size/timestamp fields, programs the host-context address into CCQP registers, then polls `CCQPSTATUS`. After CCQ creation, CQP SD processing changes from register-polled `irdma_update_sds_noccq()` to normal CCQ-driven `irdma_cqp_sds_cmd`.

Most runtime operations follow the same pattern: validate IDs or PBL/HMC boundaries, call `irdma_sc_cqp_get_next_send_wqe()` or `_idx()`, fill qwords with `FIELD_PREP()` and `set_64bit_val()`, issue `dma_wmb()` before setting the valid header qword, optionally ring `irdma_sc_cqp_post_sq()`, and complete through CCQ polling/event processing or register polling for early bring-up commands. `irdma_process_cqp_cmd()` either executes immediately under `cqp_lock` when the ring has room or queues the command on `cqp_cmd_head`; `irdma_process_bh()` drains that backlog in bottom-half context.

QP lifecycle starts with `irdma_sc_qp_init()`, which validates fragment counts, initializes the user-kernel QP (`irdma_uk_qp_init()`), checks virtual-map PBLE bounds, encodes SQ/RQ sizes, records TPH and shadow/host context addresses, and inherits the VSI QoS queue-set handle. Protocol-specific context writers then populate the host context. CQP create/modify/destroy commands reference that host context and shadow area and encode next iWARP state, QP type, hash removal, termination action, TCP-context validity, ORD/MSS/CQ fields, and virtual mapping.

HMC/FPM control is a separate bring-up flow. `irdma_sc_init_iw_hmc()` queries firmware resource maxima into the FPM query buffer and parses object sizes/counts plus Gen3 scratch-buffer needs. `irdma_cfg_fpm_val()` chooses object counts from the requested QP count and available SDs, with older generations iteratively trimming QP/MR/PBLE counts and Gen3 splitting local-memory versus host-memory resources. `irdma_sc_cfg_iw_fpm()` commits selected counts, then parses firmware-assigned bases and final SD count. SD updates use compact inline entries for up to three entries and a per-WQE side buffer for extras.

Completion processing reads valid bits with polarity, uses `dma_rmb()` before consuming CQE/AEQE contents, decodes status and operation metadata, updates software rings and CQP completion counters, and handles Gen3 deferred or out-of-order completion tickets via protected pending/available lists. CEQ processing returns a valid CQ ID and skips invalid sentinel entries; AEQ processing maps hardware AE source/code fields to QP/CQ/SRQ flags, WQE indices, TCP/iWARP state, completion context, and Gen3 error-index validity.

## State and persistence
The file maintains persistent driver state in `struct irdma_sc_dev`, `struct irdma_sc_cqp`, `struct irdma_sc_vsi`, and per-object `struct irdma_sc_qp/cq/srq/ceq/aeq` instances. CQP state includes SQ ring head/tail, polarity, requested/completed operation counters, scratch-array entries, pending command list, out-of-order/deferred completion lists, sideband SD buffer, and hardware callback selection.

VSI state includes MTU, QoS queue-set metadata, user-priority QP lists, statistics index allocation, DMA gather buffers, and timers for pre-Gen3 stats. QP state includes user priority, queue-set handle, flush flags, termination flags, event/flush codes, Q2 buffer and host/shadow context pointers, push-page index, and protocol-specific marker state.

Hardware-visible persistence is primarily in device contexts, HMC/FPM commit state, work scheduler nodes, ARP/local-MAC/qhash tables, PBLE/HMC SD programming, CQ/SRQ/QP contexts, push-page allocations, and stats instances. The driver does not persist settings across reboot; it programs hardware state for the active device lifetime and frees coherent DMA buffers during teardown. Some writes intentionally update hardware before later paths rely on state, such as QoS queue-set changes during traffic-class changes and stats index allocation/free around VSI lifetime.

## Dependencies and integration points
`ctrl.c` depends on kernel DMA coherent allocation, MMIO register access, endian conversion, list/spinlock/mutex/atomic primitives, bitfield helpers, and memory barriers. It integrates tightly with irdma user-kernel queue helpers (`irdma_uk_qp_init()`, `irdma_uk_cq_init()`, `irdma_qp_get_next_send_wqe()`, `irdma_uk_qp_post_wr()`), HMC helpers, work-scheduler functions, virtual-channel functions for unprivileged devices, multicast/AH helpers implemented elsewhere, and generation-specific hardware initialization (`i40iw_init_hw()`, `icrdma_init_hw()`, `ig3rdma_init_hw()`).

The file is the common CQP command backend for higher layers that fill `struct cqp_cmds_info`. It also exposes direct helper APIs for early bring-up paths that cannot yet rely on the CCQ, and for connection-management paths that must send LSMM/RTT or iWARP terminate messages directly on a QP SQ.

## Risks
- WQE correctness depends on exact bit layouts and generation-specific differences. A wrong `FIELD_PREP()`, qword offset, or Gen2/Gen3 branch can silently program invalid hardware state.
- Most CQP builders set the valid bit only after `dma_wmb()`. Any refactor that moves valid-bit writes before data writes can create device-visible torn WQEs.
- CQP ring state is shared among normal execution, bottom-half backlog draining, completion handling, polling paths, and cleanup. Locking around `cqp_lock` and `ooo_list_lock` is critical.
- `irdma_sc_suspend_resume_qps()` carries `qp` across user-priority loops without resetting it at each priority. The current traversal starts with the previous value; changes here should be audited carefully against list membership and QoS locking.
- `irdma_sc_qp_flush_wqes()` latches `qp->flush_sq` and `qp->flush_rq` before confirming that a WQE was allocated. If allocation fails, later flush requests may be suppressed as already requested.
- HMC/FPM sizing is complex and hardware-generation-sensitive. Loop trimming, local-memory page accounting, and PBLE/MR split decisions can underprovision resources or exceed firmware limits.
- Termination header building parses packet data from Q2 buffers using assumed Ethernet/IP/TCP/MPA layout. Malformed or short Q2 data is mostly trusted after AE flags, so bounds assumptions are important.
- Several early bring-up commands poll registers while later commands use CCQ/event completion; mixing wait types incorrectly can wedge initialization or leak CQP slots.
- Feature query buffer retry frees and reallocates DMA memory; error paths must not leak or double-free. Gen3 FPM query also allocates firmware scratch buffers and frees only partial allocations on second-buffer failure.

## Test signals
- Build the `irdma` driver across supported hardware generation configs and run static analysis focused on bitfield width/shift mismatches, unchecked integer truncation, list/ring bounds, and DMA allocation cleanup.
- Bring-up tests should cover privileged and unprivileged paths, PE-ready timeout, disabled/invalid doorbell-size handling, CQP create/destroy, CCQ/CCE creation, FPM query/commit, SD updates before and after CCQ creation, and static HMC pages allocated notification.
- CQP tests should exercise all `enum irdma_cqp_op_type` dispatch cases, immediate execution versus backlog queuing, ring-full handling, register-poll and CCQ-poll wait types, error CQEs, deferred completions, out-of-order completions, and cleanup of pending CQP operations.
- Resource tests should validate Gen1, Gen2, and Gen3 FPM sizing over small and large requested QP counts, local-memory present/absent cases, resource-version-2 paths, PBLE/MR caps, scratch-buffer allocation, and failure paths.
- QP/CQ/SRQ tests should verify invalid IDs, virtual-map PBLE bounds, queue-size encoding, context fields for iWARP/RoCE Gen2/RoCE Gen3, SRQ limits, CQ resize with virtual maps, push-page bounds, and flush duplicate suppression.
- Event tests should inject representative AEQE/CEQE/CCQE entries for every source class and confirm QP/CQ/SRQ flags, completion contexts, polarity toggling, error-index validity, and stat counter rollover behavior.
- Protocol tests should cover iWARP LSMM/RTT WQE generation, terminate send/receive flows, malformed terminate validation, Q2 data parsing, and AE-to-flush-code mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/ctrl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/defs.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/defs.h

## Purpose
`defs.h` is the central constants and bitfield-definition header for the Intel `irdma` shared-control and queue code. It names hardware states, opcodes, object limits, WQE/context bit masks, ring manipulation macros, alignment requirements, and endian-safe qword/dword accessors used by `ctrl.c` and related irdma files. The header is not business logic by itself; it is the hardware ABI map that makes the CQP/QP/CQ/AEQ/CEQ/HMC code readable and generation-aware.

## Important APIs, types, and macros
- Protocol and state constants define supported RDMA protocol modes (`enum irdma_protocol_used`), QP states, TCP states, CQ types, QP types, termination flags/actions, AE source encodings, CQP wait styles, feature bits, and common queue/resource limits.
- `enum irdma_cqp_op_type` is the driver-facing command taxonomy used by `struct cqp_cmds_info` and `irdma_exec_cqp_cmd()`. It maps high-level operations such as QP/CQ/SRQ lifecycle, stats, work-scheduler, FPM, ARP/qhash, AH, multicast, and local-MAC operations to dispatch cases.
- `IRDMA_CQP_OP_*` macros are hardware CQP SQ opcodes written into WQEs. They are distinct from the driver-facing enum and include values for QP/CQ/SRQ, STAG/MR/MW, ARP/local-MAC, FPM, CEQ/AEQ, APBVT, qhash, suspend/resume, stats, and user-priority map commands.
- CQP WQE masks define qword layouts for qhash, stats, work-scheduler nodes, user-priority map, RDMA feature query, CQP host context, QP create/modify/destroy, SRQ, CQ, STAG/MR/MW, local MAC/ARP, push pages, upload context, HMC function table, CEQ/AEQ, FPM commit/query, flush/generate-AE, update-SD, suspend/resume, and error codes.
- QP host-context masks (`IRDMAQPC_*`) define TCP/iWARP/RoCE state fields, queue sizes and DMA addresses, IP/port/VLAN/ARP fields, congestion-control knobs, PD/PKey/QKey/destination QP, sequence/window state, CQ IDs, stats indices, Q2 address, MAC address, ORD/IRD encodings, RDMA capabilities, TPH and QoS handles, local IPs, thresholds, SRQ fields, Gen3 stats/pkt-limit fields, and remote-atomic enable.
- SQ/RQ WQE masks (`IRDMAQPSQ_*`, `IRDMAQPRQ_*`, and UDA fields) define opcodes, fragment lengths/STags, inline/immediate flags, memory-window binding and fast-register fields, fences, UDP header flags, AH IDs, destination QPN/QKey, and validity/signaled bits.
- Completion and event masks (`IRDMA_CQ_*`, `IRDMACQ_*`, `IRDMA_CEQE_*`, `IRDMA_AEQE_*`) define CQE, CEQE, and AEQE valid/error/source/context layouts, including separate Gen3 AEQE fields.
- Ring macros provide head/tail initialization, movement, free/used calculations, full checks, SQ reserved-space checks, polarity-independent element accessors, and CQP WQE zeroing.
- `enum irdma_qp_wqe_size`, `enum irdma_ws_node_op`, alignment constants, and `enum icrdma_protocol_used` describe fixed sizes and compatibility values.
- `set_64bit_val()`, `set_32bit_val()`, `get_64bit_val()`, and `get_32bit_val()` are inline endian conversion helpers for indexed WQE/context access by byte offset.

## Control flow
This header has no executable control flow beyond inline helpers and ring macros, but it dictates runtime control flow in `ctrl.c`. Driver-facing CQP operation enums select `irdma_exec_cqp_cmd()` switch cases; hardware opcode macros populate WQE headers; ring macros decide whether a producer can allocate another WQE and how completion consumers advance polarity; wait-style constants select register polling, CCQ polling, or event-driven completion; and AE source/state constants drive async-event classification.

The ring macros implement the core circular-buffer algorithm. `IRDMA_RING_INIT()` clears head/tail and records size, producer-side movement checks for full or SQ-reserved conditions before advancing head, consumer-side movement advances tail modulo size, and used/free calculations are modulo arithmetic. SQ-specific macros reserve 256 entries, matching `IRDMA_SQ_RSVD`, so QP SQ accounting intentionally differs from generic ring accounting.

## State and persistence
`defs.h` does not allocate state, but its constants define the shape of persistent software and hardware state. Queue size limits and reserved entries constrain QP/SRQ/CQP rings. Bit masks define how driver state is serialized into device-owned WQEs, host contexts, completion entries, async events, FPM buffers, and shadow doorbell areas. The inline accessors persist values into little-endian DMA memory, which hardware then consumes asynchronously.

Several definitions encode generation-specific state. IRD encodings differ between older hardware and Gen3, AEQE fields have Gen3-specific masks, APBVT resources disappear on Gen3, local-memory enable bits affect FPM commit buffers, and QP context fields such as SRQ ID, remote atomics, stat index, packet limit, and local ack timeout are Gen3-sensitive. These definitions are therefore part of the compatibility contract for multiple hardware generations.

## Dependencies and integration points
The header depends on Linux bit macros such as `BIT`, `BIT_ULL`, `GENMASK`, `GENMASK_ULL`, endian helpers, and `FIELD_PREP()`/`FIELD_GET()` users in implementation files. It is included by low-level irdma files that build WQEs, parse completion entries, size resources, and manage rings. It aligns with hardware register/mask tables stored in `struct irdma_sc_dev` through the `FLD_LS_64()`, `FLD_RS_64()`, `FLD_LS_32()`, and `FLD_RS_32()` macros, which use generation-specific `hw_shifts` and `hw_masks` arrays.

Integration is strongest with `ctrl.c`: almost every WQE builder in that file uses these masks, and the CQP dispatcher depends on the enum values. User-kernel queue code also relies on the ring macros and QP WQE masks for send/receive work requests. HMC/FPM code uses query/commit masks and resource constants to parse firmware buffers and size SD/PBLE/MR objects.

## Risks
- The header is an ABI map for hardware. A one-bit mistake can corrupt WQEs or contexts while still compiling cleanly.
- Driver-facing `enum irdma_cqp_op_type` values and hardware `IRDMA_CQP_OP_*` values are intentionally different. Confusing them would dispatch the right software case but post the wrong hardware opcode, or vice versa.
- Some aliases are intentional but easy to misuse, such as `IRDMA_QP_STATE_CLOSING` and `IRDMA_QP_STATE_SQD` both being `3`, and `IRDMA_CQP_OP_GEN_AE` sharing opcode `0x22` with flush WQEs.
- Ring macros are statement-like macros with side effects and no type checking. Passing expressions with side effects or wrong ring objects can produce subtle bugs.
- SQ ring capacity reserves 256 entries, so using generic ring-free/full macros on SQs can overrun reserved space.
- Gen3 and pre-Gen3 field layouts coexist in the same namespace. Missing a generation branch when reading AEQEs or writing QP contexts can decode the wrong bits.
- Inline `set_*`/`get_*` helpers index by byte offset shifted to qword/dword index. Callers must pass aligned byte offsets; the helper does not validate alignment or bounds.
- Several masks overlap by design because different WQE formats reuse qword positions. Reusing a mask in the wrong WQE format can set a valid-looking but semantically incorrect bit.

## Test signals
- Compile coverage should include all supported irdma hardware generations and sparse/smatch-style checks for invalid `FIELD_PREP()` widths, constant truncation, and endian misuse.
- Unit-style tests or debug assertions around ring macros should cover wraparound, full/empty, SQ reserved entries, count-based movement, and polarity transitions in CQ/CEQ/AEQ consumers.
- Hardware or simulator tests should validate each CQP opcode emitted by `ctrl.c` against the corresponding `IRDMA_CQP_OP_*` and mask layout in this header.
- Event parsing tests should feed pre-Gen3 and Gen3 AEQE/CQE formats and verify source, context, state, overflow, WQE-index, and valid-bit decoding.
- FPM/HMC tests should verify query and commit field extraction, local-memory enable placement, PBLE/MR resource caps, and Gen3 scratch-buffer offsets.
- Protocol tests should cover QP state constants, TCP states, terminate action values, RDMA operation opcodes, fast-register fields, and remote-atomic feature gating.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/defs.h -->
