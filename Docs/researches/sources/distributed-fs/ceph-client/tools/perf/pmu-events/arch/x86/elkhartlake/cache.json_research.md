<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/elkhartlake/cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/elkhartlake/cache.json

## Purpose
Describes Elkhart Lake core PMU cache-related events for perf's `jevents.py` generator. The file contains 120 JSON event entries grouped around L2/LLC requests, load/store retired cache outcomes, memory-bound stall attribution, and a large set of offcore-response (`OCR.*`) encodings.

## Important APIs, Types, And Functions
This is data consumed by `tools/perf/pmu-events/jevents.py`, not executable code. Important schema fields are `EventName`, `EventCode`, `UMask`, `BriefDescription`, `PublicDescription`, `SampleAfterValue`, `Counter`, `PEBS`, `Data_LA`, `MSRIndex`, `MSRValue`, and `Deprecated`. `EventCode` and `UMask` become perf event selectors; `MSRIndex`/`MSRValue` refine offcore-response filters; `PEBS` and `Data_LA` tell perf that precise sampling and data linear-address capture are available for selected events.

## Control Flow
During the perf build, `jevents.py` discovers this `.json` under the `elkhartlake` directory referenced by `arch/x86/mapfile.csv` for `GenuineIntel-6-9[6C]`. It parses each object into generated C PMU table entries. At runtime perf matches the CPU family/model, loads the Elkhart Lake table, and exposes names such as `L2_REQUEST.MISS`, `LONGEST_LAT_CACHE.MISS`, `MEM_LOAD_UOPS_RETIRED.L3_MISS`, and `OCR.*` aliases to `perf stat` and `perf record`.

## State And Persistence
The JSON itself is static repository data. Persistent generated state is the compiled `pmu-events.c` table embedded in perf. Runtime state is limited to programmed PMU counters, offcore MSR filter values, and sampled PEBS records.

## Dependencies And Integration Points
Depends on the x86 PMU JSON schema, `jevents.py` field conversion, perf metric parsing, and the `mapfile.csv` Elkhart Lake mapping. Metrics in `ehl-metrics.json` depend on `LONGEST_LAT_CACHE.MISS`, and many `OCR.*` entries depend on Intel offcore-response MSR support being modeled correctly by `MSRIndex` and `MSRValue`.

## Risks And Edge Cases
There are 87 `OCR.*` entries with MSR filters, so copy/paste or hex-value mistakes can silently point an alias at the wrong offcore response. Eight entries are deprecated and must remain discoverable without encouraging new use. Fourteen entries carry `PEBS`; fourteen carry `Data_LA`, so precise-event metadata must stay aligned with hardware support. Blank `UMask` fields for some aggregate events rely on `jevents.py` defaulting behavior.

## Test Signals
Run `jq empty` on the file, build perf with jevents enabled, and run `perf list` on an Elkhart Lake model or generated table test to confirm cache aliases appear. Exercise `perf stat -e L2_REQUEST.MISS,LONGEST_LAT_CACHE.MISS` and an `OCR.*` alias where hardware is available. Metric smoke tests should verify `L3_Cache_Fill_BW` can resolve `LONGEST_LAT_CACHE.MISS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/elkhartlake/cache.json -->
