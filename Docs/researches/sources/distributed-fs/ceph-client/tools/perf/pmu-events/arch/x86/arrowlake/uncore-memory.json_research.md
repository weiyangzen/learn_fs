# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/arrowlake/uncore-memory.json

## Purpose

This file defines 18 Arrow Lake uncore memory-controller events. It covers free-running read/write CAS and total request counters for memory controllers 0 and 1, plus integrated memory-controller DRAM ACT, CAS, refresh, precharge, and thermal state events.

## Important APIs, Types, And Data

The schema uses `EventName`, `EventCode`, `UMask`, `Counter`, `Unit`, `PerPkg`, `BriefDescription`, `PublicDescription`, and `Experimental`. Units include `imc_free_running_0`, `imc_free_running_1`, and `iMC`, which map to uncore PMU names. Free-running entries use `EventCode` `0xff` with masks such as `0x10`, `0x20`, and `0x30`; command events use specific event codes such as ACT, CAS, PRE, REF, and thermal counters.

## Control Flow

`jevents.py` reads each record, canonicalizes the event code and nonzero umask, maps the unit to an uncore PMU, and emits compact event-table records. Runtime perf aliases then bind to memory-controller PMU devices and program either fixed/free-running style counters or programmable iMC events according to the generated config string.

## State And Persistence Behavior

The JSON stores metadata. Memory-controller counter state exists in hardware and perf file descriptors. `PerPkg` means package-level aggregation is expected. `Experimental` on `UNC_M_DRAM_THERMAL_HOT` and `UNC_M_DRAM_THERMAL_WARM` persists into generated metadata and should signal lower confidence or unstable semantics to tools that expose it.

## Dependencies And Integration Points

Dependencies include Arrow Lake model mapping, `jevents.py`, perf PMU table generation, memory-controller PMU discovery, and user-visible perf list/stat output. The records also integrate with bandwidth and DRAM-behavior analysis workflows that combine read CAS, write CAS, total requests, ACT/PRE/REF, and thermal state counts.

## Risks And Edge Cases

The same `EventCode`/`UMask` values appear under different controller units; unit mapping must not collapse controller 0 and controller 1 unless perf intentionally wildcard-matches them. Free-running counters can have different availability and programming rules than normal counters. Experimental thermal events may be missing, renamed, or semantically unstable. Incorrect `PerPkg` handling can double-count or undercount memory traffic on multi-socket systems.

## Test Signals

Validate JSON syntax, run x86 `jevents.py` generation, and inspect generated PMU entries for all three units. On compatible hardware, `perf list` should show controller-specific free-running aliases and iMC command aliases. Functional checks should compare read/write CAS counts under memory load and verify experimental thermal aliases do not break generation.
