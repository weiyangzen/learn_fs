# subset-b-006496 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8990.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm8990.c

## Purpose
`wm8990.c` is an ALSA System-on-Chip codec driver for the Wolfson WM8990 audio codec. It binds as an I2C codec component, exposes mixer and volume controls, declares the DAPM audio routing graph, implements one "wm8990-hifi" DAI, and sequences bias and anti-pop power transitions for playback and capture paths.

## Important APIs, types, and functions
- `struct wm8990_priv` stores the component regmap pointer plus cached `sysclk` and `pcmclk` values. In this file only `sysclk` is written by `wm8990_set_dai_sysclk()`, and `regmap` is consumed by bias transitions.
- `wm899x_outpga_put_volsw_vu()` wraps `snd_soc_put_volsw()` and then sets bit 8 in the affected register so output, DAC, ADC, and input volume updates are latched atomically by hardware.
- `wm8990_snd_controls[]` defines user-visible ALSA controls for input boosts, bypass volumes, line/headphone/output/speaker mute and volume controls, sidetone, ADC HPF mode, and ADC/DAC digital volumes.
- `outmixer_event()` is a DAPM pre-register guard. It rejects mutually exclusive speaker and output mixer paths such as `LDSPK` with `LDLO`, or `RDSPK` with `RDRO`.
- `wm8990_dapm_widgets[]` and `wm8990_dapm_routes[]` define the codec's analog and digital graph: line inputs, input PGAs, input mixers and ADC muxes, ADCs, DACs, output mixers, speaker mixer, output PGAs, MICBIAS, and output pins.
- `pll_factors()` and `wm8990_set_dai_pll()` compute and program PLL `N.K`, optional input prescale, `SDM`, `PLL_ENA`, and `SYSCLK_SRC`.
- `wm8990_set_dai_fmt()`, `wm8990_set_dai_clkdiv()`, `wm8990_hw_params()`, and `wm8990_mute()` implement the DAI operations for master/slave mode, I2S/right-justified/left-justified/DSP formats, clock dividers, sample word length, and DAC mute.
- `wm8990_set_bias_level()` is the main power-state machine. It performs regcache sync after OFF, anti-pop charge/discharge sequencing, VMID/VREF changes, output enables, DAC mute on OFF, and regcache dirty marking.
- `wm8990_probe()` resets the codec, forces standby bias to charge output capacitors, configures GPIO/audio clock output bits, enables OPCLK, and initializes left/right output volume.
- `wm8990_i2c_probe()` allocates private state and registers the ASoC component and DAI through `devm_snd_soc_register_component()`.

## Control flow
The I2C driver's `.probe` allocates `wm8990_priv`, stores it with `i2c_set_clientdata()`, and registers the component. ASoC then calls the component `.probe`, which writes reset and establishes initial power and GPIO/output state. Machine drivers interact with the DAI ops: format is selected with `set_fmt`, clock sources and dividers with `set_sysclk`, `set_pll`, and `set_clkdiv`, PCM word length with `hw_params`, and playback mute with `mute_stream`. During path activation, DAPM evaluates `wm8990_dapm_routes[]`, powers widgets through the PM registers, and invokes `outmixer_event()` before conflicting mixer bits are written.

Bias transitions dominate the runtime power flow. Moving from OFF to STANDBY first syncs the regcache and performs a multi-step anti-pop sequence with 300 ms, 50 ms, 100 ms, and 600 ms sleeps before settling VMID to 2x250k. PREPARE raises VMID to 2x50k. OFF reverses the process by enabling soft-start/discharge controls, muting the DAC, disabling VMID/VREF, discharging outputs, clearing anti-pop bits, and marking the regcache dirty.

## State and persistence behavior
Codec configuration lives in hardware registers accessed through ASoC component helpers and, for cache lifecycle, in `wm8990->regmap`. The driver relies on regcache synchronization after OFF and dirty marking when powering down, but this file does not create the regmap itself. Latched volume controls require the hardware update bit, which is why writes pass through `wm899x_outpga_put_volsw_vu()`. Cached `sysclk` has no direct register write in this file, so machine-driver clock correctness depends on explicit divider and PLL calls.

## Dependencies and integration points
The file depends on Linux I2C, regmap, ALSA ASoC component/DAI/DAPM/control APIs, PCM params helpers, TLV dB descriptions, and register definitions in `wm8990.h`. It integrates with board machine drivers via the DAI name `wm8990-hifi`, ALSA mixer controls, and DAPM routes. Runtime behavior assumes the component driver is registered by I2C and that the wider kernel or MFD setup supplies a valid regmap for `wm8990_priv`.

## Risks and edge cases
- `wm8990_i2c_probe()` never initializes `wm8990->regmap` locally, while `wm8990_set_bias_level()` dereferences it for `regcache_sync()` and `regcache_mark_dirty()`. If no external setup populates it, bias changes can fail or crash.
- `wm8990_hw_params()` silently accepts unsupported widths by leaving 16-bit configuration unchanged instead of returning `-EINVAL`; invalid widths should be caught by advertised formats, but defensive validation is weak.
- PLL setup does not validate zero `freq_in` when `freq_out` is nonzero beyond the outer `if (freq_in && freq_out)`, so a malformed caller disables rather than reports an error.
- The anti-pop sequence uses long blocking sleeps in the bias callback, which is typical for old codec drivers but can delay power transitions.
- Mixer conflict handling returns `-1` rather than a specific errno.
- Several controls and routes are highly register-bit sensitive; mistakes in header masks or shifts would directly misroute audio.

## Test signals
Useful validation includes I2C probe and component registration logs, successful DAPM bias transitions OFF/STANDBY/PREPARE/ON, mixer control writes that set VU bit 8, playback/capture at all advertised rates and formats, PLL lock or clock-derived audio stability for configured MCLK inputs, and attempts to enable mutually exclusive output/speaker routes verifying that `outmixer_event()` rejects them. Suspend/resume testing should confirm regcache dirty/sync behavior through an OFF-to-STANDBY cycle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8990.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8990.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm8990.h

## Purpose
`wm8990.h` is the private register map and bitfield definition header for the WM8990 codec driver. It gives `wm8990.c` symbolic names for register addresses, masks, shifts, individual enable bits, audio interface formats, clock divider encodings, mixer routes, anti-pop controls, GPIO/IRQ fields, and PLL fields.

## Important APIs, types, and definitions
- Register address macros cover the core map from `WM8990_RESET` through `WM8990_PLL3`, plus extended access registers `WM8990_EXT_ACCESS_ENA` and `WM8990_EXT_CTL1` used by the C driver's ADC clocking workaround.
- Power-management fields define output enables, MICBIAS, VMID/VREF, ADC/DAC enables, PLL/OPCLK controls, input PGA enables, output mixer enables, and line output enables.
- Audio interface definitions include word-length masks and encodings, format encodings for right-justified/left-justified/I2S/DSP, master bits, LRCLK/BCLK inversion, TDM bits, and LRCLK rate masks.
- Clock definitions cover MCLK, DACCLK, ADCCLK, and BCLK divider masks and enumerated divider values. The IDs `WM8990_MCLK_DIV`, `WM8990_DACCLK_DIV`, `WM8990_ADCCLK_DIV`, and `WM8990_BCLK_DIV` are consumed by `wm8990_set_dai_clkdiv()`.
- Volume and mixer definitions provide masks/shifts for input PGAs, output PGAs, DAC/ADC digital volumes, sidetone, bypass paths, speaker/class-D controls, and line mixers.
- Anti-pop definitions cover output discharge bits in `ANTIPOP1` and soft-start, buffer, POB, and VMID toggle bits in `ANTIPOP2`.
- PLL definitions expose `WM8990_SDM`, `WM8990_PRESCALE`, and `WM8990_PLLN_MASK`.

## Control flow enabled by this header
The header has no executable control flow, but its symbols drive every register access in `wm8990.c`. DAPM widgets map enable bits from the power-management registers; mixer controls map switch and volume bits from input/output mixer registers; DAI ops map format, word length, clock divider, PLL, and mute bits; bias handling maps anti-pop, VMID, VREF, output discharge, and extended workaround registers.

## State and persistence behavior
The header defines the codec's persistent hardware state layout. There are repeated generic update-bit names such as `WM8990_OPVU`, `WM8990_IPVU`, `WM8990_DAC_VU`, and `WM8990_ADC_VU` for volume update latches across multiple registers. Because the driver uses these masks with regmap/component reads and writes, any incorrect mask or shift persists as incorrect hardware programming until the next reset or regcache sync.

## Dependencies and integration points
This header is tightly coupled to `wm8990.c` and the ALSA ASoC control/DAPM macros that require register, shift, mask, and bit definitions. It is not a public platform-data interface; it is a local codec register contract for the driver.

## Risks and edge cases
- The file repeats macro names for update bits across multiple registers, relying on identical bit values. That is workable in C preprocessing but can obscure which register a given update bit belongs to.
- Some masks are value-width masks rather than fully shifted masks, because ASoC control macros expect a max value paired with a shift. Using these definitions with generic `update_bits()` would be wrong unless shifted first.
- The header does not encode reset defaults, readability, volatility, or access permissions, so cache correctness must come from the C driver or surrounding regmap setup.
- A typo in the many mixer bit definitions would compile cleanly but cause bad DAPM routing or control writes.

## Test signals
Build coverage should catch missing macros used by `wm8990.c`. Runtime signals are indirect: mixer controls should alter the expected register bits, DAPM route activation should power the expected widgets, clock divider controls should update `CLOCKING_1/2`, and bias sequencing should write the anti-pop and VMID fields defined here. Register dump comparison against the WM8990 datasheet is the most direct validation for this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8990.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8991.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm8991.c

## Purpose
`wm8991.c` is an ALSA ASoC codec driver for the Wolfson WM8991. It is closely related to the WM8990 driver but owns its regmap setup, register defaults, reset/chip-ID verification, and component registration. It exposes mixer controls, DAPM routes, DAI format/clock/PLL operations, and anti-pop bias sequencing for a single playback/capture DAI.

## Important APIs, types, and functions
- `struct wm8991_priv` stores the regmap and a cached `pcmclk` field. The regmap is initialized by `wm8991_i2c_probe()` and used by bias and cache operations.
- `wm8991_reg_defaults[]`, `wm8991_volatile()`, and `wm8991_regmap` define the regmap cache baseline, mark reset as volatile, and use an 8-bit register/16-bit value MAPLE cache.
- `wm899x_outpga_put_volsw_vu()` latches volume changes by setting bit 8 after the standard ASoC volume write. The header supplies `SOC_WM899X_OUTPGA_SINGLE_R_TLV()`.
- `wm8991_snd_controls[]` exposes input boost, bypass, output, speaker, DAC/ADC, sidetone, and ADC HPF controls with TLV ranges.
- `outmixer_event()` prevents illegal simultaneous output and speaker mixer source selections.
- `wm8991_dapm_widgets[]` and `wm8991_dapm_routes[]` define line inputs, input PGAs, ADC muxes, ADC/DAC widgets, output mixers, speaker mixer, output PGAs, MICBIAS, and output pins.
- `pll_factors()` and `wm8991_set_dai_pll()` calculate fractional PLL settings and program power, sysclk source, and PLL registers.
- `wm8991_set_dai_fmt()`, `wm8991_set_dai_clkdiv()`, `wm8991_hw_params()`, and `wm8991_mute()` implement DAI operations.
- `wm8991_set_bias_level()` handles VMID/VREF, output discharge, anti-pop, regcache sync, DAC mute, and regcache dirty marking across bias levels.
- `wm8991_i2c_probe()` allocates private data, initializes regmap, verifies reset ID `0x8991`, resets hardware, sets baseline GPIO/clock/VMID/DAC/output registers, and registers the component.

## Control flow
Probe starts at the I2C driver. It allocates state, initializes regmap, reads `WM8991_RESET` as an ID register, rejects non-`0x8991` devices, writes reset, configures GPIO1/audio LRCLK output behavior, enables VREF/VMID and OPCLK, clears DAC control, initializes output volumes with update bits, and registers `soc_component_dev_wm8991` with the `wm8991` DAI.

At stream setup, machine-driver calls enter the DAI ops. `set_fmt` programs master/slave and serial format bits; `set_clkdiv` updates MCLK/DAC/ADC/BCLK dividers; `set_pll` enables or disables the PLL and selects it as SYSCLK; `hw_params` updates the audio word length; `mute_stream` toggles `DAC_MUTE`. DAPM route changes use the widget graph and invoke `outmixer_event()` before committing route bits that may conflict.

Bias transitions follow the same broad anti-pop pattern as WM8990: OFF-to-STANDBY syncs cache, discharges outputs, toggles VMID and output enables with long sleeps, then settles to lower-power VMID. OFF mutes DAC, discharges outputs, disables VREF and anti-pop controls, and marks the cache dirty.

## State and persistence behavior
Unlike WM8990, this driver creates and owns a regmap with defaults, so cached register state has a defined baseline. Reset is volatile and not cached. Register writes during probe establish hardware state before component registration. During power-down, `regcache_mark_dirty()` ensures the next power-up sync replays cached state. The bias callback calls `regcache_sync()` but does not check its return value, so sync failures may be silent in this older driver.

## Dependencies and integration points
The driver depends on Linux I2C, regmap, ASoC component/DAI/DAPM/control APIs, PCM params, TLV helpers, and `wm8991.h`. It integrates with machine drivers through DAI name `wm8991`, with userspace through ALSA controls, and with DAPM through named widgets and output pins such as `LON`, `LOP`, `LOUT`, `SPKN`, `SPKP`, `ROUT`, `OUT4`, `ROP`, `RON`, and `OUT`.

## Risks and edge cases
- `wm8991_set_bias_level()` ignores the return from `regcache_sync()`, unlike newer patterns that abort on sync failure.
- `wm8991_hw_params()` does not return `-EINVAL` for unexpected widths; it relies on the DAI `.formats` mask to prevent invalid widths.
- The driver advertises rates through `SNDRV_PCM_RATE_8000_96000`, while the clock/rate programming is mostly manual and simple; board clock setup must be correct.
- `wm8991_set_dai_pll()` disables the PLL if either input or output frequency is zero, which may hide malformed callers.
- `outmixer_event()` returns `-1` rather than a typed errno.
- Route details include very similar left/right names; accidental bit or route mistakes are hard to detect without audio-path tests.

## Test signals
Probe tests should verify chip-ID rejection and successful registration on ID `0x8991`. Regmap cache behavior should be exercised by OFF-to-STANDBY cycles. Audio tests should cover playback/capture formats S16, S20_3LE, and S24_LE over the advertised rate range, PLL enable/disable and clock-divider changes, DAC mute toggling, DAPM route activation for line/headphone/speaker outputs, and rejection of conflicting speaker/output mixer paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8991.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8991.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm8991.h

## Purpose
`wm8991.h` is the private register and bitfield contract for the WM8991 ASoC codec driver. It maps named registers, masks, shifts, enable bits, PLL/clock divider IDs, and a WM899x volume-control macro used by `wm8991.c`.

## Important APIs, types, and definitions
- Register address macros cover reset, power management, audio interfaces, clocking, DAC/ADC controls and volumes, GPIO/IRQ controls, input/output volumes, class-D/speaker controls, mixer registers, anti-pop, MICBIAS, and PLL registers.
- `WM8991_REGISTER_COUNT` and `WM8991_MAX_REGISTER` describe the size of the register map, while the C driver's regmap uses `WM8991_PLL3` as `max_register`.
- Power bits define speaker, OUT3/OUT4, LOUT/ROUT, MICBIAS, VMID/VREF, ADC/DAC, input PGA, output mixer, OPGA, line output, PLL, thermal shutdown, and OPCLK controls.
- Audio interface bits define word length, data format, TDM, BCLK/LRCLK inversion, master mode, LRCLK direction/rates, companding, loopback, DAC boost, and DAC mute/de-emphasis controls.
- GPIO and interrupt fields define status, debounce, IRQ enable, pull-up/pull-down, polarity, and alternate function selection bits.
- Mixer/volume fields define all input PGA switches, input mixers, output mixers, line mixers, speaker mixer, sidetone, ADC/DAC volumes, output volumes, speaker attenuation/boost, zero-cross, mute, and volume update bits.
- `SOC_WM899X_OUTPGA_SINGLE_R_TLV()` expands to an ASoC extended TLV control using `snd_soc_get_volsw` and the driver's `wm899x_outpga_put_volsw_vu()` callback.

## Control flow enabled by this header
The header is data-only, but it enables all executable paths in `wm8991.c`: probe and reset use the reset and GPIO/power macros; DAI ops use clock, format, PLL, mute, and word-length fields; DAPM widgets and routes use power and mixer bits; controls use masks and shifts; bias sequencing uses anti-pop and VMID/VREF bits.

## State and persistence behavior
These definitions describe the persistent hardware state that is cached in regmap. The same numeric update bit appears under multiple macro names such as `WM8991_DAC_VU`, `WM8991_ADC_VU`, `WM8991_IPVU`, and `WM8991_OPVU`, matching hardware's latch pattern across volume registers. The header itself does not describe volatility or defaults; those are supplied by `wm8991.c`.

## Dependencies and integration points
`wm8991.h` is included by `wm8991.c` and depends on ASoC control helper names for the `SOC_WM899X_OUTPGA_SINGLE_R_TLV()` macro. It is not a standalone public API. Its register constants must remain consistent with the regmap defaults and DAPM/control declarations in the C file.

## Risks and edge cases
- The macro at the end references `wm899x_outpga_put_volsw_vu()`, which must be defined in the including C file before use through control array initialization.
- Several masks are unshifted field maxima intended for ASoC control macros, not full shifted update masks.
- Reused VU macro names have identical values but can make register-specific code harder to audit.
- Header drift from the WM8991 datasheet would manifest as subtle runtime audio path or power issues rather than compile failures.

## Test signals
Compile coverage verifies the macro contract with `wm8991.c`. Runtime validation should include register dumps for DAI format and clock changes, mixer path toggles, volume updates with VU latching, GPIO setup during probe, anti-pop bias transitions, and PLL programming using the masks defined here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8991.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8993.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm8993.c

## Purpose
`wm8993.c` is an ALSA ASoC codec driver for the Wolfson WM8993. Compared with WM8990/WM8991, it adds regulator-managed supplies, explicit readable/volatile regmap policy, FLL-based clock generation with interrupt-assisted lock detection, TDM slot configuration, ReTune Mobile EQ profile support, DRC/EQ controls, and shared Wolfson hub analog routing through `wm_hubs`.

## Important APIs, types, and functions
- `WM8993_NUM_SUPPLIES` and `wm8993_supply_names[]` define the six required regulators: `DCVDD`, `DBVDD`, `AVDD1`, `AVDD2`, `CPVDD`, and `SPKVDD`.
- `wm8993_reg_defaults[]`, `wm8993_volatile()`, `wm8993_readable()`, and `wm8993_regmap` define the register cache defaults, volatile status/readback registers, readable register set, 8-bit register/16-bit value layout, and MAPLE cache.
- `struct wm8993_priv` embeds `struct wm_hubs_data`, device/regmap pointers, regulator bulk data, platform data, an FLL lock completion, DAI clock/format state, TDM state, sample-rate/BCLK state, and cached FLL input/output/source values.
- `fll_factors()` computes FLL reference divider, output divider, FRATIO, integer `N`, and fractional `K` values while enforcing reference and VCO constraints.
- `_wm8993_set_fll()` disables/reconfigures/enables the FLL, selects MCLK/LRCLK/BCLK reference, waits for interrupt completion when available, falls back to short timeouts without IRQ, and caches FLL state. `wm8993_set_fll()` adapts it to the DAI op.
- `configure_clock()` selects MCLK or FLL as SYSCLK, applies MCLK divide when above 13.5 MHz, and caches `sysclk_rate`.
- `wm8993_snd_controls[]` exposes sidetone, DRC, ADC HPF, playback/capture volume, DAC boost/de-emphasis, and speaker DAC controls. `wm8993_eq_controls[]` exposes normal EQ band volumes when platform ReTune configs are absent.
- `wm8993_dapm_widgets[]` and `routes[]` model `CLK_SYS`, `CLK_DSP`, ADCs, AIF muxes, DACs, sidetone muxes, headphone muxes from `wm_hubs`, speaker mixers, and direct voice routing.
- `wm8993_set_bias_level()` coordinates `wm_hubs_set_bias_level()`, regulator enable/disable, regcache cache-only state, VMID startup, thermal shutdown, lineout VMID buffer handling, and bias shutdown.
- `wm8993_set_sysclk()`, `wm8993_set_dai_fmt()`, `wm8993_hw_params()`, `wm8993_mute()`, and `wm8993_set_tdm_slot()` implement the DAI behavior.
- `wm8993_irq()` handles thermal warning and FLL lock interrupts, acknowledges interrupt status, and completes `fll_lock`.
- `wm8993_probe()` initializes hub behavior, default volume update bits, headphone sequencing, clock auto mode, platform analog pdata, controls, DAPM widgets/routes, and idle-bias policy.
- `wm8993_i2c_probe()` allocates state, initializes regmap, obtains/enables regulators, verifies chip ID `0x8993`, resets hardware, applies a regmap patch for DC servo tuning, configures optional IRQ, disables supplies, switches regmap to cache-only, and registers the component.

## Control flow
I2C probe is the hardware bring-up entry point. It allocates `wm8993_priv`, initializes the FLL completion and regmap, gets all regulators, powers the chip, reads and validates the software reset ID, writes reset, applies a small register patch, optionally configures GPIO1 as IRQ and requests a threaded interrupt, then powers regulators back down and leaves regmap cache-only until ASoC bias enables the device. Component registration exposes the single `wm8993-hifi` DAI.

The component probe configures codec-level defaults and topology. It sets hub startup and DC servo defaults, latches DAC/ADC volume update bits, disables automatic headphone power-up so the driver can sequence stereo outputs, selects automatic clock configuration, applies platform analog settings, registers base controls and either ReTune-aware behavior or normal EQ controls, installs DAPM widgets/routes, adds shared hub analog controls/routes, and may disable idle bias when both line outputs are differential.

Stream setup flows through DAI ops. `set_sysclk` records MCLK or FLL source. `set_fmt` programs BCLK/LRCLK master directions, serial format, and clock inversion while remembering whether the codec is master. `set_tdm_slot` enables ADC/DAC TDM for slot masks `0x3` or `0xc` and stores half the slot count plus slot width for BCLK calculation. `hw_params` calculates target BCLK from rate, width, and TDM state, calls `configure_clock`, chooses nearest clock-system and sample-rate table entries, chooses the nearest non-underflow BCLK divider, writes clocking and AIF registers, and optionally swaps in the closest ReTune Mobile EQ configuration for the active sample rate.

FLL control can be called independently by machine drivers. Reconfiguration always disables the FLL first, writes fractional/integer factors and source selection, enables the FLL, waits for `wm8993_irq()` to complete lock when IRQ exists, and caches the configured reference/output/source. Suspend stops the FLL in an orderly way, preserves cached desired FLL values, and forces bias off. Resume forces standby and restarts the FLL if it had been active.

Bias control is regulator and cache aware. OFF-to-STANDBY enables supplies, leaves cache-only mode, syncs cached registers, enables VMID through shared hub code, performs a fast soft-start VMID ramp, enables lineout VMID buffering if single-ended lineouts need it, and then settles to lower-power VMID. OFF clears VMID and anti-pop bits, enables cache-only mode, marks the cache dirty, and disables regulators.

## State and persistence behavior
Persistent software state includes selected system clock source, MCLK/SYSCLK rates, stream sample rate, calculated BCLK, TDM parameters, FLL reference/output/source, platform analog configuration, ReTune profiles, and hub DC servo/startup data. Hardware register state is cached by regmap while supplies are off; `regcache_cache_only(true)` and `regcache_mark_dirty()` on OFF prevent stale hardware assumptions, while OFF-to-STANDBY syncs cached state after regulators are enabled. The FLL lock completion is edge-triggered by IRQ status, with timeout fallback when no IRQ is wired.

## Dependencies and integration points
The driver depends on Linux I2C, regmap, regulator bulk APIs, IRQ handling, completions, ASoC component/DAI/DAPM/control APIs, PCM params, platform data from `<sound/wm8993.h>`, local register definitions in `wm8993.h`, and shared analog helper code in `wm_hubs.h`. It integrates with board code through regulator names, optional I2C IRQ, WM8993 platform data including lineout/micbias/ReTune settings, DAI name `wm8993-hifi`, and DAPM pins/routes provided by both this file and `wm_hubs`.

## Risks and edge cases
- `wm8993_set_bias_level()` does not check `regcache_sync()` return, so failed cache replay after regulator enable may be missed.
- `fll_factors()` error messages print `Fref` with an "MHz" label even though the value is in Hz.
- FLL lock without IRQ uses fixed 1 ms or 3 ms waits and does not verify a lock bit afterward; marginal boards may proceed before stable lock.
- `wm8993_hw_params()` chooses nearest clock/sample entries rather than exact matches and does not explicitly reject large approximation errors.
- In TDM mode `wm8993->tdm_slots = slots / 2`; odd slot counts are not explicitly rejected.
- `wm8993_set_tdm_slot()` allows only masks `0x3` and `0xc` for active codec slots, though comments note it may generate clocks for wider slot layouts it cannot itself use.
- Probe manually requests an IRQ rather than devm-managed IRQ, requiring the remove/error paths to free it correctly.
- Regulator disable is called in remove even though supplies may already be disabled/cache-only from probe or bias OFF; bulk regulator APIs usually tolerate balanced states only if calls are balanced by successful enables.

## Test signals
Probe validation should cover missing regulators, invalid chip ID, reset success, regmap patch application, optional IRQ registration, and component registration. Power tests should exercise OFF-to-STANDBY-to-OFF transitions while checking regulator enable/disable and regcache cache-only state. Clock tests should cover MCLK and FLL SYSCLK sources, high MCLK/FLL divide behavior, FLL disable/reconfigure/re-enable, IRQ-driven FLL lock completion, and no-IRQ timeout paths. Audio tests should cover S16/S20/S24/S32 playback and capture at 8-48 kHz, symmetric-rate enforcement, BCLK/LRCLK calculations, TDM masks `0x3` and `0xc`, DAC mute, ADC/DAC mux routing, sidetone, DRC controls, EQ controls or ReTune profile selection, and shared `wm_hubs` analog routes for headphone, speaker, lineout, MICBIAS, and DC servo behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8993.c -->
