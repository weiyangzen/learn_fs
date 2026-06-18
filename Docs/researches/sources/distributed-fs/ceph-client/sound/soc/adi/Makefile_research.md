# sources/distributed-fs/ceph-client/sound/soc/adi/Makefile

## Purpose
`sound/soc/adi/Makefile` maps ADI ASoC Kconfig symbols to AXI softcore audio driver modules.

## Important APIs, Types, And Functions
It defines `snd-soc-adi-axi-i2s-y := axi-i2s.o` and `snd-soc-adi-axi-spdif-y := axi-spdif.o`, then includes those composites through `obj-$(CONFIG_SND_SOC_ADI_AXI_I2S)` and `obj-$(CONFIG_SND_SOC_ADI_AXI_SPDIF)`.

## Control Flow
There is no runtime flow. Kbuild uses the selected Kconfig symbols to produce built-in objects or modules.

## State And Persistence
Only build artifacts persist. Runtime state is in the platform drivers.

## Dependencies And Integration Points
This file is reached from `sound/soc/Makefile` when ASoC is enabled and pairs directly with `sound/soc/adi/Kconfig`.

## Risks And Edge Cases
Module naming is user-visible. Any source split or rename needs synchronized Kconfig, module alias, and packaging updates.

## Test Signals
Signals are successful builds of `snd-soc-adi-axi-i2s.ko` and `snd-soc-adi-axi-spdif.ko` under module configs, plus built-in link coverage under `y`.
