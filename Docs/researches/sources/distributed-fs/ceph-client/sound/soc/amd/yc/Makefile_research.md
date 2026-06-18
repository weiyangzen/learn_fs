# sources/distributed-fs/ceph-client/sound/soc/amd/yc/Makefile

## Purpose
This Kbuild file wires the AMD Yellow Carp ASoC objects into kernel configuration symbols. It builds the PCI ACP parent driver, the PDM DMA component, and the machine card driver.

## Important APIs, Types, And Functions
The important build targets are `snd-pci-acp6x-y := pci-acp6x.o`, `snd-acp6x-pdm-dma-y := acp6x-pdm-dma.o`, and `snd-soc-acp6x-mach-y := acp6x-mach.o`. Objects are selected by `CONFIG_SND_SOC_AMD_ACP6x` and `CONFIG_SND_SOC_AMD_YC_MACH`.

## Control Flow
Build-time only. Enabling `CONFIG_SND_SOC_AMD_ACP6x` includes both the PCI parent and PDM DMA platform component; enabling `CONFIG_SND_SOC_AMD_YC_MACH` includes the DMIC machine driver.

## State And Persistence
No runtime state. It controls which modules or built-in objects exist.

## Dependencies And Integration Points
The Makefile depends on Kconfig symbols defined elsewhere in the AMD ASoC tree. Runtime integration assumes `pci-acp6x.c` registers platform devices named `acp_yc_pdm_dma`, `dmic-codec`, and `acp_yc_mach`, matching the component names used by the machine driver.

## Risks And Test Signals
Misconfigured symbols can build a parent without a machine card, or vice versa. Test signals are successful `make sound/soc/amd/yc/`, module autoload for the AMD ACP PCI ID, and creation of the expected ASoC card when hardware/firmware gates allow it.
