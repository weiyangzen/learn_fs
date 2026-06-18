# sources/distributed-fs/ceph-client/sound/soc/codecs/tlv320adc3xxx.c

## Purpose

`tlv320adc3xxx.c` is an ASoC I2C capture codec driver for TI TLV320ADC3001/ADC3101 devices. It configures ADC clocks, PLL/dividers, serial audio format, analog/digital input routing, AGC, miniDSP IIR coefficients, micbias pins, and a small gpiolib surface for GPIO/MICBIAS outputs.

## Important APIs, Types, and Functions

`struct adc3xxx` stores device type, MCLK, regmap, reset GPIO, PLL mode, sysclk, DT pin config, master/PLL route state, and `gpio_chip`. `adc3xxx_divs[]` is the clock table. `adc3xxx_get_divs()`, `adc3xxx_setup_pll()`, and `adc3xxx_hw_params()` select and program PLL/NADC/MADC/AOSR/BDIV. `adc3xxx_set_dai_sysclk()` accepts PLL auto/enable/bypass through `clk_id`; `adc3xxx_set_dai_fmt()` programs master/slave and I2S/DSP/right/left-justified modes. `adc3xxx_coefficient_*()` exposes 16-bit coefficient arrays. GPIO behavior is implemented by `adc3xxx_gpio_request()`, `adc3xxx_gpio_direction_out()`, `adc3xxx_gpio_set()`, and `adc3xxx_gpio_get()`.

## Control Flow

Probe allocates state, obtains reset GPIO and MCLK, enables the clock, parses DT pin/micbias properties, initializes a paged regmap, toggles hardware reset, configures GPIO/MICBIAS pins, and registers the component/DAI. During stream setup, `set_sysclk()` records clock mode and frequency; `set_fmt()` updates interface format and dynamically adds/removes DAPM routes for master-generated BCLK; `hw_params()` selects a supported divider row and dynamically adds/removes the PLL route depending on whether that row uses the PLL.

## State and Persistence Behavior

Registers are cached with an RBTREE regcache over pages 0, 1, and 4. Runtime state includes selected PLL usage, master mode, sysclk, and GPIO/MICBIAS values. GPIO output state persists in hardware registers and is readable via `gpio_get()`. Remove disables MCLK, unregisters GPIOs, and unregisters the component.

## Dependencies and Integration Points

The driver depends on I2C, clocks, reset GPIO, OF properties from `dt-bindings/sound/tlv320adc3xxx.h`, regmap, gpiolib, and ASoC. It integrates as a capture-only DAI `tlv320adc3xxx-hifi` with up to two channels and board-specific analog/digital input routing through DAPM.

## Risks and Edge Cases

The driver requires MCLK even though the chip could theoretically use BCLK. Divider support is table-limited, and PLL mode constraints can reject otherwise valid MCLK/rate pairs. GPIO input mode is explicitly not implemented. Coefficient controls write raw 16-bit values into miniDSP memory, so userspace can create invalid filters. Dynamic DAPM route changes must stay synchronized with `master` and `use_pll` state.

## Test Signals

Exercise all listed MCLK/rate combinations, PLL auto/enable/bypass modes, master/slave DAI formats, GPIO and MICBIAS output requests, DT validation failures, coefficient get/put round trips, and capture smoke tests through analog and digital-mic routes.
