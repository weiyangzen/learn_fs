
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylake/uncore-cache.json

## Purpose

This file defines 15 Skylake client uncore cache events. The events expose last-level cache/coherency behavior through C-box style uncore counters and socket clock accounting. Event names include `UNC_CBO_CACHE_LOOKUP.*`, `UNC_CBO_XSNP_RESPONSE.*`, and `UNC_CLOCK.SOCKET`.

The file lets perf users name cache-slice/coherency events symbolically rather than programming raw uncore event codes and unit masks. It is especially relevant to system-level cache-hit, invalid-state lookup, write/read MESI-state, cross-core snoop hit, hit-modified, miss, eviction, and socket-cycle analysis.

## Important Schema Fields and APIs

Each object follows the PMU event descriptor schema:

- `EventName`: public alias, lowercased by `jevents.py` for generated perf aliases.
- `EventCode`: raw event selector, for example the CBO lookup or snoop-response selector.
- `UMask`: subevent selector for MESI state, read/write class, or snoop response.
- `Unit`: uncore PMU unit name, here primarily CBO/cache-box units plus the socket clock unit.
- `Counter`: allowed hardware counter selector list for the uncore unit.
- `PerPkg`: marks package-scoped accounting for socket/uncore events.
- `BriefDescription` and optional `PublicDescription`: text surfaced through `perf list`.

These fields are consumed by `jevents.py` into generated `event=...`, `umask=...`, `counter=...`, `perpkg=...`, and PMU/unit mapping strings.

## Control Flow and Data Flow

The file is read at build time as part of the Skylake model directory. The generation flow is JSON array -> `JsonEvent` objects in `jevents.py` -> generated C PMU event table -> runtime perf alias table. At runtime, a user selecting `UNC_CBO_CACHE_LOOKUP.READ_MESI` or similar causes perf to program the matching uncore PMU event code and mask on the package CBO units.

No event in this file calls another event. Higher-level data flow is from these raw events into user commands and potentially into metrics in `skl-metrics.json` that reference uncore cache or socket-clock behavior.

## State and Persistence

This is static metadata. It persists only in generated perf build outputs and in the installed perf binary. Runtime counter state lives in CPU uncore PMU registers and perf's sampling/stat aggregation buffers; it is not written back to this file.

## Dependencies and Integration Points

The file depends on the Skylake uncore PMU naming understood by perf and the kernel PMU drivers. The `Unit` and `PerPkg` fields are important because uncore counters are package-scoped rather than per-thread core counters. Integration points include `jevents.py`, the x86 mapfile's Skylake model mapping, `perf list` alias display, `perf stat -e` uncore event programming, and any Skylake metrics that combine uncore cache counts with core or clock events.

## Risks

Raw uncore encodings are hardware-specific. A wrong `EventCode`, `UMask`, `Counter`, or `Unit` can silently count a different event or fail to schedule. Package-level aggregation can be misinterpreted as per-core data, especially on multi-socket systems. The names encode MESI/snoop semantics; inaccurate descriptions may cause users to confuse lookup state, read/write state, and cross-core snoop response classes.

## Test Signals

Validation should include JSON parsing, generated `pmu-events.c` inspection for the 15 aliases, `perf list` visibility for `UNC_CBO_CACHE_LOOKUP` and `UNC_CBO_XSNP_RESPONSE`, and runtime `perf stat -e` tests on Skylake hardware with uncore PMU support. Tests should verify package aggregation and that restricted `Counter` values are accepted by the kernel PMU driver.
