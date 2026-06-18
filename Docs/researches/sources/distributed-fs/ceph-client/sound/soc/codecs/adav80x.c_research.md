# sources/distributed-fs/ceph-client/sound/soc/codecs/adav80x.c

## Purpose
Shared ASoC driver for ADAV801/ADAV803 codecs, covering analog/digital routing, dual DAIs, PLL/sysclk configuration, deemphasis, PCM format programming, rate sharing, bias transitions, and regmap defaults.

## APIs, Types, and Functions
Exports `adav80x_bus_probe()` and `adav80x_regmap_config`. `struct adav80x` stores regmap, selected clock source, sysclk, PLL source, per-DAI format, active rate, deemphasis flag, and three SYSCLK power-down states. Key functions include `adav80x_set_dai_fmt()`, `adav80x_hw_params()`, `adav80x_set_capture_pcm_format()`, `adav80x_set_playback_pcm_format()`, `adav80x_set_adc_clock()`, `adav80x_set_dac_clock()`, `adav80x_set_sysclk()`, `adav80x_set_pll()`, `adav80x_dai_startup()`, `adav80x_dai_shutdown()`, `adav80x_set_bias_level()`, `adav80x_probe()`, `adav80x_resume()`, and deemphasis get/put helpers.

## Control Flow, State, and Persistence
Bus probe allocates state and registers a component with two DAIs: HiFi and Aux. Component probe force-enables PLL pins for SYSCLK output, powers down unsupported S/PDIF receiver logic, and disables DAC zero flag. `set_sysclk()` either selects an input clock source and updates internal clock routing registers, or enables/disables SYSCLK outputs and forces/disables PLL DAPM pins under the DAPM mutex. `set_pll()` validates 27/54 MHz inputs, desired sample-rate-family outputs, PLL doubling and divider bits, then syncs DAPM when PLL source changes. `hw_params()` requires `sysclk == rate * 256`, programs capture/playback word length and ADC/DAC clocking, stores active rate, and updates deemphasis. Startup enforces one active sample rate across both DAIs until all streams shut down.

## Dependencies and Integration
Depends on ASoC controls/DAPM/DAIs, regmap, TLV controls, and bus wrappers `adav801.c` and `adav803.c`. Machine drivers must set sysclk/PLL coherently before stream startup.

## Risks and Test Signals
Risks include strict `rate * 256` sysclk requirement, only normal bit-clock/frame polarity support, shared active-rate state across both DAIs, PLL source power routes depending on DAPM pin forcing, and unsupported S/PDIF receiver being disabled unconditionally. Test signals are both DAIs operating with matching rates, PLL1/PLL2/OSC source route selection, SYSCLK output enable/disable, 16/18/20/24-bit capture/playback format programming, deemphasis changes at 32/44.1/48 kHz families, and regcache sync on resume.
