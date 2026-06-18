# sources/distributed-fs/ceph-client/arch/arm64/include/asm/mpam.h

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/mpam.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/mpam.h

### Purpose
`mpam.h` defines ARM64 MPAM register helpers and feature hooks for Memory Partitioning and Monitoring.

### Important APIs, Types, And Functions
It declares MPAM enablement predicates, system-register access helpers, CPU setup hooks, and fallback no-ops when MPAM is disabled or unavailable.

### Control Flow
CPU feature detection enables MPAM support; setup code programs MPAM system registers; subsystems can later use partition/monitoring controls if the platform exposes them.

### State, Persistence, And Dependencies
State is in CPU MPAM registers and platform resource-control data. It depends on sysreg definitions, CPU feature probing, and configuration flags.

### Integration Points
Interacts with scheduler/resource-control or platform QoS code. Filesystem workloads are affected indirectly through memory/cache/bandwidth partitioning.

### Risks
Improper register programming can affect system-wide QoS or trap behavior. Feature stubs must keep non-MPAM builds correct.

### Test Signals
Compile MPAM and non-MPAM configs; boot on MPAM-capable hardware; validate register programming and resource partition behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/mpam.h -->
