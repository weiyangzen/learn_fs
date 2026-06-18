# Research: subset-b-006445

Grouped research report for Maxim and MC13783 ASoC codec sources under `sources/distributed-fs/ceph-client/sound/soc/codecs/`. Each section is source-tree aligned and bounded by reconciliation markers for per-file splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max98520.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/max98520.c

## Purpose
Implements the Linux ASoC I2C codec driver for the Maxim MAX98520 speaker amplifier. The driver registers a single playback DAI, exposes mixer controls for speaker gain, digital volume, DHT/limiter, clock monitor, ADC readback, and maps DAPM power events to amplifier/global enable register writes.

## Important APIs, Types, and Functions
The driver uses `struct max98520_priv` from `max98520.h` to hold the regmap, optional reset GPIO, channel size, and TDM state. Key ASoC callbacks are `max98520_dai_set_fmt()`, `max98520_dai_hw_params()`, `max98520_dai_tdm_slot()`, and the DAPM event `max98520_dac_event()`. Probe paths are split between component probe `max98520_probe()` for chip initialization and I2C probe `max98520_i2c_probe()` for allocation, regmap setup, reset GPIO, revision read, and component registration. Power management is handled by `max98520_suspend()` and `max98520_resume()` through regcache cache-only mode and a software reset on resume.

## Control Flow
I2C probe verifies SMBus byte support, allocates private data, initializes a 16-bit-address/8-bit-value regmap with RBTREE cache, optionally deasserts reset, reads `MAX98520_R21FF_REVISION_ID`, then registers `max98520-aif1`. Component probe performs software reset, sets default mono mix and PCM input routing, enables the DC blocker, enables clock monitor autorestart, and enables PCM RX. During stream setup, `set_fmt` configures BCLK edge and PCM format for I2S, left-justified, DSP_A, or DSP_B. `hw_params` maps 16/24/32-bit samples and 8 kHz through 192 kHz rates into register fields, then chooses BCLK ratio unless TDM mode has already configured it. TDM setup programs BCLK, channel size, and RX source masks. DAPM POST_PMU turns on amp/global enable and delays about 30 ms; POST_PMD disables global and amp in reverse order with the same delay.

## State and Persistence
Persistent driver state is minimal: `ch_size` and `tdm_mode` influence later clock setup, while regmap cache carries register state across suspend. Suspend marks cache dirty and cache-only; resume disables cache-only, issues soft reset, then syncs cache. The optional reset GPIO is only used at probe to power on the device.

## Dependencies and Integration Points
Depends on Linux I2C, regmap, GPIO descriptor APIs, ASoC controls/DAPM/DAI registration, and OF matching for `maxim,max98520`. It integrates with machine drivers through the DAI named `max98520-aif1`, DAPM endpoint `BE_OUT`, and standard ALSA controls. It supports system sleep PM via `SYSTEM_SLEEP_PM_OPS`.

## Risks
`max98520_dai_tdm_slot()` treats all-zero slot arguments as non-TDM but still computes `slots * slot_width`, so callers attempting to clear TDM with zeros can hit an unsupported BCLK error. Several `regmap_update_bits()` calls ignore return values, so I/O errors during format, clock, and DAPM transitions may be silent. The right-channel RX source mask depends on header macros and is sensitive to shift/mask correctness. Revision is logged but not validated, so compatible but unsupported silicon revisions are not rejected.

## Test Signals
Useful tests include probing with and without reset GPIO, validating revision read, exercising 16/24/32-bit playback at every advertised rate, I2S/LJ/DSP_A/DSP_B format negotiation, TDM slot masks including disable paths, suspend/resume regcache sync, and DAPM amp enable sequencing with register tracing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max98520.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max98520.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/max98520.h

## Purpose
Defines the MAX98520 register map, bit masks, format/rate encodings, DHT/ADC control bit positions, and `struct max98520_priv` shared with `max98520.c`.

## Important APIs, Types, and Defines
The header enumerates 16-bit register addresses from software reset/status through PCM, amplifier, ADC, DHT, global enable, boost test, and revision ID. It defines PCM format encodings for I2S, left-justified, and TDM modes, channel-size masks, sampling-rate codes up to 192 kHz, RX enable bits, DSP speaker feature shifts, SSM/DHT/ADC filter shifts, and private driver storage fields.

## Control Flow Role
There is no executable control flow. The `.c` file uses these constants to validate and program DAI format, BCLK, sample rate, DAPM amp events, controls, readable/volatile regmap callbacks, and reset/revision access.

## State and Persistence
`struct max98520_priv` carries the runtime regmap pointer, optional reset GPIO, last channel size, and TDM-mode flag. The register constants define the persistent hardware state cached by regmap.

## Dependencies and Integration Points
The header is private to the MAX98520 codec implementation and depends on kernel types included by the `.c` file, notably `struct regmap` and `struct gpio_desc`.

## Risks
`MAX98520_PCM_DMIX_CH1_SHIFT` is defined as `(0xF << 0)` rather than a numeric shift count, and `MAX98520_PCM_DMIX_CH1_SRC_MASK` shifts by that value. That is suspicious because the right-channel field is used as a 4-bit field in the driver. Header values should be cross-checked against the datasheet and runtime register writes.

## Test Signals
Compile-time coverage should include mask expansion warnings, while runtime tests should validate PCM RX source programming for left and right channels, sample-rate encoding, DHT controls, and regmap readable/volatile coverage against the defined addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max98520.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max9860.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/max9860.c

## Purpose
Implements the ASoC driver for the MAX9860 mono voice codec with stereo ADC inputs and mono DAC output. It provides playback and capture DAIs, volume/AGC/filter controls, DAPM routes, runtime PM, regulator handling, and MCLK-derived clock programming.

## Important APIs, Types, and Functions
`struct max9860_priv` owns regmap, DVDDIO regulator, regulator notifier, prescaler value, PCLK rate, and cached DAI format. Core callbacks are `max9860_hw_params()`, `max9860_set_fmt()`, `max9860_set_bias_level()`, `max9860_suspend()`, `max9860_resume()`, `max9860_probe()`, and `max9860_remove()`. Regmap callbacks classify readable, writable, volatile, and precious registers.

## Control Flow
Probe allocates state, obtains and enables `DVDDIO`, registers a disable notifier, initializes regmap, gets `mclk`, validates 10-60 MHz, derives a 10-20 MHz PCLK with `psclk`, manually writes defaults with cache bypass, clears interrupt status by reading it, enables runtime PM, and registers the component/DAI. `set_fmt` only stores provider/consumer mode after validating clock-provider bits. `hw_params` builds interface register values from provider mode, channel count, format, inversion, sample width, integer-clock eligibility, and PLL mode, then writes IFC/SYSCLK/N registers. Bias level toggles the SHDN bit. Runtime suspend disables the prescaled clock and regulator; resume re-enables regulator, syncs cache, and restores `psclk`.

## State and Persistence
The cached `fmt`, `psclk`, and `pclk_rate` are essential for every stream configuration. Regcache is marked dirty/cache-only on regulator disable notification and synchronized on resume. Interrupt status is precious to avoid destructive cached reads.

## Dependencies and Integration Points
Integrates with I2C, `mclk`, `DVDDIO`, runtime PM, regmap, ASoC controls/DAPM, and OF compatible `maxim,max9860`. The DAI is `max9860-hifi`, with symmetric rates and both playback/capture from 8-48 kHz.

## Risks
The regulator notifier marks the cache dirty on disable, but unexpected regulator events during active streams could desynchronize software assumptions. `hw_params` computes PLL `n` from `pclk_rate`; bad or zero clock rates would be catastrophic, though probe bounds MCLK. Unsupported DSP_A/B sample widths and inversion combinations fail late in stream setup. The manual default-write loop must stay synchronized with header/register defaults.

## Test Signals
Probe tests should cover missing regulator, missing/bad MCLK, default writes, and interrupt clear. Audio tests should cover master/consumer modes, I2S/LJ/DSP_A/DSP_B, inversion combinations, mono/stereo streams, integer-clock and PLL modes, runtime suspend/resume, and regulator-disable notifier behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max9860.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max9860.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/max9860.h

## Purpose
Private MAX9860 register and bitfield definition header for the mono voice codec driver.

## Important APIs, Types, and Defines
Defines 8-bit registers for interrupt status, mic readback, interrupts, system/audio clocking, serial interfaces, filters, DAC/ADC gain, mic/AGC/noise gate, power management, and revision. Defines bit masks and shifts for PLL/N dividers, interface modes, BCLK selections, filter enums, inverted mixer controls, and power enables.

## Control Flow Role
The `.c` file uses this header to implement regmap access policy, DAI interface programming, PLL/integer clock configuration, ALSA controls, DAPM ADC/DAC enables, and bias-level power transitions.

## State and Persistence
Register definitions map the codec's persistent hardware state; no C runtime state is declared in the header.

## Dependencies and Integration Points
Private to `max9860.c`. It is consumed by ASoC control macros and regmap configuration.

## Risks
Many ALSA controls use inverted ranges, minimum constants, and enum counts from this header; off-by-one changes would alter user-visible mixer semantics. The `REVISION` register is `0xff` while the operational register range is sparse, so readable/writable callbacks must stay consistent with `MAX9860_MAX_REGISTER`.

## Test Signals
Validate mixer TLV scaling against register encodings, writable/readable callback behavior for reserved register `0x0d`, interrupt status precious behavior, and power bit shifts for DAC/ADC enables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max9860.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max9867.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/max9867.c

## Purpose
Implements the MAX9867 stereo audio codec driver with stereo playback/capture, input/output mixers, digital mic muxing, sidetone, filter controls, DAI clocking, and bias-level power management.

## Important APIs, Types, and Functions
`struct max9867_priv` stores MCLK, regmap, rate constraints, sysclk/PCLK, provider/format flags, and active ADC/DAC bitmask. Important callbacks include `max9867_filter_get/set()`, `max9867_adc_dac_event()`, `max9867_startup()`, `max9867_dai_hw_params()`, `max9867_set_dai_sysclk()`, `max9867_dai_set_fmt()`, `max9867_mute()`, and `max9867_set_bias_level()`.

## Control Flow
I2C probe allocates state, initializes regmap, reads revision, registers the component and DAI, then gets MCLK. `set_sysclk` validates 10-60 MHz, computes PCLK prescaler, programs SYSCLK, and installs exact-rate constraints based on 44.1 kHz or 48 kHz families. `startup` applies those constraints. `set_fmt` configures master/consumer mode, I2S or DSP_A, and inversion. `hw_params` writes NI dividers, chooses BCLK source/ratio in provider mode, selects exact integer mode when possible, or enables PLL/rapid lock in consumer mode. DAPM ADC/DAC events maintain an active bitmap; the DSP filter setter refuses changes while ADC/DAC paths are active, temporarily shuts the codec down, changes mode, then restarts it.

## State and Persistence
The driver persists `constraints`, `sysclk`, `pclk`, `provider`, `dsp_a`, and `adc_dac_active`. Regmap RBTREE cache tracks register state, and bias OFF marks the cache dirty after powering down. PM suspend/resume forces DAPM bias OFF/STANDBY.

## Dependencies and Integration Points
Depends on I2C, regmap, `mclk`, ASoC component/DAI/DAPM, and OF compatible `maxim,max9867`. The DAI `max9867-aif1` is stereo-only, 8-48 kHz, S16_LE, and symmetric-rate.

## Risks
Probe registers the component before acquiring MCLK, so a late MCLK failure occurs after component registration in devm-managed flow. Filter changes depend on a name-to-enum mapping in `max9867_adc_dac_event()`. Exact-rate constraints depend on sysclk being set before stream startup. Several register updates ignore return values in filter and DAI paths.

## Test Signals
Exercise sysclk values at each prescaler boundary, 44.1 kHz/48 kHz constraint application, provider and consumer clocking, DSP_A/I2S inversion variants, active-stream filter-change `-EBUSY`, mute control, DAPM path activation, and suspend/resume bias transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max9867.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max9867.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/max9867.h

## Purpose
Defines the MAX9867 8-bit register map and the bit masks used for clocking, interface format, filters, power, and revision.

## Important APIs, Types, and Defines
Registers cover status/jack/aux, interrupt enable, SYSCLK, audio clock N divider, IFC1A/IFC1B serial interface, codec filters, sidetone, DAC/ADC levels, line/mic gains, input/mic/mode configuration, power management, and revision. Key masks include prescaler fields, PLL/rapid lock, master mode, I2S delay, TDM, inversion, BCLK ratios, filter mode, SHDN, and revision.

## Control Flow Role
Used by `max9867.c` to drive regmap volatility, sysclk setup, DAI format, BCLK ratio, PLL/integer clock behavior, filter changes, mute, and bias-level power state.

## State and Persistence
No runtime state is declared. The constants define hardware state cached by the driver's regmap.

## Dependencies and Integration Points
Private to the MAX9867 driver and consumed by ASoC controls and DAI operations.

## Risks
Only a small set of status/aux registers is volatile; if hardware readback registers beyond those can change asynchronously, cached reads may stale. `MAX9867_CACHEREGNUM` is defined but not used by the current regmap cache setup.

## Test Signals
Check register access around volatile status/jack/aux registers, BCLK mask updates, filter mode bit behavior, and PWRMAN SHDN polarity under DAPM bias transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max9867.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max9877.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/max9877.c

## Purpose
Implements a compact ASoC amplifier component driver for MAX9877. It has no PCM DAI; it exposes amplifier controls and DAPM routes for analog input selection, speaker/headphone output volume, oscillator mode, bypass, and shutdown.

## Important APIs, Types, and Functions
The driver uses a plain regmap with five defaults. Primary data surfaces are `max9877_controls`, `max9877_dapm_widgets`, `max9877_dapm_routes`, `max9877_component_driver`, and `max9877_i2c_probe()`.

## Control Flow
I2C probe initializes the regmap, writes all default register values to force reset state, and registers an ASoC component with controls and DAPM but no DAI. DAPM input widgets feed the `SHDN` PGA, which is bit-controlled by `MAX9877_OUTPUT_MODE`; outputs route through speaker/headphone endpoints.

## State and Persistence
The driver does not allocate private state. Register values are cached by regmap RBTREE and user-visible ALSA controls persist as hardware register state.

## Dependencies and Integration Points
Depends on I2C, regmap, ASoC component controls, DAPM, and TLV helpers. It integrates as an auxiliary amplifier component controlled by a machine driver rather than as a CPU-facing codec DAI.

## Risks
Default writes ignore errors, so partial reset programming can pass silently. No OF/ACPI match table is present, so binding depends on I2C board/device IDs. With no remove or PM callbacks, power state is delegated entirely to DAPM and regmap cache.

## Test Signals
Probe with the `max9877` I2C ID, verify five default register writes, exercise all volume TLV controls, output and oscillator enums, bypass/shutdown bit behavior, and DAPM routes for speaker/headphone endpoints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max9877.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max9877.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/max9877.h

## Purpose
Defines the small MAX9877 amplifier register set and bit masks used by `max9877.c`.

## Important APIs, Types, and Defines
Defines five registers: input mode, speaker volume, left/right headphone volume, and output mode. Bit definitions cover input A/B stereo selection, zero-cross detection, output mode, oscillator selection, bypass, and shutdown.

## Control Flow Role
The `.c` file maps these constants directly to ALSA controls and DAPM shutdown routing.

## State and Persistence
No C state. The register map describes all persistent hardware configuration used by the driver.

## Dependencies and Integration Points
Private to the MAX9877 amp driver; consumed by ASoC control macros.

## Risks
`MAX9877_OUTMODE_MASK` covers four bits while the output enum exposes nine values; reserved hardware encodings remain reachable only if controls are extended or raw writes occur. Shutdown bit polarity is embedded in the DAPM PGA declaration and should match the datasheet.

## Test Signals
Validate enum-to-register mapping for all output modes, oscillator bit offsets, bypass bit behavior, and shutdown PGA polarity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max9877.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max98925.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/max98925.c

## Purpose
Implements the ASoC driver for the MAX98925 speaker amplifier with playback/capture DAI, DAI clock divider setup, VMON/IMON sense slot routing, boost/ALC/speaker controls, and DAPM amp power sequencing.

## Important APIs, Types, and Functions
Uses `struct max98925_priv` for regmap, component pointer, sysclk, VMON/IMON slots, speaker gain, and channel size. Key functions are `max98925_dac_event()`, `max98925_rate_value()`, `max98925_set_sense_data()`, `max98925_dai_set_fmt()`, `max98925_set_clock()`, `max98925_dai_hw_params()`, `max98925_dai_set_sysclk()`, `max98925_probe()`, and `max98925_i2c_probe()`.

## Control Flow
I2C probe initializes regmap, reads optional `vmon-slot-no` and `imon-slot-no` from DT, validates slot values, reads revision, rejects unknown revisions, and registers the component/DAI. Component probe writes default runtime settings for format delay, TDM slot select, DOUT Hi-Z, filters, ALC, configuration, and boost limiter. `set_sysclk` chooses MCLK or BCLK clock source and stores the frequency. `set_fmt` supports consumer and provider modes, sets master bit, configures sense slots in consumer mode, and programs inversion. `hw_params` maps sample width, BCLK ratio 32/48/64, sysclk family, sample rate, M/N dividers, sample-rate code, and MDLL multiplier.

## State and Persistence
`sysclk`, `ch_size`, `v_slot`, and `i_slot` persist in private data and drive stream setup. Regmap cache stores hardware state. DAPM pre/post events enable or disable boost and V/I ADC monitor blocks around the speaker path.

## Dependencies and Integration Points
Depends on I2C, OF properties, regmap, ASoC component/DAI/DAPM, and TLV controls. Compatible string is `maxim,max98925`; DAI is `max98925-aif1`.

## Risks
`max98925_rate_value()` selects the first table rate greater than or equal to the requested rate, while advertised rates are discrete; unexpected intermediate rates could be rounded upward if ALSA constraints allowed them. Several register writes ignore errors. The header defines `MAX98925_REG_CNT` using an undefined-style `MAX98925_R03A_BOOST_LIMITER` name, though it is unused here. Sense-slot DT validation compares against encoded constants, which currently equal numeric slot values because shift is zero.

## Test Signals
Test valid/invalid revision IDs, MCLK/BCLK clock-source selection, sysclk values 6/11.2896/12/12.288 MHz, every supported sample width/rate, BCLK ratios, OF sense-slot values, DAPM boost/ADC enable transitions, and ALSA boost/ALC controls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max98925.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max98925.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/max98925.h

## Purpose
Defines MAX98925 register addresses, revision IDs, interrupt/status/DAI/sense/ALC/boost bitfields, slot constants, and `struct max98925_priv`.

## Important APIs, Types, and Defines
The header covers status/flag/IRQ/map registers, DAI clock modes and M/N divider registers, PCM format, TDM slot selection, VMON/IMON/VBAT/VBST/FLAG DOUT configuration, Hi-Z masks, filter controls, gain, ALC, boost, block/global enable, boost limiter, and revision ID. `struct max98925_priv` stores regmap, component, optional platform-data pointer, sysclk, V/I slots, speaker gain, and channel size.

## Control Flow Role
The `.c` file consumes these definitions for regmap access policy, revision validation, DT slot programming, DAI clocks, DAPM boost/monitor enables, and user controls.

## State and Persistence
The private struct carries runtime stream configuration; register definitions represent persistent cached hardware state and volatile measurement/status registers.

## Dependencies and Integration Points
Private to the MAX98925 driver and tied to ASoC/regmap register programming.

## Risks
`MAX98925_REG_CNT` references `MAX98925_R03A_BOOST_LIMITER`, which is not defined in the visible header naming scheme; it is currently unused but would break if used. The very large bitfield surface increases the risk that copied masks diverge from datasheet values. Slot constants assume zero shift and are used as validation bounds and encoded values.

## Test Signals
Build with warnings enabled to catch unused/bad macros, validate revision constants `0x51` and `0x80`, exercise DAI and DOUT slot masks, status/volatile register behavior, boost limiter fields, and all ALC/gain controls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max98925.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max98926.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/max98926.c

## Purpose
Implements the MAX98926 ASoC speaker amplifier driver. It resembles MAX98925 but adds PDM/current-voltage routing and optional interleaved V/I sense data while using a simpler sample-rate setup without explicit M/N divider programming.

## Important APIs, Types, and Functions
Uses `struct max98926_priv` for regmap, component, sysclk, V/I slots, channel size, and interleave flag. Important functions are `max98926_set_sense_data()`, `max98926_dai_set_fmt()`, `max98926_dai_hw_params()`, `max98926_probe()`, and `max98926_i2c_probe()`. Controls expose speaker gain, ramp/ZCD, ALC, boost voltage/current limit, DAC HPF, and PDM channel settings.

## Control Flow
I2C probe allocates state, initializes regmap, reads `maxim,interleave-mode` or legacy `interleave-mode`, reads optional VMON/IMON slot properties, reads version, registers component/DAI, and logs the version. Component probe records the component pointer and sets DOUT Hi-Z defaults. `set_fmt` only supports codec consumer mode, configures V/I sense data, validates inversion, writes format delay, and updates BCLK inversion. `hw_params` maps sample format to channel size, accepts BCLK/LRCLK ratios 32/48/64, picks the first rate table entry at or above requested rate, and writes the DAI sample-rate field.

## State and Persistence
`interleave_mode`, `v_slot`, `i_slot`, and `ch_size` persist in private data and control DOUT configuration. Regmap RBTREE cache stores register state. The DAPM graph enables speaker, boost, global, VI, DAI/PDM selection blocks through register-backed widgets.

## Dependencies and Integration Points
Depends on I2C, OF, regmap, ASoC controls/DAPM/DAI. Compatible string is `maxim,max98926`; DAI is `max98926-aif1`.

## Risks
The version is read but not validated against `MAX98926_CHIP_VERSION` values. `set_fmt` computes combined inversion but only writes `MAX98926_DAI_BCI_MASK`, so word-clock inversion may not be applied. The `VI Enable` DAPM bit expression combines `MAX98926_ADC_IMON_EN_WIDTH` with `MAX98926_ADC_VMON_EN_SHIFT`, which is suspicious because one operand is a width rather than a shift/mask. DAPM route names include `"LeftRightDiv2"`, while the corresponding control label is `"(Left+Right)/2 Switch"`, risking a route/control mismatch.

## Test Signals
Test consumer-mode DAI format with all inversion variants, S16/S24/S32 sample formats, BCLK ratios, supported rates, interleave and non-interleave slot programming, PDM/PCM routes, version read, and DAPM VI/boost/speaker enables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max98926.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max98926.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/max98926.h

## Purpose
Defines the MAX98926 register map, chip versions, PDM routing bits, DAI/sense/ALC/boost bitfields, slot constants, and private state structure.

## Important APIs, Types, and Defines
Registers largely mirror MAX98925 for status/IRQ/map, DAI clocking, format, TDM, DOUT sense channels, filters, gain, speaker amp, ALC, boost, block/global enable, limiter, and version. MAX98926-specific additions include PDM current/voltage/channel/source masks and the interleave bit in FORMAT. `struct max98926_priv` stores regmap, component, sysclk, V/I slots, channel size, and interleave mode.

## Control Flow Role
The `.c` file uses these constants for regmap access, optional DT property validation, PDM mux controls, DAPM block enables, DAI format/sample-rate programming, and ALSA controls.

## State and Persistence
Private state fields store stream/slot/interleave configuration. Register definitions describe persistent hardware state, with status and version registers treated as volatile by the driver.

## Dependencies and Integration Points
Private to `max98926.c` and tied to ASoC and regmap programming.

## Risks
`MAX98926_REG_CNT` references `MAX98926_R03A_BOOST_LIMITER`, which does not match the defined register name and is unused. The header exposes `*_WIDTH` symbols beside shifts/masks, increasing the chance of misuse; the `.c` file appears to use a width in a DAPM bit expression. PDM fields packed into `DAI_CLK_DIV_N_LSBS` need hardware validation.

## Test Signals
Compile-time macro checks, PDM mux and channel controls, interleave slot fields, DAI BCI/WCI bits, block enable masks, boost current limit encoding, and volatile/status register reads should be tested.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max98926.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max98927.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/max98927.c

## Purpose
Implements the MAX98927 ASoC speaker amplifier driver with PCM/PDM playback, capture-side voltage/current sense, optional TDM and interleave, reset GPIO handling, system sleep PM, and extensive boost/brownout/envelope tracking defaults.

## Important APIs, Types, and Functions
Uses `struct max98927_priv` for regmap, component, reset GPIO, slots, interleave, channel size, rate/interface/provider flags, digital gain, and TDM state. Core functions are `max98927_dai_set_fmt()`, `max98927_get_bclk_sel()`, `max98927_set_clock()`, `max98927_dai_hw_params()`, `max98927_dai_tdm_slot()`, `max98927_dai_set_sysclk()`, `max98927_dac_event()`, `max98927_probe()`, `max98927_suspend/resume()`, `max98927_slot_config()`, `max98927_i2c_probe()`, and `max98927_i2c_remove()`.

## Control Flow
I2C probe allocates state, reads interleave properties, initializes 16-bit regmap, requests optional reset GPIO and deasserts it with a 5-6 ms delay, reads revision ID, reads V/I slot properties, and registers the component/DAI. Component probe soft-resets the device, initializes TX Hi-Z, monomix, volume/gain, DC blockers, boost/current limit, measurement ADC, brownout, envelope tracking, and V/I TX slot enable/Hi-Z registers. `set_fmt` selects consumer/provider mode, inversion, PCM formats or PDM source, enables/disables PCM RX or PDM RX, and stores interface type. `hw_params` writes sample width, PCM sample rate, IVADC sample rate, and clock setup. TDM slot setup programs RX/TX enable and Hi-Z masks. DAPM amp events clear TDM mode before power-up, enable amp/global on POST_PMU, and disable them on POST_PMD.

## State and Persistence
Private state persists sysclk, slot selection, interleave mode, channel size, interface, provider flag, and TDM mode. Regcache is set cache-only and dirty on suspend; resume soft-resets, disables cache-only, and syncs cached state. Reset GPIO is asserted on remove.

## Dependencies and Integration Points
Depends on I2C, regmap, optional reset GPIO, OF and ACPI matching, ASoC controls/DAPM/DAI, and system sleep PM. Compatible strings include OF `maxim,max98927` and ACPI `MX98927`; DAI is `max98927-aif1`.

## Risks
`max98927_dai_tdm_slot()` always sets `tdm_mode = true` and lacks a zero-argument disable path, while `max98927_dac_event()` resets TDM mode before power-up. `set_fmt` supports only NB_NF and IB_NF inversion. Slot properties are masked to four bits instead of rejecting out-of-range values. Many initialization writes ignore errors. Revision is logged but not validated.

## Test Signals
Test reset GPIO sequencing, OF and ACPI probe, PCM vs PDM format switching, provider and consumer sysclk selection, TDM RX/TX masks including slots above 7, interleave IVADC sample-rate behavior, V/I capture path, suspend/resume regcache sync, and DAPM amp/global sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max98927.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max98927.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/max98927.h

## Purpose
Defines the MAX98927 16-bit register map, PCM/PDM/amp/measurement/boost/brownout/envelope bitfields, and private driver structure.

## Important APIs, Types, and Defines
Register definitions span interrupts, clock monitor, watchdog, measurement ADC thresholds, PCM RX/TX enables and Hi-Z, PCM mode/master/clock/sample-rate, ICC/PDM, amplifier volume/DSP/source/gain, measurement enables, boost controls, brownout levels, envelope tracking, global shutdown, soft reset, and revision ID. Bitfields cover PCM RX/TX slots, source shifts, interleave, PCM format/channel size, master mode, sample-rate codes, PDM RX, amp volume/gain, DRE, measurement enable, boost voltage, brownout DSP, soft reset, and global enable. `struct max98927_priv` stores all runtime configuration used by the driver.

## Control Flow Role
The `.c` file uses this header for regmap defaults/access policy, DAI format/rate/TDM programming, DAPM amp and V/I capture paths, reset/revision handling, and PM resume reset/sync.

## State and Persistence
Private state includes reset GPIO, sysclk, V/I slots, interleave flag, channel size, rate/interface/provider flags, digital gain, and TDM mode. Register constants represent cached hardware state and volatile status/measurement fields.

## Dependencies and Integration Points
Private to `max98927.c`, with type dependencies supplied by the implementation includes.

## Risks
`MAX98927_PCM_FORMAT_*` values are unshifted while the driver shifts `format` by `FORMAT_SHIFT`, so the pair is intentionally coupled; changing one side would break format programming. `MAX98927_DRE_EN_SHIFT` is `0x1` although `DRE_CTRL_DRE_EN` is bit 0, so the DRE control may target the wrong bit. The private struct includes unused or lightly used fields (`pdata`, `spk_gain`, `rate`, `digital_gain`) that may indicate drift from older platform-data code.

## Test Signals
Validate PCM format field writes, DRE switch bit behavior, PDM source selection, boost/current controls, V/I slot source fields, volatile measurement registers, soft reset/global shutdown, and TDM Hi-Z masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max98927.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/mc13783.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/mc13783.c

## Purpose
Implements the ASoC codec driver for the Freescale/NXP MC13783 PMIC audio block. It supports the stereo DAC, voice codec capture path, synchronous or asynchronous SSI routing, analog input/output mixers, and register initialization through the parent MFD.

## Important APIs, Types, and Functions
`struct mc13783_priv` stores the parent `mc13xxx`, regmap, and chosen ADC/DAC SSI ports. Stream callbacks include `mc13783_pcm_hw_params_dac()`, `mc13783_pcm_hw_params_codec()`, `mc13783_pcm_hw_params_sync()`, `mc13783_set_fmt()`, async/sync format wrappers, sysclk wrappers, and TDM slot wrappers for DAC/codec/sync. Component lifecycle is `mc13783_probe()` and `mc13783_remove()`. Platform probe is `mc13783_codec_probe()`.

## Control Flow
Platform probe allocates state, gets ADC/DAC SSI ports from platform data or the parent DT `codec` child node, stores parent MFD data, and registers either one synchronous DAI if ports match or two async DAIs if they differ. Component probe binds the parent regmap and writes reset values for RX/TX/SSI/CODEC/DAC registers, then selects SSI1/SSI2 for codec and DAC. DAI hw_params maps DAC rates from 8-96 kHz to a register index, while codec capture only accepts 8 or 16 kHz. Format setup supports I2S and DSP_A, inversion, and provider/consumer clocking; sync mode forces the codec side to consume the DAC clock. Sysclk setup validates a fixed clock table and CLIA/CLIB clock source. TDM setup separately validates DAC slots/rx masks and codec 4-slot tx mask.

## State and Persistence
The selected SSI ports persist in private data and determine DAI topology and register SSI selection. Register state is written through the parent MFD/regmap; remove clears VAUDIOON bits in `AUDIO_RX0`. No explicit runtime PM or regcache suspend handling exists in this file.

## Dependencies and Integration Points
Depends on the `mc13xxx` MFD parent, parent regmap, platform data or OF child properties `adc-port` and `dac-port`, ASoC controls/DAPM, and platform driver registration. Exposes either `mc13783-hifi` sync DAI or `mc13783-hifi-playback` plus `mc13783-hifi-capture` async DAIs.

## Risks
Some local bit macros are unused or contain quirks, such as `AUDIO_RX1_PGARXEN` ending with a semicolon. Many `mc13xxx_reg_write()` reset writes ignore return values. DT probing returns `-ENOSYS` if the `codec` child is absent. Synchronous mode forces capture rate symmetry with playback, and codec capture is limited to 8/16 kHz. No validation checks that parent drvdata/regmap are present before use.

## Test Signals
Test platform-data and OF probe paths, same-port sync versus different-port async registration, all supported DAC rates, codec 8/16 kHz capture rejection paths, I2S/DSP_A and clock inversion/provider combinations, sysclk table entries and invalid clocks, DAC/codec TDM slot masks, DAPM analog routes, and remove clearing VAUDIOON.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/mc13783.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/mc13783.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/mc13783.h

## Purpose
Small public/private header for the MC13783 ASoC codec driver, defining clock source IDs and DAI IDs.

## Important APIs, Types, and Defines
Defines `MC13783_CLK_CLIA`, `MC13783_CLK_CLIB`, `MC13783_ID_STEREO_DAC`, `MC13783_ID_STEREO_CODEC`, and `MC13783_ID_SYNC`. These constants identify the clock input selected by `set_sysclk` and the DAI instances used by async/sync registration.

## Control Flow Role
The `.c` file uses clock IDs to select `AUDIO_CLK_SEL`, and DAI IDs to decide whether async format setup targets the stereo DAC or voice codec. The sync ID identifies the combined playback/capture DAI.

## State and Persistence
No runtime state is declared. The constants control DAI identity and clock-source selection in caller-visible ASoC operations.

## Dependencies and Integration Points
Used by `mc13783.c` and potentially machine-driver code that configures clocks or references DAI IDs.

## Risks
The header is minimal, so any ABI expectation about these numeric IDs should remain stable. Renumbering would break machine-driver assumptions.

## Test Signals
Validate machine-driver DAI lookup by ID/name, CLIA/CLIB sysclk selection, and sync versus async DAI registration behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/mc13783.h -->
