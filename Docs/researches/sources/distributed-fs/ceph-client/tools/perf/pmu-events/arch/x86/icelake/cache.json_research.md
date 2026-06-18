# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelake/cache.json

## Purpose

`icelake/cache.json` defines 109 Intel Ice Lake client core PMU aliases for cache, memory-retirement, offcore-response, prefetch, fill-buffer, store-queue, L2, L3, and load-latency behavior. It is a core event file, not an uncore catalog. It includes both simple event select/umask aliases and offcore-response (`OCR.*`) aliases that require model-specific MSR programming.

## Important APIs, types, and schema

The file uses perf JSON event fields such as `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, and optional `PublicDescription`. Specialized fields are important here: 45 `OCR.*` records use `MSRIndex` and `MSRValue`; 20 records use `Data_LA` to indicate data linear-address support when precise; 5 records use `CounterMask`; one uses `EdgeDetect`; and two `L2_RQSTS` aggregate aliases are marked `Deprecated`.

Major families include `L1D.REPLACEMENT`; `L1D_PEND_MISS.*` for pending misses, fill-buffer full periods, and L2 stalls; `L2_LINES_IN`, `L2_LINES_OUT.*`, `L2_TRANS.L2_WB`, and 15 `L2_RQSTS.*` aliases for code, demand data, RFO, software prefetch, hit, miss, and deprecated aggregate classes; `LONGEST_LAT_CACHE.MISS`; `MEM_INST_RETIRED.*`, `MEM_LOAD_RETIRED.*`, `MEM_LOAD_L3_HIT_RETIRED.*`, and `MEM_LOAD_MISC_RETIRED.UC`; `OFFCORE_REQUESTS.*` and `OFFCORE_REQUESTS_OUTSTANDING.*`; 45 `OCR` offcore-response aliases for demand code, demand data, demand RFO, and hardware prefetch response classes; `SQ_MISC.*`; and `SW_PREFETCH_ACCESS.*`.

## Control flow and integration

There is no runtime control flow in the source file. Build flow maps CPUID patterns `GenuineIntel-6-7[DE]` to `icelake`, then `jevents.py` parses each object. Missing `Unit` means `default_core`; `MSRIndex` is resolved by `lookup_msr()` and `MSRValue` is carried into the generated event string for offcore filters; `CounterMask` and `EdgeDetect` become event modifiers; `Data_LA` and `Errata` style fields augment descriptions; and `Deprecated` is preserved for user-facing deprecation metadata. Runtime perf lookup programs regular core counters and, for OCR aliases, the paired offcore response MSRs such as `0x1a6,0x1a7`.

## State and persistence behavior

The persistent state is the public Ice Lake alias catalog and the offcore filter encodings. `OCR` rows are especially stateful at the hardware level because their alias requires both a core event code pair (`0xB7, 0xBB`) and an MSR filter value. The source file itself remains immutable, but its values drive generated tables that persist in the built perf binary.

## Dependencies

Dependencies include Intel Ice Lake client PMU documentation, perf's JSON schema, `jevents.py` MSR and event encoding support, core PMU counter availability, and Ice Lake mapfile selection. The `Data_LA` records depend on precise-event/address sampling support. Offcore entries depend on kernel and perf support for programming offcore response MSRs without conflicting with other events.

## Risks

Offcore-response aliases are the highest-risk area: an incorrect `MSRValue` can produce plausible but wrong response-class counts. `EventCode` values containing comma-separated alternatives must be parsed correctly by generator code and programmed on a compatible counter path. Deprecated `L2_RQSTS.MISS` and `.REFERENCES` should remain available but should not be treated as preferred metric inputs. `CounterMask` and `EdgeDetect` change event meaning from count-like to cycle/period-like, so dropping those fields silently changes semantics. Address-capable `Data_LA` events need precise sampling context to be useful.

## Test signals

Build checks include JSON syntax and generated PMU table tests. Runtime checks include `perf list` on Ice Lake, `perf stat` with L1/L2 cache stressors, offcore tests that compare broad `OCR.*.ANY_RESPONSE` counts against narrower L3 hit and snoop classes, and sampling tests for `MEM_INST_RETIRED.*` or `MEM_LOAD_*` events that verify address capture when precise sampling is requested. Deprecation metadata should be visible for deprecated aliases.
