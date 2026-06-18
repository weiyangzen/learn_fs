# sources/distributed-fs/ceph-client/arch/powerpc/platforms/powermac/pmac.h

Purpose: declares cross-file PowerMac platform interfaces used by the local `pmac_*` implementation files. It is the internal header that ties setup, PCI, NVRAM, interrupt, feature, time, DMA, and SMP support together.

Important APIs/types/functions: declarations include `pmac_newworld`, `g5_phy_disable_cpu1`, time/RTC functions, `pmac_pci_irq_fixup`, `pmac_pci_init`, `pmac_nvram_update`, `pmac_nvram_read_byte`, `pmac_nvram_write_byte`, `pmac_pcibios_after_init`, `pmac_setup_pci_dma`, `pmac_check_ht_link`, `pmac_setup_smp`, `psurge_secondary_virq`, `low_cpu_offline_self`, `pmac_nvram_init`, `pmac_pic_init`, and `pmac_pci_controller_ops`.

Control flow: this file has no executable control flow. Its role is compile-time integration: `setup.c` pulls in platform entry points, `pci.c` exposes controller ops and IRQ fixup, `pic.c` exposes interrupt initialization, `nvram.c` exposes NVRAM setup, and `sleep.S` exposes `low_cpu_offline_self` for SMP/hotplug and sleep flows.

State and persistence: it declares shared state but owns none. The main stateful declaration is `pmac_newworld`, which affects setup, NVRAM partition lookup, and IRQ parsing policy. Persistence behavior comes from the implementation files.

Dependencies/integration: includes Linux PCI and IRQ headers plus `asm/pmac_feature.h`, so users get the platform feature-call selector context. It forward-declares `struct rtc_time` to avoid pulling RTC internals into every platform source.

Risks: as an internal header, mismatches between declarations and implementations can break platform initialization at link or runtime. Conditional definitions in implementation files mean some declarations only resolve for relevant config combinations. `low_cpu_offline_self` is marked `noreturn`; callers must treat it as terminal.

Test signals: build coverage across PPC32/PPC64, SMP/non-SMP, PM/no-PM, NVRAM enabled/disabled, and PCI configs; link verification for all declared symbols; boot smoke tests that exercise the `define_machine(powermac)` callbacks declared here.
