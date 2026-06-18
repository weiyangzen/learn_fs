# sources/distributed-fs/ceph-client/include/trace/events/wbt.h

Purpose: Instruments block writeback throttling latency, statistics, step changes, and timer activity.

Important APIs/types/functions: Defines `wbt_stat`, `wbt_lat`, `wbt_step`, and `wbt_timer`, exposing throttling window/depth, inflight counters, latency targets, step direction, and timer expiry/queue state.

Control flow: Writeback throttling code emits events when sampling latency, adjusting throttle depth, reporting stats, or arming timers. Events snapshot request-queue and throttling state.

State/persistence: WBT state remains in block-layer structures. Trace records provide persistent throttle-control observations.

Dependencies/integration: Depends on block queue/wbt internals and tracepoint infrastructure; consumed by block I/O latency diagnostics.

Risks: WBT is performance-sensitive. Tracepoint fields must not take locks or perturb throttling decisions, and queue lifetime must be respected.

Test signals: Run write-heavy block workloads with `wbt:*` enabled and verify latency/depth changes correlate with observed throttling.
