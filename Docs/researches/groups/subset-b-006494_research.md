# subset-b-006494 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8962.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm8962.h

## Purpose

`wm8962.h` is the private register-definition header for the WM8962 ASoC codec driver. It gives `wm8962.c` stable symbolic names for codec clock sources, FLL source IDs, register addresses, and per-field masks/shifts/widths across the normal control page, GPIO/IRQ page, write sequencer, DSP2 RAM, EQ, DRC, ReTune, HD bass, virtual surround, and microphone-detection areas. It also declares the one exported helper, `wm8962_mic_detect()`, used by machine drivers to hook the codec IRQ-based jack/microphone detection path into an ALSA jack.

## Important APIs, Types, and Macros

- Public-ish DAI clock IDs: `WM8962_SYSCLK_MCLK`, `WM8962_SYSCLK_FLL`, and `WM8962_SYSCLK_PLL3` are consumed by `wm8962_set_dai_sysclk()` in the companion driver to select `CLOCKING2.SYSCLK_SRC`.
- FLL IDs and sources: `WM8962_FLL`, `WM8962_FLL_MCLK`, `WM8962_FLL_BCLK`, `WM8962_FLL_OSC`, and `WM8962_FLL_INT` feed `wm8962_set_fll()` and determine the reference-clock source, oscillator enablement, forced NCO mode, and final `FLL_CONTROL_*` programming.
- Register address macros: low addresses cover audio volumes, clocking, audio interface format, ALC/noise gate, power management, anti-pop, mixers, charge pump, PLL/FLL, and control interface. Higher address regions cover GPIOs at `WM8962_GPIO_BASE`, interrupts, DSP2, write sequencer slots, DSP RAM, ReTune coefficient RAM, HD bass, virtual surround, EQ, DRC, and soundstage enables.
- Bitfield macros: for each register section the header exposes raw value macros plus `_MASK`, `_SHIFT`, and `_WIDTH` variants, which let `wm8962.c` use `snd_soc_component_update_bits()`, `regmap_update_bits()`, and ALSA control macros without literal register fields.
- Exported function declaration: `int wm8962_mic_detect(struct snd_soc_component *component, struct snd_soc_jack *jack);` is defined and exported by `wm8962.c`; it enables/disables microphone detect IRQs and reports jack state to the supplied `snd_soc_jack`.

There are no structs or inline functions in this header. The only included external types are from `<asm/types.h>` and `<sound/soc.h>`, needed for fixed-width types and `struct snd_soc_component` / `struct snd_soc_jack` names in the declaration.

## Control Flow

The header has no executable control flow. Its definitions drive companion-driver control flow in several places:

- Regmap readability/volatility/default handling switches on the address macros to classify large sparse register ranges, including DSP and ReTune RAM.
- DAI setup uses interface and clocking masks such as `WM8962_FMT_MASK`, `WM8962_WL_MASK`, `WM8962_BCLK_DIV_MASK`, `WM8962_SYSCLK_RATE_MASK`, and `WM8962_SYSCLK_SRC_MASK`.
- FLL setup writes `WM8962_FLL_CONTROL_1/2/3/5/6/7/8` with `WM8962_FLL_FRAC`, reference-source, divider, theta/lambda, and N fields.
- DSP2 controls use `WM8962_DSP2_POWER_MANAGEMENT`, `WM8962_DSP2_EXECCONTROL`, and `SOUNDSTAGE_ENABLES_*` fields for run/stop sequencing and DSP-backed feature toggles.
- IRQ handling reads status/mask registers and uses mic/FLL/PLL/thermal event bits such as `WM8962_MICD_EINT`, `WM8962_MICSCD_EINT`, and `WM8962_FLL_LOCK_EINT`.
- GPIO support derives register addresses from `WM8962_GPIO_BASE + offset`, with a companion-driver special case for the missing GPIO4 register.

## State and Persistence Behavior

The file defines state layout rather than holding state. It is authoritative for which codec bits are persistent in the regmap cache, which fields are treated as volatile status, and which write-only/reset/write-sequencer locations the driver must handle specially. The sparse address space is especially important: write sequencer entries start at `0x1000`, DSP RAM spans multiple high address windows, and algorithm coefficient regions start around `0x4000`. Any regmap configuration, cache sync, suspend/resume, or firmware-style coefficient write depends on these exact addresses.

## Dependencies and Integration Points

- Integrated directly by `sources/distributed-fs/ceph-client/sound/soc/codecs/wm8962.c`.
- Integrated indirectly with ALSA SoC core through `snd_soc_component`, `snd_soc_jack`, DAI clock/FLL callbacks, kcontrols, DAPM widgets, and jack reporting.
- Register constants map to regmap I/O over the WM8962 control bus; companion code decides bus details, cache policy, volatile registers, and IRQ registration.
- Machine drivers can call `wm8962_mic_detect()` after binding the codec component and jack.

## Risks and Edge Cases

- This is generated-style hardware metadata: a one-bit mask or shift error can silently program the wrong analog, clock, DSP, or IRQ field.
- Several generic field names intentionally repeat across left/right registers, such as volume update bits. Reusing the wrong generic macro with a side-specific register is easy during maintenance.
- The register map is sparse and very large. Code that assumes small contiguous register numbers would mishandle write sequencer, DSP, and coefficient windows.
- GPIO indexing is non-contiguous; `wm8962.c` already notes that `WM8962_GPIO_BASE + 3` does not exist, so consumers must not blindly iterate every offset as valid hardware.
- IRQ polarity and microphone-detection bits are tightly coupled. Mistakes in `MICINT_SOURCE_POL` or interrupt masks can cause stuck or inverted jack events.
- The header is private to the codec driver directory. External machine-driver usage should go through exported symbols rather than depending on internal register constants unless the kernel tree intentionally exposes them.

## Test Signals

- Build coverage for `snd-soc-wm8962` is the primary compile-time check that all register, mask, and declaration names still match `wm8962.c`.
- Runtime smoke tests should exercise DAI clock source selection, FLL lock/unlock paths, suspend/resume cache sync, and jack insertion/removal via `wm8962_mic_detect()`.
- Regmap debugfs or tracepoints can confirm writes to `CLOCKING*`, `FLL_CONTROL_*`, IRQ mask/status, GPIO, and DSP2 registers use expected addresses and values.
- A useful static check is comparing all `_MASK/_SHIFT/_WIDTH` triples against the vendor register map or regenerated header source after any mechanical update.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8962.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8971.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm8971.c

## Purpose

`wm8971.c` implements the ALSA SoC codec component and I2C driver for the Wolfson WM8971 stereo audio codec. It registers one DAI named `wm8971-hifi`, exposes mixer controls for capture, playback, tone, ALC, noise gate, bypass, mic boost, and muxing, declares a DAPM audio graph for ADC/DAC/input/output power routing, manages the codec register cache with regmap, and sequences bias/VMID charging to reduce pops during power transitions.

## Important APIs, Types, and Functions

- `struct wm8971_priv`: private component state containing the selected `sysclk`, delayed VMID charge work, and the regmap pointer.
- `wm8971_reg_defaults[]`: 43 9-bit register defaults used by regmap because two-wire control cannot read back the codec register space reliably.
- `wm8971_snd_controls[]`: ALSA controls for volumes, zero-cross switches, mutes, tone controls, ALC/noise gate parameters, attenuation, de-emphasis, playback phase/function, and mic boost.
- `wm8971_dapm_widgets[]` and `wm8971_dapm_routes[]`: DAPM power graph connecting `LINPUT1`, `RINPUT1`, and `MIC` through PGAs/muxes/ADCs and DAC/bypass paths to headphone, speaker, and mono outputs.
- `coeff_div[]` and `get_coeff()`: supported MCLK/sample-rate table for 11.2896, 12, 12.288, 16.9344, and 18.432 MHz clocks over 8 kHz through 96 kHz rates.
- DAI ops: `wm8971_set_dai_sysclk()`, `wm8971_set_dai_fmt()`, `wm8971_pcm_hw_params()`, and `wm8971_mute()`.
- Power callbacks: `wm8971_charge_work()` and `wm8971_set_bias_level()`.
- Driver binding: `wm8971_i2c_probe()` allocates private data, initializes I2C regmap, attaches client data, and registers the ASoC component plus DAI; `module_i2c_driver()` publishes the I2C module.

## Control Flow

Probe begins in `wm8971_i2c_probe()`: allocate private state, initialize a 7-bit-register/9-bit-value I2C regmap with `REGCACHE_MAPLE`, store client data, then register `soc_component_dev_wm8971` and `wm8971_dai`. Component probe initializes delayed work, issues software reset through `WM8971_RESET`, and sets volume-update bits on DAC, output, and input volume registers so stereo updates latch coherently.

DAI configuration is split across callbacks. `set_sysclk()` accepts only the hard-coded MCLK values and stores the chosen frequency. `set_fmt()` maps ASoC master/slave, I2S/right-justified/left-justified/DSP A/DSP B, and clock inversion flags into `WM8971_IFACE`. `hw_params()` combines current interface bits with sample width, looks up the MCLK/rate coefficient, writes `WM8971_IFACE`, and if a coefficient exists writes sample-rate bits to `WM8971_SRATE`. `mute_stream()` toggles bit `0x8` in `WM8971_ADCDAC`; `.no_capture_mute = 1` means this only applies to playback mute behavior.

Bias transitions preserve analog state. OFF cancels pending charge work and leaves `WM8971_PWR1` at `0x0001`. STANDBY from OFF syncs the cache, sets VMID to 5 kOhm for fast charging, and queues delayed work to move VMID to 500 kOhm after one second. PREPARE flushes that delayed work. ON sets VMID to 50 kOhm and enables VREF/output bias bits. STANDBY from a higher state mutes DACs and uses the lower-power VMID setting.

## State and Persistence Behavior

The driver keeps persistent runtime state in `wm8971_priv.sysclk` and `charge_work`. Register state is persisted in regmap cache because reads are unavailable or unreliable on the two-wire bus path. Bias state is represented in hardware registers plus DAPM's current bias level; transition decisions depend on `snd_soc_dapm_get_bias_level()`. Delayed work is part of the power state machine and must be flushed or canceled during bias changes to avoid stale VMID updates after power-off.

## Dependencies and Integration Points

- Includes Linux module, I2C, PM, delay, regmap, workqueue, and ALSA SoC/PCM headers.
- Depends on `wm8971.h` for register addresses and `WM8971_SYSCLK`.
- Built through `sound/soc/codecs/Makefile` as `snd-soc-wm8971.o` under `CONFIG_SND_SOC_WM8971`.
- Integrates with machine drivers through the codec DAI name `wm8971-hifi`, I2C modalias `wm8971`, ALSA controls, and DAPM widgets/routes.
- Uses the system power-efficient workqueue for the VMID post-charge step.

## Risks and Edge Cases

- `hw_params()` does not fail if `get_coeff()` returns `-EINVAL`; it silently leaves the sample-rate register unchanged. If `set_sysclk()` was not called or a machine driver selects a non-table MCLK/rate pair, audio may run with stale or default clocking while stream startup reports success.
- `WM8971_FORMATS` advertises 16/20/24-bit PCM, while `hw_params()` also handles 32-bit width. That 32-bit branch is effectively unreachable unless advertised formats change.
- The DAPM mono route names appear inconsistent: widgets declare `"Mono Out 1"` and output `"MONO"`, while routes use `"Mono Out"` and `"MONO1"`. If not matched elsewhere, the mono output path may not power or route as intended.
- Several DAPM routes reference `"Differential Mux"` even no explicit widget with that name is declared in this file. This may be legacy virtual routing, but it is a route-resolution risk.
- Delayed work touches `WM8971_PWR1`; cancellation/flush paths are correct, but any future remove/shutdown path must preserve them.
- The `WM8971_REG_COUNT` macro is unused; register coverage is controlled by regmap defaults and `max_register`.

## Test Signals

- Compile `snd-soc-wm8971` and boot with an I2C WM8971 device to verify component registration and DAI enumeration.
- Use `amixer` to enumerate controls and confirm volume update bits avoid one-sided volume latching.
- Start playback and capture across supported MCLK/rate combinations, especially 12 MHz USB-mode coefficients and 88.2/96 kHz.
- Validate `set_sysclk()` failure for unsupported clocks and inspect whether unsupported rate/sysclk pairs should fail in `hw_params()`.
- Use DAPM debugfs to check that headphone, speaker, mono, ADC, bypass, mic, line, and differential routes resolve and power as expected.
- Exercise suspend/resume and OFF/STANDBY/PREPARE/ON transitions while watching VMID register writes and delayed work behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8971.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8971.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm8971.h

## Purpose

`wm8971.h` is the private register-address header for the WM8971 codec driver. It maps human-readable names to the codec's 7-bit register addresses and defines the single DAI sysclk ID used by machine drivers when configuring `wm8971-hifi`.

## Important APIs, Types, and Macros

- Register address macros cover input volume (`WM8971_LINVOL`, `WM8971_RINVOL`), headphone/speaker/mono volumes, ADC/DAC control, audio interface, sample rate, DAC and ADC volume, bass/treble, reset, ALC/noise gate, additional controls, power management, input routing, output mixers, and mono output volume.
- `WM8971_RESET` is written with zero by the component probe to reset the codec.
- `WM8971_PWR1` and `WM8971_PWR2` are the key power/bias/DAPM registers used by the driver.
- `WM8971_IFACE` and `WM8971_SRATE` are programmed by DAI format and `hw_params()` callbacks.
- `WM8971_SYSCLK` is the clock ID accepted by the DAI sysclk interface, although the current implementation ignores the ID and validates only the frequency.

There are no structs, functions, or inline helpers in this header.

## Control Flow

The header has no executable control flow. Its constants are consumed by `wm8971.c` in regmap defaults, ALSA control declarations, DAPM widgets/routes, DAI format/sample-rate programming, mute handling, bias transitions, software reset, and I2C regmap `max_register`.

## State and Persistence Behavior

The header defines the persistent register namespace. Regmap cache persistence and bias state are implemented in `wm8971.c`, with these addresses identifying which hardware locations hold volumes, mutes, mixers, sample-rate state, and power state.

## Dependencies and Integration Points

- Included only by the local WM8971 codec driver in this source tree.
- Indirectly integrated with ALSA SoC machine drivers via DAI setup and control names from `wm8971.c`.
- Register values must align with the WM8971 data sheet and with the default table in `wm8971.c`.

## Risks and Edge Cases

- The header intentionally defines only addresses, not bit masks. Most bit positions in `wm8971.c` are literal constants, so future maintenance has less compile-time naming protection than newer generated headers.
- An incorrect address macro would affect multiple subsystems at once because the same names are reused in controls, DAPM, bias, and DAI setup.
- `WM8971_SYSCLK` is defined but not checked by `wm8971_set_dai_sysclk()`, so callers using a wrong `clk_id` would not be rejected as long as the frequency is supported.

## Test Signals

- Build coverage catches missing or renamed register constants.
- Runtime control enumeration and DAPM route tests validate that the address map matches hardware behavior.
- Clocking tests should verify `WM8971_IFACE` and `WM8971_SRATE` programming through regmap traces.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8971.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8974.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm8974.c

## Purpose

`wm8974.c` implements the ALSA SoC codec and I2C driver for the Wolfson WM8974, a mono-oriented codec with speaker, mono, mic, aux, ADC, DAC, EQ, ALC, limiter, companding, and PLL/clock-divider support. It registers one DAI named `wm8974-hifi`, exposes ALSA controls with TLV scales, builds the DAPM graph for input/output power routing, computes PLL factors and MCLK divisors, and handles codec reset, regmap cache, I2C binding, and bias power transitions.

## Important APIs, Types, and Functions

- `struct wm8974_priv`: stores selected input master clock `mclk` and stream sample rate `fs`; these fields jointly drive clock programming.
- `wm8974_reg_defaults[]`: regmap reset/default cache for registers 0 through `WM8974_MONOMIX`.
- Control arrays: `wm8974_snd_controls[]`, `wm8974_speaker_mixer_controls[]`, `wm8974_mono_mixer_controls[]`, `wm8974_boost_mixer[]`, and `wm8974_inpga[]`.
- DAPM graph: widgets model DAC, ADC, aux input, input PGA, boost mixer, speaker mixer, mono mixer, mic bias, speaker outputs, mono output, and physical inputs.
- PLL helpers: `struct pll_`, `FIXED_PLL_SIZE`, and `pll_factors()` compute PLL pre-divider, N, and 24-bit K values for `WM8974_PLLN/PLLK*`.
- Clock helpers: `wm8974_set_dai_pll()`, `wm8974_set_dai_clkdiv()`, `wm8974_get_mclkdiv()`, and `wm8974_update_clocks()`.
- DAI ops: `wm8974_set_dai_sysclk()`, `wm8974_set_dai_fmt()`, `wm8974_pcm_hw_params()`, `wm8974_mute()`, plus explicit `.set_clkdiv` and `.set_pll`.
- Driver binding: `wm8974_i2c_probe()` allocates private data, initializes I2C regmap, and registers the component; I2C ID and OF compatible `"wlf,wm8974"` are exported.

## Control Flow

Probe allocates `wm8974_priv`, stores it as I2C client data, initializes regmap with 7-bit register and 9-bit value fields, then registers `soc_component_dev_wm8974` and `wm8974_dai`. Component probe issues a software reset through `WM8974_RESET` and fails registration if reset write fails.

DAI setup separates format, clock, and stream parameters. `set_sysclk()` accepts only input clocks, stores `priv->mclk`, and calls `wm8974_update_clocks()`. `hw_params()` stores `priv->fs`, updates clocks, sets word length in `WM8974_IFACE`, maps sample rate to ADC/DAC filter coefficients in `WM8974_ADD`, and writes both registers. `set_fmt()` maps master/slave, serial format, and inversion flags into `WM8974_IFACE` and `WM8974_CLOCK`; DSP_A rejects frame-inversion modes that are not supported. `mute_stream()` toggles DAC mute bit `0x40`.

Clock update is stateful. If either `mclk` or `fs` is missing, `wm8974_update_clocks()` returns success without programming. Once both are known, it targets 256 * sample-rate, chooses the closest supported MCLK divider, and if direct division cannot use the supplied MCLK it selects a PLL target near 22.5792 MHz for 44.1 kHz-family rates or 24.576 MHz for 8 kHz-family rates. It then enables/disables PLL through `wm8974_set_dai_pll()` and writes the MCLK divider.

Bias management writes `WM8974_POWER1/2/3`. ON and PREPARE use VMID 50 kOhm. STANDBY enables bias and BUFIO, syncs the regcache when coming from OFF, charges caps at VMID 5 kOhm for 100 ms, then drops to VMID 500 kOhm. OFF clears the three power registers.

## State and Persistence Behavior

The codec register state is cached in regmap with `REGCACHE_FLAT`. Runtime clock state is split between `priv->mclk` from machine-driver sysclk configuration and `priv->fs` from PCM params; clock programming may therefore occur in either callback once both are present. Bias state is held in hardware power registers plus DAPM's previous bias level. The PLL state persists until explicitly disabled by `set_pll()` with zero input/output or changed by `update_clocks()`.

## Dependencies and Integration Points

- Includes Linux I2C, regmap, delay, module, PM, and ALSA SoC/PCM/TLV headers.
- Depends on `wm8974.h` for register addresses and divider constants.
- Built through `sound/soc/codecs/Makefile` as `snd-soc-wm8974.o` under `CONFIG_SND_SOC_WM8974`.
- Integrates with machine drivers through DAI name `wm8974-hifi`, I2C modalias `wm8974`, OF compatible `"wlf,wm8974"`, ASoC clock/PLL/divider callbacks, controls, and DAPM endpoints (`MICN`, `MICP`, `AUX`, `SPKOUTP/N`, `MONOOUT`).
- This driver is also referenced by comments in other codec drivers and ASoC documentation as an example/basis.

## Risks and Edge Cases

- `wm8974_update_clocks()` returns success when only `mclk` or `fs` is known. That supports flexible callback ordering, but a machine driver that never calls `set_sysclk()` can reach stream startup without valid clock programming.
- `wm8974_set_dai_sysclk()` validates direction but not `clk_id`, so unexpected clock IDs are accepted as long as direction is input.
- `pll_factors()` only prints a warning when calculated N is outside the recommended 6-12 range; it still programs the PLL.
- `wm8974_set_dai_pll()` ignores `pll_id` and `source`; this is normal for a single PLL but leaves no validation if callers pass meaningless IDs.
- `hw_params()` does not reject unsupported sample rates in its filter-coefficient switch. The DAI advertises only 8-48 kHz, so ALSA should constrain this, but direct misuse would leave prior/default filter bits.
- The control table defines both `"High Pass Filter Switch"` and `"ADC 128x Oversampling Switch"` on `WM8974_ADC` bit 8. If the datasheet does not intentionally alias this bit, userspace controls may fight over the same hardware bit.
- `playback.channels_max` and `capture.channels_max` are 2 with comments stating only one channel of data. Machine drivers and userspace may need route/channel constraints to avoid assuming true stereo hardware.

## Test Signals

- Build and module-load tests should verify I2C and OF modalias tables, component registration, and reset write success.
- PCM tests should run 8, 11.025, 16, 22.05, 32, 44.1, and 48 kHz with representative MCLKs to observe direct-MCLK versus PLL-backed clock paths.
- Regmap traces should confirm PLL disable uses `CLOCK` bit `0x100` clear and `POWER1` PLL bit clear, while PLL enable writes `PLLN/PLLK1/PLLK2/PLLK3` before selecting PLL as codec clock.
- DAPM debugfs can validate that mic/aux capture and DAC/aux/bypass playback routes power the expected widgets.
- `amixer` should be checked for duplicate or aliased ADC bit controls, TLV scale display, and speaker/mono mute behavior.
- Suspend/resume and OFF-to-STANDBY tests should confirm regcache sync and VMID charge delay do not pop or leave outputs powered.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8974.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8974.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm8974.h

## Purpose

`wm8974.h` is the private register and clock-divider constant header for the WM8974 codec driver. It maps codec register addresses and DAI clock-divider IDs/values into symbolic macros used by `wm8974.c`.

## Important APIs, Types, and Macros

- Register address macros cover reset, three power registers, audio interface, companding, clocking, additional control, GPIO, DAC/ADC control and volume, EQ bands, limiter, notch filters, ALC/noise gate, PLL, input PGA/boost, output mixer, speaker volume, and mono mixer.
- `WM8974_CACHEREGNUM` documents a 57-register cache size, although current regmap setup uses `max_register`, `reg_defaults`, and `ARRAY_SIZE()` rather than this macro.
- Divider IDs `WM8974_OPCLKDIV`, `WM8974_MCLKDIV`, and `WM8974_BCLKDIV` are accepted by `wm8974_set_dai_clkdiv()`.
- Divider values `WM8974_OPCLKDIV_*`, `WM8974_BCLKDIV_*`, and `WM8974_MCLKDIV_*` are pre-shifted bitfield values ORed into `WM8974_GPIO` or `WM8974_CLOCK`.

There are no structs, function declarations, or inline helpers in this header.

## Control Flow

The header itself has no control flow. `wm8974.c` uses these constants for reset, regmap bounds, ALSA controls, DAPM widgets, PLL writes, clock-divider writes, DAI interface setup, filter coefficient setup, mute, and bias power transitions.

## State and Persistence Behavior

The file defines where state lives in the hardware. Persistent state includes power bits in `POWER1/2/3`, interface format in `IFACE`, PLL parameters in `PLLN/PLLK*`, clock dividers in `CLOCK` and `GPIO`, and signal-path state in mixer, ADC, DAC, PGA, speaker, and mono registers. Regmap cache persistence is implemented in `wm8974.c` using these addresses.

## Dependencies and Integration Points

- Included by the local WM8974 codec implementation.
- Divider constants are part of the ASoC DAI `.set_clkdiv` integration; machine drivers may pass these values through the codec DAI ops.
- Register names must match the WM8974 data sheet and the default table in `wm8974.c`.

## Risks and Edge Cases

- Divider macros are already shifted values, not plain divisors. Callers must pass the symbolic macros rather than numeric division factors.
- `WM8974_CACHEREGNUM` can become stale because the active cache setup does not derive from it.
- Like `wm8971.h`, this header defines addresses but not per-field masks for most registers, so the C driver still relies on literal bit masks.
- Incorrect register addresses for PLL or clock registers would cause visible stream-rate failures; incorrect mixer/output addresses would present as missing controls or dead DAPM paths.

## Test Signals

- Compile coverage catches missing names and DAI divider macro references.
- Runtime clock tests should exercise every `WM8974_MCLKDIV_*` value reachable from `wm8974_get_mclkdiv()` and explicit `set_clkdiv()` calls for OPCLK/BCLK.
- Regmap tracing can verify that address constants match the hardware writes expected by reset, PLL setup, mute, and bias transitions.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8974.h -->
