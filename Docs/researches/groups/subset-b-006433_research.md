# Research Group subset-b-006433

This grouped report covers six ASoC codec source files under `sources/distributed-fs/ceph-client/sound/soc/codecs/`. Each section is bounded with the reconciliation markers required for source-tree-aligned splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs47l92.c -->
## sources/distributed-fs/ceph-client/sound/soc/codecs/cs47l92.c

### Purpose

`cs47l92.c` is the ALSA SoC component driver for the Cirrus Logic CS47L92 codec as a Madera-family child device. It exposes mixer controls, DAPM widgets/routes, DAIs, FLL programming, compressed DSP trace streams, and probe/remove lifecycle for a codec instantiated by the parent MFD. It relies heavily on shared Madera helper code for register definitions, DAI operations, input/output event sequencing, clock domain handling, FLL implementation, and ADSP support.

### Important APIs, Types, and Functions

- `struct cs47l92` embeds `struct madera_priv core` and two `struct madera_fll` instances. Most persistent driver state is in the common Madera private object and the FLL objects.
- `cs47l92_dsp1_regions[]` describes ADSP2 PM/ZM/XM/YM memory windows for `wm_adsp2_init()`.
- `cs47l92_put_demux()` implements the custom DAPM demux control for routing OUT3 hardware to HPOUT3 or HPOUT4. It validates the enum item, locks DAPM, temporarily disables OUT3 left/right, updates `MADERA_EP_SEL`, applies output mono/stereo mode from platform data, restores output enable state, waits for hardware sequencing, and then calls `snd_soc_dapm_mux_update_power()`.
- `cs47l92_adsp_power_ev()` handles DSP DAPM events by reading `MADERA_DSP_CLOCK_2`, setting the ADSP clock during `SND_SOC_DAPM_PRE_PMU`, and delegating remaining event work to `wm_adsp_early_event()`.
- `cs47l92_outclk_ev()` handles OUTCLK domain events, enabling/disabling the selected MCLK when OUTCLK is sourced from an external MCLK, then delegating to `madera_domain_clk_ev()`.
- `cs47l92_set_fll()` dispatches `set_pll` calls to `madera_fllhj_set_refclk()` for FLL1 or FLL2.
- `cs47l92_open()` accepts only the `cs47l92-dsp-trace` compressed DAI and opens ADSP compressed capture through `wm_adsp_compr_open()`.
- `cs47l92_adsp2_irq()` forwards the DSP compressed-data IRQ to `wm_adsp_compr_handle_irq()` and treats `-ENODEV` as a spurious interrupt.
- `cs47l92_component_probe()` binds the component regmap, publishes the DAPM pointer into the parent Madera object, initializes Madera inputs/outputs including mono routes, disables the haptics pin, adds ADSP rate controls, and probes the ADSP component.
- `cs47l92_probe()` is the platform-device entry point. It defers until the Madera IRQ chip is ready, allocates private state, initializes the Madera core, requests DSP and bus-error IRQs, initializes ADSP/FLL/DAI state, latches volume update bits, enables runtime PM, and registers the ASoC component.

### Control Flow

The probe path starts from the parent MFD driver data, then calls `madera_core_init()`, requests `MADERA_IRQ_DSP_IRQ1`, sets it wake-capable, initializes the ADSP descriptor, calls `wm_adsp2_init()`, initializes bus-error IRQ handling, initializes two FLLs and all DAI descriptors, latches digital volume-update bits, enables runtime PM, and finally registers the component and DAIs with ASoC. Error paths unwind in reverse order, freeing bus-error IRQs, removing ADSP state, disabling IRQ wake, freeing the IRQ, and freeing the Madera core.

The component probe path runs later during ASoC registration. It installs the regmap, connects DAPM into the parent Madera object, initializes inputs and outputs, adds runtime controls, and registers the DSP component. Component removal clears the shared DAPM pointer and removes the DSP component.

Audio routing is mostly declarative through `cs47l92_snd_controls`, `cs47l92_dapm_widgets`, and `cs47l92_dapm_routes`. DAPM powers clock domains (`SYSCLK`, `ASYNCCLK`, `DSPCLK`, `FXCLK`, `OUTCLK`, AIF clocks, SLIMbus, PWM, DFC), supplies (`CPVDD1`, `CPVDD2`, `MICVDD`, MICBIAS rails), inputs, outputs, mixers, sample-rate converters, DFCs, and the single ADSP2 instance. Physical DAIs include three AIF ports, three SLIMbus ports, and trace DAIs.

### State and Persistence Behavior

Runtime state is held in devm-managed `struct cs47l92`, `madera_priv`, two FLL descriptors, and the shared Madera object. Hardware state is persisted primarily in the device register map and the Madera regcache. DAPM state controls clock domains and analog/digital paths; the custom OUT3 demux deliberately preserves and restores output enable bits around endpoint selection. Digital volume update bits are latched at probe by setting `CS47L92_DIG_VU` on all relevant DAC volume registers.

The driver does not implement local system sleep callbacks. It enables runtime PM on the platform device and leaves most register/cache/power behavior to Madera and ASoC DAPM. ADSP firmware/runtime state is owned by `wm_adsp`.

### Dependencies and Integration Points

- Linux subsystems: platform driver core, PM runtime, regmap, IRQ, clock API, ALSA SoC component/DAI/DAPM/compress APIs.
- Madera MFD and codec helpers: `madera_core_init/free`, `madera_request_irq/free_irq`, `madera_set_irq_wake`, `madera_init_inputs`, `madera_init_outputs`, `madera_init_dai`, `madera_set_sysclk`, `madera_fllhj_set_refclk`, `madera_domain_clk_ev`, `madera_hp_ev`, `madera_out_ev`, `madera_in_ev`, and Madera register definitions.
- DSP integration: `wm_adsp2_init/remove`, `wm_adsp2_component_probe/remove`, `wm_adsp_early_event`, `wm_adsp_compr_*`, and bus-error callbacks.
- Module metadata declares a soft dependency on `madera`, `irq-madera`, and `arizona-micsupp`, and aliases `platform:cs47l92-codec`.

### Risks and Edge Cases

- `cs47l92_put_demux()` must change endpoint selection only while outputs are disabled. Any failure during read/update/restore is logged, but the function still attempts to restore and update DAPM, so error recovery depends on hardware tolerating partial sequencing.
- OUT3 demux uses `madera->pdata.codec.out_mono[2 + mux]`; platform data length and indexing must match the HPOUT3/HPOUT4 choices.
- Probe depends on `madera->irq_dev`; missing or late irqchip registration results in `-EPROBE_DEFER`.
- FLL and DAI behavior is mostly delegated to shared Madera helpers, so regressions in those helpers affect this driver.
- Compressed stream open matches the codec DAI name string exactly. DAI renames or machine-driver mismatches can break compressed trace capture.
- `madera_set_irq_wake()` failures are warnings only; wake from DSP IRQs may silently be unavailable.

### Test Signals

Useful validation signals include successful platform probe without `-EPROBE_DEFER`, ASoC component registration, visible mixer/DAPM controls, valid DAI enumeration for AIF/SLIMbus/trace interfaces, FLL lock under `set_pll`, OUT3 demux changes without pops or stuck outputs, compressed DSP trace open/capture, DSP IRQ handling without spurious IRQ logs, and clean remove/unload with IRQs and ADSP state freed. Kernel build coverage should include this file with Madera, ASoC, and wm_adsp enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs47l92.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs48l32-tables.c -->
## sources/distributed-fs/ceph-client/sound/soc/codecs/cs48l32-tables.c

### Purpose

`cs48l32-tables.c` supplies the CS48L32 regmap data and revision patch helper used by the main CS48L32 SPI codec driver. It defines a small Rev A patch, the default register cache image, the readable/volatile/precious register policies, the 32-bit big-endian SPI regmap configuration, and the exported helper that creates the regmap.

### Important APIs, Types, and Functions

- `cs48l32_reva_patch[]` is a `struct reg_sequence` array applied by `regmap_register_patch()`.
- `cs48l32_apply_patch()` registers the patch against `cs48l32->regmap` and reports failures with `dev_err_probe()`.
- `cs48l32_reg_default[]` is the regcache default table. It covers GPIO defaults, clocks, sample rates, FLL, charge pump/LDO/MICBIAS, IRQ masks, input controls, ASP controls, mixer source defaults, ISRC/EQ/DRC/LHPF/TONE/NOISE/ultrasonic controls, and selected DSP/IRQ masks.
- `cs48l32_readable_register()` explicitly allows register ranges including identity/reset/control, clocks, FLL, power, inputs, ASPs, mixers, EQ/DRC/LHPF, ultrasonic blocks, IRQ status/mask registers, and DSP memory/register windows.
- `cs48l32_volatile_register()` marks identity/status/reset, live clock/FLL/input status, IRQ status/event registers, and DSP memory/control windows volatile so regcache does not trust stale values.
- `cs48l32_precious_register()` marks packed DSP memory windows precious to keep regmap debugfs from issuing illegal unaligned accesses.
- `cs48l32_create_regmap()` calls `devm_regmap_init_spi()` with `cs48l32_regmap` and stores the result in `cs48l32->regmap`.

### Control Flow

The main driver calls `cs48l32_create_regmap()` early in SPI probe, then places the regmap in cache-only mode until power and reset sequencing are complete. After boot, the main probe path calls `cs48l32_apply_patch()` to apply the revision-specific register writes. Runtime suspend/resume in the main driver relies on the regcache defaults and volatile/readable policies defined here to decide what can be cached and what must be re-read or synchronized after power transitions.

### State and Persistence Behavior

This file does not allocate long-lived objects directly, but it defines the persistent regcache baseline. The `REGCACHE_MAPLE` cache stores writable, nonvolatile register state while the device is runtime-suspended or powered down. Volatile and precious markings prevent unsafe or stale cached access to status and DSP memory windows. The regmap is 32-bit register, 32-bit value, 4-byte stride, 32 pad bits, and big-endian for both register and value formatting, matching the CS48L32 SPI bus protocol.

### Dependencies and Integration Points

- Includes public CS48L32 structures from `<sound/cs48l32.h>` and register constants from `<sound/cs48l32_registers.h>`.
- Includes the local private header `cs48l32.h` for `struct cs48l32` and prototypes.
- Integrates with Linux regmap and regulator/device infrastructure.
- The main `cs48l32.c` file depends on `cs48l32_apply_patch()` and `cs48l32_create_regmap()`.

### Risks and Edge Cases

- Register policy omissions are high impact: a missing readable register can make legitimate driver access fail; a missing volatile marking can cache live status; an incorrect precious marking can expose unsafe debugfs access to packed DSP memory.
- The patch is named Rev A in code but is applied unconditionally by the main driver after ID/revision reads. If later revisions need different patches, the dispatch logic is not present here.
- The default table must stay synchronized with hardware reset values and with writes performed by probe/runtime resume. Wrong defaults can cause regcache sync to restore stale or invalid state after suspend.
- The packed DSP memory comment documents a bus-bridge alignment constraint; accidental debug or regmap bulk access outside aligned block rules can cause illegal bus transactions.

### Test Signals

Validation should cover SPI regmap creation, patch application, successful regcache sync after runtime resume, debugfs/register-dump behavior avoiding precious DSP memory, and normal driver accesses to all registers used by `cs48l32.c`. Build tests should catch prototype drift with `cs48l32.h` and register-name drift with generated/public CS48L32 register headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs48l32-tables.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs48l32.c -->
## sources/distributed-fs/ceph-client/sound/soc/codecs/cs48l32.c

### Purpose

`cs48l32.c` is the main ALSA SoC codec driver for the Cirrus Logic CS48L32 audio DSP over SPI. It manages power/reset/boot, supplies and clocks, regmap cache transitions, ASoC controls/widgets/routes, ASP DAIs, compressed DSP trace and voice-control DAIs, HALO DSP initialization, DSP SRAM power sequencing, FLL configuration, runtime PM, device properties, and IRQ handling for DSP data and DSP fault events.

### Important APIs, Types, and Functions

- `struct cs48l32_codec` is the central private state. It embeds `struct wm_adsp dsp` first, then `struct cs48l32 core`, clock rate fields, DAI private state, one FLL descriptor, input ramp/update state, `rate_lock`, cached DSP DMA rates, input property arrays, TDM width/slot state, cached EQ modes/coefficients, and DSP SRAM power register metadata.
- `cs48l32_spin_sysclk()` performs dummy `CS48L32_DEVID` reads and a delay to satisfy hardware requirements around sample-rate-domain writes.
- Rate/control handlers such as `cs48l32_rate_put()`, `cs48l32_in_rate_put()`, `cs48l32_low_power_mode_put()`, `cs48l32_dsp_rate_get/put()`, and `cs48l32_dai_set_sysclk()` serialize or reject unsafe changes. `rate_lock` protects rate-domain changes that need SYSCLK cycles.
- Input helpers `cs48l32_inmux_put()`, `cs48l32_dmode_put()`, `cs48l32_init_inputs()`, and `cs48l32_in_ev()` handle analog/digital input selection, single-ended/differential mode, PDM supply selection, mute/VU sequencing, and analog force-enable workarounds.
- EQ/LHPF handlers cache coefficients in driver memory, reject unstable LHPF coefficients immediately, reject unstable EQ coefficients on DAPM power-up, and write EQ coefficient blocks with `regmap_raw_write()` during `cs48l32_eq_ev()`.
- DSP helpers `cs48l32_dsp_pre_run()`, `cs48l32_dsp_memory_enable/disable()`, `cs48l32_dsp_freq_update()`, `cs48l32_dsp_freq_ev()`, and `cs48l32_dsp_mem_ev()` program HALO sample-rate registers, SRAM power registers, and DSP clock-frequency registers.
- `cs48l32_irq()` handles shared threaded IRQs: runtime-resumes the device, reads pending and mask/event registers, acknowledges unmasked events, dispatches DSP compressed-data IRQs, MPU errors, and WDT expiry to `wm_adsp`/HALO handlers, then runtime-autosuspends.
- Clock/FLL helpers include `cs48l32_set_sysclk()`, `cs48l32_set_pdm_fllclk()`, `cs48l32_fllhj_validate()`, `cs48l32_fllhj_apply()`, `cs48l32_fllhj_enable()`, `cs48l32_fllhj_disable()`, and `cs48l32_set_fll()`.
- DAI operations include `cs48l32_asp_dai_probe()`, `cs48l32_set_fmt()`, `cs48l32_startup()`, `cs48l32_hw_params()`, `cs48l32_dai_set_sysclk()`, and `cs48l32_set_tdm_slot()`.
- Lifecycle functions include `cs48l32_spi_probe()`, `cs48l32_spi_remove()`, `cs48l32_runtime_suspend()`, `cs48l32_runtime_resume()`, `cs48l32_create_codec_component()`, `cs48l32_component_probe()`, and `cs48l32_component_remove()`.

### Control Flow

SPI probe allocates `struct cs48l32_codec`, initializes `rate_lock`, stores the IRQ and input VU register, creates the SPI regmap through `cs48l32_create_regmap()`, enters regcache cache-only mode, obtains reset GPIO and optional `mclk1`, obtains and enables core supplies plus `vdd-d`, releases hard reset or performs soft reset, waits for `BOOT_DONE`, reads and validates device ID/revision/OTP, applies the patch from `cs48l32-tables.c`, masks boot-done interrupt, configures the 32 kHz clock, enables runtime PM with autosuspend, and creates the ASoC component.

Component creation parses firmware/DT properties for input type and PDM supply, initializes the HALO DSP descriptor, initializes one FLL descriptor, requests the shared IRQ, and registers the ASoC component and six DAIs. Component probe initializes input hardware, initializes per-DAI constraints, reads initial EQ modes/coefficients into cache, probes the DSP component, and unmasks DSP IRQ sources. Component remove masks DSP IRQs and removes the DSP component.

PCM startup constrains rates based on the selected system-clock domain. `hw_params` computes slot count/width, required BCLK, and hardware BCLK selector, disables ASP TX/RX if the ASP format changes, writes sample rate and ASP controls, and restores the previous ASP enable state. DAI clock selection is rejected while active and updates ASP rate-domain bits with SYSCLK guard reads when needed.

Runtime suspend writes a marker to `CS48L32_CTRL_IF_DEBUG3`, switches regmap to cache-only, and disables `vdd-d`. Runtime resume enables `vdd-d`, exits cache-only mode, waits for boot, checks whether registers reset by reading the marker, marks the cache dirty if needed, and syncs the cache.

### State and Persistence Behavior

The driver has three main state layers. First, hardware state lives in CS48L32 registers and is mirrored by regmap cache across runtime suspend. Second, driver-only state stores selected clock rates, DAI clock domains, TDM slots/widths, parsed input configuration, pending input power-up count, DSP DMA sample-rate selections, and EQ modes/coefficients. Third, ASoC/DAPM state controls which widgets, supplies, and routes are powered.

EQ coefficients are not written immediately by mixer controls; they are cached in `eq_coefficients` and flushed on EQ DAPM `PRE_PMU` after stability checks. DSP DMA rates are cached in `dsp_dma_rates` and written by `cs48l32_dsp_pre_run()` before firmware execution. Input digital volume writes hit an uncached write-only VU register and are retried by DAPM event sequencing if the codec is off. FLL state is cached in `struct cs48l32_fll` and reflected to hardware on enable/disable.

### Dependencies and Integration Points

- Linux subsystems: SPI, GPIO descriptors, clock framework, regulator framework, PM runtime, regmap, IRQ, device properties, ALSA SoC component/DAI/DAPM/compress APIs.
- CS48L32 public ABI: `<sound/cs48l32.h>`, `<sound/cs48l32_registers.h>`, and DT bindings under `<dt-bindings/sound/cs48l32.h>`.
- Local helpers from `cs48l32.h` and `cs48l32-tables.c`: regmap creation, patching, public clock/FLL constants, private structs, and register/control macros.
- DSP framework: `wm_halo_init()`, `wm_adsp2_component_probe/remove()`, `wm_adsp_compr_*`, `wm_halo_bus_error()`, and `wm_halo_wdt_expire()`.
- Machine drivers interact through standard ASoC calls: `set_sysclk`, `set_pll`, `set_fmt`, `set_tdm_slot`, PCM `hw_params`, DAPM routing, and compressed capture.

### Risks and Edge Cases

- In `cs48l32_irq()`, some error paths after a successful `pm_runtime_resume_and_get()` return without `pm_runtime_put_autosuspend()`. A failing `regmap_read()` or `regmap_multi_reg_read()` can leak a runtime-PM reference.
- `cs48l32_fllhj_enable()` jumps to `out` on `cs48l32_fllhj_apply()` failure but returns `0` at the end, losing the failure status while still setting lockdet/control update and releasing hold.
- `cs48l32_prop_get_pdm_sup()` ignores the return value from `cs48l32_prop_read_u32_array()` and then iterates over `tmp`. If the property is absent or malformed, `tmp` may not contain initialized values.
- Active input rate and low-power-mode controls deliberately return `-EBUSY`; userspace mixers must handle failures when paths are powered.
- ASP reconfiguration disables and restores TX/RX enables around register writes. Bad masks or unexpected active paths could cause audio glitches.
- EQ coefficient stability is deferred to DAPM power-up, so invalid cached coefficients can be accepted by mixer writes and fail later when enabling the EQ path.
- Runtime resume assumes boot completion after `vdd-d` enable and may mark the cache dirty depending on `CTRL_IF_DEBUG3`; incorrect reset behavior or missing boot interrupt state can break resume.

### Test Signals

Build and probe tests should verify SPI binding on `cirrus,cs48l32`, regulator/clock/reset acquisition, boot-done polling, chip ID validation, patch application, regcache sync after runtime PM, and clean remove. ASoC tests should cover controls, DAPM route power-up/down, analog/digital input switching, active-input `-EBUSY` cases, ASP1/ASP2 playback/capture with I2S/DSP/left-justified formats, TDM masks, BCLK selection, compressed DSP trace and voice-control capture, FLL lock/unlock, DSP firmware load/run, DSP SRAM power events, DSP IRQ handling, and fault IRQ handling for MPU/WDT events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs48l32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs48l32.h -->
## sources/distributed-fs/ceph-client/sound/soc/codecs/cs48l32.h

### Purpose

`cs48l32.h` is the private header shared by `cs48l32.c` and `cs48l32-tables.c`. It defines CS48L32-specific constants, control-building macros, route-building macros, private helper structs, logging macros, and function prototypes for regmap creation, patching, pin setup, and voltage-index helpers.

### Important APIs, Types, and Functions

- Hardware constants define silicon ID, reset magic/delays, boot timeout/state bit, ASP register offsets, SYSCLK frequency selectors, FLL limits/gains/thresholds, DSP clock offsets, ASP format encodings, HALO sample-rate offsets, PDM FLL clock sources, array bounds, EQ/LHPF coefficient limits, rates, and PCM formats.
- `CS48L32_MIXER_CONTROLS`, `CS48L32_MUX_ENUM_DECL`, `CS48L32_MIXER_ENUMS`, `CS48L32_MUX_WIDGETS`, `CS48L32_MIXER_WIDGETS`, `CS48L32_MUX_ROUTES`, and `CS48L32_MIXER_ROUTES` generate large sets of ALSA controls, DAPM widgets, and DAPM routes from compact declarations in `cs48l32.c`.
- `CS48L32_DSP_ROUTES_1_8_SYSCLK()` and `CS48L32_DSP_ROUTES_1_8()` define route templates for DSP preloader, DSP clocking, and eight RX mixer inputs.
- `CS48L32_RATE_CONTROL`, `CS48L32_RATE_ENUM`, and `CS48L32_DSP_RATE_CONTROL` generate sample-rate mixer controls.
- `CS48L32_EQ_COEFF_CONTROL`, `CS48L32_EQ_BAND_COEFF_CONTROLS`, `CS48L32_EQ_COEFF_CONTROLS`, and `CS48L32_LHPF_CONTROL` generate custom coefficient controls wired to `cs48l32.c` handlers.
- Private structs include `cs48l32_enum`, `cs48l32_eq_control`, `cs48l32_dai_priv`, `cs48l32_dsp_power_reg_block`, `cs48l32_dsp_power_regs`, `cs48l32_fll_cfg`, `cs48l32_fll`, and `cs48l32_codec`.
- Prototypes expose `cs48l32_apply_patch()`, `cs48l32_create_regmap()`, `cs48l32_enable_asp1_pins()`, `cs48l32_enable_asp2_pins()`, `cs48l32_micvdd_voltage_index()`, and `cs48l32_micbias1_voltage_index()`.

### Control Flow

This header does not run code directly, but it shapes most of the main driver's control flow by generating control arrays, DAPM widget arrays, and route arrays. The `struct cs48l32_codec` layout is especially important because `wm_adsp` is required to be the first field, enabling `container_of()` and asserted offsets in `cs48l32.c`.

### State and Persistence Behavior

The header defines the persistent in-memory state used by the CS48L32 driver. `struct cs48l32_codec` stores current SYSCLK/DSPCLK values, DAI private constraints, FLL state, input volume-update sequencing state, mutex-protected rate state, cached DSP DMA rates, parsed firmware properties, TDM configuration, cached EQ modes and coefficients, and DSP power-register metadata. These values complement the regmap cache and survive while the device is bound.

### Dependencies and Integration Points

- Includes `<linux/bits.h>`, ALSA SoC declarations, and the shared `wm_adsp.h` DSP interface.
- Depends on public CS48L32 structures from included sound headers through the C files that include this header.
- Macros are consumed almost entirely by `cs48l32.c`; regmap and patch prototypes are implemented in `cs48l32-tables.c`.
- Logging macros standardize FLL and ASP diagnostic prefixes.

### Risks and Edge Cases

- Macro-generated controls/routes are dense and hard to audit. A typo in a base register or route macro can replicate many bad controls.
- `struct cs48l32_codec` layout has ABI-like assumptions inside the driver; moving `dsp` away from offset zero would break `container_of()` usage and the asserted offset.
- The header declares some helpers (`cs48l32_enable_asp1_pins()`, `cs48l32_enable_asp2_pins()`, voltage-index helpers) that are not implemented in the listed files, so build coverage must include their real definitions or ensure they are unused under the selected configuration.
- Coefficient limits and FLL thresholds are centralized here; hardware-revision changes require careful updates across both control validation and FLL programming logic.

### Test Signals

The most important validation for this header is compile-time: macro expansion must produce valid controls/routes, static assertions in `cs48l32.c` must hold, and prototypes must match implementations. Runtime tests that exercise all generated controls/routes provide indirect coverage for the macro definitions and private state layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs48l32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs530x-i2c.c -->
## sources/distributed-fs/ceph-client/sound/soc/codecs/cs530x-i2c.c

### Purpose

`cs530x-i2c.c` is the I2C transport wrapper for the CS530x/CS430x/CS4282 codec family driver. It matches device-tree and I2C IDs, allocates the shared private structure, creates an I2C regmap using the shared CS530x regmap configuration, records the matched device type, and delegates the actual codec initialization to `cs530x_probe()`.

### Important APIs, Types, and Functions

- `cs530x_of_match[]` maps `cirrus,cs4282`, `cirrus,cs4302`, `cirrus,cs4304`, `cirrus,cs4308`, `cirrus,cs5302`, `cirrus,cs5304`, and `cirrus,cs5308` to enum-like device type values from `cs530x.h`.
- `cs530x_i2c_id[]` provides the same set of names for non-DT I2C matching.
- `cs530x_i2c_probe()` allocates `struct cs530x_priv` with `devm_kzalloc()`, stores it with `i2c_set_clientdata()`, creates `cs530x->regmap` with `devm_regmap_init_i2c(client, &cs530x_regmap_i2c)`, stores `devtype` from `i2c_get_match_data()`, stores `dev`, and calls `cs530x_probe(cs530x)`.
- `module_i2c_driver()` registers the I2C driver.

### Control Flow

The Linux I2C core matches the device by OF compatible or I2C ID and calls `cs530x_i2c_probe()`. Probe does transport-specific allocation and regmap creation only; all codec-specific register initialization, ASoC registration, power handling, and controls live in the shared CS530x core. Regmap initialization errors are returned through `dev_err_probe()` for deferred-probe-friendly diagnostics.

### State and Persistence Behavior

This wrapper owns no independent persistent state beyond the devm-managed `struct cs530x_priv` and its I2C regmap pointer. The lifetime of the allocation and regmap is tied to the I2C device. Runtime codec state is in the shared CS530x core and hardware registers.

### Dependencies and Integration Points

- Linux I2C driver model, OF matching, module tables, regmap I2C transport, devm allocation.
- Local `cs530x.h` for `struct cs530x_priv`, device type constants, `cs530x_regmap_i2c`, and `cs530x_probe()`.
- Imports the `SND_SOC_CS530X` namespace, making the wrapper depend on symbols exported by the shared CS530x module.

### Risks and Edge Cases

- The device type is derived from match data. If a board uses an unsupported or misspelled compatible, probe will not bind or will pass wrong type data.
- There is no explicit remove function because devm and the shared core presumably own cleanup; this is correct only if `cs530x_probe()` registers resources with devm or otherwise has no transport-specific teardown.
- Transport regmap configuration must match the device's I2C protocol. Any mismatch is hidden from this wrapper and would appear as core register access failures.

### Test Signals

Validation should include module autoload from OF and I2C ID tables, successful I2C regmap creation, correct `devtype` selection for each supported compatible/name, and successful delegation into the shared CS530x codec probe. Probe deferral and error logging should be checked by temporarily withholding bus/regmap prerequisites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs530x-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs530x-spi.c -->
## sources/distributed-fs/ceph-client/sound/soc/codecs/cs530x-spi.c

### Purpose

`cs530x-spi.c` is the SPI transport wrapper for the CS530x/CS430x/CS4282 codec family driver. It mirrors the I2C wrapper: match a supported device, allocate `struct cs530x_priv`, create an SPI regmap with the shared CS530x SPI regmap configuration, record the matched device type and device pointer, and call the shared `cs530x_probe()`.

### Important APIs, Types, and Functions

- `cs530x_of_match[]` maps OF compatible strings to CS4282/CS4302/CS4304/CS4308/CS5302/CS5304/CS5308 type constants.
- `cs530x_spi_id[]` provides equivalent SPI modalias entries.
- `cs530x_spi_probe()` allocates private state, associates it with the SPI device by `spi_set_drvdata()`, creates `cs530x->regmap` with `devm_regmap_init_spi(spi, &cs530x_regmap_spi)`, stores `devtype` from `spi_get_device_match_data()`, stores `dev`, and delegates to `cs530x_probe()`.
- `module_spi_driver()` registers the SPI driver.

### Control Flow

The SPI core calls `cs530x_spi_probe()` after matching the OF table or SPI ID table. The wrapper performs only transport setup and then hands control to the common CS530x probe. Regmap allocation failures are logged with `dev_err()` and returned directly.

### State and Persistence Behavior

The wrapper's state is devm-managed and bound to the SPI device lifetime. All durable codec behavior is in the shared CS530x core and in hardware registers accessed through the SPI regmap.

### Dependencies and Integration Points

- Linux SPI driver model, OF matching, module tables, regmap SPI transport, devm allocation.
- Local `cs530x.h` for common private structure, device type constants, shared regmap config, and `cs530x_probe()`.
- Imports the `SND_SOC_CS530X` namespace for the shared core symbols.

### Risks and Edge Cases

- The OF match table appears to list `cirrus,cs5304` twice, with the second entry carrying `CS5308` data. That likely prevents an OF-described `cirrus,cs5308` SPI device from matching correctly and can misclassify a second `cs5304` match depending on lookup behavior.
- Unlike the I2C wrapper, regmap creation uses `dev_err()` rather than `dev_err_probe()`, so deferred probe diagnostics are less standardized.
- There is no explicit remove function; this is safe only if all shared-core registrations are devm-managed or otherwise need no SPI-wrapper teardown.
- `spi_get_device_match_data()` must return non-null meaningful data for all binding paths. A mismatch between OF and SPI ID matching can pass an unintended device type.

### Test Signals

Validation should cover SPI module autoload, OF and SPI ID matching for every supported chip name, correct `devtype` propagation, SPI regmap access, and successful shared `cs530x_probe()` completion. A specific test should verify `cirrus,cs5308` OF binding because the current OF table entry looks suspicious.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs530x-spi.c -->
