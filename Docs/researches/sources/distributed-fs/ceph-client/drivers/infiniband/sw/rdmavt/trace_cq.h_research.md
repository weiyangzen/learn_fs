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
