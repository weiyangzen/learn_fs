# sources/distributed-fs/ceph-client/sound/soc/amd/renoir/Makefile

## Purpose
This Makefile wires Renoir ACP3x PDM/DMIC support into Kbuild.

## Important APIs, Types, And Functions
It defines object lists for `snd-rn-pci-acp3x`, `snd-acp3x-pdm-dma`, and `snd-acp3x-rn`. The PCI parent and PDM DMA component are built under `CONFIG_SND_SOC_AMD_RENOIR`; the machine driver is built under `CONFIG_SND_SOC_AMD_RENOIR_MACH`.

## Control Flow
Kbuild compiles `rn-pci-acp3x.o` and `acp3x-pdm-dma.o` when Renoir support is enabled, and separately includes `acp3x-rn.o` when the machine-driver symbol is enabled.

## State And Persistence Behavior
There is no runtime state. It controls module composition and dependency visibility only.

## Dependencies And Integration Points
The split between platform and machine Kconfig symbols allows the PDM DMA/PCI layer to exist independently from the Renoir DMIC ASoC card registration.

## Risks And Edge Cases
If `CONFIG_SND_SOC_AMD_RENOIR_MACH` is disabled while the PCI parent still creates `acp_pdm_mach`, the machine platform device may not bind. Object name `snd-acp3x-pdm-dma` is shared-looking with ACP3x naming but implemented by Renoir-specific source in this directory.

## Test Signals
Build with Renoir support as module and built-in, with machine-driver symbol both enabled and disabled, and verify expected module/object names are produced.
