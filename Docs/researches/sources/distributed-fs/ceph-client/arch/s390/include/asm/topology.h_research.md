## sources/distributed-fs/ceph-client/arch/s390/include/asm/topology.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/topology.h` is a s390 CPU topology model
in the s390 ceph-client Linux source snapshot. It has 110 lines and 3146 bytes; exported UAPI
contract: no.

### Important APIs, Types, And Functions
cpu_topology_s390 fields, topology cpumask macros, dedication/capacity accessors, node mapping, and
update scheduling declarations
Important macros/constants: `_ASM_S390_TOPOLOGY_H`, `topology_physical_package_id(cpu)`, `topology_thread_id(cpu)`, `topology_sibling_cpumask(cpu)`, `topology_core_id(cpu)`, `topology_core_cpumask(cpu)`, `topology_book_id(cpu)`, `topology_book_cpumask(cpu)`, `topology_drawer_id(cpu)`, `topology_drawer_cpumask(cpu)`, `topology_cpu_dedicated(cpu)`, `topology_booted_cores(cpu)`, `mc_capable()`, `topology_is_primary_thread`, `POLARIZATION_UNKNOWN`, `POLARIZATION_HRZ`, `POLARIZATION_VL`, `POLARIZATION_VM`, `POLARIZATION_VH`, `CPU_CAPACITY_HIGH`; plus 6 more.
Important types/layouts: `sysinfo_15_1_x`, `cpu`, `cpu_topology_s390`, `cpumask`.
Important declarations or inline helpers: `topology_init_early`, `topology_cpu_init`, `topology_set_cpu_management`, `topology_schedule_update`, `store_topology`, `update_cpu_masks`, `topology_expect_change`, `topology_cpu_dedicated`, `topology_booted_cores`, `topology_is_primary_thread`, `cpu_to_node`, `numa_node_id`.

### Control Flow
Control flow is inlined into callers. The header selects the appropriate architecture-specific
helper, executes any embedded instruction sequence or simple predicate, and returns normalized C
values to generic kernel code.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
STSI sysinfo, scheduler topology, NUMA, CPU hotplug, and polarization/management events. Direct
include dependencies detected here: `linux/cpumask.h`, `asm/numa.h`, `asm-generic/topology.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for STSI sysinfo, scheduler topology, NUMA, CPU
hotplug, and polarization/management events. For UAPI files, the integration point also includes
headers_install and userspace programs compiled against the exported layout.

### Risks
stale topology masks or node ids degrade scheduling and can confuse CPU hotplug

### Test Signals
topology sysfs, CPU hotplug, capacity scaling, NUMA boots, and hypervisor topology-change events
