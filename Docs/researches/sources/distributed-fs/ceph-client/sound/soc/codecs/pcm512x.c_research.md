# sources/distributed-fs/ceph-client/sound/soc/codecs/pcm512x.c

Purpose: shared ASoC codec core for PCM512x-class DACs. It implements mixer controls, DAPM, register defaults, regulator and SCLK management, runtime PM, DAI format handling, muting, and a substantial clock/PLL/divider algorithm for consumer/provider operation.

Important APIs and types: `struct pcm512x_priv` stores regmap, optional `sclk`, supplies/notifiers, DAI format, PLL input/output GPIOs, PLL coefficients, overclock allowances, mute state, mutex, BCLK ratio, and TAS575x `force_pll_on`. Exports are `pcm512x_regmap`, `pcm512x_probe()`, `pcm512x_remove()`, and `pcm512x_pm_ops`. Key functions include `pcm512x_find_pll_coeff()`, `pcm512x_set_dividers()`, `pcm512x_hw_params()`, `pcm512x_set_fmt()`, `pcm512x_mute()`, and startup constraints for master/slave.

Control flow: probe allocates state, registers regulator disable notifiers, enables supplies, resets registers, enables optional SCLK, requests standby, enables runtime PM, parses OF `pll-in`/`pll-out`, handles TAS575x PLL quirk, and registers the component. Startup applies master constraints based on SCLK/PLL or fixed slave rates. `hw_params()` sets word length; consumer mode enables clock autoset and skips PLL setup, while provider mode programs PLL coefficients, clock dividers, GPIO PLL routing, DAC/NCP/OSR/BCLK/LRCLK/IDAC dividers, FS speed, and clock synchronization halt/resume.

State and persistence: mute state is software-combined from stream mute and user digital switch bits under a mutex. Overclock controls persist in private fields and are only writable while bias is OFF/STANDBY. Regcache is RBTREE with paged range mapping; regulator notifiers mark cache dirty/cache-only on supply disable. Runtime suspend powers down and disables supplies/SCLK; resume restores cache and clears powerdown.

Dependencies and integration points: Linux clk, regulators, regmap, runtime PM, gcd math, ALSA SoC controls/DAPM/DAI ops, OF properties, and I2C/SPI wrappers.

Risks: PLL coefficient search can fall back to approximate rates. Master mode requires a valid SCLK; slave mode can switch PLL reference to BCLK when SCLK is absent. Device tree `pll-in` and `pll-out` must be both set or both absent and not equal. Several control changes are bias-level constrained. Error paths in resume can leave supplies or clocks enabled on late failures.

Test signals: provider/consumer modes, I2S/left/right/DSP_A/DSP_B formats, BCLK ratio boundaries, SCLK absent/present, PLL GPIO routing, overclock control EBUSY behavior, mute polling, runtime PM cache sync, and TAS575x force-PLL behavior.
