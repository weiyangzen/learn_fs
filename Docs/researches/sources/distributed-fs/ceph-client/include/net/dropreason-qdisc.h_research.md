# sources/distributed-fs/ceph-client/include/net/dropreason-qdisc.h

Read `sources/distributed-fs/ceph-client/include/net/dropreason-qdisc.h` completely for this pass (114 lines, 3761 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/net/dropreason-qdisc.h_research.md`.

Purpose: defines traffic-control qdisc-specific drop reasons as a subsystem-encoded extension of skb drop reasons, enabling detailed diagnostics for queueing discipline drops.

Important APIs/types/functions: `DEFINE_QDISC_DROP_REASON(FN, FNe)` lists qdisc reasons. `enum qdisc_drop_reason` starts at `QDISC_DROP_UNSPEC`, defines `__QDISC_DROP_REASON` as `SKB_DROP_REASON_SUBSYS_QDISC << SKB_DROP_REASON_SUBSYS_SHIFT`, then enumerates `QDISC_DROP_GENERIC`, `OVERLIMIT`, `CONGESTED`, `MAXFLOWS`, `FLOOD_PROTECTION`, `BAND_LIMIT`, `HORIZON_LIMIT`, `FLOW_LIMIT`, `L4S_STEP_NON_ECN`, and `QDISC_DROP_MAX`.

Control flow: qdisc implementations select a qdisc-specific reason when enqueue/dequeue algorithms drop packets. Tracepoints can combine the reason with qdisc handle/name and map it through the qdisc drop reason list registered for the subsystem.

State and persistence: no state is stored. Values are part of the diagnostic reason namespace and should remain stable for tracing.

Dependencies and integration points: depends on `net/dropreason.h` for subsystem tagging. It integrates with TC qdisc algorithms such as CoDel/PIE/RED/FQ/SFQ/CAKE/DualPI2 and qdisc tracepoints.

Risks: `QDISC_DROP_UNSPEC` is a sentinel like not-dropped, not a valid final reason. Reasons must stay below subsystem bounds and must have matching registered strings. Algorithm-specific drops should choose the most precise reason to preserve observability.

Test signals: qdisc trace tests for overlimit, active congestion, flow-table exhaustion, flood protection, band/flow/horizon limits, DualPI2 non-ECN L4S drops, string mapping registration, and fallback to generic where appropriate.
