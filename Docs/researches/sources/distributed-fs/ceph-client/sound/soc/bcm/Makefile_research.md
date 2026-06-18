# sources/distributed-fs/ceph-client/sound/soc/bcm/Makefile

## Purpose
Build rules for Broadcom ASoC platform modules.

## Important APIs, Types, And Functions
Maps `SND_BCM2835_SOC_I2S` to `snd-soc-bcm2835-i2s.o`, `SND_SOC_CYGNUS` to `snd-soc-cygnus.o` from `cygnus-pcm.o cygnus-ssp.o`, and `SND_BCM63XX_I2S_WHISTLER` to `snd-soc-63xx.o` from `bcm63xx-i2s-whistler.o bcm63xx-pcm-whistler.o`.

## Control Flow
Kernel build includes each object bundle according to its `CONFIG_*` symbol.

## State And Persistence
Build-time only.

## Dependencies And Integration Points
Tightly matches `sound/soc/bcm/Kconfig` and expects the BCM63XX PCM companion file to provide symbols declared in `bcm63xx-i2s.h`.

## Risks
Object bundle membership is the link-time contract between BCM63XX I2S and PCM code; removing one side breaks unresolved symbols. Any config rename must be updated here.

## Test Signals
Module build/link for each Broadcom symbol and unresolved-symbol checks for `snd-soc-63xx`.
