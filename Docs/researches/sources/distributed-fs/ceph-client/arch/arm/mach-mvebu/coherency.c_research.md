# sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/coherency.c

Purpose: MVEBU hardware coherency fabric support for Armada 370/375/38x/XP, including DMA coherency enablement and CPU coherent entry.

Important APIs/types/functions: Defines global `coherency_base`, `coherency_phys_base`, `set_cpu_coherent()`, `coherency_init()`, `coherency_available()`, SoC-specific init helpers, CPU/PCI notifiers, and low-level assembly hooks `ll_enable_coherency()`/`ll_add_cpu_to_smp_group()`.

Control flow: Init locates coherency fabric and CPU config nodes, maps registers, detects coherency type, enables fabric features for supported SoCs, and records physical base. CPU paths call low-level assembly to add CPUs to SMP/coherency groups. Late init installs DMA-coherent ops or notifiers, and PCI init can attach coherency notifier support.

State and persistence: Global state includes coherency bases, CPU config base, physical base, and notifier registration. Hardware state includes IO sync barriers, CPU config shared-L2 bits, coherency fabric target windows, and DMA coherency behavior.

Dependencies and integration points: Depends on OF address mapping, MBUS, DMA mapping ops, PCI, SMP platform helpers, `coherency_ll.S`, and MVEBU SoC ID detection.

Risks: Coherency misconfiguration causes data corruption, not just boot failure. SoC revision differences matter. Notifier ordering with device creation/PCI probing is subtle. Assembly helpers depend on global symbols being mapped/initialized.

Test signals: Stress DMA on Ethernet/SATA/PCIe/USB before and after SMP bring-up, test CPU hotplug, and verify coherent DMA ops on each Armada family.
