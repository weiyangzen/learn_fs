<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/common-and-microarch.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/common-and-microarch.json

## Purpose
Defines the Arm64 architecture-wide event dictionary used when model files dereference standard events with `ArchStdEvent`. It contains 369 named `EventName`/`EventCode` records spanning base architectural counters, cache/TLB, stall, branch, SPE, SVE, FP, and Armv9-style microarchitectural extensions; the densest name families are SVE (54), ASE (51), L1D (29), FP (29), STALL (27), L1I (24), BR (22), L2D (21).

## APIs, Types, and Functions
This data file exports JSON objects with `EventName`, `EventCode`, `BriefDescription`, and sometimes `PublicDescription`. Early canonical entries include `SW_INCR`=`0x00`, `L1I_CACHE_REFILL`=`0x01`, `L1I_TLB_REFILL`=`0x02`, `L1D_CACHE_REFILL`=`0x03`, `L1D_CACHE`=`0x04`, `L1D_TLB_REFILL`=`0x05`, `LD_RETIRED`=`0x06`, `ST_RETIRED`=`0x07`; later entries include newer FP/SVE/ASE forms such as `FP_BF16_FIXED_MIN_OPS_SPEC`, `FP_FP8_FIXED_MIN_OPS_SPEC`, `FP_SP_SCALE_MIN_OPS_SPEC`, `FP_HP_SCALE_MIN_OPS_SPEC`, `FP_BF16_SCALE_MIN_OPS_SPEC`, `FP_FP8_SCALE_MIN_OPS_SPEC`. It is consumed as a lookup table by `tools/perf/pmu-events/jevents.py` when a model JSON names an `ArchStdEvent`.

## Control Flow, State, and Persistence
There is no mutable state or runtime control flow in the file. Build-time control flow is data-driven: `jevents.py` discovers the JSON, resolves any `ArchStdEvent` through the Arm64 common dictionary, canonicalizes event codes, and emits generated C tables. At runtime perf selects the table through `arch/arm64/mapfile.csv` and exposes aliases through `perf list`/`perf stat`; the source JSON itself is persistent configuration.

## Dependencies and Integration
Depends on `tools/perf/pmu-events/jevents.py`, `tools/perf/pmu-events/metric.py`, `arch/arm64/mapfile.csv`. The generated tables are linked into perf before runtime, then selected for matching CPUs or uncore devices so users can request these symbols by name rather than raw event numbers.

## Risks and Test Signals
Primary risks are wrong raw `EventCode` values produce misleading perf counts. Useful test signals are JSON parsing with `json.load`, perf `jevents.py` generation, `perf list` alias visibility, hardware `perf stat` smoke tests on the named CPU/SoC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/common-and-microarch.json -->
