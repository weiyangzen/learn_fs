<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/knightslanding/virtual-memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/knightslanding/virtual-memory.json

## Purpose
This JSON file defines Knights Landing core virtual-memory PMU events for perf. It exposes DTLB miss retirement and page-walk cycle/walk counters. The complete 65-line array was read and contains 7 records: one `MEM_UOPS_RETIRED` DTLB-miss load event and six `PAGE_WALKS` events.

## Important APIs, Types, and Functions
The records use core PMU schema fields `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, and `BriefDescription`, with optional `PublicDescription`, `PEBS`, `Data_LA`, and `EdgeDetect`. There is no `Unit`, so `jevents.py` maps the records to `default_core` rather than an uncore PMU.

`MEM_UOPS_RETIRED.DTLB_MISS_LOADS` is precise (`PEBS` `1`) and supports address reporting through `Data_LA`. The `PAGE_WALKS.*_CYCLES` records count cycles with D-side, I-side, or any page walk in progress. The `PAGE_WALKS.*_WALKS` records use `EdgeDetect` to count completed or started walks rather than occupancy cycles, with sample periods of `100003` instead of the `200003` used by cycle-style events.

## Control Flow
The perf build discovers this JSON through `tools/perf/pmu-events/Build`. `jevents.py` maps missing `Unit` to `default_core`, converts `EventCode` to `event=`, `UMask` to `umask=`, `SampleAfterValue` to `period=`, `EdgeDetect` to `edge=`, and appends description text for precise/address-capable events. The x86 map row `GenuineIntel-6-(57|85),v16,knightslanding,core` selects these aliases for Knights Landing systems.

## State and Persistence
The file has no mutable state. Generated perf tables persist the alias names, event encodings, sampling periods, PEBS support, and edge-detect modifiers. Runtime behavior depends on core PMU support for PEBS and data linear address capture for the retired DTLB miss load event.

## Dependencies and Integration Points
Dependencies are perf's PMU JSON schema, `jevents.py`, x86 CPU model mapping, and core PMU support for the documented event encodings. The file integrates with `perf stat` and `perf record` for TLB and page-walk analysis. It is especially useful alongside Knights Landing memory and cache events when diagnosing whether memory latency originates from translation walks rather than MCDRAM/DDR/cache traffic.

## Risks
The main risk is confusing cycle occupancy events with edge-detected walk-count events. Several records share `EventCode` `0x05` and differ only by `UMask` and `EdgeDetect`, so a bad mask or dropped `edge=1` changes semantics completely. The DTLB miss event depends on precise sampling and data address support; losing `PEBS` or `Data_LA` metadata would make sampling workflows less useful even if the raw event still counts. The file also has no `Unit`, so accidental insertion of an uncore unit would move aliases to the wrong PMU namespace.

## Test Signals
Validate JSON syntax and generated event strings containing `period=`, `umask=`, and `edge=1` for the walk-count records. `perf list` should show the aliases as core events, not uncore events. Hardware tests should compare D-side and I-side page-walk behavior under pointer-chasing, instruction-cache/TLB stress, 4K page workloads, and huge-page workloads. `perf record` tests for `MEM_UOPS_RETIRED.DTLB_MISS_LOADS` should verify precise sampling and address availability when the platform supports it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/knightslanding/virtual-memory.json -->
