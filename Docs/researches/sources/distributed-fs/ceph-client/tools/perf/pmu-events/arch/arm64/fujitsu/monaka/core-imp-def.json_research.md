<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/core-imp-def.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/core-imp-def.json

## Purpose
Small Monaka implementation-defined override topic for a single instruction-cache prefetch event. It adds a local description for `L1I_CACHE_PRF`, counting L1I cache activity caused by hardware or software prefetch.

## APIs, Types, and Functions
The only record uses `ArchStdEvent: L1I_CACHE_PRF` plus `BriefDescription`. There are no functions or local event codes; the schema relies on standard ARM64 event metadata and local descriptive text.

## Control Flow, State, and Persistence
`jevents.py` resolves `L1I_CACHE_PRF` from the ARM64 standard table while preserving the Monaka-specific description. Runtime perf alias exposure follows the Monaka CPUID mapfile entry. The file contains no mutable state.

## Dependencies and Integration
Depends on `common-and-microarch.json` containing `L1I_CACHE_PRF` and on `arch/arm64/mapfile.csv` mapping CPUID `0x00000000460f0030` to `fujitsu/monaka`. It complements `l1i_cache.json`, which covers demand, refill, hit, and prefetch instruction-cache counters.

## Risks and Test Signals
The main risk is a dangling `ArchStdEvent` if the standard event catalog changes. Test signals are successful JSON parsing, generated alias presence, and instruction-prefetch workloads increasing `L1I_CACHE_PRF` consistently with broader L1I cache counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/core-imp-def.json -->
