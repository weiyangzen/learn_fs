# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylake/cache.json

## Purpose

`cache.json` defines 243 Skylake core PMU events focused on cache hierarchy behavior, load/store retirement, prefetch activity, offcore request/response classification, and split-lock/prefetch side events. It gives `perf list` and `perf stat/record -e` the Skylake-specific names and encodings needed to program model-specific performance counters for cache analysis.

The file is dominated by offcore response variants: 173 `OFFCORE_RESPONSE.*` records combine request type (`DEMAND_CODE_RD`, `DEMAND_DATA_RD`, `DEMAND_RFO`, `OTHER`), supplier state (`L3_HIT`, `L3_HIT_E/M/S`, `L4_HIT_LOCAL_L4`, `SUPPLIER_NONE`), and snoop result (`ANY_SNOOP`, `SNOOP_HITM`, `SNOOP_MISS`, `SNOOP_NONE`, `SNOOP_NOT_NEEDED`, `SPL_HIT`). Smaller clusters cover L1D fill-buffer pressure, L2 requests and evictions, retired load/store classes, L3 hit snoop outcomes, outstanding offcore request occupancy, and software prefetch accesses.

## Important schema/API surface

Each array entry is a perf event descriptor. Important fields include:

- `EventName`: public event selector, for example `L1D.REPLACEMENT`, `L2_RQSTS.ALL_DEMAND_MISS`, `MEM_LOAD_RETIRED.L3_MISS`, and the many `OFFCORE_RESPONSE.*` combinations.
- `EventCode` and `UMask`: raw event select and unit-mask encodings programmed into the generic PMU event-select MSRs.
- `Counter`: allowed generic counter list, usually `0,1,2,3`.
- `CounterMask`, `AnyThread`, `EdgeDetect`, `Invert`: optional hardware qualifier bits for cycle/threshold style events.
- `MSRIndex` and `MSRValue`: offcore response filter programming. Most `OFFCORE_RESPONSE.*` records use `MSRIndex` `0x1a6,0x1a7` with a request/supplier/snoop-specific `MSRValue`.
- `PEBS` and `Data_LA`: mark precise load/store events, notably `MEM_INST_RETIRED.*`, `MEM_LOAD_RETIRED.*`, `MEM_LOAD_L3_HIT_RETIRED.*`, and `MEM_LOAD_MISC_RETIRED.UC`.
- `Errata` and `Deprecated`: annotate known hardware caveats, such as `LONGEST_LAT_CACHE.*` with `SKL057` and `L2_LINES_OUT.USELESS_PREF` as deprecated in favor of `L2_LINES_OUT.USELESS_HWPF`.
- `BriefDescription`, `PublicDescription`, and `SampleAfterValue`: user-facing event help and sampling defaults.

## Control flow and integration

There is no runtime control flow in the file itself. At build or runtime, perf's PMU event table generator/parser reads this JSON, associates it with the Skylake CPU model map, and exposes the event names through the perf event alias layer. When a user asks for an event by name, perf resolves the descriptor to a raw event encoding, applies optional qualifiers, writes any required offcore filter MSR, and opens the hardware event via `perf_event_open`.

Offcore response events have the most important integration behavior. The base event is not sufficient: perf must also program one of the offcore response MSRs listed in `MSRIndex` with the descriptor's `MSRValue`. That makes this data coupled to kernel support for offcore-response extra registers and to counter scheduling rules that avoid incompatible simultaneous offcore filters.

## State and persistence behavior

The file is static architecture metadata. It persists only in the source tree and generated perf event tables; it does not mutate at runtime and has no local storage. Runtime state is in hardware PMU registers selected from the JSON values, plus perf's in-memory event aliases and measurement buffers.

## Dependencies

The descriptors depend on Skylake architectural PMU semantics, Intel event documentation, perf's JSON schema, perf's Skylake CPU model mapping, and kernel PMU support for PEBS, data linear address capture, generic counter masks, and offcore-response MSR filters. The many events using fixed `0x1a6,0x1a7` MSR filters also depend on the kernel allowing those extra registers for this CPU family.

## Risks and maintenance notes

The largest risk is encoding drift. A one-bit error in `MSRValue` or `UMask` can silently report the wrong memory supplier or snoop class. The offcore matrix is repetitive, so copy/paste mistakes are easy and may not be caught by JSON syntax validation.

Deprecated and errata-tagged events need clear preservation. Removing `L2_LINES_OUT.USELESS_PREF` would break users with old scripts, while failing to surface its deprecation would keep steering users to stale naming. `LONGEST_LAT_CACHE.*` carries `SKL057`, so analysis tools should treat it as hardware-caveated rather than universally reliable.

Precise events marked with `PEBS`/`Data_LA` can fail or degrade on kernels, privilege settings, or virtualized environments that do not expose the required precise sampling support. Reports should distinguish "event not known" from "event known but unavailable on this host".

## Test signals

Useful validation includes `jq empty` for syntax, schema checks that all array entries have `EventName`, `EventCode`, `UMask`, and descriptions, duplicate-name checks within the Skylake event set, and perf table generation tests. Runtime smoke tests on Skylake hardware should verify representative aliases: `L1D.REPLACEMENT`, `L2_RQSTS.MISS`, `MEM_LOAD_RETIRED.L3_MISS`, one `OFFCORE_REQUESTS_OUTSTANDING.*`, and several `OFFCORE_RESPONSE.*` aliases that require MSR filter programming.
