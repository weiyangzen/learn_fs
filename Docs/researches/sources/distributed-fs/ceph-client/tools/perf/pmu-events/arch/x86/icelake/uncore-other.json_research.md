# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelake/uncore-other.json

## Purpose

This one-entry file defines the Ice Lake client uncore socket clock alias `UNC_CLOCK.SOCKET`. It provides a package-level uncore clock reference counter for perf users and for sanity-checking uncore measurements.

## Important APIs, Types, And Data

The entry uses `EventName`, `EventCode`, `Counter`, `Unit`, `PerPkg`, and `BriefDescription`. `EventCode` is `0xff`, `Counter` is `FIXED`, `Unit` is `CLOCK`, and `PerPkg` is `1`. The description identifies it as a 48-bit UCLK fixed counter.

## Control Flow

`jevents.py` parses the single JSON object, maps `Unit` `CLOCK` to the generated uncore clock PMU table, and emits the fixed-counter alias into `pmu-events.c`. At runtime, perf resolves `unc_clock.socket` against matching uncore clock PMU devices and reads the fixed package clock counter.

## State And Persistence Behavior

The JSON persists only the alias and description. The 48-bit uncore clock count is hardware state and can wrap during long measurements depending on frequency and read interval. Perf handles runtime reads and aggregation; this file stores no samples.

## Dependencies And Integration Points

This event depends on Ice Lake model selection, uncore unit mapping in `jevents.py`, generated PMU tables, and kernel exposure of the uncore clock PMU. It integrates with `perf list`, `perf stat`, and uncore workflows where a socket-clock denominator or liveness check is useful.

## Risks And Edge Cases

Fixed counters may have different programming semantics from programmable uncore counters. The 48-bit width matters for long-running sessions and should not be lost from the description. Unit-name drift would make the alias undiscoverable, and `PerPkg` aggregation must remain package-scoped rather than per-core.

## Test Signals

Use `jq empty uncore-other.json`, x86 event generation, and `perf test pmu-events`. On compatible systems, `perf list` should show `unc_clock.socket` under an uncore clock PMU, and `perf stat` should report a monotonically increasing package-level count without requiring programmable counter slots.
