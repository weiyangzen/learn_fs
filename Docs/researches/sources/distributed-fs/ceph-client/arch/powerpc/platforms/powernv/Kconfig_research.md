
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/Kconfig

Purpose: defines build-time configuration for the IBM PowerNV non-virtualized PowerPC platform and selected platform features.

Important symbols: `PPC_POWERNV` requires `PPC64 && PPC_BOOK3S`, defaults to enabled, and selects platform MMU, interrupt, PCI, MSI, CPU frequency, doorbell, SMP, radix TLBIE, and debug-console capabilities. `OPAL_PRD` enables the OPAL PRD driver for processor recovery diagnostics. `PPC_MEMTRACE` enables runtime allocation of RAM for hardware tracing and depends on PowerNV, memory hotplug, and contiguous allocation. `SCOM_DEBUGFS` exposes SCOM controllers through debugfs when `DEBUG_FS` is enabled.

Control flow and state: this file has no runtime control flow. It shapes compile-time inclusion, dependency solving, and implied architecture capabilities for the PowerNV platform.

Dependencies and integration points: integrates with top-level PowerPC Kconfig, OPAL firmware-facing drivers, PCI/interrupt subsystems, memory hotplug, debugfs, and platform files selected in the sibling Makefile.

Risks: `PPC_POWERNV` selects many foundational features, so dependency changes can alter architecture-wide builds. Feature symbols such as `PPC_MEMTRACE` expose privileged runtime interfaces and must remain gated by required memory-management support.

Test signals: `olddefconfig`/`allyesconfig`/PowerNV defconfig resolution, successful PowerNV kernel builds, expected object inclusion from the Makefile, and no impossible dependency cycles.
