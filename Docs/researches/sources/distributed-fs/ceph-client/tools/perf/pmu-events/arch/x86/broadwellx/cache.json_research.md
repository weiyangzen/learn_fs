# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellx/cache.json

## Purpose

`cache.json` defines 88 BroadwellX core PMU events for L1D, L2, LLC, offcore request/response, memory uop retirement, and lock/cache behavior. It supplies the raw aliases that perf users can request directly and that higher-level BroadwellX metrics use for cache hit/miss, memory-bound, offcore snoop, false-sharing, bandwidth, and latency analysis.

## Important APIs, types, and schema

The file is an array of event dictionaries with fields such as `EventName`, `EventCode`, `UMask`, `Counter`, `CounterMask`, `SampleAfterValue`, `BriefDescription`, `PublicDescription`, `AnyThread`, `PEBS`, `Data_LA`, `Errata`, `MSRIndex`, and `MSRValue`. `jevents.py` converts each entry to a `struct pmu_event`: `EventName` becomes lowercase `name`, raw fields become an event encoding string, descriptions become `desc` and `long_desc`, `PEBS` appends precise-event notes, and `Errata` is appended to descriptions as a spec-update note.

Important event families include `L1D.REPLACEMENT`, `L1D_PEND_MISS.*`, `L2_LINES_IN.*`, `L2_RQSTS.*`, `L2_TRANS.*`, `LONGEST_LAT_CACHE.*`, `MEM_LOAD_UOPS_RETIRED.*`, `MEM_LOAD_UOPS_L3_HIT_RETIRED.*`, `MEM_LOAD_UOPS_L3_MISS_RETIRED.*`, `OFFCORE_REQUESTS.*`, `OFFCORE_REQUESTS_OUTSTANDING.*`, `OFFCORE_RESPONSE.*`, `SQ_MISC.SPLIT_LOCK`, and `LOCK_CYCLES.CACHE_LOCK_DURATION`. Offcore response entries use `MSRIndex` `0x1a6,0x1a7` and `MSRValue` masks, which `jevents.py` maps to `offcore_rsp=...`.

## Control flow and integration

The perf build treats `cache.json` as a topic file named `cache`; `get_topic()` turns the filename into the topic string that is stored on generated events. `read_json_events()` loads all entries, and `add_events_table_entries()` appends only records with `EventName` to the BroadwellX event table. At runtime these aliases are resolved by PMU name `default_core` unless a `Unit` field overrides it. Metrics in `bdx-metrics.json` rely heavily on this file for L1/L2/LLC MPKI, pending-miss cycles, offcore outstanding cycles, local/remote cache access, store latency, lock latency, and memory bandwidth decomposition.

## State and persistence behavior

The file has no mutable state. Its persistent output is a generated compact PMU event table in `pmu-events.c`. Runtime effects occur when perf programs the BroadwellX general-purpose counters and, for offcore events, the offcore response MSRs. `Counter` fields restrict scheduling to compatible hardware counters; `CounterMask`, `AnyThread`, and `PEBS` affect how the kernel configures the sampled event.

## Dependencies

Dependencies include Intel BroadwellX PMU semantics, perf's JSON schema, `jevents.py` MSR mapping for offcore response registers, and kernel support for the underlying core PMU events. Higher-level dependencies include `bdx-metrics.json`, which assumes these exact names, and `metricgroups.json`, which describes groups that include metrics built from these events.

## Risks

Offcore encodings are high risk because an incorrect `MSRValue` can silently count the wrong request/response class. Errata-marked events such as `MEM_LOAD_UOPS_L3_*`, `OFFCORE_REQUESTS_OUTSTANDING.*`, and several PEBS load events should be treated carefully in tests and documentation. Some events are constrained to counter 2 or require precise sampling/address support; ignoring `Counter` or `PEBS` can produce unschedulable groups or unexpected sampling behavior. Because metrics use many of these names verbatim, changing capitalization or suffixes breaks metric expansion even though JSON validation still passes.

## Test signals

Validation should include `jq empty cache.json`, a `jevents.py` generation run, and duplicate-alias checks from `print_pending_events()` assertions. Runtime or fixture tests should confirm `perf list cache` includes representative aliases such as `l1d.replacement`, `l2_rqsts.miss`, and `offcore_response.*`, and that metrics using `MEM_LOAD_UOPS_RETIRED.L3_MISS`, `L1D_PEND_MISS.PENDING`, and offcore response aliases expand without missing event errors.
