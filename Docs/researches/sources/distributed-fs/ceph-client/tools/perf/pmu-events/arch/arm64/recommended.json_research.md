# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/recommended.json

## Purpose
This 76-entry Arm64 architecture-root file defines recommended architectural event names and encodings for cache, TLB, bus, memory, unaligned/speculative operations, barriers, exceptions, release-consistency operations, and L3 cache activity. It provides common definitions that CPU-specific files can reference or align with.

## Important Data Fields
Rows use `PublicDescription`, `EventCode`, `EventName`, and `BriefDescription`. Unlike CPU-specific `ArchStdEvent` wrapper files, this file is the concrete catalog of recommended Arm event encodings, for example `L1D_CACHE_RD` at `0x40` and `L3D_CACHE_INVAL` at `0xa8`.

## Control Flow And Integration
`jevents.py` loads architecture-root JSON files as standard event sources. CPU model files use `ArchStdEvent` to dereference entries based on `EventName`, reducing duplication across Arm64 CPU directories. Generated perf tables inherit these names, encodings, and descriptions into model-specific maps.

## State, Dependencies, Risks, And Tests
The file is shared static build input. Its blast radius is broad: an incorrect encoding or renamed event can affect every Arm64 model that dereferences it. Risks include breaking `ArchStdEvent` resolution, altering alias semantics across vendors, and accidentally changing generic recommended behavior to match one implementation. Test signals are full Arm64 `jevents.py` generation, `perf test pmu-events`, JSON schema checks, and spot checks of CPU-specific generated aliases.
