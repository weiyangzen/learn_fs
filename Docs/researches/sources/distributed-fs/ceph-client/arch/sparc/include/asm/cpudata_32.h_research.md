<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/cpudata_32.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/cpudata_32.h

## Purpose
This header defines SPARC32 per-CPU data structures.

## Important APIs, Types, and Functions
It declares the CPU data layout used for CPU identity, loops-per-jiffy/calibration, and architecture-specific per-CPU fields.

## Control Flow
Boot CPU and secondary CPU setup initialize these structures; runtime code reads them through per-CPU accessors.

## State and Persistence Behavior
Per-CPU data persists for each online CPU and changes during CPU setup/hotplug-like paths.

## Dependencies and Integration Points
It integrates with SMP setup, scheduler CPU data, delay calibration, and platform CPU probing.

## Risks
Layout assumptions may be shared with assembly; drift can corrupt per-CPU reads.

## Test Signals
Boot UP and SMP SPARC32 configs, verify CPU enumeration, delay calibration, and per-CPU data access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/cpudata_32.h -->
