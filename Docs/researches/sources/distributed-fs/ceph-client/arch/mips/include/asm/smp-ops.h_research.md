<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/smp-ops.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/smp-ops.h

Purpose: Defines the platform SMP operation vector used by generic MIPS SMP code to delegate CPU setup, boot, IPI, and hotplug behavior to the active platform implementation.

Important APIs/types/functions: `struct plat_smp_ops` callbacks `send_ipi_single`, `send_ipi_mask`, `init_secondary`, `smp_finish`, `boot_secondary`, `smp_setup`, `prepare_cpus`, `prepare_boot_cpu`, `cpu_disable`, `cpu_die`, and `cleanup_dead_cpu`; `register_smp_ops`; wrappers `plat_smp_setup`, registration helpers for UP/VSMP/CPS, and generic IPI send declarations.

Control flow: Early boot registers an SMP ops implementation, generic MIPS setup calls `plat_smp_setup`/prepare hooks, secondary bring-up calls platform boot/init/finish callbacks, and IPI helpers route reschedule or call-function events through the registered ops.

State and persistence: The central state is the registered `plat_smp_ops` pointer held by implementation code. Callback side effects include CPU masks, boot state, interrupt routing, and hotplug state.

Dependencies and integration points: Depends on Linux CPU masks and errno handling. Integrated with MIPS SMP core, platform-specific SMP backends, `CONFIG_SMP`, `CONFIG_MIPS_MT_SMP`, and `CONFIG_MIPS_CPS`.

Risks: Missing callbacks or wrong registration can leave secondary CPUs unbootable or IPIs unrouted. Stub helpers for non-SMP must remain harmless and compile away cleanly.

Test signals: SMP boot/hotplug, IPI stress, call-function/reschedule tests, and defconfig coverage for UP, VSMP, and CPS registrations are useful.

Source read size: 107 lines, 2296 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/smp-ops.h -->
