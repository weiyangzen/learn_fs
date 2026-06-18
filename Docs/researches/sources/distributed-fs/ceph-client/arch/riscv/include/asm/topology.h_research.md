<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/topology.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/topology.h

Purpose: Connects RISC-V CPU topology to generic Linux topology and optional NUMA scheduling data.

Important APIs/types/functions: Defines topology macros and includes generic topology defaults, with NUMA/cpumask integration when enabled.

Control flow: No direct runtime flow; generic scheduler/topology code consumes the macros and per-CPU data.

State and persistence: Persistent topology state is maintained by generic CPU/NUMA code.

Dependencies and integration points: Used by scheduler domains, sysfs topology, ACPI/DT CPU discovery, and NUMA setup.

Risks: Incorrect topology reporting harms scheduling placement and hotplug behavior.

Test signals: Topology sysfs, lscpu validation, NUMA scheduling, CPU hotplug, ACPI and DT boots.

Source read size: 26 lines, 822 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/topology.h -->
