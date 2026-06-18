# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/ivytown/other.json

Purpose: Defines 4 Ivy Town miscellaneous core PMU aliases for current privilege level cycle accounting and split/uncacheable lock duration. These fill gaps not covered by cache, frontend, floating-point, or pipeline-specific files.

Important APIs/types/functions: Entries use `EventName`, `EventCode`, `UMask`, `Counter`, `CounterMask`, `EdgeDetect`, `SampleAfterValue`, `BriefDescription`, and `PublicDescription`. The `CPL_CYCLES` family includes `RING0`, `RING0_TRANS`, and `RING123`; `RING0_TRANS` uses `CounterMask: 1` and `EdgeDetect: 1` to count intervals/transitions rather than raw cycles. `LOCK_CYCLES.SPLIT_LOCK_UC_LOCK_DURATION` counts cycles with L1/L2 locked due to split or uncacheable locks.

Control flow: Perf's table generator includes these aliases in the Ivy Town core event map. Runtime lookup schedules the selected event on core programmable counters and applies edge/counter-mask qualifiers where present. System or OS metrics can use CPL cycle aliases to estimate kernel/user privilege activity, while lock-cycle aliases help diagnose pathological locked memory operations.

State and persistence: Static metadata only. Hardware PMU counters and perf outputs hold runtime counts.

Dependencies/integration: Depends on Ivy Town core PMU definitions and perf support for edge-detected events. It complements `ivt-metrics.json` OS/system metrics, which separately use privilege-qualified cycle and instruction aliases, and cache lock events from `cache.json`.

Risks: `CPL_CYCLES.RING123` combines rings 1, 2, and 3; most user workloads run ring 3, but the alias name should not be simplified to user-only in documentation. Transition counts and cycle counts have different units despite shared event code. Split/UC lock behavior can be rare and workload-specific, so zero counts are not necessarily a failure.

Test signals: Validate schema and generated aliases, including `EdgeDetect` on `RING0_TRANS`. Runtime smoke tests should compare ring0/ring123 counts under syscall-heavy versus user-space loops and trigger split-lock/UC-lock scenarios only in controlled tests where the platform permits them.
