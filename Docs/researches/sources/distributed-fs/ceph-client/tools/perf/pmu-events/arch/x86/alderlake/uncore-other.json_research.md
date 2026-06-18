# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlake/uncore-other.json

## Purpose

This one-entry file defines the Alder Lake package-level uncore clock event `UNC_CLOCK.SOCKET`. It describes a 48-bit fixed counter that counts UCLK cycles. The event provides a timing/normalization source for uncore measurements.

## Important APIs, Types, and Data

The single event object uses `EventName`, `EventCode`, `Counter`, `Unit`, `PerPkg`, and `BriefDescription`. `EventCode` is `0xff`, `Counter` is `FIXED`, `Unit` is `CLOCK`, and `PerPkg` is `1`. Unlike programmable event catalogs, this record points at a fixed package-level uncore counter rather than a selectable event/umask pair.

## Control Flow

Perf parses the record into an uncore alias. At runtime, selecting `UNC_CLOCK.SOCKET` binds to the uncore clock PMU's fixed counter and reads package-level UCLK cycles for the measurement interval. Metrics can use it to normalize uncore occupancy, request, or memory-controller counts.

## State and Persistence Behavior

The persistent state is the alias and fixed-counter metadata. Runtime state is the hardware fixed counter value, which is package-scoped and may be read over an interval. The 48-bit width matters for long-running sessions because wrap handling must be correct in the kernel/perf read path.

## Dependencies and Integration Points

This file integrates with perf's uncore PMU support, package-level metric normalization, `perf list`, and uncore interconnect/memory analyses. It depends on kernel exposure of the Alder Lake `CLOCK` uncore unit and correct fixed-counter read semantics.

## Risks

The main risks are incorrect aggregation, counter wrap in long intervals, and assuming UCLK is equivalent to core frequency or invariant TSC. Because it is package-level, CPU filters and per-thread interpretations are misleading. If the kernel does not expose the `CLOCK` unit on a platform, metrics depending on this alias must degrade clearly.

## Test Signals

Validation should include JSON parsing, `perf list` visibility, smoke reads over known sleep intervals, wrap-safe long-duration reads where practical, and metric tests that use `UNC_CLOCK.SOCKET` to normalize uncore occupancy or request events.
