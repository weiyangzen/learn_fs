<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/tigerlake/uncore-other.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/tigerlake/uncore-other.json

## Purpose

`uncore-other.json` defines the Tiger Lake uncore fixed-clock event `UNC_CLOCK.SOCKET`. It gives perf a package-level UCLK cycle counter that can be used as a denominator for uncore rates, residency-style calculations, and sanity checks for uncore PMU activity.

## Important APIs, Types, and Data Fields

The file is a one-entry JSON event array. The record uses `EventName: UNC_CLOCK.SOCKET`, `EventCode: 0xff`, `Counter: FIXED`, `Unit: CLOCK`, `PerPkg: 1`, and a `BriefDescription` stating that this 48-bit fixed counter counts UCLK cycles. Unlike programmable event files, it does not have a `UMask`, sample period, or multiple event variants.

## Control Flow and Data Flow

There is no executable flow. Perf's generator creates a fixed uncore clock alias for the Tiger Lake `CLOCK` PMU, and runtime perf reads the fixed counter over an interval. Other uncore analyses can use the value to normalize ARB occupancy events, memory-controller rates, or uncore frequency-related measurements.

## State and Persistence Behavior

Only the static alias metadata is persistent in the repository and generated tables. Runtime counter state lives in the hardware fixed counter and perf's measurement interval. Because the counter is fixed-width and hardware-owned, long intervals require normal perf counter wrap handling.

## Dependencies and Integration Points

The event depends on Tiger Lake uncore CLOCK PMU support. It integrates with `perf stat`, package-level uncore diagnostics, and formulas that need UCLK cycles as a denominator. It complements `uncore-interconnect.json` occupancy events and memory free-running counters by providing a time/cycle reference.

## Risks and Edge Cases

The event is package-scoped, not task-scoped. Misinterpreting UCLK cycles as core cycles can produce wrong rates, especially when core and uncore frequencies differ. The 48-bit width makes wrap behavior a consideration for long-running measurements if the kernel/tooling does not handle deltas correctly. Since it is fixed-counter metadata, consumers must not treat `Counter: FIXED` like programmable counter lists.

## Test Signals

Validation should include JSON parse success, generated alias exposure in `perf list`, and a runtime test that `UNC_CLOCK.SOCKET` advances during idle and busy intervals. Rate checks should compare deltas over known wall-clock intervals to plausible UCLK frequency ranges and confirm the alias can be collected alongside programmable uncore events without counter-scheduling conflicts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/tigerlake/uncore-other.json -->
