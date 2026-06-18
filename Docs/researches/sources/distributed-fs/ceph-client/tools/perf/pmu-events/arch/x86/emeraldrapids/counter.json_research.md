<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/emeraldrapids/counter.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/emeraldrapids/counter.json

## Purpose
Declares PMU counter inventory for Emerald Rapids core and uncore units. It contains 16 unit entries, including the core PMU and server uncore blocks such as PCU, IRP, M2PCIe, IIO, iMC, M2M, M3UPI, UPI, CHA, CXL, HBM, UBOX, and MDF-related units.

## Important APIs, Types, And Functions
Each object uses `Unit`, `CountersNumFixed`, and `CountersNumGeneric`. The `core` unit declares four fixed counters and eight generic counters. Most uncore units declare zero fixed counters and four generic counters; `IRP` and `UBOX` declare two generic counters; `CXLCM` declares eight.

## Control Flow
`jevents.py` ingests this file with the rest of the Emerald Rapids directory. Generated metadata is selected by the `GenuineIntel-6-CF` mapfile row. Runtime perf uses unit-specific counter counts when exposing PMU capabilities and constraining event groups across core and uncore PMUs.

## State And Persistence
The file contains static hardware metadata. The generated perf table persists after build; runtime state is limited to perf's scheduling decisions and active PMU counter allocations.

## Dependencies And Integration Points
Integrates with both core files such as `cache.json` and Emerald Rapids uncore event files in the same directory. Unit names must match the `Unit` fields used by uncore JSON event descriptions and perf's PMU name mapping.

## Risks And Edge Cases
Wrong counts can make perf overcommit or underuse PMU counters. Unit-name drift is especially risky for uncore blocks because the file spans many PMU instances. Server platforms may expose only a subset depending on SKU, BIOS settings, or kernel PMU support, so metadata must describe architectural capacity without assuming every runtime PMU is present.

## Test Signals
Validate syntax and generated tables. On Emerald Rapids hardware, compare `perf list` uncore PMUs and event scheduling against the declared counts. Group tests should cover the eight-counter core PMU, two-counter `IRP`/`UBOX`, and four-counter memory/interconnect units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/emeraldrapids/counter.json -->
