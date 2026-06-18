# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/hygon.c

Purpose: registers and initializes Hygon x86 CPUs, mostly following AMD-family behavior with Hygon-specific vendor identity, feature exposure, NUMA correction, cache/TLB detection, and virtualization/security quirks.

Important APIs and flow: `hygon_cpu_dev` supplies early, BSP, regular, and TLB callbacks to `cpu_dev_register()`. `early_init_hygon()` records microcode, maps power bits to constant/nonstop TSC, accumulated power and RAPL, enables syscall32 on x86-64, sets extended APIC ID and VMMCALL capability. `bsp_init_hygon()` checks TSC frequency behavior, enables MWAITX delay, configures LS_CFG-based SSBD if architectural bits are absent, and invokes resctrl detection. `init_hygon()` enables Zen-like features, cacheinfo, NUMA SRAT handling, SVM BIOS-disable detection, LFENCE serialization, ARAT, SYSRET bug marking, null-segment checks, and APIC MSR fence clearing. `cpu_detect_tlb_hygon()` fills global TLB sizing variables from extended CPUID leaves.

State and persistence: state is per-CPU capability/bug flags, global TLB descriptors, NUMA CPU-to-node mapping, and cached SSBD MSR base/mask data. No filesystem persistence.

Dependencies and integration: integrates with generic CPU identification, NUMA, cacheinfo, APIC/SMP, resctrl, speculation-control, SVM, and delay-loop code.

Risks and test signals: risks are misclassified capabilities or NUMA nodes on unusual firmware. Test signals include CPU bring-up logs, `/proc/cpuinfo` flags, SVM availability under BIOS disable, NUMA topology under broken SRAT, cache/TLB reporting, and suspend/idle timing on MWAITX systems.
