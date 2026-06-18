# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen5/l3-cache.json

Purpose: Defines 17 Zen 5 L3 PMU events for coherent lookup hit/miss state and sampled cross-interconnect latency/request counters.

Important APIs/types/functions: The schema includes `EventName`, `EventCode`, `UMask`, `Unit: L3PMC`, `SliceId`, `ThreadMask`, `EnAllSlices`, and `EnAllCores`, plus descriptions. Families are `l3_lookup_state.*`, `l3_xi_sampled_latency.*`, and `l3_xi_sampled_latency_requests.*`.

Control flow: Perf maps these uncore/L3 aliases to the L3 PMU. Recommended metrics use lookup events for L3 accesses/misses and divide sampled latency counters by sampled request counters for all, local DRAM, and remote DRAM latency estimates.

State and persistence: No runtime state is kept in JSON. The persistent behavior is all-slice/all-core L3 counting via `EnAllSlices`/`EnAllCores` and fixed `SliceId`/`ThreadMask` settings.

Dependencies and integration: Integrates with the L3 PMU driver, recommended L3 metrics, and memory hierarchy analysis alongside L2 and load-store fill-source events.

Risks: Sampled latency values are only meaningful with matching request counters and nonzero denominators. The L3 events are uncore-style and may require careful aggregation across CCD/slice topology. Extension-memory and near/far source masks must track hardware documentation.

Test signals: Validate `perf list l3_`, run cache-working-set tests that hit and miss LLC, check all-slice aggregation, and verify recommended L3 latency metrics avoid divide-by-zero through `d_ratio` or equivalent handling.
