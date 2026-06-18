# sources/distributed-fs/ceph-client/sound/soc/codecs/tlv320aic31xx.c

## Purpose

`tlv320aic31xx.c` is the ASoC I2C driver for TI TLV320AIC31xx and DAC31xx codecs. It supports multiple codec variants, regulator/reset power sequencing, paged regmap caching, playback/capture DAI setup, PLL/divider programming, DAPM widgets/routes, jack detection IRQ handling, mic bias, output common-mode voltage selection, and optional DAC3100 coefficient firmware loading.

## Important APIs, Types, and Functions

`struct aic31xx_priv` stores component, regmap, codec type, reset GPIO, micbias, platform data, supplies, regulator notifiers, jack pointer, sysclk, P divider, rate-div table index, IRQ, and OCMV. `aic31xx_divs[]` is the PLL/divider table. Major functions include `aic31xx_setup_pll()`, `aic31xx_hw_params()`, `aic31xx_set_dai_fmt()`, `aic31xx_set_dai_sysclk()`, `aic31xx_clk_on/off()`, `aic31xx_power_on/off()`, `aic31xx_set_bias_level()`, `aic31xx_irq()`, `aic31xx_add_controls()`, `aic31xx_add_widgets()`, and `tlv320dac3100_fw_load()`.

## Control Flow

I2C probe initializes a paged regmap in cache-only mode, reads firmware/platform properties, gets reset GPIO and six supplies, configures OCMV, optionally configures GPIO1/INT1 and requests a threaded IRQ, optionally loads DAC3100 coefficients, then registers either DAC-only or full codec DAI(s). Component probe registers regulator-disable notifiers, marks the cache dirty, adds variant-specific controls/widgets/routes, and caches OCMV. Bias OFF-to-STANDBY powers regulators, resets hardware, syncs regcache, and restores jack detection. PREPARE turns clocks on; STANDBY from PREPARE turns clocks off; STANDBY-to-OFF disables supplies.

## State and Persistence Behavior

Regmap cache is authoritative while powered off and is synced after reset on power-on. Regulator disable notifiers assert reset and mark cache dirty if supplies disappear. Runtime persistent state includes selected sysclk source/frequency, P divider, rate-div line, codec variant, jack pointer, and dynamic clock-master DAPM route status. Jack-detection configuration is in a volatile status register and is restored separately after cache sync.

## Dependencies and Integration Points

Dependencies include I2C, regmap range pages, regulators, optional reset GPIO, firmware loading, ASoC, jack reporting, OF/ACPI matching, and DT bindings for mic-bias values. Integration varies by codec type: DAC31xx exposes playback only, AIC31xx exposes playback and capture, AIC311x variants add stereo Class-D routes, and AIC310x variants add mono speaker routes.

## Risks and Edge Cases

The PLL table is finite and exact frame-size/BCLK constraints can reject configurations or warn about inexact bitclocks. BCLK-as-PLL-input sysclk is derived in `hw_params()`, so params sequencing matters. IRQ handling reads volatile sticky flags and reports jack state only if a jack is registered. Firmware coefficient loading is strict about 153-byte size, magic, and version. `aic31xx_set_bias_level()` calls `BUG()` for unexpected bias transitions, which is harsh if framework sequencing changes.

## Test Signals

Validate each compatible variant, regulator failures and disable notifiers, reset GPIO polarity/timing, OFF/STANDBY/PREPARE/ON transitions, sysclk sources and sample rates from 8-192 kHz, DAI formats including DSP polarity inversion, master-clock DAPM route add/remove, jack/headset/button IRQ reports, overflow/short-circuit logs, DAC3100 firmware acceptance/rejection, and suspend/resume cache restoration.
