<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xics/icp-native.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xics/icp-native.c

Purpose: Implements the native MMIO XICS Interrupt Presentation Controller backend.

Important APIs/types/functions: Entry point is `icp_native_init()`. Important functions are `icp_native_get_irq()`, exported `icp_native_eoi()`, `icp_native_set_cpu_priority()`, `icp_native_teardown_cpu()`, `icp_native_flush_ipi()`, `icp_native_flush_interrupt()`, exported `xics_wake_cpu()`, and SMP `icp_native_cause_ipi()`/`icp_native_ipi_action()`.

Control flow: Init scans `ibm,ppc-xicp` or `PowerPC-External-Interrupt-Presentation` nodes, maps each ICP MMIO range to a Linux CPU by hard CPU id, reserves memory, and records KVM XICS physical addresses. Runtime `get_irq` first consumes KVM-latched XICS interrupts, then reads XIRR, maps the vector, pushes CPPR, or masks/EOIs unknown vectors. EOI writes popped CPPR plus hwirq to XIRR. IPIs set QIRR/MFRR and use KVM host IPI latches.

State and persistence: State is `icp_native_regs[NR_CPUS]`, global `icp_ops`, KVM XICS physical-address registration, per-CPU CPPR stack, and hardware XIRR/QIRR registers.

Dependencies and integration points: Depends on OF address/range parsing, hard CPU id mapping, KVM PowerPC XICS latch hooks, SMP IPI demux, XICS common code, and memory resource reservation.

Risks: Source comments call out the assumption that interrupt server numbers match hard CPU numbers. Failed `request_mem_region()` leaks the allocated resource-name string. Offline interrupt flushing must correctly distinguish IPIs from external interrupts or it disables unknown vectors.

Test signals: Native XICS bare-metal boot, CPU hotplug/offline interrupt flushing, KVM host IPI latch behavior, MMIO mapping for every present CPU, and unknown-vector handling.

Source read size: 325 lines, 7101 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xics/icp-native.c -->
