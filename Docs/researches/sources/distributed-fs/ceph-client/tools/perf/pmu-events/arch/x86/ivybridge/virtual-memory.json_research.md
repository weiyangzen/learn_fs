# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/ivybridge/virtual-memory.json

Purpose: Defines 18 Ivy Bridge core PMU aliases for instruction/data TLB misses, page walks, TLB flushes, and EPT walk cycles. The file supports virtual-memory and address-translation analysis in perf.

Important APIs/types/functions: Entries expose `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, and occasional `PublicDescription`. Families include `DTLB_LOAD_MISSES`, `DTLB_STORE_MISSES`, `ITLB_MISSES`, `ITLB`, `TLB_FLUSH`, and `EPT`. The aliases distinguish first-level TLB misses that hit the second-level TLB, misses that cause page walks, completed walks, large-page walks, walk duration cycles, and thread/STLB flush events.

Control flow: Perf parses this JSON into the Ivy Bridge event table. At runtime, a requested alias such as `DTLB_LOAD_MISSES.WALK_DURATION` is resolved to event select/unit mask and scheduled on a core programmable counter. Sampling aliases use `SampleAfterValue` as a default period. Higher-level metrics can divide walk duration or walk counts by clocks or instructions.

State and persistence: Static PMU metadata only. The file has no mutable state; hardware PMU counters represent runtime translation behavior.

Dependencies/integration: Depends on Ivy Bridge core PMU definitions and perf's JSON parser. It integrates with topdown memory-TLB metrics in Ivy Town metric data, where expressions reference events like `DTLB_LOAD_MISSES.WALK_DURATION`, `DTLB_STORE_MISSES.WALK_DURATION`, and `ITLB_MISSES.WALK_DURATION`.

Risks: Similar names differ sharply between count and duration events. Some descriptions say STLB load misses for ITLB paths, so documentation wording should be checked before relying on it for user-facing education. Page-walk duration events are cycle-like and should not be summed with completed-walk counts without normalization. EPT events are virtualization-specific and may read as zero outside VM workloads.

Test signals: Schema checks should enforce valid event fields and unique names. Runtime smoke tests should request representative load, store, instruction, and flush aliases. Metric tests should ensure all TLB aliases referenced by Ivy Bridge/Ivy Town topdown formulas are present and resolvable.
