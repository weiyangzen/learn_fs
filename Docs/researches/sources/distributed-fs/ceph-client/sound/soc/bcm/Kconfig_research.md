# sources/distributed-fs/ceph-client/sound/soc/bcm/Kconfig

## Purpose
Kconfig menu for Broadcom ASoC platform drivers. It exposes BCM2835 I2S, Cygnus audio, and BCM63XX Whistler I2S support.

## Important APIs, Types, And Functions
Configuration symbols are `SND_BCM2835_SOC_I2S`, `SND_SOC_CYGNUS`, and `SND_BCM63XX_I2S_WHISTLER`.

## Control Flow
Selecting a symbol controls which Makefile object bundle is built. BCM2835 depends on `ARCH_BCM2835 || COMPILE_TEST` and selects generic dmaengine PCM and regmap MMIO. Cygnus depends on `ARCH_BCM_CYGNUS || COMPILE_TEST`. BCM63XX selects regmap MMIO.

## State And Persistence
Build-time `.config` only.

## Dependencies And Integration Points
Integrates with the BCM Makefile and platform-specific DT/device drivers. BCM63XX does not declare an architecture dependency here, so platform code must provide the matching runtime pieces.

## Risks
Missing `COMPILE_TEST` or architecture dependencies on BCM63XX can expose build/runtime mismatches depending on the rest of the tree. Kconfig selects must match helper APIs used by the C files.

## Test Signals
Kconfig allmodconfig coverage, architecture-specific builds, and ensuring selected helper dependencies are sufficient.
