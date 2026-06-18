# sources/distributed-fs/ceph-client/sound/soc/codecs/rk3328_codec.h

## Purpose
This header defines the RK3328 codec register offsets, bit masks, symbolic values, DAI ID, and a small register/mask/value helper struct used by the RK3328 codec driver.

## Important APIs, types, and functions
The only type is `struct rk3328_reg_msk_val`, used for ordered playback open/close register update lists. Macros define `CODEC_RESET`, DAC init/precharge/power/clock/mixer/select/headphone/gain/pop registers, reset bits, pin direction, I2S master/slave mode, sample valid length, PCM/I2S/LJ/RJ modes, precharge/discharge current controls, headphone mute/init/work bits, DAC select bits, and gain masks.

## Control flow and integration
`rk3328_codec.c` uses these constants in DAI `set_fmt`, `hw_params`, mute control, reset, power on/off, playback open/close lists, and regmap readable/writeable filters. The address macros shift register indices by two, matching the 32-bit MMIO stride configured in regmap.

## State and persistence
The header describes hardware state but stores none. It establishes the bit values that drive persistent codec output state such as mute, DAC work, precharge current, HPMIX enable/init, and headphone pop mode.

## Dependencies
It includes `<linux/bitfield.h>` for `BIT()` and `GENMASK()`. The bit definitions are local to RK3328 and should not be reused for other Rockchip codecs.

## Risks and test signals
Because the driver uses ordered arrays of these constants for analog sequencing, a wrong mask/value pair can create pops, no output, or stuck mute. Tests should confirm register offsets match the hardware manual, sample-width macros produce correct LRCLK framing, and the open/close lists leave reset/default state compatible with `rk3328_codec_reg_defaults`.
