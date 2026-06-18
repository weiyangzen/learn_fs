# sources/distributed-fs/ceph-client/sound/soc/amd/raven/Makefile

## Purpose
This Makefile wires Raven Ridge ACP3x legacy ASoC modules into Kbuild.

## Important APIs, Types, And Functions
It defines object lists for `snd-pci-acp3x`, `snd-acp3x-pcm-dma`, and `snd-acp3x-i2s`, then includes each object under `CONFIG_SND_SOC_AMD_ACP3x`.

## Control Flow
When the ACP3x Kconfig symbol is enabled, Kbuild compiles `pci-acp3x.o`, `acp3x-pcm-dma.o`, and `acp3x-i2s.o` into separate modules or built-in objects according to kernel build mode.

## State And Persistence Behavior
There is no runtime state. The file controls build inclusion and module composition only.

## Dependencies And Integration Points
The Makefile integrates the Raven PCI parent, PCM DMA component, and I2S DAI component as a coordinated driver set. Machine drivers are outside this directory or platform-specific selection.

## Risks And Edge Cases
All three objects are tied to one Kconfig symbol, so partial builds of only PCI or only I2S/DMA are not represented here. Build failures in register headers or shared declarations affect all three outputs.

## Test Signals
Use kernel build coverage with `CONFIG_SND_SOC_AMD_ACP3x=m` and `=y`, then confirm generated objects or modules include `snd-pci-acp3x`, `snd-acp3x-pcm-dma`, and `snd-acp3x-i2s`.
