# sources/distributed-fs/ceph-client/sound/soc/xtensa/Makefile

## Purpose
Kbuild manifest for the Xtensa XTFPGA I2S ASoC module.

## Important APIs, Types, and Functions
Builds `snd-soc-xtfpga-i2s.o` from `xtfpga-i2s.o` under `CONFIG_SND_SOC_XTFPGA_I2S`.

## Control Flow, State, and Persistence
No runtime behavior. It provides a single-module build mapping.

## Dependencies and Integration Points
Integrates the Xtensa I2S source with Kbuild and the local Kconfig symbol.

## Risks and Test Signals
Risks are limited to config/object rename drift. Test signal is successful module build.
