# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/nehalemep/memory.json

Purpose: defines 67 Nehalem EP offcore memory response events focused on DRAM and LLC-miss outcomes. The rows form a matrix across request classes such as any data, instruction fetch, RFO, writeback, demand data, demand instruction fetch, demand RFO, prefetch data, prefetch instruction fetch, prefetch RFO, other, and aggregate request groups, crossed with response locations such as any DRAM, any LLC miss, local DRAM, and remote DRAM.

Important APIs/types/functions: every row uses `EventName`, `EventCode` `0xB7`, `UMask` `0x1`, constrained `Counter` `2`, `MSRIndex` `0x1A6`, an `MSRValue` filter, `SampleAfterValue`, and `BriefDescription`. The `MSRIndex`/`MSRValue` pair is the key schema surface: perf must program the offcore response filter MSR as well as the architectural event selector.

Control flow: at build time `jevents.py` recognizes `MSRIndex`, looks it up through its MSR mapping, and emits event strings that include the offcore filter. At runtime perf schedules the event on counter 2, writes the offcore response MSR filter, and counts requests matching both request type and response location.

State and persistence: no mutable source state. Runtime state includes a programmable counter plus the model-specific offcore response MSR, which is shared hardware configuration and must be managed carefully by perf scheduling. Measurements persist only through perf output.

Dependencies and integration points: depends on Nehalem EP offcore response MSR semantics, kernel support for programming offcore filters, and perf event generation. Integrates tightly with `cache.json`, where broader cache/offcore aliases and retired memory events provide complementary views of cache misses and data sources.

Risks: all rows share the same event code, umask, MSR index, and counter, so the `MSRValue` is the only differentiator for many aliases; copy/paste errors are hard to spot. Counter 2 exclusivity can create scheduling conflicts. Local versus remote DRAM semantics matter on multi-socket systems; on unsuitable hardware, counts may be zero or misleading. Some aggregate filters such as `ANY_LLC_MISS` include broad response masks rather than just DRAM.

Test signals: validate JSON, inspect generated event strings for `offcore_rsp`/MSR filters, verify `perf list` aliases, and run local versus remote NUMA memory workloads on Nehalem EP-class systems. Scheduling tests should combine two offcore response events to ensure perf handles the shared MSR and counter constraint correctly.
