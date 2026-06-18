<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/brbe.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/brbe.json

## Purpose
NVIDIA T410 BRBE topic file selecting the standard branch-record filtering event. It exposes `BRB_FILTRATE` for branch record buffer filtering activity.

## APIs, Types, and Functions
The only entry is `ArchStdEvent: BRB_FILTRATE` with a public description. There are no local event codes or functions.

## Control Flow, State, and Persistence
Build-time alias resolution imports the standard BRBE event into the generated T410 PMU table. Runtime behavior depends on PMU and BRBE support exposed by the kernel; the JSON stores no state.

## Dependencies and Integration
Depends on `common-and-microarch.json` containing `BRB_FILTRATE` and on T410 mapfile selection. It integrates with branch sampling/recording workflows rather than ordinary branch count metrics alone.

## Risks and Test Signals
Risks include BRBE support being disabled or absent in the kernel despite alias availability, and users expecting counts without configuring branch records. Test signals are successful alias generation, `perf list` visibility, and branch-recording workloads that exercise BRB filtering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/brbe.json -->
