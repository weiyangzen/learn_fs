# sources/distributed-fs/ceph-client/sound/soc/amd/vangogh/Makefile

## Purpose
This Makefile wires Vangogh ACP5x legacy ASoC support into Kbuild.

## Important APIs, Types, And Functions
It defines object lists for `snd-pci-acp5x`, `snd-acp5x-i2s`, `snd-acp5x-pcm-dma`, and `snd-soc-acp5x-mach`. The PCI, I2S, and DMA objects build under `CONFIG_SND_SOC_AMD_ACP5x`; the machine driver builds under `CONFIG_SND_SOC_AMD_VANGOGH_MACH`.

## Control Flow
Kbuild compiles the ACP5x PCI parent, CPU DAI, PCM DMA component, and optionally the codec-specific machine driver according to these Kconfig symbols.

## State And Persistence Behavior
There is no runtime state. It only defines build-time composition.

## Dependencies And Integration Points
The file ties together `pci-acp5x.c`, `acp5x-i2s.c`, `acp5x-pcm-dma.c`, and optionally `acp5x-mach.c`. The optional machine driver is needed for Valve Jupiter/Galileo cards.

## Risks And Edge Cases
If the machine symbol is disabled, the PCI parent can still create `acp5x_mach` but no card driver will bind. The legacy driver may be bypassed by SOF config selection in the PCI driver even when these objects are built.

## Test Signals
Build with ACP5x as module and built-in, with and without `CONFIG_SND_SOC_AMD_VANGOGH_MACH`, and confirm module/object names and dependencies resolve.
