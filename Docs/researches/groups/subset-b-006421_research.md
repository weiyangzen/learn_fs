<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/adau1761.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/adau1761.c

## Purpose
Device-specific ASoC component driver for the ADAU1361/ADAU1461/ADAU1761/ADAU1961 family. It layers codec controls, DAPM widgets/routes, platform-data policy, bias handling, and regmap defaults on top of the shared ADAU17x1 core.

## APIs, Types, and Functions
The public entry point is `adau1761_probe()`, exported for bus glue. It selects either the constrained ADAU1361 DAI or the wider ADAU1761 DAI, calls `adau17x1_probe()`, optionally probes compatibility mode, enables regcache cache-only mode, and registers `adau1761_component_driver`. Important helpers include `adau1761_component_probe()`, `adau1761_set_bias_level()`, `adau1761_setup_digmic_jackdetect()`, `adau1761_setup_headphone_mode()`, `adau1761_compatibility_probe()`, `adau1761_dejitter_fixup()`, and `adau1761_readable_register()`. The file defines large ALSA control arrays for input gain, differential capture, ALC, playback volumes, mixers, bias modes, mono output, jack-detect automute, and DAPM route tables for analog I/O, digital clocks, DSP, digital mic, and capless headphone support.

## Control Flow, State, and Persistence
Probe delegates shared state allocation to `adau17x1_probe()`, then `adau1761_compatibility_probe()` temporarily bypasses the cache, enables the core clock, writes/reads `ADAU17X1_SERIAL_SAMPLING_RATE`, and marks an actual ADAU1761 as `ADAU1761_AS_1361` when it was declared as ADAU1361-compatible. Runtime component probe adds common ADAU17x1 widgets first, then chooses single-ended or differential capture controls from platform data, configures lineout/headphone modes, chooses jack-detect/no-DMIC/DMIC routing, and adds DSP or non-DSP routes according to `adau->type`. Bias transition to standby enables `SYSCLK`, disables cache-only mode, and syncs cached writes after OFF; bias OFF disables `SYSCLK` and returns to cache-only mode. State lives in the shared `struct adau`: type, regmap, master flag, DSP/SigmaDSP handles, and PLL/slot state from the common core.

## Dependencies and Integration
Depends on ALSA SoC component/DAI/DAPM APIs, regmap, `linux/platform_data/adau17x1.h`, and the common `adau17x1` exported DAI ops and register helpers. Bus-specific I2C/SPI files call `adau1761_probe()` with an initialized regmap and optional SPI mode-switch callback. Firmware integration is via the shared SigmaDSP path using `adau1761.bin` for real ADAU1761-class devices.

## Risks and Test Signals
Risks include platform-data driven routing being wrong for a board, cache-only writes being lost if bias never reaches standby, compatibility probing touching registers while clocks are not stable, duplicate/incorrect table defaults such as swapped ALC attack/decay control names, and subtle DAPM route differences between ADAU1361, real ADAU1761, and compatibility mode. Test signals are probe success on I2C/SPI, DAPM graph creation for single-ended, differential, DMIC, jack-detect, mono, capless and DSP cases, regcache sync across suspend/resume and bias OFF/STANDBY, stream setup through `adau17x1_dai_ops`, and hardware audio validation for line/headphone/mono output modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/adau1761.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/adau1761.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/adau1761.h

## Purpose
Small internal interface for ADAU1761-family bus drivers and the shared codec implementation.

## APIs, Types, and Functions
Declares `adau1761_probe(struct device *dev, struct regmap *regmap, enum adau17x1_type type, void (*switch_mode)(struct device *dev))` and exports `adau1761_regmap_config`. It includes `linux/regmap.h` and `adau17x1.h`, so callers use the common enum values such as `ADAU1361` and `ADAU1761`.

## Control Flow, State, and Persistence
The header has no runtime state. It defines the compile-time contract by which I2C/SPI glue passes transport-specific regmap settings and optional SPI mode-switch logic to the common component registration code.

## Dependencies and Integration
Integrated by ADAU1761 bus glue and the main `adau1761.c` implementation. The regmap config declared here carries 16-bit register addressing, 8-bit values, default register cache data, and ADAU17x1 precious/volatile helpers.

## Risks and Test Signals
The main risk is ABI drift between this declaration and `adau1761.c`, or callers passing a type unsupported by the component policy. Build coverage from bus modules is the primary signal; runtime probe validates that the passed regmap and switch callback work for the selected bus.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/adau1761.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/adau1781-i2c.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/adau1781-i2c.c

## Purpose
I2C transport glue for ADAU1381/ADAU1781 ASoC codecs.

## APIs, Types, and Functions
`adau1781_i2c_probe()` copies `adau1781_regmap_config`, sets 8-bit values and 16-bit register addresses for I2C, creates a devm I2C regmap, and calls `adau1781_probe()` with match data. `adau1781_i2c_remove()` calls `adau17x1_remove()` for clock cleanup. The file registers I2C IDs for `adau1381` and `adau1781`, optional OF compatible strings, and an `i2c_driver` via `module_i2c_driver()`.

## Control Flow, State, and Persistence
All persistent codec state is allocated by `adau17x1_probe()` in the core path. The I2C file only adapts probe/remove and device matching. There is no explicit I2C remove state beyond disabling any prepared optional `mclk`.

## Dependencies and Integration
Depends on Linux I2C, regmap, mod_devicetable, and the shared ADAU1781 header. It integrates with device tree compatible strings `adi,adau1381` and `adi,adau1781`, plus legacy I2C ID matching.

## Risks and Test Signals
Risk is match data mismatch: the OF table entries omit `.data`, so `i2c_get_match_data()` must be checked against kernel matching behavior and fallback ID matching for the targeted tree. Test signals are successful I2C probe, correct type selection, regmap bus transactions with 16-bit registers, and removal without leaked prepared clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/adau1781-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/adau1781-spi.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/adau1781-spi.c

## Purpose
SPI transport glue for ADAU1381/ADAU1781 codecs.

## APIs, Types, and Functions
`adau1781_spi_switch_mode()` issues three dummy `spi_w8r8()` reads to pull CLATCH low and put the device into SPI mode. `adau1781_spi_probe()` gets the SPI ID, copies `adau1781_regmap_config`, sets 8-bit values, 24-bit register framing, and `read_flag_mask = 0x1`, then calls `adau1781_probe()` with the switch callback. `adau1781_spi_remove()` delegates to `adau17x1_remove()`. The SPI and OF ID tables cover `adau1381` and `adau1781`.

## Control Flow, State, and Persistence
Probe only initializes transport format and then lets the shared core allocate `struct adau`, set up optional clocks, firmware, and component registration. The switch callback is stored in `struct adau` and reused by resume to re-enter SPI mode before regcache sync.

## Dependencies and Integration
Uses SPI, regmap, ASoC, and the ADAU1781/common ADAU17x1 exported APIs. It integrates with boards declaring SPI devices or OF compatibles `adi,adau1381`/`adi,adau1781`.

## Risks and Test Signals
Risks include failing to enter SPI mode if dummy reads are not accepted by board wiring, no check of `spi_w8r8()` return values, OF entries without explicit `.data`, and incorrect 24-bit address/read-flag configuration. Test signals are register reads after switch mode, resume regcache sync after SPI mode re-entry, successful firmware attach, and stream setup via the common DAI ops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/adau1781-spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/adau1781.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/adau1781.c

## Purpose
ASoC component implementation for ADAU1381/ADAU1781 codecs, using the common ADAU17x1 clock, DAI, TDM, PLL, regmap, and SigmaDSP code while defining ADAU1781-specific analog controls and routing.

## APIs, Types, and Functions
Exports `adau1781_probe()` and `adau1781_regmap_config`. Important internal functions include `adau1781_component_probe()`, `adau1781_set_bias_level()`, `adau1781_set_input_mode()`, `adau1781_dejitter_fixup()`, and `adau1781_readable_register()`. It defines TLV ranges for speaker, PGA, beep and sidetone controls; DAPM widgets for PGAs, speaker, beep mixer, lineout mixers, mono mixer, digital power domains, zero crossing, BEEP, analog mic inputs, and optional DMIC routing. The DAI driver exposes 2-8 channel playback/capture up to 96 kHz and delegates operations to `adau17x1_dai_ops`.

## Control Flow, State, and Persistence
`adau1781_probe()` chooses `adau1381.bin` or `adau1781.bin`, calls the shared `adau17x1_probe()`, and registers the component. Component probe adds common controls/widgets, applies platform-data input differential bits, chooses DMIC or analog ADC routes, and then adds common ADAU17x1 routes. Bias standby enables core `SYSCLK` and precharge via `ADAU1781_DIG_PWDN1`; bias OFF clears precharge bits and disables `SYSCLK`. DAPM post events rewrite the dejitter register after power graph changes, with different behavior when the codec is not the bit-clock master.

## Dependencies and Integration
Depends on `adau17x1.c`, `sigmadsp`, ASoC DAPM/control APIs, regmap, and optional `adau1781_platform_data`. I2C and SPI transport files supply regmap framing and optional SPI mode-switch callbacks.

## Risks and Test Signals
Risks include duplicate/default typo in `adau1781_reg_defaults` for `DIG_PWDN1`, duplicated DAPM route entries, platform-data-only DMIC/differential configuration with limited device-tree policy, and dependence on shared PLL/TDM logic for all stream setup. Test signals are route creation for analog versus DMIC capture, bias ON/OFF register changes, dejitter fixup after DAPM power transitions, SigmaDSP firmware load at stream rate, and capture/playback with 2/4/8 channel slot maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/adau1781.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/adau1781.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/adau1781.h

## Purpose
Internal API shared by ADAU1781 transport glue and the core ADAU1781 component driver.

## APIs, Types, and Functions
Declares `adau1781_probe()` with device, regmap, ADAU17x1 type, and optional mode-switch callback arguments, plus `extern const struct regmap_config adau1781_regmap_config`.

## Control Flow, State, and Persistence
The header has no runtime state. It ensures I2C/SPI bus drivers pass a typed codec selection and a preconfigured regmap into the common implementation.

## Dependencies and Integration
Includes `linux/regmap.h` and `adau17x1.h`, tying the file to the shared ADAU17x1 enum and helpers. Used directly by `adau1781-i2c.c`, `adau1781-spi.c`, and `adau1781.c`.

## Risks and Test Signals
Risks are limited to declaration/configuration drift or invalid type values. Build tests across I2C and SPI modules and runtime probe with each compatible string are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/adau1781.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/adau17x1.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/adau17x1.c

## Purpose
Shared ADAU1x61/ADAU1x81 ASoC support layer. It owns common controls, DAPM resources, DAI operations, PLL/sysclk programming, TDM slot routing, SigmaDSP firmware attachment and safeload, regmap readability/volatility policy, optional MCLK handling, and remove/resume cleanup.

## APIs, Types, and Functions
Exports `adau17x1_dai_ops`, `adau17x1_probe()`, `adau17x1_remove()`, `adau17x1_resume()`, `adau17x1_add_widgets()`, `adau17x1_add_routes()`, `adau17x1_set_micbias_voltage()`, and regmap helpers `adau17x1_readable_register()`, `adau17x1_volatile_register()`, and `adau17x1_precious_register()`. Key internal functions are `adau17x1_set_dai_pll()`, `adau17x1_set_dai_sysclk()`, `adau17x1_auto_pll()`, `adau17x1_hw_params()`, `adau17x1_set_dai_fmt()`, `adau17x1_set_dai_tdm_slot()`, `adau17x1_startup()`, `adau17x1_setup_firmware()`, `adau17x1_safeload()`, and DAPM callbacks for PLL and ADC fixup.

## Control Flow, State, and Persistence
Probe allocates `struct adau`, gets optional `mclk`, defaults to auto-PLL when MCLK exists, precomputes PLL registers, enables MCLK, stores regmap/type/switch callback, optionally initializes SigmaDSP firmware, and performs SPI mode switching when supplied. Stream setup chooses MCLK or PLL frequency, validates sample-rate divisors, writes converter and DSP sampling-rate registers, reloads firmware if the rate changes, and adjusts right-justified delays by sample width. TDM setup maps tx/rx masks to converter pairs and rewrites DSP serial routes when bypassing the DSP. DAPM powers the PLL by raw-writing the six-byte PLL register atomically and selecting PLL as core clock after lock delay. Firmware setup locks DAPM, preserves DSP sample-rate/run state, enables DSP, calls `sigmadsp_setup()`, then restores state. Safeload writes up to 20 bytes in 4-byte words with zero padding, target address minus one, and trigger word count.

## Dependencies and Integration
Depends on ALSA SoC core, regmap, `clk`, delay helpers, SigmaDSP, `adau-utils` PLL math, and bus glue callbacks. ADAU1761 and ADAU1781 component drivers call into this layer and reuse its DAI ops.

## Risks and Test Signals
Risks include strict PLL input range and sample-rate divisor validation, unguarded return values from several `regmap_update_bits()` calls, cache synchronization after bus mode changes, right-justified delay mistakes, TDM mask assumptions requiring adjacent stereo slot pairs, firmware pop avoidance depending on `current_samplerate`, and safeload length assumptions. Test signals are successful PLL/MCLK/sysclk transitions, TDM slot tests for stereo/TDM4/TDM8, SigmaDSP firmware load and safeload writes, resume regcache sync with SPI switch mode, DAPM PLL route toggling, and ADC SNR workaround execution during capture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/adau17x1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/adau17x1.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/adau17x1.h

## Purpose
Shared private header for the ADAU17x1 codec family.

## APIs, Types, and Functions
Defines `enum adau17x1_type`, PLL/source/clock enums, the shared `struct adau`, exported helper prototypes, `extern const struct snd_soc_dai_ops adau17x1_dai_ops`, and common register/bit definitions. `struct adau` persists sysclk, PLL frequency and six-byte PLL register image, optional MCLK, selected clock source, type, SPI mode-switch callback, DAI format, master flag, stream-to-TDM-slot mapping, DSP bypass flags, regmap, and SigmaDSP pointer.

## Control Flow, State, and Persistence
The header itself has no logic, but it defines the state that `adau17x1.c`, `adau1761.c`, and `adau1781.c` share across probe, stream setup, DAPM transitions, firmware loading, suspend/resume, and remove.

## Dependencies and Integration
Includes regmap, platform data for ADAU17x1 board options, and `sigmadsp.h`. It is the integration boundary between device-specific drivers, bus glue, and the common core.

## Risks and Test Signals
Risks include shared state fields being updated by multiple code paths without clear locking outside normal ASoC serialization, register constants being reused by devices with slightly different maps, and enum/type mismatches in bus match data. Build coverage and stream tests across ADAU1361, ADAU1761, ADAU1381, and ADAU1781 are the meaningful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/adau17x1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/adau1977-i2c.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/adau1977-i2c.c

## Purpose
I2C bus wrapper for ADAU1977/ADAU1978/ADAU1979 ADC codecs.

## APIs, Types, and Functions
`adau1977_i2c_probe()` copies `adau1977_regmap_config`, sets 8-bit register and value widths for I2C, creates an I2C regmap, and calls `adau1977_probe()` with match data and no mode-switch callback. The I2C ID table maps `adau1977` to `ADAU1977` and both `adau1978` and `adau1979` entries to `ADAU1978` in this source.

## Control Flow, State, and Persistence
All persistent state is in `struct adau1977` allocated by the common probe. This file only performs transport setup and driver registration through `module_i2c_driver()`.

## Dependencies and Integration
Depends on Linux I2C, regmap, ASoC headers, and `adau1977.h`. Integrates with legacy I2C device IDs; this file does not define OF match data, so OF-only systems rely on modalias/I2C board registration elsewhere.

## Risks and Test Signals
Risks include the `adau1979` ID using `ADAU1978` instead of `ADAU1979`, lack of OF table in the I2C wrapper, and match-data dependence. Test signals are probe with each I2C ID, correct component type behavior such as MICBIAS only for ADAU1977, and successful regmap reads/writes with 8-bit addressing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/adau1977-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/adau1977-spi.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/adau1977-spi.c

## Purpose
SPI bus wrapper for ADAU1977/ADAU1978/ADAU1979 codecs.

## APIs, Types, and Functions
`adau1977_spi_switch_mode()` performs three dummy SPI reads to enter SPI mode. `adau1977_spi_probe()` gets the SPI device ID, copies the common regmap config, uses 8-bit values, 16-bit register framing, and `read_flag_mask = 0x1`, then calls `adau1977_probe()` with the mode switch callback. SPI and OF match tables cover `adi,adau1977`, `adi,adau1978`, and `adi,adau1979`.

## Control Flow, State, and Persistence
Probe only initializes the bus-level regmap and passes type and callback to the shared driver. The callback is stored in `struct adau1977` and used again during power-enable after reset/regcache state changes.

## Dependencies and Integration
Depends on SPI, OF, regmap, ASoC, and the ADAU1977 shared implementation. It integrates with board descriptions using SPI modalias or OF compatible strings.

## Risks and Test Signals
Risks include unchecked dummy-read failures, `adau1979` mapped to `ADAU1978` in the SPI ID table, and OF entries not carrying `.data` even though `spi_get_device_id()` is used for type. Test signals are successful SPI-mode register access, power-cycle re-entry into SPI mode, and correct DAI sysclk/TDM behavior after registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/adau1977-spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/adau1977.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/adau1977.c

## Purpose
ASoC capture-only driver for ADAU1977/ADAU1978/ADAU1979 multichannel ADCs, including regulator/reset sequencing, micbias configuration, SAI/TDM programming, clock/rate constraints, gain and filter controls, and regmap caching.

## APIs, Types, and Functions
Exports `adau1977_probe()` and `adau1977_regmap_config`. `struct adau1977` stores regmap, format flags, sysclk source/frequency, reset GPIO, regulator handles, rate constraints, switch callback, maximum provider sample rate, slot width, enabled state, and clock-provider mode. Important functions are `adau1977_power_enable()`, `adau1977_power_disable()`, `adau1977_reset()`, `adau1977_set_bias_level()`, `adau1977_set_sysclk()`, `adau1977_hw_params()`, `adau1977_set_dai_fmt()`, `adau1977_set_tdm_slot()`, `adau1977_startup()`, `adau1977_mute()`, `adau1977_set_tristate()`, and `adau1977_setup_micbias()`.

## Control Flow, State, and Persistence
Probe allocates state, requests AVDD and optional DVDD, gets optional reset GPIO, powers the chip, optionally configures ADAU1977 MICBIAS from `adi,micbias`, clears block power bits while preserving internal LDO behavior when DVDD is absent, powers the chip back off, and registers the component. Bias STANDBY powers regulators, releases reset, exits regcache-only mode, switches SPI mode if needed, issues software reset, powers up, syncs cache, and manually handles PLL register sync if reset left it at default. Bias OFF powers down, marks cache dirty, asserts reset, enters cache-only mode, and disables regulators. Sysclk setup validates MCLK or LRCLK sources and builds a rate constraint mask. TDM setup maps RX slots to channel-map registers and limits bitclock in clock-provider mode. `hw_params()` computes FS and MCS from rate/sysclk and applies format-specific width handling.

## Dependencies and Integration
Depends on ASoC, regmap, regulator, GPIO descriptor, device properties, dt-binding `adi,adau1977.h`, and bus glue for I2C/SPI framing. Machine drivers call component `set_sysclk`, DAI `set_fmt`, and `set_tdm_slot` to select clocking and slot mapping.

## Risks and Test Signals
Risks include the apparent duplicate declaration line in `adau1977_set_dai_fmt()` in this source snapshot, unreachable duplicate `return -EINVAL` in lookup code, `slot[1..3]` use after fewer than four slots are provided, rate table typo `172400` instead of `176400`, fragile PLL/cache reset handling, and variant ID mapping in bus files. Test signals are regulator/reset sequencing with and without DVDD, all MCLK rate-constraint masks, LRCLK clock source mode, TDM2/4/8/16 slot mapping, right-justified 16/24-bit streams, mute/tristate controls, and volatile status/clip register reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/adau1977.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/adau1977.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/adau1977.h

## Purpose
Internal public contract for ADAU1977-family bus wrappers and component code.

## APIs, Types, and Functions
Defines `enum adau1977_type` with ADAU1977/1978/1979, declares `adau1977_probe()`, declares `adau1977_regmap_config`, and defines component sysclk identifiers: `ADAU1977_SYSCLK` plus `ADAU1977_SYSCLK_SRC_MCLK` and `ADAU1977_SYSCLK_SRC_LRCLK`.

## Control Flow, State, and Persistence
No runtime state is held in the header. It determines what variant and clock source values machine drivers and bus wrappers can pass into `adau1977.c`.

## Dependencies and Integration
Includes `linux/regmap.h` and forward declares `struct device`. Used by both I2C/SPI glue and the main codec implementation.

## Risks and Test Signals
Risks are enum mismatch between bus ID tables and runtime type-specific behavior. Build coverage plus probe tests for all three chip names are the primary validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/adau1977.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/adau7002.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/adau7002.c

## Purpose
Minimal platform ASoC driver for the ADAU7002 stereo PDM-to-I2S/TDM converter.

## APIs, Types, and Functions
Defines `struct adau7002_priv` with a `wakeup_delay`. `adau7002_component_probe()` allocates it and reads `wakeup-delay-ms`. `adau7002_aif_event()` sleeps after AIF power-up when a wake delay is configured. The component defines an AIF output widget, PDM input, IOVDD regulator supply, routes to capture, and a capture-only DAI with two channels, 8-96 kHz rates, broad PCM formats, and 20 significant bits.

## Control Flow, State, and Persistence
Platform probe registers the component and DAI. Component probe stores private wakeup-delay state in the component. DAPM POST_PMU on the AIF delays capture startup; POST_PMD is included in the event mask but does not currently perform work. There is no register map or suspend state.

## Dependencies and Integration
Depends on ASoC, DAPM regulator supply handling, OF and ACPI matching. Matches `adi,adau7002` and ACPI ID `ADAU7002`.

## Risks and Test Signals
Risks are limited configuration surface, wakeup delay only being applied after AIF power-up, no explicit format negotiation beyond DAI capabilities, and reliance on board-level clocks. Test signals are component probe, regulator supply activation through DAPM, correct delay from device property, and capture audio with 20-bit PDM conversion over the board-selected serial format.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/adau7002.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/adau7118-hw.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/adau7118-hw.c

## Purpose
Platform wrapper for ADAU7118 standalone hardware mode, where serial configuration is controlled by pins rather than I2C registers.

## APIs, Types, and Functions
`adau7118_probe_hw()` calls `adau7118_probe(&pdev->dev, NULL, true)`. The file declares OF and platform ID matches for `adau7118` and registers a `platform_driver`.

## Control Flow, State, and Persistence
All state lives in the shared `adau7118.c` implementation. Passing `hw_mode = true` suppresses regmap usage and selects the simpler hardware-mode DAPM graph and no DAI ops assignment.

## Dependencies and Integration
Depends on platform-device infrastructure, OF matching, and the common ADAU7118 header. Integrates with device tree nodes using `adi,adau7118` when the chip is strap-configured.

## Risks and Test Signals
Risks include sharing the same OF compatible with the I2C driver and therefore depending on bus topology to bind the intended wrapper, and limited software observability in hardware mode. Test signals are platform probe, regulator enable/disable through the shared bias path, and capture path routing from PDM inputs to a single AIF output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/adau7118-hw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/adau7118-i2c.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/adau7118-i2c.c

## Purpose
I2C wrapper and regmap description for software-controlled ADAU7118 PDM-to-I2S/TDM converters.

## APIs, Types, and Functions
Defines `adau7118_reg_defaults` for vendor/device/revision, enables, decimation/clock-map, HPF, serial-port controls, eight channel slot registers, drive strength, and reset. `adau7118_volatile()` marks the reset register volatile. `adau7118_probe_i2c()` creates an 8-bit I2C regmap and calls `adau7118_probe(..., false)`. OF and I2C ID tables register the `adau7118` I2C driver.

## Control Flow, State, and Persistence
Probe initializes regmap and transfers all persistent behavior to `adau7118.c`. Regcache defaults are used while the core driver powers regulators off and sets cache-only mode.

## Dependencies and Integration
Depends on I2C, regmap, and the common header register definitions. Integrates with OF compatible `adi,adau7118`.

## Risks and Test Signals
Risks include reset register volatility, shared compatible string with hardware-mode platform wrapper, and default slot map correctness for board channel order. Test signals are successful I2C regmap init, soft reset in common probe, device-property decimation/clock-map programming, and regcache sync after regulator power-up.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/adau7118-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/adau7118.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/adau7118.c

## Purpose
Shared ASoC driver for ADAU7118 eight-channel PDM-to-I2S/TDM converters, supporting software-controlled I2C mode and standalone hardware mode.

## APIs, Types, and Functions
Exports `adau7118_probe()`. `struct adau7118_data` stores regmap, device, IOVDD/DVDD regulators, slot width/count, hardware-mode flag, and right-justified state. Important functions are `adau7118_set_channel_map()`, `adau7118_set_fmt()`, `adau7118_set_tristate()`, `adau7118_set_tdm_slot()`, `adau7118_hw_params()`, `adau7118_set_bias_level()`, `adau7118_component_probe()`, `adau7118_regulator_setup()`, and `adau7118_parset_dt()`. The DAI supports capture-only 1-8 channel continuous rates from 4 kHz to 192 kHz with up to 24 significant bits.

## Control Flow, State, and Persistence
Probe allocates state, stores `hw_mode`, optionally assigns regmap and DAI ops, performs a full soft reset in software mode, parses `adi,decimation-ratio` and `adi,pdm-clk-map`, sets regulators, marks regcache dirty/cache-only while off, and registers the component. Component probe initializes regmap and adds software widgets/routes for PDM switches, PDM clocks, and eight AIF outputs, or hardware-mode widgets/routes for a single AIF output. Bias STANDBY enables IOVDD then DVDD, exits cache-only and syncs cache in software mode. Bias OFF disables regulators and marks cache dirty/cache-only. Format setup programs I2S/left-justified/DSP_A data format immediately; right-justified is deferred until `hw_params()` can calculate delay from slot width and data width.

## Dependencies and Integration
Depends on ASoC, regmap, regulator consumers, device properties, and bitfield macros. I2C and platform wrappers call into this file for software or hardware mode.

## Risks and Test Signals
Risks include no validation of `adi,pdm-clk-map` values, no use of `tx_mask`/`rx_mask` in `set_tdm_slot()`, right-justified format state not reset when a later format is non-right-justified, global mutation of the static `adau7118_dai.ops`, and property parser spelling `parset`. Test signals are regulator sequencing, cache sync after OFF/STANDBY, decimation ratios 16/32/64, PDM clock mapping, slot widths 16/24/32, right-justified delay cases 8/12/16 bits, channel-map writes for eight outputs, and hardware-mode operation without regmap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/adau7118.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/adau7118.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/adau7118.h

## Purpose
Shared register and probe contract for ADAU7118 I2C and hardware-mode wrappers.

## APIs, Types, and Functions
Defines the 8-bit register map from vendor/device IDs through enables, decimation/clock map, HPF, serial-port controls, channel slot registers `ADAU7118_REG_SPT_CX(num)`, drive strength, and reset. Declares `adau7118_probe(struct device *dev, struct regmap *map, bool hw_mode)`.

## Control Flow, State, and Persistence
The header contains no runtime logic. It controls the address vocabulary used by the regmap wrapper and shared component driver.

## Dependencies and Integration
Forward declares `struct regmap` and `struct device`; included by `adau7118.c`, `adau7118-i2c.c`, and `adau7118-hw.c`.

## Risks and Test Signals
Risk is register macro drift, especially the computed channel slot macro used for eight adjacent registers. Build coverage and regmap default table coverage validate the interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/adau7118.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/adav801.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/adav801.c

## Purpose
SPI bus wrapper for the ADAV801 codec using the shared ADAV80x core.

## APIs, Types, and Functions
Defines SPI ID `adav801`, `adav80x_spi_probe()`, and a `spi_driver`. Probe copies `adav80x_regmap_config`, sets `read_flag_mask = 0x01`, initializes an SPI regmap, and delegates to `adav80x_bus_probe()`.

## Control Flow, State, and Persistence
This file holds no persistent codec state. The shared `struct adav80x` is allocated by `adav80x_bus_probe()` and registered with two DAIs.

## Dependencies and Integration
Depends on SPI, regmap, ASoC, and `adav80x.h`. It integrates with SPI modalias `adav801`.

## Risks and Test Signals
Risks include SPI framing/read-flag mismatches and lack of OF matching in this wrapper. Test signals are successful regmap reads/writes over SPI, registration of both ADAV80x DAIs, and playback/capture format setup through the shared implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/adav801.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/adav803.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/adav803.c

## Purpose
I2C bus wrapper for the ADAV803 codec using shared ADAV80x logic.

## APIs, Types, and Functions
Defines I2C ID `adav803`, `adav803_probe()`, and an `i2c_driver`. Probe initializes an I2C regmap using `adav80x_regmap_config` and calls `adav80x_bus_probe()`.

## Control Flow, State, and Persistence
All state is owned by `adav80x.c`; this file only adapts I2C transport to the common component.

## Dependencies and Integration
Depends on I2C, regmap, ASoC, and `adav80x.h`. It binds by I2C modalias rather than an OF table in this source.

## Risks and Test Signals
Risks are minimal but include no OF match table and any mismatch between the shared regmap pad/register layout and I2C bus framing. Test signals are I2C probe, regmap access, and shared component registration with two audio interfaces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/adav803.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/adav80x.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/adav80x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/adav80x.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/adav80x.h

## Purpose
Internal header for ADAV801/ADAV803 shared bus/component integration.

## APIs, Types, and Functions
Declares `adav80x_regmap_config` and `adav80x_bus_probe()`. Defines PLL source enum values (`XIN`, `XTAL`, `MCLKI`), PLL identifiers `ADAV80X_PLL1/PLL2`, input clock selectors (`XIN`, `MCLKI`, `PLL1`, `PLL2`, `XTAL`), and SYSCLK output IDs (`SYSCLK1..3`).

## Control Flow, State, and Persistence
No runtime state is stored here. The enum values are written into ADAV80x internal clock routing fields by `adav80x_set_sysclk()` and `adav80x_set_pll()`.

## Dependencies and Integration
Includes regmap and forward declares `struct device`. Used by SPI/I2C wrappers and `adav80x.c`.

## Risks and Test Signals
Risks include overlapping enum values where `ADAV80X_CLK_XTAL` and `ADAV80X_CLK_SYSCLK1` both use 6 but are disambiguated by clock direction. Validation comes from machine-driver sysclk/PLL calls and build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/adav80x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ads117x.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/ads117x.c

## Purpose
Simple platform ASoC codec driver for TI ADS1174/ADS1178 ADCs with no software register control.

## APIs, Types, and Functions
Defines DAPM inputs `Input1` through `Input8`, routes all inputs to `Capture`, a capture-only DAI named `ads117x-hifi`, and `ads117x_probe()` which registers the component. The DAI advertises 1-32 capture channels, 8-48 kHz rates, and S16_LE format.

## Control Flow, State, and Persistence
There is no private state, regmap, power sequencing, or DAI ops. Platform probe registers static DAPM and DAI descriptors. Runtime behavior is defined by the machine driver and external hardware wiring.

## Dependencies and Integration
Depends on ASoC and platform/OF infrastructure. Matches `ti,ads1174` and `ti,ads1178`.

## Risks and Test Signals
Risks include a very broad 32-channel maximum despite only eight DAPM inputs, no format/clock validation, and no power supply controls. Test signals are successful platform probe, DAPM route visibility, and board-level capture verification with the expected channel count and S16_LE data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ads117x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ak4104.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/ak4104.c

## Purpose
ASoC SPI driver for the AK4104 S/PDIF transmitter, handling register verification, VDD regulator power, DAI format/rate setup, channel status bytes, and transmitter enable.

## APIs, Types, and Functions
`struct ak4104_private` stores regmap and regulator. Important functions include `ak4104_spi_probe()`, `ak4104_probe()`, `ak4104_remove()`, optional PM suspend/resume, `ak4104_set_dai_fmt()`, and `ak4104_hw_params()`. The DAI is playback-only stereo, supporting common 22.05 kHz through 192 kHz rates and 16/24-bit PCM formats. Regmap uses SPI read/write flag masks and a 10-register range.

## Control Flow, State, and Persistence
SPI probe forces 8-bit words and SPI mode 0, allocates state, gets VDD, initializes regmap, optionally gets reset GPIO high, reads the reserved register expecting `0x5b` as a device-presence check, stores driver data, and registers the component. Component probe enables the regulator, sets power and reset bits, and enables TXE. Remove powers down and disables the regulator. `set_dai_fmt()` permits right-justified, left-justified, and I2S only as clock consumer. `hw_params()` writes IEC958 consumer status and sample-rate code into channel-status registers.

## Dependencies and Integration
Depends on SPI, regmap, GPIO descriptors, regulators, ASoC, and IEC958 status definitions. Matches OF compatible `asahi-kasei,ak4104` and SPI ID `ak4104`.

## Risks and Test Signals
Risks include relying on a reserved-register value as device ID, not using regmap defaults for cached power state, regulator suspend/resume not restoring register state beyond supply power, and no provider-mode support. Test signals are reserved-register probe, regulator enable/disable paths, DAI format selection, channel-status sample-rate encoding, and S/PDIF transmitter output with TXE route powered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ak4104.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ak4118.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/ak4118.c

## Purpose
ASoC I2C driver for the AK4118 S/PDIF receiver/transceiver, exposing input selection, IEC958 status controls, IRQ-driven status notifications, and serial audio format selection.

## APIs, Types, and Functions
`struct ak4118_priv` stores regmap, reset GPIO, IRQ GPIO, and component pointer. Important functions include `ak4118_i2c_probe()`, component `ak4118_probe()`/`ak4118_remove()`, `ak4118_irq_handler()`, `ak4118_set_dai_fmt()`, and provider/consumer format helpers. The component exposes DAPM inputs INRX0-INRX7, an Input Mux, IEC958 controls for parity/no-audio/PLL lock/non-PCM/sample frequency, and a capture DAI supporting 2-channel 22.05-192 kHz PCM.

## Control Flow, State, and Persistence
I2C probe allocates state, initializes regmap with no cache, gets reset and IRQ GPIOs, requests a threaded rising-edge IRQ, and registers the component. Component probe stores the component pointer, releases reset, unmasks INT1 sources, enables RX detection on all channels, and adds IEC958 controls. IRQ handler notifies ALSA controls so userspace can refresh status. Remove asserts reset. `set_dai_fmt()` chooses different DIF bit patterns depending on whether the codec is clock provider or consumer.

## Dependencies and Integration
Depends on I2C, GPIO descriptors, IRQ infrastructure, regmap, ASoC controls/DAPM, and OF match `asahi-kasei,ak4118`.

## Risks and Test Signals
Risks include no regcache, IRQ GPIO being mandatory, status controls using simple SOC_SINGLE reads without debouncing, no `hw_params()` validation, and limited serial formats in provider/consumer modes. Test signals are reset release/assert, IRQ notifications for IEC958 changes, input mux routing across eight RX pins, DIF bit programming for I2S/left/right justified modes, and capture data with real S/PDIF lock transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ak4118.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ak4375.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/ak4375.c

## Purpose
I2C ASoC playback DAC/headphone amplifier driver for AK4375/AK4375A, including regulator and PDN GPIO power sequencing, runtime PM, PLL programming from sample rate, DAC mute, volume/filter controls, and DAPM charge-pump sequencing.

## APIs, Types, and Functions
`struct ak4375_priv` stores device, regmap, PDN GPIO, AVDD/TVDD supplies, active rate, PLL divider state, and saved mute bits. Key functions are `ak4375_i2c_probe()`, `ak4375_power_on()`, `ak4375_power_off()`, runtime suspend/resume, `ak4375_hw_params()`, `ak4375_dai_set_pll()`, `ak4375_mute()`, and `ak4375_dac_event()`. Controls cover digital output volume, headphone analog volume, DAC inversion, digital volume control mode, DAC level, charge pump mode, and digital filter mode.

## Control Flow, State, and Persistence
Probe initializes regmap, gets supplies and optional PDN GPIO, powers the device, bypasses cache to read `DEVICEID`, rejects unsupported/untested IDs, enables runtime PM, and registers the component. Runtime suspend caches only and powers off; resume powers on, exits cache-only, marks dirty, and syncs regcache. `hw_params()` stores the sample rate, chooses a PLL pre-divider, selects 112.896 MHz or 122.88 MHz PLL output by rate family, and calls `snd_soc_dai_set_pll()`. PLL setup writes sample-rate and clock-mode fields separately, programs reference/feedback dividers, SRC clock source, DAC divider, and logs computed values. DAPM DAC events sequence PMPLL, charge pump, LDO and headphone charge pump with required delays.

## Dependencies and Integration
Depends on I2C, OF match data, regmap, regulators, GPIO descriptors, runtime PM, delays, and ASoC. Matches `asahi-kasei,ak4375`.

## Risks and Test Signals
Risks include returning from probe error paths after power-on without powering off in some device-ID failures, only AK4375-compatible IDs accepted despite shared register constants, PLL math relying on BCLK-derived `freq_in`, no explicit set_fmt op, and mute restore depending on previous register state. Test signals are device-ID reads, runtime PM power cycles with cache sync, playback at every advertised rate from 8 kHz to 192 kHz, PLL divider register values by rate family, DAC DAPM delay sequencing, and mute/unmute preserving selected DAC mixing bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ak4375.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ak4458.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/ak4458.c

## Purpose
I2C ASoC playback driver for AK4458 multichannel DACs and AK4497 stereo DACs. It supports PCM and DSD formats, TDM mode selection, filter/attenuation controls, runtime PM with supplies/reset/mute GPIO, and variant-specific DAPM/DAI registration.

## APIs, Types, and Functions
Defines `enum ak4458_type`, `struct ak4458_drvdata`, and `struct ak4458_priv`. Important functions include `ak4458_i2c_probe()`, `ak4458_runtime_suspend()`, `ak4458_runtime_resume()`, `ak4458_reset()`, `ak4458_hw_params()`, `ak4458_set_dai_fmt()`, `ak4458_set_dai_mute()`, `ak4458_set_tdm_slot()`, `ak4458_get_tdm_mode()`, `ak4458_rstn_control()`, and digital-filter get/set controls. AK4458 exposes four stereo DAC volume controls and widgets; AK4497 exposes one stereo DAC path and optional `dsd-path`.

## Control Flow, State, and Persistence
Probe creates regmap, gets variant match data, optional reset and mute GPIOs, optional AK4497 `dsd-path`, DVDD/AVDD supplies, registers the variant component/DAI, enables runtime PM, and leaves regcache cache-only until resume. Runtime resume enables supplies, asserts external mute if present, deasserts reset, exits cache-only, marks dirty, and syncs cache. Runtime suspend enters cache-only, asserts reset, deasserts mute GPIO, and disables supplies. `set_fmt()` accepts consumer-mode I2S, left/right justified, DSP_B, and PDM, writes DSD/PCM path bit, and toggles RSTN. `hw_params()` handles DSD bit-clock selection, PCM data interface bits based on physical/slot width and format, auto MCLK mode, TDM daisy-chain enabling when channel count exceeds variant maximum, optional AK4497 DSD path, then resets the DAC core. Muting uses attenuation transition speed from `ATS` bits to delay around digital mute and external mute GPIO changes.

## Dependencies and Integration
Depends on I2C, OF match data, runtime PM, regulator bulk APIs, reset controls, optional GPIO, regmap cache, ASoC controls/DAPM/DAIs, and constants from `ak4458.h`. Matches `asahi-kasei,ak4458` and `asahi-kasei,ak4497`.

## Risks and Test Signals
Risks include no clock-provider mode, `set_dai_mute()` dividing by `fs/1000` if mute is called before `hw_params()` initializes `fs`, DSD512 support restricted to AK4497, PDM mode represented through `SND_SOC_DAIFMT_PDM`, and runtime PM leaving hardware off until the core resumes it. Test signals are runtime PM supply/reset/cache sync, PCM widths 16/32 in I2S/LJ/RJ/DSP_B, TDM128/256/512 selection, DSD64/128/256/512 validation by variant, digital filter bit updates across three registers, mute GPIO behavior, and channel counts beyond two/four stereo DACs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ak4458.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ak4458.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/ak4458.h

## Purpose
Register and bitfield definition header for the AK4458/AK4497 DAC driver.

## APIs, Types, and Functions
Defines register addresses `AK4458_00_CONTROL1` through `AK4458_14_R4CHATT` and bit masks/shifts for digital filter bits (`SD`, `SLOW`, `SSLOW`), data-interface format (`DIF`), reset (`RSTN`), TDM mode, attenuation transition speed (`ATS`), daisy chain, DSD select, and DSD/PCM path.

## Control Flow, State, and Persistence
No runtime state is stored here. The masks are consumed by `ak4458.c` during `set_fmt()`, `hw_params()`, `set_tdm_slot()`, digital filter control writes, mute delay calculation, and reset toggling.

## Dependencies and Integration
Includes regmap for consistency with the implementation. Used only inside the codec driver family.

## Risks and Test Signals
Risks include bit definitions applying differently between AK4458 and AK4497 variants and mask definitions such as `GENMASK(0, 0)` reused for fields in different registers. Validation comes from register-level tests or hardware playback in each supported format and filter mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ak4458.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ak4535.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/ak4535.c

## Purpose
ASoC I2C driver for the AK4535 codec, covering simple stereo playback/capture, analog routing, mixer controls, bias power bits, sysclk-derived sample-rate mode, mute, and regmap caching.

## APIs, Types, and Functions
`struct ak4535_priv` stores regmap and sysclk. Key functions include `ak4535_i2c_probe()`, `ak4535_set_dai_sysclk()`, `ak4535_hw_params()`, `ak4535_set_dai_fmt()`, `ak4535_mute()`, `ak4535_set_bias_level()`, `ak4535_resume()`, and `ak4535_volatile()`. The driver defines extensive controls for ALC, mono/headphone/mic selection, bass, capture/playback volumes, sidetone and bypass volumes, plus DAPM widgets/routes for stereo/mono/input mixers, DAC, ADC, speaker, headphone, line, mono, mic bias, and inputs.

## Control Flow, State, and Persistence
I2C probe allocates private state, creates regmap with defaults and volatile status register, stores client data, and registers the component and DAI. Machine driver `set_sysclk()` stores the input clock. `hw_params()` computes `fs = sysclk / rate` and writes MODE2 bits for 256/512/1024fs cases. `set_fmt()` accepts I2S or left-justified, always requests 32fs BCLK for power saving, and writes MODE1. Mute toggles DAC bit 0x20. Bias ON unmutes, PREPARE mutes, STANDBY powers selected PM bits, and OFF clears power management. Resume syncs regcache.

## Dependencies and Integration
Depends on I2C, regmap, ASoC, TLV/initval headers, and register definitions from `ak4535.h`. Binds by I2C ID `ak4535`.

## Risks and Test Signals
Risks include no OF match table, limited format/rate support, `hw_params()` silently ignoring unsupported `fs` ratios instead of returning error, no regulator/reset handling, and legacy control naming. Test signals are I2C regmap initialization, DAPM route activation across all analog outputs, sysclk/rate combinations for 256/512/1024fs, I2S and left-justified mode writes, bias power transitions, mute behavior, and regcache sync after resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ak4535.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ak4535.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/ak4535.h

## Purpose
Register address header for the AK4535 codec driver.

## APIs, Types, and Functions
Defines register constants from `AK4535_PM1` through `AK4535_STATUS` for power management, signal routing, modes, DAC, mic, timers, ALC, PGA, left/right attenuation, volume, and status.

## Control Flow, State, and Persistence
The header has no behavior or state. It provides the register namespace used by `ak4535.c` regmap defaults, controls, DAPM widgets, DAI operations, bias transitions, and volatility checks.

## Dependencies and Integration
It is included only by `ak4535.c` in this subset and has no external dependencies.

## Risks and Test Signals
Risks are limited to incorrect address constants affecting every control path. Build coverage and simple register write/read validation through the codec driver are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ak4535.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ak4554.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/ak4554.c

## Purpose
Very small platform ASoC driver for the registerless AK4554 stereo ADC/DAC.

## APIs, Types, and Functions
Defines DAPM inputs `AINL/AINR`, outputs `AOUTL/AOUTR`, routes capture/playback to those pins, and a single DAI `ak4554-hifi` with stereo playback and capture, 8-48 kHz rates, S16_LE format, and symmetric rate. `ak4554_soc_probe()` registers the component and DAI.

## Control Flow, State, and Persistence
There is no private state, register map, DAI ops, regulator handling, or suspend logic. Platform probe registers static descriptors and the machine driver is responsible for fixed serial format and clocks.

## Dependencies and Integration
Depends only on platform driver infrastructure through module registration and ASoC. Matches OF compatible `asahi-kasei,ak4554`.

## Risks and Test Signals
The source comment warns that playback uses right-justified format and capture uses left-justified format on the same clocks, but the driver has no `set_fmt()` op to enforce or validate that. Test signals are platform probe, symmetric-rate enforcement, DAPM route visibility, and board-level full-duplex audio with CPU DAIs configured exactly as documented.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ak4554.c -->
