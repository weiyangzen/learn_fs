# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwell/cache.json

## Purpose
Broadwell cache, memory hierarchy, TLB, lock, and offcore event table for Linux `perf`. The file is a JSON array of 275 event definitions consumed by the perf PMU-events generator. It supplies the raw event names and encodings used directly by users and indirectly by metrics in `bdw-metrics.json`.

Coverage includes L1D replacements and pending misses, L2 line fills/evictions/transactions/requests, longest-latency cache references and misses, retired memory uop source levels, STLB misses, split loads/stores, locked loads, offcore request issue/outstanding cycles, offcore response filter combinations, superqueue fullness, and split locks.

## Important APIs, Types, and Functions
The schema is perf's event object contract:

- `EventName`: exported event alias such as `L1D.REPLACEMENT`, `L2_RQSTS.DEMAND_DATA_RD_MISS`, `MEM_LOAD_UOPS_RETIRED.L3_MISS`, `OFFCORE_REQUESTS_OUTSTANDING.DEMAND_DATA_RD`, or `OFFCORE_RESPONSE.DEMAND_DATA_RD.L3_HIT.SNOOP_HITM`.
- `EventCode`: raw event select value. Most events use a single hex value; `OFFCORE_RESPONSE.*` entries use `0xB7, 0xBB`, reflecting the paired offcore response event-select slots.
- `UMask`: unit mask for the subevent. Offcore response rows use `0x1` while their full filter meaning is encoded by the event alias and perf's offcore response handling.
- `Counter`: programmable counter constraints. Nearly all rows allow `0,1,2,3`; `L1D_PEND_MISS.PENDING`, `PENDING_CYCLES`, and `PENDING_CYCLES_ANY` constrain to counter `2`.
- `CounterMask`: optional cmask for cycle-qualified variants, including pending-cycle rows, offcore cycles-with rows, and threshold rows such as `OFFCORE_REQUESTS_OUTSTANDING.DEMAND_DATA_RD_GE_6`.
- `AnyThread`: used by `L1D_PEND_MISS.PENDING_CYCLES_ANY`.
- `SampleAfterValue`: default sampling period field for perf.
- `BriefDescription` and `PublicDescription`: user-facing descriptions.

There are no functions, but repeated event families act like data-driven APIs. `L2_RQSTS.*` distinguishes hits, misses, references, RFOs, code reads, demand data reads, and prefetches. `MEM_LOAD_UOPS_RETIRED.*` maps retired load data source levels. `OFFCORE_RESPONSE.*` forms a matrix across request types (`ALL_DATA_RD`, `DEMAND_DATA_RD`, `DEMAND_RFO`, `ALL_RFO`, prefetch code/data/RFO variants, `COREWB`, `OTHER`) and response/snoop categories (`ANY_RESPONSE`, `L3_HIT.*`, `SUPPLIER_NONE.*`).

## Control Flow
Perf controls runtime behavior. The PMU-events build step parses this JSON into event tables. At runtime, selecting an event name causes perf to program the listed event select, umask, cmask, any-thread bit, counter constraints, and offcore response filters where applicable.

The main data-driven flow is selection and expansion:

1. User or metric expression references an event alias.
2. Perf resolves the alias in the Broadwell PMU map.
3. Perf checks counter constraints, including the hard counter-2 requirement for some L1D pending miss events.
4. For offcore response aliases, perf must program one of the offcore response event-selects plus the corresponding offcore response MSR filter.
5. Counts are returned to direct users or to metrics in `bdw-metrics.json`.

## State and Persistence Behavior
The JSON is persistent static metadata. Runtime counter state exists only in CPU PMU registers, offcore response MSRs, perf file descriptors, and sample buffers. This file does not persist collected data.

The event aliases are a stable interface for Broadwell perf users and for in-tree metric expressions. Removing aliases, changing counter constraints, or changing event encodings alters that interface. Offcore rows are especially stateful at runtime because event selection consumes both a programmable counter and an offcore filter register; scheduling two incompatible offcore filters can force multiplexing or rejection.

## Dependencies and Integration Points
This file integrates with the rest of the Broadwell PMU-events directory and the perf PMU-events generator. Metrics in `bdw-metrics.json` consume many of its aliases, including `L1D_PEND_MISS.*`, `L2_LINES_IN.ALL`, `L2_RQSTS.*`, `LONGEST_LAT_CACHE.*`, `MEM_LOAD_UOPS_RETIRED.*`, `MEM_LOAD_UOPS_L3_HIT_RETIRED.*`, `MEM_UOPS_RETIRED.*`, `OFFCORE_REQUESTS*`, `OFFCORE_RESPONSE.DEMAND_RFO.L3_HIT.SNOOP_HITM`, and `SQ_MISC.SPLIT_LOCK`.

The event table also depends on Broadwell PMU hardware semantics: general programmable counters, cmask filtering, any-thread filtering, precise event behavior for retired memory uops, and offcore response MSR encoding. It is used by `perf list`, `perf stat`, `perf record`, metric evaluation, and tests that validate generated event maps.

## Risks
Primary risks are event correctness and scheduling constraints:

- Offcore response complexity: 203 of the 275 rows are `OFFCORE_RESPONSE.*` aliases. These require special offcore MSR programming and cannot be treated like simple event-code/umask pairs.
- Counter constraints: `L1D_PEND_MISS.*` rows constrained to counter `2` can conflict with other events and cause scheduling failures if ignored.
- Similar aliases with different semantics: `L2_TRANS.*` counts transactions accessing the L2 pipe including rejects, while `L2_RQSTS.*` counts non-rejected request outcomes; confusing them changes metric meaning.
- Retired load-source caveats: `MEM_LOAD_UOPS_RETIRED.*` descriptions note limitations for AVX-256 loads and unknown/uncacheable sources.
- Cmask threshold semantics: events with `CounterMask` count cycles meeting a condition, not occurrences. Metrics must distinguish duration/count variants.
- Duplicate event-select use: many rows share the same `EventCode` and differ only by umask or offcore filter, so alias resolution must preserve the full encoding.
- Broadwell specificity: encodings and request/response categories should not be generalized to other Intel generations without checking their PMU tables.

## Test Signals
Validation should include JSON parsing, PMU-events generation, `perf list` visibility for representative aliases, and runtime `perf stat -e` tests for each family: `L1D.REPLACEMENT`, `L2_RQSTS.REFERENCES`, `L2_RQSTS.MISS`, `MEM_LOAD_UOPS_RETIRED.L1_HIT`, `MEM_LOAD_UOPS_RETIRED.L3_MISS`, `OFFCORE_REQUESTS.DEMAND_DATA_RD`, `OFFCORE_REQUESTS_OUTSTANDING.CYCLES_WITH_DEMAND_DATA_RD`, and one or more `OFFCORE_RESPONSE.*` aliases. Scheduling tests should cover counter-2-only L1D pending events, cmask cycle events, and incompatible offcore filters. Metric tests from `bdw-metrics.json` are also indirect validation because many top-down memory metrics depend on this table.
