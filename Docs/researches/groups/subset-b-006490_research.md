# subset-b-006490 research

Grouped research for:
- `sources/distributed-fs/ceph-client/sound/soc/codecs/wm8753.h`
- `sources/distributed-fs/ceph-client/sound/soc/codecs/wm8770.c`
- `sources/distributed-fs/ceph-client/sound/soc/codecs/wm8770.h`
- `sources/distributed-fs/ceph-client/sound/soc/codecs/wm8776.c`
- `sources/distributed-fs/ceph-client/sound/soc/codecs/wm8776.h`
- `sources/distributed-fs/ceph-client/sound/soc/codecs/wm8782.c`
- `sources/distributed-fs/ceph-client/sound/soc/codecs/wm8804-i2c.c`
- `sources/distributed-fs/ceph-client/sound/soc/codecs/wm8804-spi.c`
- `sources/distributed-fs/ceph-client/sound/soc/codecs/wm8804.c`
- `sources/distributed-fs/ceph-client/sound/soc/codecs/wm8804.h`
- `sources/distributed-fs/ceph-client/sound/soc/codecs/wm8900.c`
- `sources/distributed-fs/ceph-client/sound/soc/codecs/wm8900.h`
- `sources/distributed-fs/ceph-client/sound/soc/codecs/wm8903.c`
- `sources/distributed-fs/ceph-client/sound/soc/codecs/wm8903.h`

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8753.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm8753.h

## Purpose

`wm8753.h` is the symbolic register and clock-divider contract for the Wolfson WM8753 ASoC codec driver. It does not implement runtime logic; it gives the corresponding codec implementation and machine-driver clock setup code stable names for the WM8753 register map, PLL IDs, clock input IDs, clock divider IDs, and encoded divider values.

## Important APIs, types, and definitions

The header defines the WM8753 register addresses from core digital-audio registers through DAC/ADC controls, power controls, GPIO/interrupt registers, mixer/output/input controls, clocking, PLL1/PLL2 control blocks, bias, and additional ADC controls. The register names are the values passed to ASoC/regmap component accessors in the implementation.

It also defines public clock IDs: `WM8753_PLL1`, `WM8753_PLL2`, `WM8753_MCLK`, `WM8753_PCMCLK`, and divider selectors `WM8753_PCMDIV`, `WM8753_BCLKDIV`, and `WM8753_VXCLKDIV`. Encoded divider constants such as `WM8753_PCM_DIV_1`, `WM8753_BCLK_DIV_8`, and `WM8753_VXCLK_DIV_16` are pre-shifted bitfield values for the codec clock registers.

No functions, structs, or inline helpers are declared in this header.

## Control flow

There is no executable control flow in this file. Compile-time inclusion lets the WM8753 driver avoid raw register numbers when resetting the codec, configuring PLLs and audio interfaces, setting sample rates, changing DAPM power bits, or programming mixers and volume controls.

## State and persistence behavior

The header stores no state and has no persistence behavior. Runtime state lives in the codec implementation, hardware registers, and any regmap cache used by that implementation. Values defined here become part of the ABI-like contract between machine drivers and the codec driver for clock IDs and divider encodings.

## Dependencies and integration points

The file has only include-guard dependencies. It integrates with the ALSA SoC WM8753 implementation and any board code that uses the public PLL/clock/divider identifiers through ASoC DAI operations.

## Risks and edge cases

The main risk is incorrect numeric register or divider definitions. Because the constants are raw hardware encodings, a wrong shift or value would compile cleanly but program the wrong register field, causing silent clock, PLL, mixer, or power sequencing failures. The pre-shifted divider constants also require callers to use the matching bitfield context; mixing PCM, BCLK, and VXCLK divider values would not be type-checked.

## Test signals

Useful signals are successful build coverage of the WM8753 codec driver, probe/reset on WM8753 hardware, working playback and capture at clock configurations using both PLL IDs and clock inputs, and register/debugfs inspection showing expected clock-divider fields after machine-driver setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8753.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8770.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm8770.c

## Purpose

`wm8770.c` implements the ALSA SoC codec driver for the Wolfson WM8770, a SPI-controlled multichannel DAC/ADC codec. It exposes a stereo playback/capture DAI, ALSA mixer controls for global and per-DAC/per-output volume/mute/phase/deemphasis, DAPM routes for eight analog inputs, auxiliary inputs, ADC bypass, four DACs, and four analog outputs, and regulator-aware power/cache management.

## Important APIs, types, and functions

`struct wm8770_priv` is the per-device state: regmap, three regulator supplies (`AVDD1`, `AVDD2`, `DVDD`), one regulator disable notifier per supply, a component pointer, and cached `sysclk` used for master-mode MCLK/LRCLK ratio selection.

The regmap configuration uses 7-bit register addresses, 9-bit values, `REGCACHE_MAPLE`, defaults for registers 0-30, and marks `WM8770_RESET` volatile. The driver is SPI-only and registers as `wm8770` with OF compatible `wlf,wm8770`.

Key callbacks include:
- `wm8770_spi_probe()`, which allocates private state, obtains regulators, installs disable notifiers, creates the SPI regmap, and registers the ASoC component plus DAI.
- `wm8770_probe()`, which enables supplies, resets the codec, latches volume update bits, mutes DAC playback, and disables supplies again.
- `wm8770_set_bias_level()`, which enables supplies, syncs the regcache, and clears global powerdown when entering standby from off, then powers down and disables regulators on off.
- `wm8770_set_fmt()`, `wm8770_hw_params()`, `wm8770_set_sysclk()`, and `wm8770_mute()`, which implement ASoC DAI format, sample width, master clock ratio, sysclk storage, and DAC mute.
- `vout12supply_event()` and `vout34supply_event()`, which update output mux power bits around DAPM output-supply transitions.

The single DAI `wm8770-hifi` supports 2-channel playback at 8-192 kHz, 2-channel capture at 8-96 kHz, S16/S20_3LE/S24/S32 formats, and symmetric rates.

## Control flow

Probe is bus-first: SPI probe allocates state and regmap, then ASoC component probe performs hardware initialization. Component probe temporarily powers the rails, writes reset, sets volume-update latches for global DAC/VOUT and per-channel volume registers, mutes all DACs, and powers rails back down. Runtime bias transitions bring the part up only when needed; moving from off to standby enables regulators, syncs cached register state, and writes `WM8770_PWDNCTRL` to clear global powerdown, while off writes global powerdown and disables regulators.

DAI setup starts with `set_fmt()`, which accepts codec master (`SND_SOC_DAIFMT_CBP_CFP`) or slave (`SND_SOC_DAIFMT_CBC_CFC`), I2S/right-justified/left-justified formats, and four clock inversion modes. `hw_params()` writes word length into `WM8770_IFACECTRL`; when the codec is master it derives `sysclk / sample_rate`, matches it against the allowed ratio table `[128, 192, 256, 384, 512, 768]`, and writes the playback or capture ratio field in `WM8770_MSTRCTRL`. Playback uses the upper ratio field; capture starts from the ADC field.

DAPM routes connect `AIN1`-`AIN8` to a capture mux and ADC, route each DAC and selected AUX/bypass source to the corresponding `VOUTn Mixer`, and gate the output mux supply bits through grouped VOUT12/VOUT34 supply events.

## State and persistence behavior

Persistent runtime state is in memory only: `sysclk`, regulator notifier state, and the regmap cache. Register state is cached while regulators are off; regulator-disable notifiers mark the cache dirty so the next power-up performs a full `regcache_sync()`. There is no filesystem persistence. ALSA control changes persist only for the lifetime of the driver instance and regmap cache.

## Dependencies and integration points

The driver depends on Linux SPI, regmap, regulator consumer APIs, ASoC component/DAI/DAPM/control APIs, PCM parameters, and OF device matching. Machine drivers interact through the `wm8770-hifi` DAI, set sysclk/format via standard ASoC DAI ops, and route board inputs/outputs through the named DAPM endpoints (`AIN*`, `AUX*`, `VOUT*`).

## Risks and edge cases

Master-mode operation requires `set_sysclk()` before `hw_params()`. If `sysclk` is zero or not an exact supported multiple of the sample rate, `hw_params()` fails. The capture and playback ratio selection starts at different indexes in the same table, so changes to the table or index logic can break one direction only. Supply-disable notifiers deliberately mark the cache dirty but probe logs notifier registration failures without aborting, which can leave cache resync less reliable on affected systems. DAPM output supply events modify magic masks `0x180` in output mux registers; incorrect sequencing could pop outputs or leave VOUT groups muted.

## Test signals

Build the SPI driver and OF table. Runtime validation should show successful regulator acquisition, reset, ASoC component registration, `wm8770-hifi` DAI availability, mixer controls in `amixer`, stereo playback to each DAC/VOUT path, stereo capture from each AIN mux setting, mute behavior, and successful suspend/off-to-standby regcache restore. Master-mode tests should cover all allowed MCLK/sample-rate ratios and a rejected unsupported ratio.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8770.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8770.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm8770.h

## Purpose

`wm8770.h` defines the register-address contract for the WM8770 ASoC codec driver. It is included by `wm8770.c` so the implementation can address volume, DAC, ADC, interface, power, mux, and reset registers by name.

## Important APIs, types, and definitions

The file lists WM8770 register addresses for VOUT1-4 left/right volumes, master analog and digital volumes, DAC1-4 volumes, DAC phase, DAC controls, DAC mute, interface control, master control, powerdown, ADC controls, ADC mux, output muxes, and reset. `WM8770_CACHEREGNUM` declares the cacheable register count boundary used by older cache-oriented code.

No functions or structs are declared.

## Control flow

There is no runtime control flow. `wm8770.c` uses these constants in regmap defaults, volatile-register decisions, ALSA controls, DAPM routes, reset, DAI format and clock programming, mute, and bias transitions.

## State and persistence behavior

The header has no state. Its constants identify hardware state managed by the codec and the regmap cache in `wm8770.c`.

## Dependencies and integration points

The header has no external include dependencies beyond its guard. It integrates directly with the WM8770 SPI codec implementation.

## Risks and edge cases

Incorrect register numbering would affect many unrelated call sites because the `.c` file uses these constants everywhere. The reset register is outside the main cached register range and is marked volatile by the implementation; changing these values would impact reset/cache behavior.

## Test signals

Compile `wm8770.c`, probe hardware successfully, verify reset and regmap defaults, and exercise ALSA controls whose register addresses come from this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8770.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8776.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm8776.c

## Purpose

`wm8776.c` implements the ALSA SoC codec driver for WM8775/WM8776 devices. It exposes separate playback and capture DAIs for the DAC and ADC sides, ASoC controls for headphone/DAC/ADC volume and filters, DAPM routes for analog input mixing, DAC playback, output bypass, VOUT, and headphone outputs, plus regmap-backed I2C and SPI bus support.

## Important APIs, types, and functions

`struct wm8776_priv` holds the regmap and a two-element `sysclk[]` array indexed by DAI ID (`WM8776_DAI_DAC` and `WM8776_DAI_ADC`). `enum wm8776_chip_type` distinguishes I2C IDs `wm8775` and `wm8776`, though the match data is not otherwise consumed in this file.

The regmap uses 7-bit addresses, 9-bit values, reset-register volatility, `REGCACHE_MAPLE`, and defaults for registers 0-22. The component driver declares controls, widgets, routes, bias handling, suspend-bias-off, idle-bias-on, powerdown timing, and endianness.

Key callbacks include:
- `wm8776_spi_probe()` and `wm8776_i2c_probe()`, which allocate state, create bus-specific regmaps, store driver data, and register the component with two DAIs.
- `wm8776_probe()`, which resets the chip and latches right-channel headphone and DAC volume update bits.
- `wm8776_set_fmt()`, which chooses DAC or ADC interface register by DAI ID, configures master/slave, audio format, and inversion.
- `wm8776_hw_params()`, which programs word length and, in master mode, writes the selected MCLK/LRCLK ratio for the specific DAI.
- `wm8776_set_sysclk()` and `wm8776_mute()`, which cache per-DAI sysclk and write DAC mute.
- `wm8776_set_bias_level()`, which syncs the cache and clears global powerdown when leaving off, then asserts global powerdown when off.

## Control flow

Module initialization conditionally registers the I2C driver and SPI driver based on kernel configuration. Each bus probe creates a regmap and registers the ASoC component. Component probe resets the device and enables volume-update latches.

DAI control flow is per-interface. `set_fmt()` maps `WM8776_DAI_DAC` to `WM8776_DACIFCTRL` and master bit `0x80`, and `WM8776_DAI_ADC` to `WM8776_ADCIFCTRL` and master bit `0x100`. It accepts I2S, right-justified, and left-justified formats, plus normal/inverted bit and frame clock combinations. `hw_params()` writes sample width encodings for 16/20/24/32-bit samples, then if the relevant master bit is set, compares `sysclk[dai_id] / rate` against `[128, 192, 256, 384, 512, 768]` and writes the matching ratio field in `WM8776_MSTRCTRL`.

DAPM routes connect `AIN1`-`AIN5` through the input mixer to ADC capture, route DAC/AUX/input bypass through the output mixer to `VOUT`, and route the same output mixer through the headphone PGA to `HPOUTL`/`HPOUTR`.

## State and persistence behavior

Runtime state is limited to the regmap cache and per-DAI sysclk values. There is no regulator management in this driver, so power state is controlled by codec powerdown bits and external platform power wiring. Register cache is synced when returning from off to standby, allowing ALSA control state to be restored after bias-off transitions. No state is persisted outside memory.

## Dependencies and integration points

The file depends on ASoC core APIs, regmap, optional I2C, optional SPI, OF matching (`wlf,wm8776`), and PCM parameter helpers. Machine drivers bind to `wm8776-hifi-playback` and `wm8776-hifi-capture`, configure sysclk/format independently, and route board endpoints through DAPM names such as `AIN*`, `AUX`, `VOUT`, and `HPOUT*`.

## Risks and edge cases

The two-DAI split means the correct DAI ID is critical for selecting the right interface register, master bit, and `sysclk[]` entry. Master-mode `hw_params()` fails if sysclk is unset or not an exact supported ratio. The module init returns the last registration result, so if both I2C and SPI are enabled and I2C registration fails but SPI succeeds, the final return may hide the earlier failure. The code has no regulator or runtime PM support; boards must ensure supplies and clocks are valid around codec use.

## Test signals

Build with I2C-only, SPI-only, and both enabled. Runtime validation should cover both DAI names, playback and capture at supported rates, master and slave modes, all supported word lengths, DAC mute, input mixer bypass, headphone/VOUT paths, bias-off to standby regcache sync, and probe through both bus types where hardware is available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8776.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8776.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm8776.h

## Purpose

`wm8776.h` defines register addresses and DAI IDs used by the WM8776/WM8775 ASoC codec driver.

## Important APIs, types, and definitions

The register list covers headphone volume, headphone master volume, DAC left/right/master volume, phase swap, DAC controls and mute, DAC and ADC interface controls, master clock control, powerdown, ADC volumes, ALC/noise-gate/limiter controls, ADC mux, output mux, and reset. `WM8776_CACHEREGNUM` gives the cache register count boundary. `WM8776_DAI_DAC` and `WM8776_DAI_ADC` are public IDs used by `wm8776.c` to index DAI-specific logic and sysclk state.

No functions or structs are declared.

## Control flow

There is no executable control flow. The implementation uses these constants to build controls, DAPM routes, regmap defaults, DAI callbacks, and reset/power paths.

## State and persistence behavior

The header stores no state. The DAI ID constants influence how `wm8776.c` maps runtime ASoC DAI callbacks to DAC or ADC register fields.

## Dependencies and integration points

It has no external include dependencies. It integrates only with the WM8776 codec implementation and any code that needs the DAI ID definitions.

## Risks and edge cases

Wrong DAI ID values would corrupt `sysclk[]` indexing and interface-register selection in `wm8776.c`. Incorrect register addresses would lead to valid-looking regmap writes against the wrong WM8776 hardware controls.

## Test signals

Compile and probe the WM8776 driver, then verify separate playback/capture DAI setup, reset, mute, and mixer controls that use the constants defined here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8776.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8782.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm8782.c

## Purpose

`wm8782.c` is a minimal ASoC platform codec driver for the WM8782, a strap-pin-configured 24-bit stereo ADC. Because the chip is configured externally rather than through a control bus, the driver mainly exposes a capture-only DAI, constrains the maximum sample rate from device-tree configuration, models the two analog inputs in DAPM, and manages the analog and digital supplies.

## Important APIs, types, and functions

`struct wm8782_priv` stores two regulator supplies (`Vdda`, `Vdd`) and the computed `max_rate`. `wm8782_probe()` allocates state, obtains regulators, reads optional OF property `wlf,fsampen`, maps that strap value to a maximum sample rate, and registers the ASoC component and one DAI.

`wm8782_dai_startup()` applies a runtime hardware constraint limiting `SNDRV_PCM_HW_PARAM_RATE` to 8 kHz through `priv->max_rate`. The DAI is named `wm8782`, capture-only, stereo, and supports S16_LE, S20_3LE, and S24_LE formats with nominal rates up to 192 kHz before startup constraints.

The component callbacks `wm8782_soc_probe()`, `wm8782_soc_remove()`, and optional PM `wm8782_soc_suspend()`/`wm8782_soc_resume()` enable and disable the two regulator supplies. DAPM exposes `AINL` and `AINR` as inputs routed to `Capture`.

## Control flow

Platform probe obtains supplies and parses `wlf,fsampen`. The default is `0`, intentionally selecting 48 kHz maximum to avoid overclocking when no property is provided. Values `1` and `2` allow 96 kHz and 192 kHz respectively; any other value aborts probe with `-EINVAL`.

When the ASoC component probes, both regulators are enabled and remain enabled until component remove or suspend. On PCM startup, the driver applies the rate constraint based on the parsed strap value, so ALSA negotiation rejects rates above the configured hardware capability.

## State and persistence behavior

The only persistent runtime state is `max_rate` and regulator handles in private memory. There is no register cache, control bus state, or filesystem persistence. Power state is represented by regulator enable/disable calls during component lifecycle and PM transitions.

## Dependencies and integration points

The driver depends on platform devices, OF matching (`wlf,wm8782`), regulator consumer APIs, and ASoC component/DAI/DAPM APIs. Machine drivers use the `wm8782` capture DAI and board routing to the `AINL`/`AINR` endpoints. Device tree supplies must provide `Vdda` and `Vdd`, and may provide `wlf,fsampen`.

## Risks and edge cases

The `wlf,fsampen` property must match board strap wiring. If omitted, the conservative 48 kHz cap may reject valid higher rates; if overstated, the system may overclock the ADC. Since the codec has no readable registers, runtime failures often appear only as silent/bad capture data or regulator errors. Component probe enables regulators but does not have DAPM-controlled per-stream power gating.

## Test signals

Build the platform driver and OF match. Runtime tests should verify regulator enable/disable on probe/remove/suspend/resume, ALSA capture device registration, accepted maximum rates for `wlf,fsampen` values 0/1/2, rejection of invalid property values, and clean stereo capture at S16/S20_3LE/S24_LE formats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8782.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8804-i2c.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm8804-i2c.c

## Purpose

`wm8804-i2c.c` is the I2C bus wrapper for the shared WM8804 S/PDIF transceiver codec core. It creates an I2C regmap and delegates all hardware identification, ASoC registration, regulator handling, reset, clocking, runtime PM, and DAPM behavior to `wm8804.c`.

## Important APIs, types, and functions

`wm8804_i2c_probe()` initializes a regmap with `devm_regmap_init_i2c(i2c, &wm8804_regmap_config)` and calls `wm8804_probe(&i2c->dev, regmap)`. `wm8804_i2c_remove()` calls `wm8804_remove(&i2c->dev)`. The I2C ID table contains `wm8804`; OF compatible is `wlf,wm8804`; ACPI IDs include `1AEC8804` and `10138804`. The driver attaches shared `wm8804_pm` through `pm_ptr()`.

## Control flow

Kernel I2C matching invokes the probe callback. If regmap creation fails, probe returns the PTR_ERR. Otherwise the shared core probe owns all remaining initialization. Remove delegates to the shared core remove so runtime PM is disabled.

## State and persistence behavior

This wrapper stores no private state beyond devm-managed regmap data and the shared private data installed by `wm8804_probe()`. There is no persistence outside device lifetime.

## Dependencies and integration points

It depends on Linux I2C, ACPI, module infrastructure, regmap through `wm8804.h`, and the exported symbols from `wm8804.c`: `wm8804_regmap_config`, `wm8804_pm`, `wm8804_probe()`, and `wm8804_remove()`. It integrates the codec with I2C/OF/ACPI enumeration.

## Risks and edge cases

Any bus-specific issue is concentrated in regmap initialization or device matching. Because core probe is shared, the I2C wrapper must use the exact shared regmap configuration; mismatched reg/val widths would break ID reads and register writes. ACPI/OF match coverage needs to remain aligned with platform firmware naming.

## Test signals

Build with I2C enabled, confirm module alias tables for I2C/OF/ACPI, probe a WM8804 over I2C, read the expected device ID through the core, register the `wm8804-spdif` DAI, and verify remove/runtime-PM cleanup through unbind or module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8804-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8804-spi.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm8804-spi.c

## Purpose

`wm8804-spi.c` is the SPI bus wrapper for the shared WM8804 S/PDIF transceiver codec core. It creates a SPI regmap and delegates the complete codec implementation to `wm8804.c`.

## Important APIs, types, and functions

`wm8804_spi_probe()` uses `devm_regmap_init_spi(spi, &wm8804_regmap_config)` and calls `wm8804_probe(&spi->dev, regmap)`. `wm8804_spi_remove()` calls `wm8804_remove(&spi->dev)`. The driver matches OF compatible `wlf,wm8804`, names the SPI driver `wm8804`, and uses shared `wm8804_pm` for runtime PM hooks.

## Control flow

SPI core matching invokes probe. Probe returns immediately on regmap creation failure; otherwise the shared WM8804 core validates ID/revision, configures reset/regulators, registers ASoC, and enables runtime PM. Remove delegates to the shared core remove path.

## State and persistence behavior

The file maintains no independent private state. Device state is devm-managed regmap state plus the shared `wm8804_priv` allocated by `wm8804_probe()`.

## Dependencies and integration points

It depends on Linux SPI, module infrastructure, and exported symbols declared in `wm8804.h`. It integrates WM8804 hardware on SPI buses with the same codec core and DAI surface as I2C systems.

## Risks and edge cases

The wrapper must stay in sync with the shared regmap format. SPI register-access quirks would affect all core register reads/writes, including the device-ID check. Unlike the I2C wrapper, this file has no ACPI table; SPI systems must match through board data or OF.

## Test signals

Build with SPI support, verify OF module aliases, probe over SPI, validate core ID/revision logging, ASoC `wm8804-spdif` registration, playback/capture over the S/PDIF transceiver, and clean unbind/module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8804-spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8804.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm8804.c

## Purpose

`wm8804.c` is the shared ASoC codec core for the WM8804 S/PDIF transceiver. It implements device identification, reset, regulator and runtime-PM handling, regmap defaults, the S/PDIF/AIF DAPM graph, DAI format and word-length programming, PLL/sysclk/clock-divider control, and exported probe/remove/regmap/PM hooks used by both I2C and SPI wrappers.

## Important APIs, types, and functions

`struct wm8804_priv` stores the device, regmap, `PVDD`/`DVDD` regulators, regulator disable notifiers, `mclk_div`, optional reset GPIO, and an `aif_pwr` reference count used to power the AIF only while playback/capture paths need it.

Exported integration points are `wm8804_regmap_config`, `wm8804_probe()`, `wm8804_remove()`, and `wm8804_pm`. The regmap has 8-bit registers/values, defaults for PLL, S/PDIF, GPO, AIF, receiver, and powerdown registers, `REGCACHE_MAPLE`, and volatile ID/status/channel-status registers.

Key codec functions include:
- `wm8804_probe()`, which allocates state, gets optional reset GPIO `wlf,reset`, obtains regulators, installs notifiers, enables supplies, releases reset, validates device ID `0x8805`, logs revision, performs soft reset if no reset GPIO exists, registers the component/DAI, and starts runtime PM.
- `wm8804_runtime_resume()`/`wm8804_runtime_suspend()`, which enable/sync or disable supplies and power OSCCLK.
- `wm8804_set_fmt()`, `wm8804_hw_params()`, `wm8804_set_sysclk()`, `wm8804_set_clkdiv()`, and `wm8804_set_pll()`, which implement ASoC clock and audio-interface programming.
- `pll_factors()`, which derives PLL prescale, mclkdiv, freqmode, N, and K values while keeping the PLL around 90-100 MHz.
- `txsrc_put()` and `wm8804_aif_event()`, which safely switch transmit source and maintain AIF power reference counting.

The single DAI `wm8804-spdif` supports stereo playback and capture at 32-192 kHz and S16_LE/S20_3LE/S24_LE formats with symmetric rates.

## Control flow

Bus wrappers create a regmap and call `wm8804_probe()`. Core probe powers the device, reads and validates ID/revision, resets the chip if needed, registers ASoC, marks runtime PM active, enables runtime PM, and idles the device. Regulator-disable notifiers mark the cache dirty if supplies disappear outside the driver's control.

DAPM routes model two directions: AIF playback can be transmitted to S/PDIF output, or S/PDIF input can be retransmitted; S/PDIF input also routes to AIF capture. The "Tx Source" mux is special: `txsrc_put()` powers down the transmitter before changing the source bit in `WM8804_SPDTX4`, then restores the prior transmitter power state. AIF RX/TX widgets call `wm8804_aif_event()` after power changes, incrementing/decrementing `aif_pwr` and toggling the AIF powerdown bit only when the first path appears or the last path disappears.

Clock setup accepts I2S/right-justified/left-justified/DSP formats, codec master or slave for AIFRX, normal/inverted BCLK/LRCLK, and 16/20/24-bit samples. PLL programming either powers the PLL down and drops the runtime-PM reference, or computes divisors, ensures runtime resume, writes PLL registers while powered down, and powers the PLL back up. `set_sysclk()` chooses TX clock source or CLKOUT source and validates direct MCLK frequency ranges. `set_clkdiv()` programs CLKOUT divider or caches MCLK divider selection used by later PLL factor calculation.

## State and persistence behavior

State is in memory and hardware registers. Regmap cache preserves register writes across runtime suspend and regulator loss; notifiers mark it dirty when a regulator is disabled. Runtime PM controls the regulators and OSCCLK. `aif_pwr` is a software reference count for two DAPM AIF widgets. `mclk_div` is cached for PLL calculations. There is no filesystem persistence.

## Dependencies and integration points

The core depends on regmap, regulators, GPIO descriptors, runtime PM, ASoC component/DAI/DAPM APIs, and the bus wrappers. Machine drivers configure the `wm8804-spdif` DAI via standard DAI ops and route board endpoints to `SPDIF In` and `SPDIF Out`. The exported regmap config and PM ops are required by `wm8804-i2c.c` and `wm8804-spi.c`.

## Risks and edge cases

PLL setup is sensitive to valid source/output frequencies and the prior `mclk_div` setting; unsupported ratios fail from `pll_factors()`. In `wm8804_set_pll()`, runtime PM reference handling depends on whether the PLL powerdown bit changed, so mismatched external register state could unbalance PM. `aif_pwr` is not protected by a lock in the event callback, relying on DAPM serialization. `txsrc_put()` validates only the enum bit value and assumes the transmitter powerdown bit can be safely toggled around source changes. Core probe disables regulators on failures before runtime PM is enabled, while `wm8804_remove()` only disables runtime PM; devm/resource and runtime PM ordering should be tested on unbind paths.

## Test signals

Test I2C and SPI wrappers against the shared core. Validate ID/revision read, optional reset GPIO and soft-reset paths, regulator disable/resume regcache sync, runtime suspend/resume, S/PDIF input capture, AIF playback to S/PDIF output, S/PDIF retransmit source selection, DAI formats/inversions/word lengths, direct MCLK and PLL clocking, unsupported PLL frequency rejection, and unbind/module unload cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8804.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8804.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm8804.h

## Purpose

`wm8804.h` is the shared interface between the WM8804 bus wrappers and codec core. It defines the WM8804 register map, public clock-source/divider IDs, selected divider values, and exported core symbols used by `wm8804-i2c.c` and `wm8804-spi.c`.

## Important APIs, types, and definitions

The register definitions cover reset/device ID/revision, PLL1-6, S/PDIF mode/status/channel registers, S/PDIF transmit registers, GPO registers, AIF TX/RX controls, S/PDIF RX control, and powerdown. `WM8804_REGISTER_COUNT` and `WM8804_MAX_REGISTER` define regmap bounds.

Public DAI clock constants include `WM8804_TX_CLKSRC_MCLK`, `WM8804_TX_CLKSRC_PLL`, `WM8804_CLKOUT_SRC_CLK1`, `WM8804_CLKOUT_SRC_OSCCLK`, divider IDs `WM8804_CLKOUT_DIV` and `WM8804_MCLK_DIV`, and MCLK divider values `WM8804_MCLKDIV_256FS` and `WM8804_MCLKDIV_128FS`.

The header declares exported `wm8804_regmap_config`, exported runtime-PM ops `wm8804_pm`, and core entry points `wm8804_probe(struct device *dev, struct regmap *regmap)` and `wm8804_remove(struct device *dev)`.

## Control flow

The header has no executable flow. It enables the bus wrappers to instantiate the correct regmap and delegate to the shared core, and enables machine drivers to pass public clock IDs to standard ASoC DAI operations.

## State and persistence behavior

No state is stored here. The declarations point to stateful objects and functions implemented in `wm8804.c`; register state is held by hardware and regmap cache.

## Dependencies and integration points

The file includes `<linux/regmap.h>` for `struct regmap_config` and `struct regmap`. It also relies on `struct device` and `struct dev_pm_ops` declarations from kernel headers included by users. It is consumed by the shared WM8804 bus wrappers and codec core.

## Risks and edge cases

Register constants, clock IDs, and divider encodings are public within the driver family; changing them breaks both bus wrappers and machine-driver clock setup. The exported core API assumes wrappers pass a regmap configured with the declared `wm8804_regmap_config`.

## Test signals

Build both WM8804 bus wrappers, verify they link against exported symbols, and run clock setup paths using the public clock/divider IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8804.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8900.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm8900.c

## Purpose

`wm8900.c` implements the ALSA SoC codec driver for the WM8900. It provides register definitions and defaults, a broad set of ALSA controls, a DAPM graph for analog inputs, ADC/DAC paths, line outputs, headphone output sequencing, FLL and DAI clock programming, bias/suspend/resume sequencing, and I2C/SPI bus registration.

## Important APIs, types, and functions

`struct wm8900_priv` stores the regmap and cached FLL input/output rates. The regmap uses 8-bit register addresses, 16-bit values, `REGCACHE_MAPLE`, defaults for the nonvolatile register range, and marks the ID/reset register volatile.

Major callback groups include:
- `wm8900_spi_probe()` and `wm8900_i2c_probe()`, which allocate state, initialize the bus regmap, store driver data, and register the ASoC component and `wm8900-hifi` DAI.
- `wm8900_probe()`, which verifies ID `0x8900`, resets the codec, forces standby bias, latches volume update bits, and sets DAC/mixer output bias.
- `wm8900_set_bias_level()`, which implements startup bias/VMID charging, standby bias, thermal shutdown enable, off discharge, HP clamp clearing, and master-clock stop timing.
- `wm8900_suspend()`/`wm8900_resume()`, which orderly stop and restore the FLL, force bias off/standby, reset the chip, and sync regcache.
- DAI ops `wm8900_hw_params()`, `wm8900_set_dai_fmt()`, `wm8900_set_dai_clkdiv()`, `wm8900_set_dai_pll()`, and `wm8900_mute()`.
- `fll_factors()` and `wm8900_set_fll()`, which compute and program FLL ratio, divider, N/K fractional values, slow-lock reference mode, oscillator enable, and FLL enable.
- `wm8900_hp_event()`, which sequences headphone clamp, short, input stage, output stage, delays, and shutdown across DAPM events.

The DAI supports 1-2 channel playback/capture at common 8-48 kHz rates and S16_LE/S20_3LE/S24_LE formats.

## Control flow

Module init conditionally registers I2C and SPI drivers. Bus probe creates regmap and registers the component. Component probe reads the chip ID, resets, brings the codec into standby through the bias state machine, latches update bits for input, output, DAC, and ADC volumes, and writes output bias.

Bias control handles analog power sequencing. From off to standby, it enables startup bias, soft-start VMID, waits for capacitor charge, enables bias, then settles into normal VMID/bias and SYSCLK state. Bias off discharges caps, clears headphone control, powers down blocks, waits briefly, and leaves SYSCLK enable set as required by the datasheet restart sequence. Bias on enables thermal shutdown bits.

DAI format setup configures BCLK/LRCLK master directions, I2S/right/left-justified/DSP_A/DSP_B formats, and valid inversion combinations. `hw_params()` writes word length and enables the DAC sloping stopband filter at sample rates up to 24 kHz. Clock dividers are written by ID using constants from `wm8900.h`. FLL setup disables the FLL before changes, disables oscillator and source on zero frequencies, computes divisors for nonzero frequencies, writes FLL control registers, and switches MCLK source to FLL.

DAPM routes model input PGAs/mixers from three left/right inputs and AUX, ADC capture, DAC playback, bypass paths into output mixers, line output PGAs, optional LINEOUT2 low-power route, and a mono headphone amplifier fed externally through LINEOUT2.

## State and persistence behavior

FLL input/output rates are cached in memory so suspend can stop the FLL while preserving desired rates, and resume can reprogram it after reset/cache sync. Register state is held in the regmap cache and restored on resume. Bias and DAPM state live in ASoC core/hardware registers. There is no filesystem persistence.

## Dependencies and integration points

The driver depends on Linux I2C/SPI, regmap, PM, ASoC component/DAI/DAPM/control APIs, and PCM params. Machine drivers use `wm8900-hifi`, DAI clock divider constants from `wm8900.h`, and board routes for inputs (`LINPUT*`, `RINPUT*`, `AUX`) and outputs (`LINEOUT*`, `HP_*`).

## Risks and edge cases

FLL support is explicitly limited: TODO notes say only MCLK source configuration is supported. `wm8900_set_fll()` returns 0 even after `fll_factors()` failure via the `reenable` path, so callers may not see invalid FLL programming as an error. Bias sequencing contains long sleeps and datasheet-specific ordering; shortening or bypassing it risks pops or failed restarts. The I2C remove callback is empty because resources are devm-managed, but component-level power state relies on ASoC callbacks. Module init can mask an earlier I2C registration failure if later SPI registration succeeds.

## Test signals

Test chip ID failure and success, I2C/SPI probe, full bias on/off transitions, suspend/resume with and without FLL active, FLL programming across valid and invalid rates, DAI formats and inversions including DSP modes, divider IDs from `wm8900.h`, low-rate DAC filter behavior, headphone power sequencing, and playback/capture through DAPM-routed inputs/outputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8900.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8900.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm8900.h

## Purpose

`wm8900.h` exposes public clock and FLL identifiers plus encoded clock-divider values for WM8900 machine-driver integration.

## Important APIs, types, and definitions

`WM8900_FLL` identifies the FLL for ASoC `set_pll()`. Divider IDs `WM8900_BCLK_DIV`, `WM8900_ADC_CLKDIV`, `WM8900_DAC_CLKDIV`, `WM8900_ADC_LRCLK`, `WM8900_DAC_LRCLK`, `WM8900_OPCLK_DIV`, and `WM8900_LRCLK_MODE` are consumed by `wm8900_set_dai_clkdiv()`. The header also defines pre-encoded BCLK divider values from 1 through 48, ADC clock dividers from 1 through 6, and DAC clock dividers from 1 through 6.

No functions or structs are declared.

## Control flow

The header has no runtime control flow. Machine drivers pass these IDs and values into the WM8900 DAI ops, where `wm8900.c` maps them to `CLOCKING1`, `CLOCKING2`, `AUDIO3`, `AUDIO4`, and `DACCTRL` fields.

## State and persistence behavior

No state is stored here. The constants affect hardware register state through DAI callbacks in `wm8900.c`.

## Dependencies and integration points

The file has no external include dependencies. It is included by `wm8900.c` and by board/machine code configuring WM8900 clocks.

## Risks and edge cases

The divider values are already encoded for the target register fields. Passing them to the wrong divider ID, or changing encodings without updating `wm8900_set_dai_clkdiv()`, would silently program invalid clocks. There is no type distinction between divider families.

## Test signals

Compile users of the header and run DAI clock-divider setup for each divider ID, verifying register writes and actual BCLK/LRCLK/DAC/ADC clock behavior on hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8900.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8903.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm8903.c

## Purpose

`wm8903.c` implements the ALSA SoC codec driver for the WM8903 over I2C. It handles register defaults and cache policy, regulator-powered probe and reset, DAPM routes for analog/digital input/output paths, DAI format and clock programming, dynamic deemphasis, DC servo and write-sequencer coordination, Class W charge-pump behavior, microphone/jack detection through IRQs, optional GPIO controller exposure, and platform-data/device-tree configuration.

## Important APIs, types, and functions

`struct wm8903_priv` stores platform data, device/regmap, four regulators (`AVDD`, `CPVDD`, `DBVDD`, `DCVDD`), sysclk, IRQ, a mutex, current sample rate and deemphasis state, pending/cached DC servo state, Class W bypass-user count, microphone jack reporting state, mic detection delay, and optional `gpio_chip`.

The regmap uses 8-bit registers, 16-bit values, readable and volatile register callbacks, `REGCACHE_MAPLE`, and reset defaults for the nonvolatile register set. The component driver registers controls, DAPM widgets/routes, `wm8903_set_bias_level()`, `wm8903_seq_notifier()`, resume cache sync, suspend-bias-off, idle-bias-on, powerdown timing, and endianness.

Important exported/local functions include:
- `wm8903_i2c_probe()` and `wm8903_i2c_remove()`, which parse platform data/OF, manage regulators, validate ID/revision, reset the device, initialize GPIOs, configure mic detection and IRQs, latch volume-update bits, enable DAC soft mute, and register ASoC.
- `wm8903_mic_detect()`, exported for machine drivers to attach an ASoC jack and enable mic detect/short interrupts.
- `wm8903_irq()`, which handles write-sequencer and microphone detection interrupts, toggles interrupt polarity after each mic event, delays for debounce if configured, and reports jack state.
- `wm8903_hw_params()`, `wm8903_set_dai_fmt()`, `wm8903_set_dai_sysclk()`, and `wm8903_mute()`, which implement PCM clocking, DAI format, sysclk cache, and DAC mute.
- `wm8903_seq_notifier()` and `wm8903_dcs_event()`, which start/restore/calibrate DC servo offsets after DAPM sequences.
- `wm8903_class_w_put()`, which disables Class W when analog bypass paths are active and re-enables it when only DAC outputs are in use.
- GPIO callbacks for request, direction, get, and set when `CONFIG_GPIOLIB` is enabled.

The `wm8903-hifi` DAI supports stereo playback at 8-96 kHz, stereo capture at 8-48 kHz, S16_LE/S20_3LE/S24_LE, and symmetric rates.

## Control flow

I2C probe allocates private state and regmap, creates default platform data if none is supplied, derives IRQ polarity from IRQ trigger and OF properties, obtains and enables regulators, reads ID `0x8903` and revision, resets the device, registers GPIOs, writes platform GPIO configuration, configures mic-detect registers, requests a threaded IRQ when available, latches ADC/DAC/headphone/line/speaker volume update bits, enables DAC soft mute, and registers the component/DAI. Remove disables regulators, frees IRQ, and removes GPIOs.

Bias sequencing performs a staged analog startup when leaving off: startup bias and speaker discharge, VMID soft-start with waits, temporary speaker enable/disable, normal VMID resistance, bias enable, and Class W enable. Prepare lowers VMID resistance for active use; standby uses 250K; off disables bias, soft-discharges VMID, waits, and clears VMID and startup bias bits.

`hw_params()` chooses nearest DSP sample-rate code, selects sample width, computes target BCLK, searches a `sysclk/fs` ratio table for the closest achievable `CLK_SYS`, optionally divides MCLK by two, computes BCLK divider not below the target BCLK, writes clock/audio-interface registers, records `fs`, updates deemphasis selection, and toggles the low-rate DAC stopband filter. `set_dai_fmt()` handles codec/provider clock directions, I2S/right/left/DSP modes, and legal inversion modes.

DAPM routes model analog input muxing including differential modes, ADC versus DMIC input, capture channel muxing, sidetone, playback channel muxing, DACs, output and speaker mixers, headphone/lineout startup sequences, DC servo enable paths, charge pump, and speaker outputs. The seq notifier completes pending DC servo work after DAPM paths have been powered.

## State and persistence behavior

All driver state is in memory and hardware/register cache. `sysclk` must be set by the machine driver for accurate `hw_params()` clocking. `fs` and `deemph` persist across controls and stream setup to choose the best deemphasis register value. `dcs_cache[]` stores measured DC servo offsets for reuse unless Class W/bypass conditions require recalibration. `class_w_users` is a reference count for bypass paths. Mic jack state stores the last reported bits and active polarity. Regmap cache is synced on component resume. No state is written to disk.

## Dependencies and integration points

The driver depends on Linux I2C, regmap, regulators, IRQ, mutex, optional gpiolib, OF/platform-data parsing, ASoC controls/DAPM/DAI/jack APIs, and tracepoints when built in. It includes `<sound/wm8903.h>` for platform data and the local `wm8903.h` for register fields. Machine drivers configure `wm8903-hifi`, call `wm8903_mic_detect()` for jack reporting, may consume the codec GPIO controller, and provide platform data or OF properties `micdet-cfg`, `micdet-delay`, and `gpio-cfg`.

## Risks and edge cases

`hw_params()` approximates clocks rather than requiring an exact sysclk/fs ratio; this can make audio work with imperfect clocks but risks subtle rate error if board sysclk is wrong. The sample-rate search includes a terminating `{0,0}` entry and uses `ARRAY_SIZE`, so the zero entry can become the best match for unusual rates if future ranges change. DC servo caching is timing-sensitive and intentionally bypassed when Class W users exist; wrong sequencing can cause output offsets or pops. Mic IRQ handling toggles polarity after each event and clears status by read, so lost interrupts are possible if mic detection is enabled before the machine driver calls `wm8903_mic_detect()`. GPIO configuration translation differs between DT and platform-data representations and rejects invalid high values.

## Test signals

Build with and without `CONFIG_GPIOLIB`, with I2C/OF support. Runtime tests should cover ID/revision probe, regulator errors, OF parsing for mic and GPIO config, GPIO direction/get/set, IRQ polarity active-high/active-low, `wm8903_mic_detect()` jack and short reporting, suspend/resume regcache sync, bias transitions, DAPM route activation for analog, DMIC, sidetone, headphone, lineout, and speaker paths, DC servo calibration/cache reuse, Class W changes when bypass paths toggle, DAI formats/inversions, sysclk-derived clock setup, deemphasis updates, and low-rate DAC filter behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8903.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8903.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm8903.h

## Purpose

`wm8903.h` is the local/public register-definition header for the WM8903 codec driver. It declares the machine-driver-visible microphone detection helper and defines the register map plus field masks, shifts, widths, and selected encoded values consumed by `wm8903.c`.

## Important APIs, types, and definitions

The exported API declaration is `wm8903_mic_detect(struct snd_soc_component *component, struct snd_soc_jack *jack, int det, int shrt)`, used by machine drivers to enable codec IRQ-backed microphone presence and short detection reporting.

The register map covers ID/revision, bias/VMID/mic-bias, analog DAC/ADC, power management, clock rates, audio interfaces, digital ADC/DAC volume/control, digital microphone, DRC, analog input/mixer/output, speaker output, DC servo and readback, headphone/lineout sequencing, charge pump, Class W, write sequencer, control interface, GPIO controls, interrupt status/mask/polarity/control, clock-rate test, and analog output bias.

Field definitions provide masks and shifts for bias, VMID, power, clocking, audio-interface format/word length/TDM/BCLK/LRCLK, volume update bits, DAC mute/deemphasis/filtering, ADC HPF and DRC, input mux/mode, output mixers, DC servo, charge pump/Class W, write sequencer, GPIO function/direction/level, microphone interrupts, IRQ polarity, and DMIC selection. Helper values such as `WM8903_VMID_RES_50K`, `WM8903_VMID_RES_250K`, and `WM8903_VMID_RES_5K` encode common VMID resistance settings.

## Control flow

The header contains no executable flow. It drives the control flow in `wm8903.c` by defining the bits used for probe/reset checks, bias sequencing, DAPM power events, DC servo calibration, clock selection, DAI format setup, jack IRQ handling, GPIO mode changes, and regmap readable/volatile policies.

## State and persistence behavior

The header stores no state. It defines addresses for hardware state and fields mirrored in the regmap cache. Runtime state such as `sysclk`, `deemph`, `dcs_cache`, mic report bits, and GPIO chip registration lives in `wm8903.c`.

## Dependencies and integration points

It includes `<linux/i2c.h>` and references ASoC types (`struct snd_soc_component`, `struct snd_soc_jack`). It is included by `wm8903.c` and can be included by machine drivers needing `wm8903_mic_detect()`. It complements `<sound/wm8903.h>`, which supplies platform data rather than register-field definitions.

## Risks and edge cases

This header has a large volume of raw hardware definitions; register-field drift is the primary risk. A wrong mask or shift can affect clocks, power sequencing, GPIO direction, IRQ polarity, DC servo, or audio routing while still compiling. Some macro names such as volume-update bits repeat for left and right registers, so edits must preserve their intended register context. Public helper declaration changes would break machine drivers using codec mic detection.

## Test signals

Compile `wm8903.c` and any machine drivers using `wm8903_mic_detect()`. Hardware validation should cover register-field consumers: bias/VMID transitions, DAI clock/format setup, GPIO operation, mic IRQ reporting, DC servo sequencing, volume update latches, and DAPM routes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8903.h -->
