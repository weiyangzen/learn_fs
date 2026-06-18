# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/clearwaterforest/frontend.json

Purpose: Defines two Clearwater Forest instruction-cache frontend PMU aliases: `ICACHE.ACCESSES` and `ICACHE.MISSES`. These support perf analysis of instruction stream cache-line entry and instruction-cache miss behavior.

Important APIs/types/functions: Both records use `EventCode: 0x80`, counters `0,1,2,3,4,5,6,7`, and `SampleAfterValue: 1000003`. `ICACHE.ACCESSES` uses `UMask: 0x3`; `ICACHE.MISSES` uses `UMask: 0x2`. There are no metrics, MSR filters, or public descriptions beyond the brief descriptions.

Control flow: `jevents.py` generates two Clearwater Forest frontend aliases from the JSON. At runtime, perf maps the aliases to core PMU event `0x80` with the selected umask, allowing users to count instruction-cache line accesses and missing cache-line entries. The same event code with different masks lets users compute miss ratios if the hardware definitions are compatible.

State and persistence behavior: Static build metadata only. Runtime state is per-core frontend PMU counting while the event is enabled. `SampleAfterValue` sets the default sampling period for record-style use but does not affect stat-mode counts.

Dependencies: Depends on the Clearwater Forest core PMU implementing event `0x80` as described, perf JSON generation, and the x86 model map. It also depends on users understanding that the access definition includes sequential line walks and jump redirections into new cache lines.

Integration points: Integrates with `pipeline.json` frontend-bound topdown events and branch events. I-cache misses can help explain `TOPDOWN_FE_BOUND.ALL` or branch-resteer-heavy workloads, while `ICACHE.ACCESSES` gives the denominator for miss-rate style analysis.

Risks: The miss description ends with a dangling hyphen and lacks a `PublicDescription`, so generated help text is thin. Accesses and misses share one event code; a wrong umask would invert or collapse the ratio. Instruction-cache behavior can be sensitive to SMT, code layout, and predecode/fetch details that are not captured in this metadata.

Test signals: JSON parse, `jevents.py` generation, and `perf list` should show both `icache.accesses` and `icache.misses`. Hardware smoke tests should compare tight loops that fit in the I-cache against large code-footprint or branch-heavy workloads and check that misses rise while accesses remain plausible.
