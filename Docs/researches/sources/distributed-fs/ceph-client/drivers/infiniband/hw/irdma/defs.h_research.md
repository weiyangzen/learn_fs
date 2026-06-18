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
