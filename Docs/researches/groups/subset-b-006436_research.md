# Research: subset-b-006436

Grouped research report for DA7219 AAD, DA7219 codec, and DA732x codec sources under `sources/distributed-fs/ceph-client/sound/soc/codecs/`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/da7219-aad.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/da7219-aad.c

## Purpose

`da7219-aad.c` implements the DA7219 accessory auto-detect block for the main DA7219 ASoC codec driver. It owns headset/headphone/line-out detection, four-button headset reporting, mic-bias preparation for 4-pole jacks, headphone impedance testing for non-headset plugs, DT/ACPI firmware property conversion for AAD tuning, IRQ handling, and AAD suspend/resume integration.

## Important APIs, Types, and Functions

- `da7219_aad_jack_det()` is the public bridge from the codec component `.set_jack` callback. It stores the `snd_soc_jack`, sends an initial empty jack report, resets `jack_inserted`, and enables or disables `DA7219_ACCDET_EN_MASK`.
- `da7219_aad_probe()` allocates `struct da7219_aad_priv`, attaches it to `struct da7219_priv`, and fills missing AAD platform data from the firmware child node `da7219_aad`.
- `da7219_aad_init()` binds the component pointer, applies platform data to AAD registers, creates a single-thread `da7219-aad` workqueue, initializes button/headphone-test/ground-switch work items, requests a threaded IRQ, and unmasks AAD IRQs.
- `da7219_aad_exit()` masks AAD IRQs, frees the IRQ, cancels all queued work, and destroys the workqueue.
- `da7219_aad_irq_thread()` is the central threaded interrupt handler. It reads and acknowledges `ACCDET_IRQ_EVENT_A/B`, interprets jack insertion/removal/detect-complete/button events, queues slower work, maintains `jack_inserted`, and emits `snd_soc_jack_report()` updates.
- `da7219_aad_btn_det_work()` prepares headphone outputs and mic bias, optionally pulses mic bias to wake headset microphones, then enables button-detection timing with `btn_cfg`.
- `da7219_aad_hptest_work()` performs a destructive but restored headphone load test using the tone generator, DACs, mixout path, HP amps, charge pump, PLL/MCLK, and regmap cache synchronization. It reports `SND_JACK_HEADPHONE` or `SND_JACK_LINEOUT`.
- `da7219_aad_suspend()` and `da7219_aad_resume()` disable or restore AAD when the parent codec is not a wake source, including mic-bias restoration for an inserted 4-pole jack.
- Firmware parsing helpers translate `dlg,*` properties into `sound/da7219-aad.h` enum values and register fields.

## Control Flow

The normal jack flow starts when `da7219_aad_jack_det()` enables ACCDET. A hardware IRQ wakes `da7219_aad_irq_thread()`, which bulk-reads event registers, reads `ACCDET_STATUS_A`, schedules ground-switch enable work on jack insertion, then writes the event bytes back to clear latched interrupts. On detect complete, it cancels the pending ground-switch work, disables the ground switch, and branches by `JACK_TYPE_STS`: 4-pole jacks immediately report `SND_JACK_HEADSET` and queue `btn_det_work`; non-headset plugs queue `hptest_work` to decide headphone versus line-out. Button press and release bits are translated to `SND_JACK_BTN_0` through `SND_JACK_BTN_3`. Removal cancels all delayed or pending work, undrives HP outputs, disables button detection and mic bias, clears the ground switch, resets `jack_inserted`, and reports a zero state for the full AAD mask.

The headphone-test path locks DAPM, `ctrl_lock`, and `pll_lock`, then temporarily changes many audio-path registers with regcache bypass enabled so the previous cached settings can be restored. If MCLK is absent it uses an internal oscillator frequency and additional settle delays; if MCLK exists but PLL is bypassed it temporarily enables the PLL. After tone generation and comparator readout, it syncs individual register regions from cache back to hardware, restores gain ramp and PLL state, disables any prepared MCLK, unlocks, and reports only if `jack_inserted` is still true.

## State and Persistence

Persistent runtime state lives in `struct da7219_aad_priv`: IRQ number, component pointer, jack pointer, workqueue and work items, platform-tuned mic-bias pulse settings, button timing, ground-switch delay, `jack_inserted`, and `micbias_resume_enable`. It also modifies parent `struct da7219_priv` state through `micbias_on_event`, `regmap`, `mclk`, `pll_lock`, and `ctrl_lock`. Hardware state is mainly DA7219 ACCDET registers plus hidden vendor/unlock registers `0xF0`, `0x75`, and `0xFB`. The driver relies on regmap cache to restore user-visible audio controls after HP test, and on DAPM pin state to persist mic-bias power intent.

## Dependencies and Integration Points

The file depends on the main DA7219 codec private structure and exported `da7219_set_pll()`. It integrates with ALSA ASoC jack reporting, DAPM, regmap, Linux workqueues, threaded IRQs, device properties/fwnodes, I2C client data, clocks, and PM wake IRQ support. Public platform enums and pdata come from `<sound/da7219-aad.h>` and `<sound/da7219.h>`, while local register definitions come from `da7219-aad.h` and `da7219.h`.

## Risks and Edge Cases

- `da7219_aad_init()` returns immediately if `request_threaded_irq()` fails, but the workqueue was already created; a failure path leak is possible unless caller teardown handles an only partially initialized AAD block.
- The IRQ handler uses raw register addresses `0xFB`, `0xF0`, and `0x75`; these hidden-page writes are hard to audit against datasheet revisions and can break silently if register paging semantics change.
- `delay = gnd_switch_delay * (internal_osc ? 2 : 1) - 2` can become small or negative if future configuration changes produce low delays.
- HP test temporarily rewrites many live audio-path registers. Locking protects DAPM, controls, and PLL, but concurrent low-level register writes outside those locks could still race the cache-restore sequence.
- Mic-bias status polling only warns on timeout and continues enabling button detection, so marginal hardware may produce incorrect button events.
- The IRQ handler calls `snd_soc_jack_report()` even with a zero `mask` in some paths; harmless but useful to watch for redundant reports.

## Test Signals

Useful validation includes jack insertion/removal tests for 3-pole and 4-pole accessories, line-out versus headphone impedance classification, button A/B/C/D press and release reporting, suspend/resume with an inserted headset, wake-source versus non-wake-source suspend behavior, IRQ storm or spurious IRQ handling, and register-cache restoration after HP test while user controls have non-default values. Kernel logs to watch include failed IRQ/event reads, mic-bias timeout warnings, SRM/PLL messages from the parent codec, and missing or incorrect `SND_JACK_*` input events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/da7219-aad.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/da7219-aad.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/da7219-aad.h

## Purpose

`da7219-aad.h` is the local private contract for the DA7219 accessory auto-detect implementation. It defines ACCDET register addresses, bit masks, timing constants, private AAD state, and the internal functions used by `da7219.c` and `da7219-aad.c`.

## Important APIs, Types, and Constants

- Register definitions cover `DA7219_ACCDET_STATUS_A/B`, IRQ event/mask registers, and `DA7219_ACCDET_CONFIG_1` through `_8`.
- Bit fields define jack insertion, jack type, pin order, mic-bias-up status, button press/release events, IRQ masks, debounce/rate fields, button threshold registers, averaging/repeat controls, force bits, and headphone-test controls.
- `DA7219_AAD_MAX_BUTTONS` and `DA7219_AAD_REPORT_ALL_MASK` describe the supported ALSA jack reporting surface.
- Timing constants include mic-bias polling delay/retries and headphone-test ramp, period, and internal oscillator path delays.
- `enum da7219_aad_event_regs` indexes the two event bytes used in bulk regmap reads/writes.
- `struct da7219_aad_priv` is the complete private runtime state for the AAD subdriver.
- Exports include `da7219_aad_jack_det()`, optional PM helpers, `da7219_aad_init()`, `da7219_aad_exit()`, and `da7219_aad_probe()`.

## Control Flow

This header has no executable flow, but its declarations shape the AAD lifecycle. The main codec allocates AAD private data during I2C probe, initializes AAD from component probe, calls `da7219_aad_jack_det()` from `.set_jack`, delegates PM transitions to the AAD helpers, and calls `da7219_aad_exit()` during component remove. The event-register enum and report mask are used by the IRQ handler to read, clear, and report jack state atomically by event group.

## State and Persistence

`struct da7219_aad_priv` persists the component binding, IRQ, ground-switch delay, firmware-derived mic-bias/button configuration, three work items, single workqueue, current jack object, mic-bias resume intent, and physical jack-insertion flag. This state is not stored outside driver memory and is reconstructed on probe; hardware register state is synchronized by init, IRQ handling, and PM hooks.

## Dependencies and Integration Points

The header depends on Linux timer/mutex declarations, ASoC component and jack types, and public DA7219 AAD platform definitions from `<sound/da7219-aad.h>`. It is tightly coupled to `da7219.h` for parent codec register definitions and `struct da7219_priv` access in the implementation.

## Risks and Edge Cases

- Register and bit definitions must remain aligned with the DA7219 datasheet and with the regmap defaults in `da7219.c`.
- `DA7219_AAD_REPORT_ALL_MASK` determines what removal clears; missing a future button or jack bit would leave stale input state.
- The private structure contains both workqueue and IRQ-owned state, so implementation changes must preserve cancellation ordering around `jack_inserted`, `micbias_resume_enable`, and queued work.

## Test Signals

Header-level validation is mostly compile-time: all bit masks must match users in `da7219-aad.c`, PM stubs must compile with and without `CONFIG_PM`, and ALSA jack bits must match supported headset functionality. Runtime tests are the AAD insertion/button/PM scenarios described for the `.c` file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/da7219-aad.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/da7219.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/da7219.c

## Purpose

`da7219.c` is the main ALSA SoC codec driver for the Dialog/Renesas DA7219. It registers the I2C regmap-backed component and DAI, exposes mixer controls and DAPM routing, configures clocks/PLL/TDM/audio formats, handles regulators and bias transitions, provides optional common-clock WCLK/BCLK outputs, initializes the AAD subdriver, and implements component PM.

## Important APIs, Types, and Functions

- `soc_component_dev_da7219` is the ASoC component driver with probe/remove, suspend/resume, jack, bias, controls, widgets, and routes.
- `da7219_dai` exposes the `da7219-hifi` playback/capture DAI with 1 to 2 channels, 8 kHz through 96 kHz rates, 16/20/24/32-bit formats, and symmetric stream constraints.
- `da7219_dai_ops` wires `.hw_params`, `.set_sysclk`, `.set_pll`, `.set_fmt`, and `.set_tdm_slot`.
- `da7219_i2c_probe()` allocates `struct da7219_priv`, initializes regmap, obtains platform or firmware data, runs AAD probe allocation, and registers the component.
- `da7219_probe()` is the component-level hardware bring-up: regulators, cache bypass/reset, chip revision patching, pdata application, MCLK acquisition, optional DAI clock registration, default control programming, and AAD init.
- `da7219_remove()` tears down AAD, DAI clocks, MCLK reference, and regulators.
- `da7219_set_pll()` is exported to the AAD file and programs PLL bypass, normal PLL, or SRM mode using MCLK-derived integer/fractional dividers.
- `da7219_set_dai_fmt()`, `da7219_hw_params()`, and `da7219_set_dai_tdm_slot()` map ALSA DAI format, sample width, sample rate, channel count, and TDM slot state to DA7219 DAI registers and optional clock framework rates.
- Kcontrol helper functions lock selected controls with `ctrl_lock`, handle 16-bit little-endian tone generator frequency registers, and trigger ALC recalibration when relevant controls change.

## Control Flow

I2C probe creates the private state and regmap, parses firmware into `struct da7219_pdata`, allocates AAD state, then registers the ASoC component. Component probe initializes locks, enables supplies, bypasses regcache to inspect and reset live hardware, reinitializes regcache, applies IO voltage and revision-specific patches, applies mic-bias and mic-input pdata, acquires optional `mclk`, registers optional DAI clocks, programs stable defaults, and starts AAD.

PCM setup flows through DAI ops. `set_sysclk` validates and records a 2 to 54 MHz MCLK source and optionally configures an external `mclk` clock. `set_pll` calculates input dividers and fractional feedback values, with source selecting bypass, normal PLL, or SRM. `set_fmt` validates master/slave, serial protocol, and clock polarity. `hw_params` programs word length, channel count, sample rate, and BCLK/WCLK ratios; in master mode it either sets exported clock rates or writes the hardware BCLK-per-WCLK field. `set_tdm_slot` enables two-slot maximum TDM, validates offset against `DA7219_DAI_OFFSET_MAX`, and adjusts master BCLK to match frame size.

DAPM controls power sequencing. The DAI supply enables clocks in master mode and checks SRM lock before stream activation, then releases clocks and returns PC count to free-run after power-down. Mic PGA events add a mic-bias-dependent delay after first capture following mic-bias enable. Mixout and gain-ramp events apply pop-suppression delays and restore user gain-ramp settings after DAPM transitions. Bias transitions enable MCLK for prepare, master bias for standby, and disable master bias in off unless the codec is a wake source.

## State and Persistence

`struct da7219_priv` holds component, AAD pointer, pdata pointer, wake-source flag, regulators, regmap, `ctrl_lock`, `pll_lock`, optional common-clock objects/lookups, MCLK pointer and rate, clock source, master/TDM/ALC flags, mic-bias event flag, mic PGA delay, and saved gain ramp control. Persistent hardware state is represented by the regmap cache and default register table. Probe explicitly handles a chip that may already be active from a previous boot stage by powering down audio paths before reset. Suspend/resume forces DAPM bias off/standby and delegates AAD PM if the codec is not a wake source.

## Dependencies and Integration Points

The driver integrates with Linux I2C, regmap RBTREE cache, regulators `VDD`, `VDDMIC`, and `VDDIO`, optional `mclk`, optional common-clock provider/clkdev registration, OF and ACPI matching, ALSA ASoC component/DAI/DAPM/control APIs, and the DA7219 AAD subdriver. Firmware properties include `wakeup-source`, `clock-output-names`, `dlg,micbias-lvl`, and `dlg,mic-amp-in-sel`.

## Risks and Edge Cases

- Several calibration and status loops busy-wait with sleeps and no hard error on timeout, such as ALC auto-calibration and SRM lock warning paths.
- `da7219_probe()` calls `da7219_aad_init()` late; if AAD init fails after DAI clocks and regulators are enabled, the error path frees clocks and regulators but depends on AAD init not leaving a partially requested IRQ/workqueue behind.
- Register defaults include AAD registers, so changes in `da7219-aad.h` must stay synchronized with the main regmap table.
- TDM supports only two enabled slots; machine drivers using wider masks will fail.
- Master-mode clock handling has two paths, common-clock exported clocks and direct register writes; both need test coverage.
- The optional HP test in the AAD file calls `da7219_set_pll()` directly, so PLL locking and cached MCLK state must stay valid across both files.
- Firmware parser defaults are permissive and warn on invalid values, meaning bad platform data may still produce a working but unexpected audio configuration.

## Test Signals

Useful tests include I2C probe/remove with regulator failures, VDDIO low/high voltage selection, chip revision AA patch application, all supported sample rates and word lengths, master and slave DAI formats for I2S/left/right/DSP_B and polarity combinations, TDM enable/disable and invalid masks, optional common-clock WCLK/BCLK registration and rate rounding, ALC enable and mixin gain recalibration, DAPM route power-up/down pop suppression, suspend/resume with and without wake source, and AAD jack reporting through `.set_jack`. Kernel logs for unsupported MCLK, PLL range errors, SRM lock warnings, and failed clock/regulator operations are high-value diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/da7219.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/da7219.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/da7219.h

## Purpose

`da7219.h` is the private register and state definition header for the DA7219 codec driver. It provides the register map, bit fields, hardware limits, timing constants, private driver state, and the exported PLL helper declaration shared with the AAD implementation.

## Important APIs, Types, and Constants

- Register defines cover gain/status, CIF, sample-rate, PLL, DAI, routing, ALC, references, mic/mixin/ADC/DAC/HP/mixout controls, IO, charge pump, noise gate, tone generator, system status, and system active registers.
- Bit masks and shifts are grouped by register and provide the values consumed by `da7219.c` kcontrols, DAPM widgets, DAI ops, PLL code, probe defaults, and AAD HP-test code.
- Hardware limits include sample-rate codes, DAI formats and word lengths, maximum two DAI channels and TDM slots, DAC/HP gain defaults, ALC limits, tone generator ranges, and PLL input divider codes.
- General constants define register-byte helpers, PLL output frequencies, SRM retry count, system-controller retry/delay values, and pop/noise suppression delays.
- `enum da7219_clk_src`, `enum da7219_sys_clk`, and `enum da7219_supplies` encode internal clock source, PLL mode, and regulator indexes.
- `struct da7219_priv` is the shared private state for the main codec and AAD subdriver.
- `da7219_set_pll()` is declared for use outside `da7219.c`.

## Control Flow

This header has no executable logic, but it drives almost every control path. DAI format and `hw_params` logic write the DAI and sample-rate fields declared here; DAPM widgets use enable/mute/ramp bits; probe/reset uses register defaults and status definitions; AAD uses ACCDET and HP/tone-generator fields to perform jack classification; and common-clock callbacks use sample-rate and BCLK-per-WCLK fields.

## State and Persistence

`struct da7219_priv` persists cross-subsystem state that cannot be inferred solely from registers: platform data, AAD state, wake-source behavior, regulator handles, regmap, locks, common-clock objects, MCLK rate/source, master/TDM/ALC mode flags, mic-bias event tracking, mic PGA delay, and saved gain-ramp register value. Hardware state is persisted through regmap defaults and cache synchronization.

## Dependencies and Integration Points

The header depends on Linux clock, clkdev, clock-provider, regmap, regulator, and public `<sound/da7219.h>` platform definitions. It is included by both `da7219.c` and `da7219-aad.c`, making it the coupling point between core codec and accessory-detection code.

## Risks and Edge Cases

- Duplicate macro names such as `DA7219_MODE_SUBMIT_SHIFT` for input and output system-mode registers are intentional but easy to misuse.
- The header exposes raw register constants for private hardware behavior; any datasheet or silicon revision mismatch affects many code paths.
- `struct da7219_priv` layout is internal but shared across compilation units, so adding state needs careful initialization in I2C/component probe and cleanup in remove/error paths.
- Max values and enum codes must match ALSA control declarations; off-by-one mistakes create invalid mixer ranges or rejected DAI parameters.

## Test Signals

Compile coverage with `CONFIG_COMMON_CLK` and `CONFIG_PM` on/off validates the conditional state and prototypes. Runtime signals come from all DA7219 codec paths: regmap default sync, DAI setup, DAPM power transitions, AAD HP test, PLL programming, and regulator/clock handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/da7219.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/da732x.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/da732x.c

## Purpose

`da732x.c` implements an ALSA SoC codec driver for the Dialog DA732x/DA7320 family. It registers a regmap-backed I2C component with two DAI interfaces, many analog/digital mixer controls, DAPM routes for microphones, AUX inputs, ADCs, DACs, headphone and line/class-D outputs, PLL/sysclk handling, charge-pump and bias sequencing, and headphone DC offset cancellation.

## Important APIs, Types, and Functions

- `struct da732x_priv` stores the regmap, current sysclk, and whether the PLL is enabled.
- `da732x_reg_cache` provides default values for the regmap cache across analog, clock, AIF, DSP, ADC, DAC, EQ, DMA, and unlock registers.
- `da732x_get_input_div()` maps sysclk ranges to PLL input-divider codes and writes `DA732X_REG_PLL_CTRL`.
- `da732x_set_charge_pump()` enables or disables CP clocks and charge-pump registers for headphone/output operation.
- `da732x_hpf_get()` and `da732x_hpf_set()` implement custom enum controls because HPF mode spans two non-contiguous bits.
- `da732x_snd_controls` exposes mic/AUX/ADC/DAC/headphone/lineout volumes, switches, HPF modes, EQ controls, and output controls.
- `da732x_adc_event()` powers ADC1/ADC2 clocks, reset bits, and power-down bits during DAPM transitions.
- `da732x_out_pga_event()` toggles output enable and high-impedance behavior around HP/line output PGA power changes.
- `da732x_hw_params()` maps PCM width and rate to AIF word-length bits and global sample-rate bits.
- `da732x_set_dai_fmt()` configures AIFA or AIFB master/slave mode, interface format, inversion, MCLK generation, and PC pulse source.
- `da732x_set_dai_pll()` is exposed as the component `.set_pll` operation and programs PLL bypass or fractional PLL dividers.
- `da732x_set_bias_level()` performs the largest state transition sequence: bias startup, DSP bypass/digital enable, charge pump, zero crossing, HP DC calibration, regcache sync, standby PLL disable, and off-state cache-only mode.
- `da732x_i2c_probe()` allocates private data, initializes I2C regmap, reads and logs silicon revision, and registers the component and two DAIs.

## Control Flow

Probe is simple: allocate state, initialize regmap, read `DA732X_REG_ID`, log revision, and register the ASoC component with both DAI descriptors. Most hardware bring-up is deferred to bias transitions. When DAPM moves from off to standby, `da732x_set_bias_level()` fast-charges VMID, enables codec bias, waits for startup, enables DAC reference, bypasses DSP routing, enables the digital subsystem, configures HP helper registers, enables the charge pump and core clocks, enables input/output zero crossing, performs HP DC offset cancellation, then exits cache-only mode and syncs regmap. On standby from higher power, it lowers bias boost and disables PLL. On off, it switches regmap to cache-only, disables charge pump and bias, and marks PLL disabled.

PCM configuration flows through DAI ops. `set_sysclk` only records a frequency; `set_dai_pll` later validates it for bypass or derives fractional dividers. `hw_params` validates 16/20/24/32-bit samples and common sample rates, then writes AIF word length and sample-rate code. `set_fmt` chooses AIFA or AIFB registers by DAI ID, supports slave or clock-provider modes, supports I2S/right-justified/left-justified/DSP_B, and applies a limited set of clock inversion modes.

DAPM routes connect MIC/AUX sources through ADC muxes to AIFA/AIFB capture, and playback from AIFA/AIFB through DACs to HP, line outputs, and class-D output. ADC supplies and output PGAs use event callbacks to sequence clocks, reset bits, high-impedance bits, and output enables.

## State and Persistence

Driver memory state is limited to `sysclk` and `pll_en`, with most codec state represented by hardware registers and regmap cache. The bias-level code deliberately keeps writes cached in off state via `regcache_cache_only(true)` and syncs on startup. HP DC offset cancellation writes calibration trim registers during bias startup and leaves final trim values in hardware/cache. PLL state is guarded only by the component/core sequencing, not by a local mutex.

## Dependencies and Integration Points

The driver depends on Linux I2C, regmap, ALSA ASoC component/DAI/DAPM/control/TLV APIs, and register definitions from `da732x.h` and `da732x_reg.h`. Unlike DA7219, this file has no OF/ACPI match table and no regulator or clock-provider integration; machine drivers must provide sysclk/PLL/DAI format setup through ASoC calls.

## Risks and Edge Cases

- `da732x_set_dai_pll()` checks `pll_en` and returns `-EBUSY` if already enabled, but there is no mutex, so concurrent callers could race.
- `da732x_hw_params()` accepts `88100` instead of `88200` for the 88.1 kHz code while `DA732X_RATES` advertises standard 8 kHz to 96 kHz rates; this is likely a bug and can reject normal 88.2 kHz streams.
- The component `.set_pll` operation exists, but `da732x_dai_ops` does not include `.set_pll`; callers must use component-level PLL plumbing rather than DAI-level ops.
- Bias startup does substantial work, including calibration and regcache sync, so resume or first stream startup can be slow and sensitive to power sequencing.
- The ADC supply widgets request `SND_SOC_DAPM_PRE_PMU` but `da732x_adc_event()` switches on `SND_SOC_DAPM_POST_PMU`; depending on ASoC event semantics, the power-up clock/reset branch may not run as intended.
- Some control names contain typos or suspicious register targets, such as `ACD2` labels and `ADC2 EQ Overall Volume` using `DA732X_REG_ADC1_EQ5`.
- PLL bypass validates hardcoded sysclk values and ignores the `freq_in` argument, so machine-driver assumptions must match `set_sysclk` ordering.

## Test Signals

Tests should cover component probe, revision read failure, DAPM off-to-standby and standby-to-off transitions, HP DC offset calibration paths, charge-pump enable/disable, AIFA and AIFB playback/capture, all advertised sample rates with special attention to 88.2 kHz, all supported word widths, master/slave and inversion format combinations, PLL bypass versus fractional PLL enable/disable, HPF enum get/set round trips, ADC supply power sequencing, output high-impedance behavior, and mixer control register targets for the typo-prone EQ controls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/da732x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/da732x.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/da732x.h

## Purpose

`da732x.h` defines non-register constants, limits, dB scales, clock values, control limits, and sample-rate enum values used by the DA732x ASoC codec driver.

## Important APIs, Types, and Constants

- General byte-size and shift helpers support fractional PLL divider packing in `da732x.c`.
- Calibration constants define HP DAC/output offset step sizes, trim defaults, stabilization delay, and array indexes for left/right DACs and headphone amps.
- Clock constants define startup delay, PLL output frequencies, allowed MCLK thresholds, MCLK divider codes, DAI IDs, and source-clock IDs.
- Kcontrol constants define max values, shifts, enable/disable values, HPF modes, inversion flags, charge-pump flags, and ADC reset values used in control declarations and DAPM events.
- dB constants define TLV ranges for mic, mic boost, AUX, HP, lineout, EQ, DAC, and ADC controls.
- `enum da732x_sysctl` maps sample-rate values to codec sample-rate register codes.

## Control Flow

The header is declarative, but it controls DA732x probe and stream behavior indirectly. `da732x_hw_params()` uses `enum da732x_sysctl` for sample-rate programming; PLL setup uses the MCLK threshold constants and byte shifts; calibration routines use the HP step/index constants; and Kcontrol tables use the max/shift/dB constants to generate ALSA mixer controls.

## State and Persistence

No state is declared in this header. Its constants define how `struct da732x_priv` state in `da732x.c` is interpreted and how register state is encoded. Changes here persist only through compiled driver behavior and hardware register writes.

## Dependencies and Integration Points

The file includes `<sound/soc.h>` for ASoC declarations and is included by `da732x.c` alongside `da732x_reg.h`. It complements the register header by describing semantic ranges and user-visible mixer scale information rather than raw addresses.

## Risks and Edge Cases

- Clock and sample-rate constants must match actual DA732x hardware; an incorrect value propagates directly into PLL and sample-rate programming.
- TLV dB min/increment values define user-visible mixer behavior, so mistakes affect alsamixer/UCM policy and test expectations.
- The header defines `DA732X_PLL_OUT_180634` as `180633600`, a rounded-name mismatch that can confuse audits even if numerically intentional.
- `DA732X_ADC_VOL_DB_INC` is `-1`, which is unusual for a TLV step and should be verified against the hardware scale.

## Test Signals

Compile-time users are all in `da732x.c`. Runtime tests should verify mixer dB ranges, HPF mode values, calibration array indexing, PLL divider selection for MCLK ranges below 10 MHz, 10 to 20 MHz, 20 to 40 MHz, and 40 to 54 MHz, and sample-rate register programming for each enum value.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/da732x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/da732x_reg.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/da732x_reg.h

## Purpose

`da732x_reg.h` is the raw DA732x register-map header. It names codec register addresses, maximum register bounds, and bit masks for status, bias, mic/AUX inputs, headphone and line outputs, charge pump, PLL, clocks, AIF interfaces, routing, DSP/DMA, ADCs, DACs, HPF, EQ, and softmute controls.

## Important APIs, Types, and Constants

- Register address definitions span `0x00` through `DA732X_REG_UNLOCK` at `0xE0`, with `DA732X_MAX_REG` used by regmap configuration.
- Status and bias bits define PLL lock/MCLK detect, headphone detect, brownout, VMID/reference control, and bias boost/enable.
- Input bits cover mic-bias voltage/enable, mic detect, mic boost/gain/mute/enable, AUX gain/mute/enable, input pin bias, zero crossing, and ADC input mux selection.
- Output bits cover HP detect, HP DAC/output offset trim and comparator controls, HP output DAC/high-Z/mute/enable, lineout volume/DAC/high-Z/mute/enable, output zero crossing, and HP ground selection.
- Charge-pump and PLL/clock bits define CP operating modes, CP clocks, PLL input/SRM/enable, sample-rate nibbles, DSP frequency, and clock gates.
- AIF bits define frame width, source selection, master/slave clocking, word length, protocol mode, inversion, and enable bits for AIFA/AIFB.
- Routing and DSP bits define direct DSP bypass/all-to-DSP routes, digital/DSP core enable, mailbox/DMA selection, and DMA status.
- ADC/DAC bits define reset/power-down/enable/mute/volume, softmute, HPF, and 5-band EQ controls.

## Control Flow

This header has no control flow, but `da732x.c` uses it throughout probe, DAPM, controls, PLL, and calibration. The regmap maximum and volatile register callbacks depend on register definitions here. DAPM event handlers use ADC reset/power bits and output high-Z/enable bits. PLL and DAI ops use PLL divider, AIF, clock, and sample-rate fields. Bias startup and HP calibration use reference, charge pump, HP trim, DSP routing, and zero-crossing definitions.

## State and Persistence

All persistent hardware state encoded by DA732x regmap defaults and runtime writes is defined by this header. The most stateful areas are bias/reference power, clock gates, PLL enable/dividers, AIF format, DAPM endpoint enable/mute/high-Z state, ADC/DAC reset and power state, and HP calibration trim registers. Only `HPL_DAC_OFF_CNTL` and `HPR_DAC_OFF_CNTL` are marked volatile by the driver, even though other status registers also describe live hardware state.

## Dependencies and Integration Points

The header is consumed by `da732x.c` and indirectly by any future DA732x helper code. It has no includes, so it relies on plain integer macros. Its constants must align with the regmap default table, DAPM widget/register declarations, mixer control ranges in `da732x.h`, and the DA732x datasheet.

## Risks and Edge Cases

- Typos in macro names or comments can propagate into controls; for example the driver already has typo-prone ADC2 EQ control labels.
- `DA723X_CP_DIS` appears amid DA732x constants and may be intentional compatibility or a naming mistake; it should be checked before reuse.
- Some status registers are not marked volatile in the driver, so reading them through regmap cache may be misleading unless the driver bypasses cache or extends `da732x_volatile()`.
- Route and DSP bit definitions are broad; writing the wrong combination can silently redirect audio through DSP or bypass paths.
- Calibration masks and sign bits must be exact because the binary-search trim routines invert and combine them directly.

## Test Signals

Validation should include regmap default sync against this register map, bias and CP sequencing, AIF format programming for both AIFA/AIFB, ADC/DAC DAPM power transitions, HP offset calibration comparator behavior, DSP bypass routing, EQ/HPF control writes, DMA status reads if DSP DMA is ever used, and volatile-register behavior for live status fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/da732x_reg.h -->
