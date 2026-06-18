# sources/distributed-fs/ceph-client/sound/soc/xtensa/Kconfig

## Purpose
Kconfig menu for Xtensa XTFPGA ASoC I2S controller support.

## Important APIs, Types, and Functions
Defines `SND_SOC_XTFPGA_I2S`, a tristate option that selects `REGMAP_MMIO` and enables the XTFPGA I2S master driver.

## Control Flow, State, and Persistence
No runtime behavior. Build-time selection controls whether `xtfpga-i2s.c` is compiled.

## Dependencies and Integration Points
Integrates Xtensa FPGA audio support with ASoC and regmap MMIO infrastructure. Users must also select suitable codec and machine-card pieces outside this file.

## Risks and Test Signals
Risks are sparse dependency declaration and relying on users to enable the rest of the audio subsystem. Test signals are Kconfig resolution and module build with `REGMAP_MMIO` selected.
