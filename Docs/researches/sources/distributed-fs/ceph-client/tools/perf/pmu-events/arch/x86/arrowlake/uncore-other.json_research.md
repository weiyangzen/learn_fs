# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/arrowlake/uncore-other.json

## Purpose

This one-entry file defines `UNC_CLOCK.SOCKET`, the Arrow Lake uncore socket clock fixed counter. It provides a 48-bit UCLK cycle reference for uncore measurements.

## Important APIs, Types, And Data

The entry uses `EventName`, `EventCode`, `Counter`, `Unit`, `PerPkg`, and `BriefDescription`. `EventCode` is `0xff`, `Unit` is `CNCU`, and `PerPkg` marks package-level scope. There is no `UMask`, so `jevents.py` emits only the event selector.

## Control Flow

Generation follows the standard PMU JSON path: `jevents.py` builds a `JsonEvent`, maps `CNCU` to an uncore PMU name, and emits the alias into generated tables. Runtime perf uses the compiled alias to open the corresponding uncore clock counter.

## State And Persistence Behavior

The source file persists the alias and description. Hardware maintains the 48-bit uncore clock count. The JSON does not persist samples or derived rates.

## Dependencies And Integration Points

This event integrates with Arrow Lake uncore PMU discovery and can serve as a denominator or sanity signal for other uncore package events. It depends on kernel PMU support for the CNCU uncore device and on generated table lookup in perf.

## Risks And Edge Cases

Fixed clock counters often have different programming semantics from programmable counters. A width assumption mismatch around the 48-bit count can affect long-running measurements. Unit-name drift would make the alias hard to find.

## Test Signals

Use JSON validation, event generation, and `perf list` alias checks. On hardware, count monotonicity under idle and load is the main functional signal; the event should be package scoped and should not appear as a core PMU event.
