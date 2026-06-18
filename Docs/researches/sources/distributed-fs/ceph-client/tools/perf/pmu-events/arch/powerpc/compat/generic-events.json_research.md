# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/compat/generic-events.json

## Purpose
This 23-entry PowerPC compatibility table supplies generic event aliases for fallback PowerPC mappings. It includes cycles, completed instructions, FLOPs, TLB misses, frontend availability, loads/stores, dispatched instructions, run cycles, branches, L1 cache misses, L3/memory source events, and branch mispredictions.

## Important Data Fields
Rows use `EventCode`, `EventName`, and `BriefDescription`. The PowerPC mapfile maps `0x00ffffff` to `compat`, so these encodings provide a generic core table when no more specific model table applies.

## Control Flow And Integration
`jevents.py` emits this table as a PowerPC core event table. PowerPC runtime CPU identification, including architecture-specific header support, chooses either exact model tables or this compatibility directory. The aliases also support generic metrics that expect names like `PM_RUN_INST_CMPL` and `PM_CYC`.

## State, Dependencies, Risks, And Tests
The file is static but important for fallback behavior. Risks include overpromising event availability across PowerPC CPUs, using event codes that are not valid on older or unusual models, and breaking generic perf scripts that rely on these names. Test signals include PowerPC generation, mapfile matching tests, `perf list` on fallback systems, and representative `perf stat` runs for the generic names.
