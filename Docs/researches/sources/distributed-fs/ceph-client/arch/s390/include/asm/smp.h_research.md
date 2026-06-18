## sources/distributed-fs/ceph-client/arch/s390/include/asm/smp.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/smp.h` is a s390 SMP coordination
declarations in the s390 ceph-client Linux source snapshot. It has 90 lines and 2633 bytes; exported
UAPI contract: no.

### Important APIs, Types, And Functions
CPU bring-up, IPI, IPL CPU calls, emergency stop, CPU address lookup, topology/capacity,
polarization, and dump status hooks
Important macros/constants: `__ASM_SMP_H`, `arch_scale_cpu_capacity`.
Important types/layouts: `lowcore`, `mutex`, `task_struct`, `cpumask`.
Important declarations or inline helpers: `__cpu_up`, `arch_send_call_function_single_ipi`, `arch_send_call_function_ipi_mask`, `smp_call_ipl_cpu`, `smp_emergency_stop`, `smp_find_processor_id`, `smp_store_status`, `smp_save_dump_ipl_cpu`, `smp_save_dump_secondary_cpus`, `smp_yield_cpu`, `smp_cpu_set_polarization`, `smp_cpu_get_polarization`, `smp_cpu_set_capacity`, `smp_set_core_capacity`, `smp_cpu_get_capacity`, `smp_cpu_get_cpu_address`, `smp_fill_possible_mask`, `smp_detect_cpus`, `smp_rescan_cpus`, `cpu_die`; plus 7 more.

### Control Flow
Control flow is inlined into callers. The header selects the appropriate architecture-specific
helper, executes any embedded instruction sequence or simple predicate, and returns normalized C
values to generic kernel code.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
generic SMP, lowcore, SIGP, topology, hotplug, and scheduler capacity accounting. Direct include
dependencies detected here: `asm/processor.h`, `asm/lowcore.h`, `asm/machine.h`, `asm/sigp.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for generic SMP, lowcore, SIGP, topology,
hotplug, and scheduler capacity accounting. For UAPI files, the integration point also includes
headers_install and userspace programs compiled against the exported layout.

### Risks
CPU-address mismatches or stale topology capacity can break IPI routing and scheduler placement

### Test Signals
CPU hotplug, smp_call_function, topology updates, polarization changes, and panic dump tests
