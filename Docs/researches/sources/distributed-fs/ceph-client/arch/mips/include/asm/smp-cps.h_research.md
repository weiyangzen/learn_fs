<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/smp-cps.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/smp-cps.h

Purpose: Declares data structures and entry points for MIPS Coherent Processing System SMP boot and power-management support.

Important APIs/types/functions: `CPS_ENTRY_PATCH_INSNS`; `struct vpe_boot_config`, `struct core_boot_config`, `struct cluster_boot_config`; global `mips_cps_cluster_bootcfg`; boot/init APIs `mips_cps_core_boot`, `mips_cps_core_init`, `mips_cps_boot_vpes`; PM hooks `mips_cps_pm_save`, `mips_cps_pm_restore`; exception vector externs; and `mips_cps_smp_in_use()` with a non-SMP false stub.

Control flow: CPS SMP code fills cluster/core/VPE boot descriptors, patches or copies boot vectors, boots secondary VPEs/cores, initializes per-core state, and saves/restores CPS state over power-management transitions.

State and persistence: Persistent state is the shared cluster boot configuration and per-core/VPE boot descriptors containing PC, GP, SP, and synchronization fields. Hardware state includes GCR/CPS registers and exception vectors.

Dependencies and integration points: Integrated by `arch/mips/kernel/smp-cps.c`, CPS assembly boot code, exception handlers, and `CONFIG_MIPS_CPS`/SMP build paths.

Risks: Boot descriptors are shared between CPUs before normal scheduling is active; cache coherency, CCA setup, and ordering are critical. Stub behavior must match non-SMP builds.

Test signals: MIPS CPS SMP boot on multi-core systems, hotplug/secondary bring-up tests, suspend/resume, and non-SMP compile coverage are the main signals.

Source read size: 63 lines, 1383 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/smp-cps.h -->
