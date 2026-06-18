# sources/distributed-fs/ceph-client/include/trace/events/napi.h

Purpose: Provides tracepoints for NAPI poll execution and dynamic queue limit stall detection in networking drivers. It helps correlate driver poll budget use, work completion, and transmit queue stalls.

Important APIs/types/functions: `napi_poll` records a `struct napi_struct *`, associated `struct net_device *`, poll work, and budget. `dql_stall_detected` records stall counters from `struct dql`, the running DQL numbers, a device name, queue index, and the source line that emitted the trace.

Control flow: Network drivers and core NAPI scheduling code call `trace_napi_poll()` after poll callbacks return. DQL code calls the stall event when queue accounting suggests transmit completion progress has stopped. Trace assignment snapshots device naming and queue counters while the caller still owns the relevant objects.

State and persistence: The header stores no state. Runtime state lives in NAPI instances, netdev queues, and DQL accounting; emitted records are transient tracing data.

Dependencies and integration points: Includes netdevice, tracepoint, and ftrace headers. It integrates with driver poll loops, byte queue limits, perf/ftrace, and troubleshooting of interrupt moderation and softirq receive processing.

Risks and test signals: Risks include stale device pointers during unregister, inaccurate budget/work interpretation for drivers with unusual poll semantics, and high-volume tracing on busy queues. Test signals include NAPI selftests or driver RX stress, DQL stall injection, netdev teardown with tracing enabled, and build coverage for drivers using byte queue limits.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/napi.h` completely for this pass (77 lines, 1945 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/napi.h_research.md`.
