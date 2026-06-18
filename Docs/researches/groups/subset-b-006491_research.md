# subset-b-006491 Research

Grouped source research for Wolfson/Cirrus ALSA SoC codec drivers and private codec register headers. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8904.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm8904.c

## Purpose

`sources/distributed-fs/ceph-client/sound/soc/codecs/wm8904.c` is the ALSA SoC codec driver for WM8904-family I2C audio codecs, with variant handling for WM8904 and WM8912 and an I2C alias for WM8918. It registers one `wm8904-hifi` DAI, manages codec supplies and MCLK, exposes mixer controls, builds a DAPM graph for ADC/DAC/capture/playback paths, configures FLL/sysclk/BCLK/LRCLK, applies board-provided DRC and ReTune Mobile EQ profiles, and implements bias-level power sequencing. The source was read as a complete 2644-line file for this report.

## Important APIs, Types, and Functions

The central state type is `struct wm8904_priv`, which stores `regmap`, `mclk`, `devtype`, regulator bulk data, platform data, current deemphasis/DRC/ReTune selections, FLL state, clocking state, TDM settings, current sample rate, and cached DC-servo offsets for four output channels. `enum wm8904_type` distinguishes WM8904 from WM8912.

Register integration is through `wm8904_reg_defaults`, `wm8904_volatile_register()`, `wm8904_readable_register()`, and `wm8904_regmap`, using 8-bit register addresses, 16-bit values, and `REGCACHE_MAPLE`. Codec registration uses `soc_component_dev_wm8904`, `wm8904_dai_ops`, `wm8904_dai`, `wm8904_i2c_probe()`, and `wm8904_i2c_driver`.

Clock and stream APIs are `wm8904_set_sysclk()`, `wm8904_set_fll()`, `fll_factors()`, `wm8904_configure_clocking()`, `wm8904_hw_params()`, `wm8904_set_fmt()`, `wm8904_set_tdm_slot()`, and `wm8904_mute()`. Runtime controls include `wm8904_set_deemph()`, `wm8904_put_deemph()`, `wm8904_set_drc()`, `wm8904_put_drc_enum()`, `wm8904_set_retune_mobile()`, and `wm8904_put_retune_mobile_enum()`. DAPM/event behavior is concentrated in `cp_event()`, `sysclk_event()`, `out_pga_event()`, `wm8904_add_widgets()`, `wm8904_handle_dmic_pdata()`, and `wm8904_handle_pdata()`.

Device-tree/platform-data parsing is handled by `wm8904_set_pdata_from_of()`, `wm8904_parse_drc_cfg_from_of()`, `wm8904_parse_retune_cfg_from_of()`, and the shared `wm8904_read_cfg_reg_arr()` helper. The driver consumes platform structures from `include/sound/wm8904.h`, including DRC, ReTune Mobile, GPIO, mic-bias, and DMIC pin routing data.

## Control Flow

Probe allocates private state, obtains an `mclk` clock, initializes regmap, selects the device type via match data, parses OF platform data when present, requests the five supplies (`DCVDD`, `DBVDD`, `AVDD`, `CPVDD`, `MICVDD`), powers the codec long enough to read and validate the device ID, reads revision, resets the device, adjusts default register policy, applies GPIO and mic-bias platform configuration, reads the ADC test register into cache, then switches the regmap to cache-only and powers supplies off before registering the component.

Component probe validates the variant, removes capture capability for WM8912 by zeroing the DAI capture descriptor, installs the appropriate control and DAPM graph, then applies platform-dependent DRC/ReTune/DMIC routing. WM8904 gets ADC, DAC, sidetone, bypass, headphone, lineout, and capture widgets. WM8912 only gets DAC/output routing and no capture path. DMIC platform flags decide whether capture PGAs connect directly to ADCs, route through ADC/DMIC muxes, or add a DMIC1/DMIC2 mux.

PCM setup begins in `wm8904_hw_params()`: the driver records the sample rate, computes target BCLK from either normal PCM params or TDM slot settings, encodes sample width, calls `wm8904_configure_clocking()`, selects the closest `CLK_SYS_RATE`, sample-rate code, BCLK divider, and LRCLK rate, writes the AIF and clock registers, then refreshes ReTune Mobile and DAC deemphasis for the new rate. DAI format setup maps ALSA master/slave, I2S/left/right/DSP format, and inversion flags into `AUDIO_INTERFACE_1` and `AUDIO_INTERFACE_3`.

FLL control computes reference dividers, FLL fratio, output divider, integer N, and fractional K, then gates SYSCLK and the FLL while reprogramming. `WM8904_CLK_AUTO` compares desired rate with the framework-provided MCLK and uses the FLL when MCLK does not match. DAPM starts the FLL only when the `SYSCLK` supply is needed, and stops it on power-down.

Output power-up is event-driven. `out_pga_event()` powers the relevant headphone or lineout PGAs and amplifiers as stereo pairs, starts or restores DC-servo calibration, waits for completion with bounded sleeps, unshorts outputs after power-up, and caches DC-servo offsets before shutdown. Bias transitions enable supplies and MCLK only when moving out of OFF, sync regcache, ramp VMID, lower current in standby, and reset/cache/disable regulators and MCLK on OFF.

## State and Persistence Behavior

The driver persists no file-backed data. Runtime state lives in `wm8904_priv`, ALSA controls, DAPM state, hardware registers, and regcache. Regcache is deliberately made cache-only while powered off; OFF marks cache dirty after a software reset so the next STANDBY transition replays software-visible state. DRC and ReTune controls retain selected indices in private state, and their register arrays are either platform-provided or devm-allocated from OF properties. ReTune selection is name-based and sample-rate-sensitive, so changing `fs` reselects the nearest rate variant for the active profile.

DC-servo offsets are cached in `dcs_state[]` after output shutdown and restored on later output power-up, reducing calibration latency. These cached values are volatile driver state only; they disappear on driver unload or reboot and are invalidated only by driver logic, not by external analog changes.

## Dependencies and Integration Points

The driver depends on Linux I2C, clocks, regulators, regmap, PM, delays, ALSA core/PCM/ASoC/TLV helpers, private `wm8904.h`, and public `<sound/wm8904.h>` platform data. External machine drivers interact through ASoC DAI callbacks, DAPM route activation, mixer controls, and clock/FLL APIs. Device-tree integration uses compatibles `wlf,wm8904` and `wlf,wm8912`, plus properties for DMIC pin reuse, GPIO/mic-bias arrays, and DRC/ReTune profile arrays.

Hardware dependencies are strict: supplies must be named as expected, `mclk` must exist, the ID register must read `0x8904`, and board routing must match the DAPM topology and DMIC flags. The public DAI supports stereo playback and capture for WM8904, stereo playback for WM8912, rates 8 kHz to 96 kHz, and S16/S20_3LE/S24/S32 formats.

## Risks and Edge Cases

`wm8904_dai` is a static global that is mutated in WM8912 probe by clearing its capture descriptor. If multiple variants could be probed in one kernel image, this shared mutation can affect subsequent instances. `wm8904_put_retune_mobile_enum()` validates against `pdata->num_retune_mobile_cfgs` rather than the unique-text count, while the enum stores unique names; this works for many configurations but is a mismatch to watch. `wm8904_set_drc()` assumes valid platform data when the DRC enum exists.

Clock selection uses nearest table entries and may produce a BCLK different from the original target; machine drivers should verify the selected clocks on unusual MCLK or TDM configurations. The BCLK divider table contains duplicate/divergent entries, so regression tests around boundary rates are important. FLL free-running mode uses a forced 12 MHz path and hidden test-key register access. Output pop/click behavior depends on DAPM event ordering, DC-servo completion bits, and the cached offset path; timeout handling warns but still proceeds to enable the output stage.

OF profile parsing requires parallel property arrays with exact lengths and correct 16-bit register data. GPIO defaults use `0xffff` as "do not touch"; any board data that intends to write all ones or mismatched property width should be checked carefully.

## Test Signals

Useful signals include successful module build with ASoC enabled, I2C probe logs showing ID `0x8904` and revision, clean regulator and clock enable/disable traces, `regmap` cache sync without errors after OFF-to-STANDBY, and `aplay`/`arecord` coverage for all supported sample widths and key rates. Clock tests should cover direct MCLK, AUTO-to-FLL, explicit FLL from MCLK/BCLK/LRCLK, TDM slots 2 and 4, and unsupported formats returning `-EINVAL`. DAPM tests should exercise headphone, lineout, bypass, capture, sidetone, and DMIC route combinations, checking DC-servo ready/timeout logs. Control tests should toggle DAC mute, deemphasis, ADC OSR, DRC mode, ReTune Mobile EQ mode, EQ enable, and volume VU/ZC behavior. Device-tree tests should cover absent optional properties, invalid profile arrays, both DMIC pins, and WM8912 no-capture registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8904.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8904.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm8904.h

## Purpose

`sources/distributed-fs/ceph-client/sound/soc/codecs/wm8904.h` is the private register definition header for the WM8904 ASoC codec driver. It defines driver-facing clock and FLL IDs, the codec register address map, register-count limits, and a large set of bit masks, shifts, and widths for all fields used by `wm8904.c`. The source was read as a complete 1590-line file for this report.

## Important APIs, Types, and Functions

This header has no functions or types. Its important API is the macro namespace consumed by `wm8904.c`: clock IDs (`WM8904_CLK_AUTO`, `WM8904_CLK_MCLK`, `WM8904_CLK_FLL`), FLL reference IDs (`WM8904_FLL_MCLK`, `WM8904_FLL_BCLK`, `WM8904_FLL_LRCLK`, `WM8904_FLL_FREE_RUNNING`), register addresses from `WM8904_SW_RESET_AND_ID` through `WM8904_FLL_NCO_TEST_1`, `WM8904_REGISTER_COUNT`, and `WM8904_MAX_REGISTER`.

The bitfield macros cover bias/VMID, mic bias and detection, ADC/DAC power, clock rates, audio interface format/TDM/BCLK/LRCLK, digital volumes and deemphasis, digital microphone muxing, DRC, analog input mux/gain, headphone/lineout volume and zero-cross, DC-servo enable/trigger/readback/DAC restore, output stage shorting and staged enables, charge pump/Class W, write sequencer, FLL N/K/fratio/outdiv/source/refdiv, GPIOs, interrupts, EQ coefficients, test-key access, ADC test bits, output bias, and FLL NCO test controls.

## Control Flow

There is no executable control flow in the header. It drives control flow indirectly by giving `wm8904.c` named constants for switch statements, readable/volatile register filters, regmap defaults, DAPM register bindings, DAI format mapping, FLL programming, DC-servo calibration, and OF/platform register writes.

## State and Persistence Behavior

The header owns no storage. Its macros define the layout of state stored in WM8904 hardware registers and mirrored in `REGCACHE_MAPLE`. The persistence behavior is therefore inherited from the driver: writes are cached while the chip is powered off, restored on regcache sync, and reset to defaults when the software reset register is written.

## Dependencies and Integration Points

The header is included by `wm8904.c` after public `<sound/wm8904.h>`. It is private to the codec implementation and should stay synchronized with the datasheet and the driver's regmap readable/volatile/default tables. Public board-facing data such as DRC profile sizes, GPIO array sizes, mic-bias settings, and DMIC flags live in `include/sound/wm8904.h`, not this private file.

## Risks and Edge Cases

Because the macros encode hardware ABI, errors in masks, shifts, register addresses, or duplicate names can silently program the wrong analog or clocking bit. Several fields share generic names such as volume-update bits across left/right registers, so users must apply them to the correct register context. Test-key and ADC-test fields are especially sensitive because they touch undocumented or special-purpose controls. Header changes must be audited together with `wm8904_readable_register()`, `wm8904_volatile_register()`, `wm8904_reg_defaults`, DAPM widgets, and clocking code.

## Test Signals

Compile coverage is the first signal, since almost every constant is referenced through C macros. Runtime signals include successful regmap reads/writes at expected addresses, stable DAPM route power sequencing, correct FLL lock/clock behavior, and mixer controls manipulating expected bits as observed through regmap debugfs or bus traces. Any header update should be paired with hardware smoke tests for bias, playback/capture, FLL, output power-up/down, DC-servo, DRC/EQ, GPIO/interrupt, and DMIC paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8904.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8940.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm8940.c

## Purpose

`sources/distributed-fs/ceph-client/sound/soc/codecs/wm8940.c` is the ALSA SoC codec driver for the WM8940 mono/stereo-capable codec over I2C. It registers a `wm8940-hifi` DAI with playback and capture, exposes mixer/ALC/limiter/filter/volume controls, defines DAPM widgets and routes for speaker, mono, auxiliary, mic, boost, ADC, and DAC paths, validates the chip ID, and configures interface format, sample width, sample-rate control, MCLK divisors, and the optional PLL. The source was read as a complete 878-line file for this report.

## Important APIs, Types, and Functions

`struct wm8940_priv` stores the configured MCLK rate, current sample rate, and regmap pointer. Register policy is described by `wm8940_reg_defaults`, `wm8940_readable_register()`, `wm8940_volatile_register()`, and `wm8940_regmap`. The component driver is `soc_component_dev_wm8940`, with controls in `wm8940_snd_controls`, DAPM widgets in `wm8940_dapm_widgets`, and routes in `wm8940_dapm_routes`.

DAI callbacks are `wm8940_i2s_hw_params()`, `wm8940_set_dai_sysclk()`, `wm8940_mute()`, `wm8940_set_dai_fmt()`, `wm8940_set_dai_clkdiv()`, and `wm8940_set_dai_pll()`. Clock helpers include `pll_factors()`, `wm8940_get_mclkdiv()`, and `wm8940_update_clocks()`. Power sequencing is handled by `wm8940_set_bias_level()`, while `wm8940_probe()` checks the chip ID, resets the part, forces standby bias, writes initial VMID settings, and applies the optional `wm8940_setup_data.vroi` platform setting.

## Control Flow

I2C probe allocates private state, initializes an 8-bit-address/16-bit-value regmap, stores client data, and registers the ASoC component and DAI. Component probe reads `WM8940_SOFTRESET` as the chip ID and requires `WM8940_CHIP_ID`, writes software reset, moves DAPM to standby, writes `POWER1`, and optionally applies board VROI output resistance.

During DAI format setup, the driver programs master/slave mode in `WM8940_CLOCK`, serial format in `WM8940_IFACE`, and BCLK/LRCLK inversion bits. During `hw_params`, it records `fs`, calls `wm8940_update_clocks()`, sets stereo capture routing for two-channel capture, maps sample rates to `ADDCNTRL`, maps 8-bit audio into companding control and 16/20/24/32-bit widths into interface word-length bits, and writes the changed registers.

Clock update is demand-driven by either sysclk setup or PCM params. If MCLK divides cleanly to 256 * fs, the driver uses MCLK directly. Otherwise it selects 22.5792 MHz for 44.1 kHz-family rates or 24.576 MHz for 8/48 kHz-family rates, computes PLL factors around the codec's preferred high-frequency operating range, enables PLL output as codec clock, and writes the MCLK divider. `wm8940_set_dai_pll()` can also be called directly and programs PLLN/PLLK registers after disabling the PLL.

Bias transitions keep buffer/bias bits set for ON/PREPARE/STANDBY, choose VMID resistance according to level, enable thermal shutdown in ON, sync regcache when leaving OFF, and clear active bias bits in OFF.

## State and Persistence Behavior

There is no file persistence. Regmap cache stores register state across suspend/bias-off operation. `mclk` and `fs` in private state determine later clock recalculation; if either is zero, clock update is skipped. The PLL helper writes to a file-scope static `pll_div` scratch structure, so PLL factor calculations are global to the module rather than per device, although normally serialized through codec setup paths.

## Dependencies and Integration Points

The driver depends on Linux I2C/regmap/ASoC/TLV/delay infrastructure and private `wm8940.h`. Board integration is through the I2C ID `wm8940`, OF compatible `wlf,wm8940`, DAI operations used by machine drivers, and optional legacy platform data `struct wm8940_setup_data` for VROI. The exposed DAI supports playback and capture, one or two channels, rates 8 kHz to 48 kHz, and S8/S16/S20_3LE/S24/S32 formats. DAPM exposes physical inputs `MICN`, `MICP`, `AUX` and outputs `MONOOUT`, `SPKOUTP`, and `SPKOUTN`.

## Risks and Edge Cases

The file itself documents unsupported features: notch filter control, AUX mode selection, current gain readout with ALC, GPIO use, fast VMID discharge, soft start, DLR/ALR swaps, and digital sidetone. `wm8940_set_dai_fmt()` lacks a final default error for unknown serial formats and inversion values in some switches, so unsupported values may leave defaults rather than always returning `-EINVAL`. The PLL path is marked untested and uses a module-global `pll_div`, making multi-device race review worthwhile. Clock divisor selection uses approximate ratios and can silently choose the next supported divider. Only `SND_SOC_CLOCK_IN` is accepted for sysclk.

## Test Signals

Probe should show a valid chip ID and successful reset. Functional tests should cover playback and capture at 8, 11.025, 16, 22.05, 32, 44.1, and 48 kHz; one- and two-channel capture; each supported sample width; I2S, left/right justified, and DSP A/B formats; master and slave modes; and direct MCLK versus PLL-generated codec clocks. Control tests should toggle ALC, limiter, companding, high-pass filter, capture PGA/boost, speaker/mono mixers, mute, and zero-cross switches. Power tests should inspect bias transitions, regcache sync after OFF, and thermal-shutdown/output-control behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8940.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8940.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm8940.h

## Purpose

`sources/distributed-fs/ceph-client/sound/soc/codecs/wm8940.h` is the private register and platform-data header for the WM8940 ASoC driver. It supplies the driver with register addresses, clock-divider selector IDs, divider encodings, the chip ID constant, cache-register count, and the small legacy platform-data structure used for output VREF-to-analog-output resistance. The source was read as a complete 102-line file for this report.

## Important APIs, Types, and Functions

The only type is `struct wm8940_setup_data`, containing the one-bit `vroi` field and its values `WM8940_VROI_1K` and `WM8940_VROI_30K`. Register address macros cover reset, power, interface, companding, clock, ADC/DAC controls, GPIO, notch filters, DAC limiter, ALC/noise gate, PLLN/PLLK, input/PGA/boost, output/speaker mixer, speaker volume, and mono mixer registers.

Divider APIs are macro IDs `WM8940_BCLKDIV`, `WM8940_MCLKDIV`, and `WM8940_OPCLKDIV`, with encoded values for MCLK divisors 1 through 12, BCLK divisors 1 through 32, and OPCLK divisors 1 through 4. `WM8940_CHIP_ID` is the probe-time ID value expected from register 0.

## Control Flow

The header has no executable flow. Its constants are used by `wm8940.c` in regmap policy, ALSA controls, DAPM widgets, DAI format and clock-divider callbacks, PLL programming, chip-ID validation, and optional platform-data setup.

## State and Persistence Behavior

The header owns no state. It defines the hardware register layout and bit encodings that are persisted in the codec hardware and mirrored in regmap cache by the driver. The `wm8940_setup_data` instance, when supplied by board code, is external lifetime state read at component probe.

## Dependencies and Integration Points

This header is included only by the WM8940 codec driver. Its platform-data struct is a legacy non-DT integration hook; DT matching only supplies the compatible string and does not parse additional properties in this driver.

## Risks and Edge Cases

The register map is sparse, and wrong max-register/cache assumptions can make regmap reject or omit registers. Divider constants are raw hardware encodings, not divisor values, so callers must pass the macros rather than literal divisors. Changing `WM8940_CHIP_ID` or reset register definitions would directly affect probe acceptance.

## Test Signals

Compile coverage ensures every macro used by `wm8940.c` remains available. Runtime evidence should include correct chip-ID readback, successful writes to clock divider registers through `.set_clkdiv`, PLL register writes through `.set_pll`, and platform-data VROI changing `OUTPUTCTL` as expected on legacy-board tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8940.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8955.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm8955.c

## Purpose

`sources/distributed-fs/ceph-client/sound/soc/codecs/wm8955.c` is the ALSA SoC codec driver for the WM8955 playback codec over I2C. It registers a playback-only `wm8955-hifi` DAI, manages four power supplies, exposes DAC tone/output/mixer controls, configures serial format and sample width, calculates sample-rate and PLL clocking, defines DAPM routes for DAC, bypass, mono input, headphone, speaker, mono, and OUT3 paths, and sequences VMID/VREF/bias through ASoC bias levels. The source was read as a complete 1016-line file for this report.

## Important APIs, Types, and Functions

`struct wm8955_priv` stores the regmap pointer, effective MCLK rate, deemphasis state, current sample rate, and regulator bulk data for `DCVDD`, `DBVDD`, `HPVDD`, and `AVDD`. Register policy is defined by `wm8955_reg_defaults`, `wm8955_writeable()`, `wm8955_volatile()`, and `wm8955_regmap`, using 7-bit register addresses, 9-bit values, and `REGCACHE_MAPLE`.

Clocking logic is implemented by `wm8955_set_sysclk()`, `wm8955_hw_params()`, `wm8955_configure_clocking()`, `wm8955_pll_factors()`, and the DAPM supply event `wm8955_sysclk()`. Audio format and mute are handled by `wm8955_set_fmt()` and `wm8955_mute()`. Power and registration are handled by `wm8955_set_bias_level()`, `wm8955_probe()`, `wm8955_i2c_probe()`, `soc_component_dev_wm8955`, and `wm8955_i2c_driver`. Mixer controls and widgets are declared in `wm8955_snd_controls`, `wm8955_dapm_widgets`, `wm8955_dapm_routes`, and the local mixer control arrays.

## Control Flow

I2C probe allocates private state, initializes regmap, stores client data, and registers the component and DAI. Component probe requests four supplies, enables them, resets the codec, enables volume-update and zero-cross defaults, enables adaptive bass boost, applies optional platform data (`out2_speaker` inverts ROUT2 for speaker drive and `monoin_diff` enables differential mono input), forces DAPM into standby, then disables the extra supply enable so bias management owns runtime power.

The DAI `set_sysclk` callback accepts only `WM8955_CLK_MCLK`. If MCLK exceeds 15 MHz it halves the effective rate and sets `MCLKDIV2`; otherwise it uses the supplied rate directly. `hw_params` maps 16/20/24/32-bit samples into `WL`, stores `fs`, updates deemphasis, and if the digital engine is already enabled, gates the engine and PLL before reconfiguring clocks.

Clock configuration chooses a table entry from `clock_cfgs` for the active sample rate. If the effective MCLK exactly matches an entry, it programs `USB` and `SR` directly. If not, it chooses the last suitable table clock for that sample rate, computes PLL N/K/outdiv to synthesize that clock from MCLK, writes PLL control registers, enables fractional mode when K is nonzero, starts the PLL, and selects PLL as MCLK source. The `SYSCLK` DAPM supply always disables digital clocks and PLL first; on PRE_PMU it reconfigures and enables the chosen clock path.

DAPM routes connect `DACL` and `DACR` to `SYSCLK`, then route playback, line bypass, and mono input through left/right/mono mixers to LOUT1/ROUT1/LOUT2/ROUT2/MONOOUT/OUT3 PGAs. Bias transitions enable supplies and sync regcache when leaving OFF, ramp VREF/VMID with a 500 ms sleep, switch VROI high in standby and low before OFF discharge, and adjust VMID and bias-current fields for PREPARE/STANDBY.

## State and Persistence Behavior

Runtime state is in `wm8955_priv`, hardware registers, DAPM state, ALSA controls, and regcache. The driver does not persist state to disk. Current `fs` influences both clock-table selection and deemphasis; if no stream rate exists yet, clock configuration defaults to 8 kHz. Regulator state is intentionally tied to ASoC bias, while clock state is tied to DAPM `SYSCLK`. Platform data is read once at probe and then represented as register bits.

## Dependencies and Integration Points

The driver depends on Linux I2C, regmap, regulator bulk APIs, delays, ALSA SoC and TLV helpers, private `wm8955.h`, and public `<sound/wm8955.h>`. Machine drivers integrate through the I2C ID `wm8955`, the playback DAI, sysclk/format/hw_params callbacks, and optional legacy platform data. There is no OF match table in this file. The DAI supports stereo playback only, rates 8 kHz to 96 kHz, and S16/S20_3LE/S24/S32 formats.

## Risks and Edge Cases

`wm8955_configure_clocking()` assumes the sample rate is present in `clock_cfgs`; unsupported rates produce an error and warning. PLL generation uses integer arithmetic and assumes the chosen target keeps the oscillator around 90-100 MHz. If MCLK is zero or not set before stream startup, PLL division would be invalid, so machine drivers must call `set_sysclk`. The bias standby write uses shifted VREF/VMID constants in a compact expression and deserves hardware verification around VMID ramp behavior. The DAPM route for OUT3 is marked as not currently implemented even though an OUT3 PGA/output route exists.

## Test Signals

Probe tests should verify regulator acquisition, reset, default volume-update/zero-cross writes, platform-data bits, and standby transition. Audio tests should cover all listed clock-table rates, both exact MCLK and PLL-synthesized paths, MCLK greater than 15 MHz with `MCLKDIV2`, all supported widths, I2S/left/right/DSP A/B formats, master/slave modes, and mute/deemphasis toggles. DAPM tests should exercise headphone, speaker, mono, line-bypass, mono-input, and OUT3 routes. Power tests should inspect regulator enable/disable balance, 500 ms VMID ramp behavior, regcache sync on wake, and PLL shutdown on DAPM power-down.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8955.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8955.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm8955.h

## Purpose

`sources/distributed-fs/ceph-client/sound/soc/codecs/wm8955.h` is the private register definition header for the WM8955 ASoC codec driver. It defines the MCLK clock ID, register address map, register-count limits, and bitfield masks/shifts/widths used by `wm8955.c` to program DAC playback, tone controls, output mixers, power, sample rate, and PLL state. The source was read as a complete 483-line file for this report.

## Important APIs, Types, and Functions

This header has no functions or structs. Its macro API includes `WM8955_CLK_MCLK`, register addresses from `WM8955_LOUT1_VOLUME` through `WM8955_PLL_CONTROL_4`, `WM8955_REGISTER_COUNT`, and `WM8955_MAX_REGISTER`. Bitfields cover headphone/speaker/mono volume update and zero-cross bits, DAC mute/deemphasis, audio interface format/word length/master/inversion, sample-rate `USB`/`SR`/MCLKDIV2/BCLKDIV2 fields, bass/treble controls, thermal shutdown and bias-voltage selection, output mode switches, VMID/VREF/digital-engine enable, DAC/output power bits, VROI, left/right/mono output mixer sources and attenuation, differential mono input enable, clock-source/PLL enable/outdiv bits, PLL N/K fields, and fractional K enable.

## Control Flow

The header contains no executable control flow. It shapes driver behavior by supplying constants for regmap writeability and volatility, DAPM widget register bindings, ALSA controls, DAI format encoding, clock-table programming, PLL factor writes, bias transitions, and platform-data output configuration.

## State and Persistence Behavior

No storage is owned by this file. The macros describe state stored in WM8955 hardware registers and mirrored by regmap. Persistence across power states depends on `wm8955.c` bias handling and `REGCACHE_MAPLE`; reset returns hardware to defaults and the driver reapplies selected cached/default state.

## Dependencies and Integration Points

The header is private to the codec implementation and is included by `wm8955.c` alongside public `<sound/wm8955.h>`, which supplies board-facing platform data. It must stay synchronized with the WM8955 datasheet, the driver's register defaults, and the regmap writeable/volatile filters.

## Risks and Edge Cases

The WM8955 uses 9-bit register values and a 7-bit register address space, so masks above bit 8 or wrong `max_register` values would be suspicious. PLL K is split across three registers and depends on correct masks for each slice. Several output paths share similar volume-update and zero-cross naming, so changes should be reviewed against the DAPM and control register usage. A comment in the header labels it as "WM8904 ASoC driver", which appears copied and can mislead readers, but does not affect code generation.

## Test Signals

Compile tests catch missing or renamed macros. Runtime signals include correct regmap writes to 9-bit registers, successful DAI format changes, expected PLL N/K register values for representative MCLK/sample-rate pairs, working mute/deemphasis/tone controls, and DAPM output routes toggling the intended power bits. Header edits should be validated with hardware playback through headphone, speaker, mono, bypass, and PLL/non-PLL clock paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8955.h -->
