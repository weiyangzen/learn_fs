<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/knightslanding/uncore-memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/knightslanding/uncore-memory.json

## Purpose
This JSON file defines Knights Landing uncore memory-controller PMU events for perf. It covers MCDRAM EDC access, EDC read/write queue inserts, EDC clockticks, DDR iMC CAS counts, and iMC clockticks. The complete 120-line array was read and contains 14 records across `EDC_ECLK`, `EDC_UCLK`, `iMC_DCLK`, and `iMC_UCLK` units, all with `PerPkg` `1`.

## Important APIs, Types, and Functions
There are no functions or classes; the file's API is its perf aliases. Event families are `UNC_E_EDC_ACCESS` (5 records), `UNC_M_CAS_COUNT` (3), `UNC_E_RPQ_INSERTS`, `UNC_E_WPQ_INSERTS`, `UNC_E_E_CLOCKTICKS`, `UNC_E_U_CLOCKTICKS`, `UNC_M_D_CLOCKTICKS`, and `UNC_M_U_CLOCKTICKS`. Ten records have explicit `EventCode` and `UMask`; the four clocktick records omit one or both of those fields and rely on generator defaults plus their `Unit`.

The `UNC_E_EDC_ACCESS.*` records distinguish MCDRAM cache hits and misses by clean, dirty, and invalid state. `UNC_E_RPQ_INSERTS` and `UNC_E_WPQ_INSERTS` count MCDRAM read and write requests across flat, cache, and hybrid memory modes. `UNC_M_CAS_COUNT.RD`, `.WR`, and `.ALL` expose DDR CAS traffic through the iMC DCLK domain.

## Control Flow
The file is discovered by `tools/perf/pmu-events/Build` and parsed by `jevents.py`. Units not explicitly listed in the fixed unit table are converted to lowercase uncore PMU names, so `EDC_ECLK` becomes `uncore_edc_eclk`, `EDC_UCLK` becomes `uncore_edc_uclk`, `iMC_DCLK` becomes `uncore_imc_dclk`, and `iMC_UCLK` becomes `uncore_imc_uclk`. `EventCode` and `UMask` become generated `event=` and `umask=` fields when present, and zero/missing values are omitted or defaulted according to generator behavior. The Knights Landing model map row selects these aliases for family/model `GenuineIntel-6-(57|85)`.

## State and Persistence
The JSON is immutable source metadata. Persistence is the generated perf event table, and runtime state lives only in hardware PMU counters and kernel uncore PMU instances. The file's descriptions contain important mode semantics: several EDC access events are valid only in MCDRAM cache or hybrid mode, while RPQ/WPQ inserts are valid in flat, cache, and hybrid modes.

## Dependencies and Integration Points
Dependencies include the perf JSON schema, `jevents.py`, x86 model mapping, and kernel uncore drivers for the EDC and iMC clock domains. The file integrates with Knights Landing memory-mode analysis: MCDRAM hit/miss cleanliness comes from EDC events, DDR bandwidth comes from iMC CAS counts, and clockticks provide normalization denominators. It pairs naturally with `uncore-cache.json` TOR/home-agent traffic and `uncore-io.json` M2PCIe traffic when attributing memory pressure.

## Risks
Mode validity is the main semantic risk. EDC cache hit/miss events are not meaningful in every MCDRAM configuration, so users can misread flat-mode counts without checking platform mode. Unit naming is another risk because `jevents.py` derives uncore PMU names from mixed-case strings; kernel PMU naming must match the derived lowercase names. Missing `EventCode`/`UMask` on clockticks is intentional-looking but should be guarded by generated-output tests. `UNC_E_EDC_ACCESS.MISS_INVALID` has a terse description compared with the other MCDRAM events, increasing user-facing ambiguity.

## Test Signals
Test with `jq empty`, a perf tools build, and generated aliases under the expected `uncore_edc_*` and `uncore_imc_*` PMUs. Hardware smoke tests should run in flat, cache, and hybrid MCDRAM modes where available, checking that EDC access events behave according to their stated mode validity. Bandwidth validation can compare `UNC_M_CAS_COUNT.RD/WR/ALL` ratios and use clockticks to normalize rates. Generated C diffs should flag any accidental loss of `PerPkg` or unit-derived PMU names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/knightslanding/uncore-memory.json -->
