# sources/distributed-fs/ceph-client/sound/soc/codecs/rk817_codec.c

## Purpose
This is the ASoC codec driver for the RK817 PMIC-integrated audio codec. It registers one playback/capture DAI, initializes codec registers through the parent RK808 regmap, provides DAPM routes for mic capture, headphone playback, and class-D speaker playback, and supports a DT option for differential microphone input.

## Important APIs, types, and functions
`struct rk817_codec_priv` stores the component, parent `struct rk808`, MCLK, cached sysclk, and `mic_in_differential`. Key functions are `rk817_init()`, `rk817_set_component_pll()`, volume controls, virtual playback mux, DAPM widget/route tables, `rk817_set_dai_sysclk()`, `rk817_set_dai_fmt()`, `rk817_hw_params()`, `rk817_digital_mute()`, component probe/remove, DT parsing, and platform probe/remove.

## Control flow and integration
Platform probe gets the parent RK808 data, parses the child `codec` node for `rockchip,mic-in-differential`, enables parent `mclk`, and registers the component. Component probe initializes the ASoC regmap from the parent PMIC regmap, stores the component, asserts a digital top reset value, writes vendor-kernel-derived defaults, conditionally enables differential mic mode, and programs fixed PLL values through `snd_soc_component_set_pll()`. DAI format currently only selects codec slave or master mode; hw_params writes 16-bit or 24-bit TX/RX word length registers.

## State and persistence
Most state lives in PMIC registers and is managed by DAPM supplies. `stereo_sysclk` records the requested sysclk but is not otherwise used. The fixed PLL configuration is persistent until changed. `mic_in_differential` is DT-derived and applied once during init.

## Dependencies
The driver depends on the RK808 MFD parent, RK817 codec register definitions from `<linux/mfd/rk808.h>`, parent regmap, MCLK, ASoC DAPM/control/DAI APIs, and simple-card compatible clock/PLL setup.

## Risks and test signals
Several PLL values and init registers are hard-coded from vendor code with comments noting poor documentation, so portability across boards is uncertain. `of_get_child_by_name()` failure leaves `node` NULL but still passes it to `of_property_read_bool()`, which is typically safe but worth checking. `RK817_FORMATS` advertises S20_3LE, yet `rk817_hw_params()` rejects S20_3LE. Test signals include module bind under the RK808 MFD, MCLK enable/disable on probe/remove, playback mux exclusivity between HP and SPK, mute control, 16/24/32-bit stream behavior, rejection or support alignment for S20_3LE, and differential mic DT behavior.
