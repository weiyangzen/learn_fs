# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/lunarlake/uncore-interconnect.json

## Purpose

`uncore-interconnect.json` defines a single Lunar Lake uncore interconnect event: `UNC_CLOCK.SOCKET`. It represents a 48-bit fixed counter for UCLK cycles on the `SANTA` unit and is package-scoped via `PerPkg: "1"`. The event provides a clock reference for uncore/interconnect analysis and for normalizing package-level uncore activity.

## Important APIs, Types, And Data Shape

The file is a one-element JSON array. The event object uses `BriefDescription`, `Counter: "FIXED"`, `EventCode: "0xff"`, `EventName`, `PerPkg`, and `Unit: "SANTA"`. Unlike core PMU events, there is no `UMask`, no programmable counter list, and no sample-after value. The unit name must map through perf's uncore PMU matching rather than the hybrid `cpu_core` or `cpu_atom` paths.

## Control Flow

The generator treats the file as an ordinary event array, gives it the topic `uncore-interconnect`, and emits an event alias for the `SANTA` PMU. At runtime, perf can list and open the alias only if the kernel exposes a matching uncore PMU. Because the counter is fixed and per-package, aggregation semantics differ from per-thread core events.

## State And Persistence

The source is static. Generated perf tables persist the alias, fixed counter selector, package scope, and description. Runtime state is the uncore counter programmed by perf on a matching Lunar Lake system.

## Dependencies And Integration Points

This file depends on kernel support for the Lunar Lake `SANTA` uncore PMU name and fixed counter event `0xff`. It integrates with the same `jevents.py` event table generation as other JSON files, but runtime collection goes through uncore PMU discovery and package aggregation rather than per-CPU core scheduling.

## Risks

The main risk is PMU-name mismatch: if the kernel exposes a different uncore PMU name than `SANTA`, the generated alias will not bind. Fixed-counter semantics also mean generic event scheduling assumptions do not apply. Since there is only one event, missing or malformed data removes the whole interconnect topic for Lunar Lake.

## Test Signals

Validation should confirm JSON array length 1 and the exact `Unit`, `EventName`, `Counter`, and `PerPkg` fields. Runtime smoke tests on matching hardware should include `perf list uncore-interconnect` and `perf stat -e uncore_santa/unc_clock.socket/` or the kernel-specific PMU spelling exposed under `/sys/bus/event_source/devices`.
