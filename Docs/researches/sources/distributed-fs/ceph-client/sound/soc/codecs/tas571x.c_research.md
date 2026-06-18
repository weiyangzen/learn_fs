# sources/distributed-fs/ceph-client/sound/soc/codecs/tas571x.c

## Purpose
This is a family ASoC I2C driver for TAS5707/TAS5711/TAS5717/TAS5719/TAS5721/TAS5733/TAS5753 class-D amplifier devices. It abstracts per-chip supplies, controls, register defaults, volume register width, and regmap configuration while sharing DAI format setup, mute behavior, power bias clocking, and custom multiword coefficient access.

## APIs, Types, and Functions
Key types are `struct tas571x_chip` for per-device static configuration and `struct tas571x_private` for runtime state. Major functions include `tas571x_i2c_probe()`, `tas571x_i2c_remove()`, `tas571x_reg_read()`, `tas571x_reg_write()`, `tas571x_reg_read_multiword()`, `tas571x_reg_write_multiword()`, `tas571x_coefficient_get()`, `tas571x_coefficient_put()`, `tas571x_hw_params()`, `tas571x_set_dai_fmt()`, `tas571x_mute()`, and `tas571x_set_bias_level()`. The `BIQUAD_COEFS` macro creates integer-array ALSA controls for 5-coefficient biquad registers.

## Control Flow
Probe selects chip data from OF/I2C match data, obtains optional MCLK, enables the chip-specific regulator set, creates a regmap using custom I2C accessors, configures optional `pdn` and active-low reset GPIOs, writes oscillator trim, builds a component-driver copy with chip-specific controls, adjusts 16-bit volume default LSBs for supported parts, and registers the component and DAI. `set_fmt` stores the requested serial format; `hw_params` maps right-justified/I2S/left-justified plus width into `TAS571X_SDI_REG`. `mute_stream` toggles the shutdown bit in system control 2 and waits briefly. Bias OFF disables MCLK; transition from OFF to STANDBY enables it.

## State and Persistence
Runtime state is small: selected chip descriptor, regmap cache, regulator handles, optional MCLK, DAI format, GPIOs, and component-driver copy. Regmap defaults preserve per-chip reset values for volume, mux, mixer, delay, modulation, and biquad-related registers. Coefficient controls directly read/write 20-byte or smaller multiword registers using big-endian 32-bit values and are not normalized by the driver.

## Dependencies and Integration
Depends on I2C, regmap with custom callbacks, regulators, optional clocks and GPIOs, ASoC controls/DAPM/DAI, TLV helpers, and the register definitions in `tas571x.h`. It integrates with machine drivers through `tas571x-hifi`, a 2-channel playback DAI accepting 8 to 48 kHz and 16/24/32-bit samples, and exposes chip-specific mixer/biquad controls to user space.

## Risks and Test Signals
Risks include mixed register sizes, direct coefficient writes with broad 32-bit ranges despite 26-bit effective coefficients, family-specific defaults that are easy to regress, optional MCLK error handling, and reliance on the caller setting DAI format before `hw_params`. Test signals include probing every compatible string, regulator unwind on GPIO/regmap failures, reset/pdn timing, 1-byte versus 2-byte volume behavior, coefficient read/write round trips, mute shutdown bit behavior, and serial format mapping for right/I2S/left justified widths.
