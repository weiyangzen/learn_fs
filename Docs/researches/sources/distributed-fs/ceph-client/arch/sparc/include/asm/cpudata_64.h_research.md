<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/cpudata_64.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/cpudata_64.h

## Purpose
This header defines SPARC64 per-CPU data structures and access declarations.

## Important APIs, Types, and Functions
It describes CPU metadata used by SMP, NUMA, scheduler topology, trap handling, and low-level CPU state.

## Control Flow
Early boot and CPU bringup populate per-CPU structures; runtime code uses them for CPU-local decisions.

## State and Persistence Behavior
Per-CPU data persists while CPUs are possible/online and is updated during hotplug or topology initialization.

## Dependencies and Integration Points
It integrates with SPARC64 SMP bringup, NUMA, trap blocks, scheduler, and percpu allocation.

## Risks
Assembly/C layout coupling and hotplug updates are correctness-sensitive.

## Test Signals
Boot large SMP/NUMA SPARC64 configs, exercise CPU hotplug, and verify topology/per-CPU debug data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/cpudata_64.h -->
