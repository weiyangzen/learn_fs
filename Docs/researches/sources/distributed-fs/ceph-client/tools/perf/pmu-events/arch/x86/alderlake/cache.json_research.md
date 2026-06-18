# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlake/cache.json

## Purpose

This JSON file is an Alder Lake cache and memory-hierarchy PMU event table consumed by Linux `perf`'s pmu-events tooling. It contains 150 event records split across hybrid core PMU units: 86 `cpu_core` entries and 64 `cpu_atom` entries. The catalog describes L1D pending misses, L2 requests and line movement, last-level cache references and misses, retired memory operations, offcore response filters, prefetches, store-buffer and memory-scheduler behavior, and a small topdown frontend-bound signal. It is data, not executable code, but it forms part of the API that lets users run named events such as `L2_RQSTS.DEMAND_DATA_RD_MISS` instead of hand-encoding event select, unit mask, counters, and model-specific MSR filters.

## Important APIs, Types, and Data

The schema is the standard perf JSON event object shape: `EventName`, `EventCode`, `UMask`, `BriefDescription`, optional `PublicDescription`, `Counter`, `SampleAfterValue`, and `Unit`. Several records also use `CounterMask`, `EdgeDetect`, `Deprecated`, `Errata`, `Data_LA`, `MSRIndex`, and `MSRValue`. `Data_LA` marks precise load-address sampling candidates for PEBS-style data linear-address capture. `MSRIndex`/`MSRValue`, especially `0x1a6,0x1a7`, encode offcore-response request/response filters that perf must program in addition to the architectural event select registers.

The major event families are `L1D`, `L1D_PEND_MISS`, `L2_RQSTS`, `LONGEST_LAT_CACHE`, `MEM_INST_RETIRED`, `MEM_LOAD_RETIRED`, `MEM_LOAD_UOPS_RETIRED`, `MEM_UOPS_RETIRED`, `OCR`, `OFFCORE_REQUESTS`, `OFFCORE_REQUESTS_OUTSTANDING`, and `SW_PREFETCH_ACCESS`. There are duplicate event names across core and atom units where the same user-facing concept maps to different encodings. Two entries are deprecated and three carry errata annotations, so callers must not assume every named record is equally recommended.

## Control Flow

There is no local function control flow. At runtime, perf's pmu-events generator reads this array, validates required fields, converts each object into C tables or runtime JSON-derived descriptors, and exposes aliases under the Alder Lake model. When a user requests an event, perf resolves the active PMU unit (`cpu_core` or `cpu_atom`), selects matching records, programs the listed event select and umask values, and programs any offcore MSR filters before starting the counter. Hybrid systems make the unit field a control-flow input: a cache event may be legal on P-cores, E-cores, or both with different encodings.

## State and Persistence Behavior

The file is persistent source data checked into the tools tree. Runtime counter state lives in PMU hardware and perf event file descriptors, not in this JSON. The persistent contract is the stable set of event names, encodings, descriptions, sampling defaults, and flags. `Deprecated` entries remain as compatibility aliases but should steer users or metrics toward replacements. Offcore MSR values are persistent encoding data and are high risk because a small bit drift changes the semantic filter while leaving JSON syntactically valid.

## Dependencies and Integration Points

This table integrates with `tools/perf/pmu-events` JSON parsing, generated pmu-events C tables, `perf list`, `perf stat`, `perf record`, metric expressions in adjacent Alder Lake metric JSON files, and Intel hybrid PMU naming. It depends on kernel PMU support for Alder Lake core and atom event encodings, PEBS load-address sampling where `Data_LA` is present, and offcore response MSR programming for `OCR` events. Higher-level metrics in `adl-metrics.json` and group labels in `metricgroups.json` can reference these events by name.

## Risks

The main risks are schema-valid but semantically wrong encodings, duplicate event names selecting the wrong hybrid unit, stale deprecated aliases, and offcore MSR filters that do not match Intel documentation. `Data_LA` flags can imply unsupported precise sampling if the corresponding PMU or kernel path lacks support. Counter restrictions matter because many events list limited programmable counters; ignoring `Counter` can produce scheduling failures or multiplexed results. Event families with similar names, such as `MEM_LOAD_RETIRED` versus `MEM_LOAD_UOPS_RETIRED`, must remain separated because they describe different core types and counting domains.

## Test Signals

Useful validation includes `jq`/schema parsing, pmu-events generation, `perf list` on Alder Lake exposing the aliases under the expected PMU units, event-encoding tests comparing generated config/umask/MSR fields to known-good tables, and smoke runs for representative L1, L2, LLC, retired-load, prefetch, and offcore events. Metric tests should confirm that formulas referencing cache events resolve for both core and atom PMUs and skip gracefully when a unit-specific event is unavailable.
