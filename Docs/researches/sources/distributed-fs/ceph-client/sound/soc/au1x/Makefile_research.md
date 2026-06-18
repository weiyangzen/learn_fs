# sources/distributed-fs/ceph-client/sound/soc/au1x/Makefile

## Purpose
Build rules for Au1x ASoC CPU DAI, DMA, and board drivers. It maps Kconfig symbols to module object names and their single C source files.

## Important APIs, Types, And Functions
Important object mappings include `snd-soc-au1xpsc-dbdma-y := dbdma2.o`, `snd-soc-au1xpsc-i2s-y := psc-i2s.o`, `snd-soc-au1xpsc-ac97-y := psc-ac97.o`, `snd-soc-au1x-dma-y := dma.o`, `snd-soc-au1x-ac97c-y := ac97c.o`, `snd-soc-au1x-i2sc-y := i2sc.o`, `snd-soc-db1000-y := db1000.o`, and `snd-soc-db1200-y := db1200.o`.

## Control Flow
The kernel build includes each module when its `CONFIG_*` variable is enabled. Board objects are separate from controller/DMA objects.

## State And Persistence
Build-time only; no runtime state.

## Dependencies And Integration Points
Integrates with `sound/soc/au1x/Kconfig` symbols and the top-level sound/soc build.

## Risks
Any Kconfig rename must be mirrored here. Board drivers may build without all runtime platform devices present, so load order is determined by platform registration rather than Makefile ordering.

## Test Signals
Module build for each symbol and `modinfo`/object naming consistency with platform-driver names.
