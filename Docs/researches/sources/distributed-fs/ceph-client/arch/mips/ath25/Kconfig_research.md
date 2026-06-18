## sources/distributed-fs/ceph-client/arch/mips/ath25/Kconfig

Purpose: defines build-time options for Atheros ATH25 SoC support. It splits support between AR5312/AR2312-class and AR2315-class SoCs and optionally enables the AR2315 PCI controller.

Important symbols: `SOC_AR5312` enables AR5312/AR2312+ support and depends on `ATH25`. `SOC_AR2315` enables AR2315+ support and depends on `ATH25`. `PCI_AR2315` depends on `SOC_AR2315`, selects `ARCH_HAS_PHYS_TO_DMA` and `FORCE_PCI`, and defaults on.

Control flow: none at runtime. These symbols control which C files are compiled and which code paths are available in headers through `#ifdef CONFIG_SOC_*`.

State and persistence: none directly. The selected symbols shape the kernel image.

Dependencies and integration: integrates with the parent ATH25 platform Kconfig and the local Makefile. PCI selection pulls in architecture DMA translation and PCI core support for AR2315 host mode.

Risks: both SoC families default on, so dead code or wrong runtime dispatch can remain hidden until boot on specific hardware. Forcing PCI for AR2315 may be inappropriate for stripped-down images unless the option is manually disabled.

Test signals: build configurations should include the expected objects. Boot tests on AR5312/AR2312 and AR2315/16/17/18 hardware validate that the Kconfig mix matches runtime CPU detection.
