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
