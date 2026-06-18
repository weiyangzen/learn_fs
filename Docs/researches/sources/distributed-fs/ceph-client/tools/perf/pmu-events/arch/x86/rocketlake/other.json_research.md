# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/rocketlake/other.json

## Purpose
This JSON file contributes five Rocket Lake x86 PMU event aliases in the `other` topic for Linux perf's generated PMU event tables. It covers two distinct areas that do not fit cleanly in pipeline, cache, or virtual-memory topics: core power/turbo license level accounting and offcore response counting for miscellaneous and streaming-write transactions.

At build time, `tools/perf/pmu-events/jevents.py` reads this JSON together with the rest of `arch/x86/rocketlake`, converts each object into generated `struct pmu_event` data, and links the generated tables into perf. At runtime, the x86 mapfile entry `GenuineIntel-6-A7,v1.04,rocketlake,core` selects this directory for Rocket Lake CPUs, allowing users and metric expressions to reference event names symbolically.

## Data shape and important fields
The file is a JSON array of 5 objects. The observed keys are `EventName`, `BriefDescription`, `PublicDescription`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `MSRIndex`, and `MSRValue`.

The first three entries are `CORE_POWER.LVL0_TURBO_LICENSE`, `CORE_POWER.LVL1_TURBO_LICENSE`, and `CORE_POWER.LVL2_TURBO_LICENSE`. They all use event code `0x28`, counters `0,1,2,3`, and distinct umasks to distinguish baseline/non-AVX, AVX2-like, and AVX512-like turbo license levels. Their sample period is `200003`.

The remaining entries are `OCR.OTHER.ANY_RESPONSE` and `OCR.STREAMING_WR.ANY_RESPONSE`. They use event codes `0xB7, 0xBB`, counters `0,1,2,3`, and MSR programming through `MSRIndex` `0x1a6,0x1a7`. `jevents.py` maps these MSR indexes to `offcore_rsp=` encodings, so these objects are not just simple event/umask aliases; they require correct offcore response register programming.

## Control flow and integration
There is no executable control flow in the file. The effective flow is declarative:

1. `jevents.py` parses each JSON object into a `JsonEvent`.
2. Event fields are normalized into perf event strings, including `event=`, `umask=`, `period=`, and offcore response fields derived from `MSRIndex` and `MSRValue`.
3. Generated C tables expose the aliases through the `pmu_event` API in `pmu-events.h`.
4. Perf commands such as `perf list`, `perf stat -e CORE_POWER.LVL0_TURBO_LICENSE`, and perf metric evaluation can resolve these aliases on Rocket Lake.

The file also feeds `rkl-metrics.json`: metrics such as turbo license utilization and streaming-store bottleneck estimates reference `CORE_POWER.LVL*_TURBO_LICENSE` and `OCR.STREAMING_WR.ANY_RESPONSE`.

## State, persistence, and dependencies
The file is static source data. It has no runtime persistence, no mutable state, and no direct I/O. Its persisted effect is the generated `pmu-events.c` content produced during perf builds. It depends on the perf PMU JSON schema and on x86 event encoding semantics for `EventCode`, `UMask`, programmable counter masks, sample periods, and offcore response MSR values.

The offcore events depend on the generator's `lookup_msr()` handling for `0x1A6` and `0x1A7`. A schema-valid but semantically wrong MSR value would build successfully yet count the wrong offcore response class.

## Risks
The main risk is semantic drift between Intel event definitions and the encoded values. The turbo license events influence power and throttling metrics, so incorrect umasks would mislead turbo/AVX utilization analysis. The OCR entries carry higher risk than simple core events because the event code list, MSR index list, and MSR value must remain consistent.

Another risk is cross-file dependency breakage. `rkl-metrics.json` references `OCR.STREAMING_WR.ANY_RESPONSE` and all three `CORE_POWER` aliases. Renaming or removing these events without updating metrics will leave perf metrics unresolved even though this file remains valid JSON.

## Test signals
Useful checks are: `jq empty other.json` for JSON syntax; a perf `jevents` build to ensure the offcore encodings are accepted; `perf list --json` on a Rocket Lake-capable build to confirm the five aliases appear; and metric parser tests that resolve formulas using `CORE_POWER.LVL0_TURBO_LICENSE`, `CORE_POWER.LVL1_TURBO_LICENSE`, `CORE_POWER.LVL2_TURBO_LICENSE`, and `OCR.STREAMING_WR.ANY_RESPONSE`.
