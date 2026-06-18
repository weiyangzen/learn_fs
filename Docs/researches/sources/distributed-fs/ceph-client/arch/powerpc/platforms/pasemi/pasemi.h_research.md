# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pasemi/pasemi.h

Purpose: shared PA Semi platform declarations for time, PCI, DMA setup, register mapping, idle assembly, cpufreq astate hooks, and PCI controller ops.

Important APIs and control flow: declares `pas_get_boot_time`, `pas_pci_init`, `pas_pci_dma_dev_setup`, `pasemi_pci_getcfgaddr`, `pasemi_map_registers`, `idle_spin`, `idle_doze`, and `pasemi_pci_controller_ops`. Provides no-op cpufreq helpers when `CONFIG_PPC_PASEMI_CPUFREQ` is absent so idle code avoids power-saving modes.

State, dependencies, and risks: state is external and spread across PA Semi source files. Dependencies include `struct pci_dev`, MMIO annotations, and optional cpufreq. Risks are mismatched declarations with objects and fallback cpufreq behavior intentionally preventing deeper idle. Test signals are compile coverage across cpufreq enabled/disabled and users of exported PA Semi helpers.
