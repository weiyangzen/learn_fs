# sources/distributed-fs/ceph-client/sound/soc/amd/Makefile

## Purpose
`sound/soc/amd/Makefile` maps AMD ASoC Kconfig symbols to legacy ACP DMA/machine objects, platform-family subdirectories, and the newer common ACP implementation.

## Important APIs, Types, And Functions
Composite modules include `acp_audio_dma-y := acp-pcm-dma.o`, `snd-soc-acp-da7219mx98357-mach-y`, `snd-soc-acp-rt5645-mach-y`, `snd-soc-acp-es8336-mach-y`, `snd-soc-acp-rt5682-mach-y`, and `snd-acp-config-y := acp-config.o`. Object inclusion covers `acp_audio_dma.o`, legacy CZ/Stoney machine drivers, `raven/`, `renoir/`, `vangogh/`, `yc/`, `acp/`, `snd-acp-config.o`, and `ps/`.

## Control Flow
There is no runtime flow. Kbuild includes composites or descends into subdirectories based on AMD ASoC symbols.

## State And Persistence
Only build artifacts persist. Runtime state belongs to the built drivers.

## Dependencies And Integration Points
This Makefile pairs with `sound/soc/amd/Kconfig` and is reached from the top-level ASoC Makefile. It connects the files in this subset to their module names and platform directories.

## Risks And Edge Cases
Some symbols include both a subdirectory and a config module, e.g. `SND_AMD_ACP_CONFIG` builds `acp/` and `snd-acp-config.o`; mismatches can break machine selection. Module names are stable artifacts expected by userspace packaging and kernel auto-loading.

## Test Signals
Build tests should confirm each enabled symbol emits expected modules and subdirectory objects, especially combinations of legacy ACP DMA, `snd-acp-config`, and `amd/acp` common modules.
