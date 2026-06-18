# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/retired.json

## Purpose
This 23-entry T410 Arm64 table defines architecturally executed or retired instruction and branch events. It includes `INST_RETIRED`, register-write retirement events, branch-retired families, and prediction/misprediction variants for immediate, indirect, return, taken, skipped, and non-return indirect branches.

## Important Data Fields
All entries use `ArchStdEvent` with `PublicDescription`, so this file is a T410 selection layer over Arm architecture-standard event definitions rather than a local encoding table. The event names become perf aliases after resolution by the PMU event generator.

## Control Flow And Integration
`jevents.py` dereferences each `ArchStdEvent` using the architecture root catalog, carries the local public descriptions into generated C data, and attaches the generated table to the T410 CPU mapping. These events feed perf commands that need architected counts, branch-retirement analysis, and topdown-style retired-work metrics.

## State, Dependencies, Risks, And Tests
There is no mutable runtime state. The file depends heavily on the architecture-standard event catalog being complete and semantically compatible with T410. Risks are missing standard definitions, mismatch between Arm architectural retirement semantics and NVIDIA implementation behavior, or alias collisions with other topic files. Useful test signals are JSON validity, `jevents.py` reference resolution, generated-table inspection, and branch-heavy `perf stat` runs on T410.
