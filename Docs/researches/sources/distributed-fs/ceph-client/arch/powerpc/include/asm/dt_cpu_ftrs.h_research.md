## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/dt_cpu_ftrs.h

Purpose: declares the device-tree CPU feature discovery path that can supersede PVR-based CPU table discovery.

Important APIs/types/functions: `dt_cpu_ftrs_init()`, `dt_cpu_ftrs_scan()`, and `dt_cpu_ftrs_in_use()`, with false/no-op stubs when `CONFIG_PPC_DT_CPU_FTRS` is disabled.

Control flow: boot code initializes from the flattened device tree, scans `/cpus/features`, and later checks whether DT feature mode is active.

State and persistence: implementation maintains feature-discovery state elsewhere. The header exposes status through `dt_cpu_ftrs_in_use()`.

Dependencies and integration: includes UAPI cputable bits and integrates with early boot CPU feature setup, feature fixups, and firmware-provided CPU capability descriptions.

Risks and test signals: DT feature parsing must stay consistent with cputable feature masks. Test signals include pseries/PowerNV boots with `/cpus/features`, fallback to PVR discovery, feature fixup results, and HWCAP consistency.
