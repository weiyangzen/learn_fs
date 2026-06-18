# Research: subset-b-006469

Grouped research for Realtek RT715, RT721 SDCA, and RT722 SDCA SoundWire ASoC codec sources. Each section preserves the source path for source-tree-aligned splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt715-sdca.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt715-sdca.c

Purpose: implements the SDCA-flavored RT715 ASoC component logic behind the SoundWire transport. It exposes ALSA mixer controls, DAPM widgets/routes, SoundWire DAI operations, and hardware initialization for the RT715 SDCA microphone-array codec. Unlike legacy `rt715.c`, this file programs SDCA controls through `SDW_SDCA_CTL(...)` addresses and vendor-indexed MBQ registers rather than HD-audio verb translation.

Important APIs and functions: `rt715_sdca_init()` allocates `struct rt715_sdca_priv`, stores normal and MBQ regmaps, starts regcache in cache-only mode, registers the component and two capture DAIs. `rt715_sdca_io_init()` is called once the SoundWire slave is attached; it enables regcache I/O, marks runtime PM active on first hardware init, reads product revision, selects the external clock, configures extra DMIC pins by revision, triggers DFLL/VAD setup, enables SMPU trigger mode and interrupt masking, and sets `hw_init`. `rt715_sdca_pcm_hw_params()` maps AIF1 to DP6 and AIF2 to DP4, selects SDW input routing via vendor register `RT715_SDW_INPUT_SEL`, adds the slave to the SoundWire stream, and writes the SDCA sample-frequency index. `rt715_sdca_pcm_hw_free()`, `rt715_sdca_set_sdw_stream()`, and `rt715_sdca_shutdown()` manage stream lifetime.

Control flow: mixer puts convert ALSA values to SDCA fixed-point gain values (`rt715_sdca_vol_gain()`, `rt715_sdca_boost_gain()`) and write per-channel MBQ controls. Gets reverse fixed-point values through `rt715_sdca_get_gain()`. Mux controls read/write `RT715_HDA_LEGACY_MUX_CTL1` through `rt715_sdca_index_read()` and `rt715_sdca_index_update_bits()`, using control names to select the nibble for ADC 22 through 25. DAPM routes connect analog/digital mic inputs to ADCs and DP4/DP6; the `PDE23_24` supply writes SDCA request-power control on power up/down.

State and persistence: persistent driver state is in `rt715_sdca_priv`: two regmaps, SoundWire slave, `hw_init`, `first_hw_init`, hardware SDW version, and cached kcontrol originals used to report mixer change. Regcache starts offline and is enabled only after SoundWire attach. Runtime PM autosuspend is configured in init, but the device is not marked active until attach. On reinitialization, hardware-facing settings are restored by `io_init()` and regcache synchronization is handled by the SDW glue.

Dependencies and integration points: depends on Linux ASoC component/DAI/DAPM APIs, SoundWire stream setup (`snd_sdw_params_to_config()`, `sdw_stream_add_slave()`), runtime PM, regmap, and SDCA address macros. It is called from `rt715-sdca-sdw.c`, and its register constants/private state come from `rt715-sdca.h`.

Risks: mux selection depends on matching control names with `strstr()`, so renaming controls can break routing. Hardware revision paths for `RT715_AD_FUNC_EN` differ subtly. Several writes do not check return values, especially initialization and DAPM event writes. `rt715_sdca_pcm_hw_params()` advertises only 44.1/48 kHz DAIs while its switch accepts many SDCA rates, which may hide broader hardware support. Source inspection also shows duplicated tokens in this snapshot around one function declaration and duplicate `44100` case text; those are build-signal risks if this tree is compiled as-is.

Test signals: compile with this file enabled, boot-probe an RT715 SDCA SoundWire device, verify two capture DAIs enumerate, run `arecord` on DP4/DP6 at advertised rates/formats, exercise `FU0A/FU02/FU06` capture volume/switch and `FU0C/FU0E` boost controls through `amixer`, change each ADC mux, suspend/resume with active and idle capture, and confirm SDCA init writes occur once per attach and are restored after detach/re-attach.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt715-sdca.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt715-sdca.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt715-sdca.h

Purpose: shared header for the RT715 SDCA component and SoundWire bus glue. It defines private driver state, custom kcontrol metadata, register/node IDs, SDCA function/entity/control/channel constants, sample gain scaling, DAI IDs, and the public initialization entry points used by the bus driver.

Important types and APIs: `struct rt715_sdca_priv` carries both regmaps (`regmap` for normal SDCA controls and `mbq_regmap` for 16-bit MBQ/vendor controls), a SoundWire slave pointer, runtime flags (`hw_init`, `first_hw_init`), hardware SoundWire version, and arrays caching previous control values. `struct rt715_sdca_kcontrol_private` is embedded through macro-cast private values for custom ALSA controls and records register base, channel count, max, shift, and invert semantics. Public functions are `rt715_sdca_io_init()` and `rt715_sdca_init()`.

Control and integration role: constants map RT715 legacy NIDs (`RT715_MIC_ADC`, `RT715_MUX_IN*`, `RT715_VENDOR_REG`, `RT715_VENDOR_HDA_CTL`) to the SDCA implementation. The `FUN_*`, `RT715_SDCA_*`, and `CH_*` definitions are consumed by `SDW_SDCA_CTL(...)` in `rt715-sdca.c` and `rt715-sdca-sdw.c` to construct register addresses for frequency, mute, volume, gain, power, and SMPU trigger controls. `RT715_SDCA_DB_STEP` defines the 0.375 dB step conversion used by gain helpers.

State and persistence behavior: the header makes the two-regmap model explicit. Runtime PM and regcache correctness depends on `hw_init` and `first_hw_init`, while mixer change detection depends on the cached arrays in `rt715_sdca_priv`. There is no persistent storage outside kernel memory; values persist across runtime suspend through regcache and through reinitialization code.

Dependencies: includes Linux regmap, SoundWire, SoundWire type definitions, ASoC, workqueue, and device headers. The header does not include a reg-default table; that is supplied by the SDW-specific header/source pair for this driver variant.

Risks: `struct snd_soc_codec *codec` and fields such as `adc_mute_work`, debug IDs, `params`, and `l_is_unmute/r_is_unmute` appear unused by the current implementation, which increases maintenance ambiguity. The macro namespace uses generic channel symbols (`CH_00` etc.) that can collide if headers are combined carelessly. Function prototypes form the contract with the SDW glue, so changing their argument order would break probe.

Test signals: compile coverage should include every user of this header. Static analysis should check for unused state fields and macro collisions. Runtime validation is indirect: successful probe, control registration, and SDCA register access through `rt715-sdca.c` prove the constants and private state layout are coherent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt715-sdca.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt715-sdw.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt715-sdw.c

Purpose: SoundWire transport driver for the legacy/non-SDCA RT715 codec. It provides two regmaps: a raw 8-bit SoundWire register map and a higher-level 24-bit/32-bit codec regmap that translates HDA-like verb and private-index accesses into SoundWire transactions. It also handles slave property publication, attach-driven hardware initialization, bus clock programming callbacks, probe/remove, and suspend/resume.

Important APIs and functions: `rt715_sdw_probe()` creates `sdw_regmap` with `devm_regmap_init_sdw()` and a synthetic codec regmap with custom `rt715_sdw_read()`/`rt715_sdw_write()`, then calls `rt715_init()`. `rt715_readable_register()` and `rt715_volatile_register()` define cache visibility. `rt715_sdw_read()` translates index registers (`reg > 0xffff`) and HDA-style reads by writing command bytes through `sdw_regmap`, then reading `RT715_READ_HDA_3..0` to build a 32-bit value. `rt715_sdw_write()` performs matching multi-register command emission for private, 0x7000, and R-channel 0x8300-style operations.

Control flow: `rt715_read_prop()` advertises DP4/DP6 source ports, parity/bus-clash masks, no paging, invalid initial parity quirk, wake capability, and channel prepare timing. `rt715_update_status()` calls `rt715_io_init()` only when the slave reaches `SDW_SLAVE_ATTACHED` and hardware is not initialized. `rt715_bus_config()` stores bus params in `rt715_priv` and calls `rt715_clock_config()` to map current data-rate frequency to RT715 clock selector values. PM suspend marks the codec regmap cache-only. PM resume waits up to 5 seconds for SoundWire reinitialization when the slave detached, clears `unattach_request`, re-enables cache I/O, and syncs codec register regions.

State and persistence: runtime state lives in `struct rt715_priv` from `rt715.h`. `hw_init` gates attach init; `first_hw_init` gates PM resume and cache synchronization. Regcache preserves writable codec state during suspend, while the raw SDW regmap is uncached. Bus params are persisted in memory for clock config.

Dependencies and integration points: integrates with Linux SoundWire driver registration (`module_sdw_driver()`), `sdw_slave_ops`, regmap custom bus operations, runtime/system PM, and ASoC component logic in `rt715.c`. Device IDs match Realtek manufacturer `0x025d` product `0x714/0x715`, SDW version/class tuple `(0x2,0,0)`.

Risks: custom read/write translation is complex and several branches rely on register-number encodings; regressions can silently program the wrong HDA verb bytes. `rt715_sdw_read()` uses `*val` during command construction for some read paths, so callers must provide initialized values for those command encodings. Some writes after `sdw_stream_add_slave()` failures in higher layers are not unwound here. Source inspection shows a duplicated `if (ret < 0)` line in one branch; compile/test should confirm this snapshot's syntax.

Test signals: build the SDW module, verify probe against both IDs, inspect regmap debugfs readable/volatile behavior, validate DP4/DP6 source port properties, test attach/detach and bus clock changes, run runtime and system suspend/resume with cached mixer values, and exercise HDA/private indexed reads through ALSA controls that depend on custom regmap translation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt715-sdw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt715-sdw.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt715-sdw.h

Purpose: register-default table for the legacy RT715 SoundWire regmap. It is included by `rt715-sdw.c` to seed `rt715_regmap` with known reset/default values for codec, HDA verb, converter, mux, gain, and private-index registers.

Important data: `rt715_reg_defaults[]` is a static `struct reg_default` array spanning low SoundWire-accessible areas (`0x0000` ranges), function/converter/mux regions (`0x2000`, `0x2200`, `0x2230`), HDA verb addresses (`0x3122..0x3125`, `0x36xx`, `0x37xx`, `0x4c..0x4f`), ADC format registers, gain/mute registers, and the private vendor default `0x752039`. The table is consumed by `rt715_regmap` with `REGCACHE_MAPLE`.

Control flow and integration: the header contains no executable logic. Its defaults inform regcache comparisons, regcache sync after suspend, and initial software-visible state before the physical device is attached. `rt715_sdw.c` separately declares which of these registers are readable or volatile; defaults only matter for cached/nonvolatile addresses.

State and persistence: these defaults are not persisted outside the module image. During runtime, regcache uses them as baseline values and later tracks writes from `rt715.c`. Resume paths sync selected regions from this cache back to hardware after SoundWire detach or suspend.

Dependencies: requires `struct reg_default` from regmap but the header itself relies on being included after suitable Linux headers. It is tightly coupled to address constants and translation behavior in `rt715-sdw.c` and to control addresses in `rt715.h`.

Risks: stale default values can cause regcache to skip writes that hardware actually needs after reset. Defaults for volatile or readback-derived registers have limited value and must match the readable/volatile filters. The large literal table is easy to drift from vendor programming sequences in `rt715.c`.

Test signals: verify regcache sync restores mute, format, mux, and input-selection state across suspend/resume; compare defaults against vendor datasheet or known-good kernel; use regmap debugfs to ensure nonvolatile cached defaults match expected reset state; run ALSA controls before and after resume to catch skipped cache writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt715-sdw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt715.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt715.c

Purpose: ASoC component implementation for the legacy RT715 SoundWire microphone codec. It registers capture-only DAIs, ALSA mixer controls, DAPM routes, bias management, PCM SoundWire stream setup, hardware reset/init, and bus clock configuration.

Important APIs and functions: `rt715_init()` allocates `rt715_priv`, stores regmaps/slave, puts the codec regmap in cache-only mode, registers the component and two DAIs, and enables runtime PM autosuspend. `rt715_io_init()` performs attach-time hardware programming: reset, mute ADC nodes, enable DMIC pins, set stream IDs, write DMIC pin configuration defaults, power down to D3, and set `hw_init/first_hw_init`. `rt715_clock_config()` maps SoundWire bus frequency to selector values written to `0xe0` and `0xf0`. Index helpers (`rt715_index_write*`, `rt715_index_read_nid()`, `rt715_index_update_bits()`) target private vendor registers through the custom regmap.

Control flow: ALSA controls manipulate HDA gain/mute verbs. `rt715_set_amp_gain_put/get()` handles two-channel boost controls while preserving mute/gain bits and retrying writes up to three times. `rt715_set_main_switch_put/get()` and `rt715_set_main_vol_put/get()` provide 8-channel capture switch/volume across four ADC nodes. Mux get/put functions read/write connect-select verbs and normalize ADC 24/25 values where hardware has duplicate mux indices. DAPM maps MIC/LINE/DMIC inputs through muxes into ADCs and DP4/DP6 capture endpoints. `rt715_set_bias_level()` writes D0 on prepare and D3 on standby with the RT715 power-up delay.

PCM integration: `rt715_pcm_hw_params()` converts ALSA params to SoundWire stream/port config, maps AIF1 to port 6 and AIF2 to port 4, programs `RT715_SDW_INPUT_SEL`, adds the slave to the stream, validates rate/channels/width, and writes format registers for all ADC converters. `rt715_pcm_hw_free()` removes the slave from the stream.

State and persistence: `rt715_priv` stores register maps, SoundWire slave, bus params, init flags, and previous mixer values. Regcache is offline before attach and becomes the persistence layer for mixer/routing state across suspend. Init sequences are rerun after attach; PM resume in `rt715-sdw.c` syncs selected cached regions.

Dependencies and integration points: depends on ASoC controls/DAPM/DAI, SoundWire stream helpers, runtime PM, HDA verb constants, regmap, and `rt715-sdw.c` for transport and PM callbacks.

Risks: many initialization and control `regmap_write()` calls ignore errors. The gain update paths manually preserve bitfields and retry; subtle readback mismatches can leave ALSA state diverged from hardware. If `sdw_stream_add_slave()` succeeds and later sample-rate/format validation fails, this function returns an error without removing the slave. Source inspection shows duplicated local declaration text in this snapshot, which should be caught by compilation.

Test signals: build-test with `CONFIG_SND_SOC_RT715`, enumerate both DAIs, capture from DP4/DP6 at 44.1/48 kHz and all advertised formats, exercise capture volume/switch/boost controls, validate bias transitions with runtime PM, test clock configs across supported SoundWire rates, and suspend/resume while preserving mux and gain state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt715.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt715.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt715.h

Purpose: shared declarations for the legacy RT715 ASoC/SoundWire driver. It defines private state, codec node IDs, HDA verb/register encodings, derived register-address macros, gain bit shifts, DAI IDs, power delay, and public entry points used between `rt715.c` and `rt715-sdw.c`.

Important types and APIs: `struct rt715_priv` stores high-level and raw SoundWire regmaps, SoundWire slave, bus params, init flags, and cached mixer values for two-channel and eight-channel controls. Public functions are `rt715_init()`, `rt715_io_init()`, and `rt715_clock_config()`. The enum defines `RT715_AIF1` and `RT715_AIF2`.

Control and integration role: constants encode RT715 NIDs (`RT715_MIC_ADC`, `RT715_DMIC*`, `RT715_MUX_IN*`, vendor node `RT715_VENDOR_REGISTERS`), HDA verbs (`RT715_VERB_SET_*`), private index/data addresses, ADC format registers, and convenience macros such as `RT715_SET_GAIN_MIC_ADC_H` or `RT715_SET_STREAMID_MIX_ADC2`. `RT715_DIR_IN_SFT` and `RT715_DIR_OUT_SFT` drive gain/mute command construction. `RT715_POWER_UP_DELAY_MS` is used during bias transition.

State and persistence behavior: the header defines the in-memory state that persists across runtime PM events while the device object exists. `hw_init` prevents duplicate attach init, `first_hw_init` differentiates first attach from later restore, and cached control arrays allow put callbacks to report changes without relying entirely on hardware reads. Actual register persistence is handled by regcache in the source files.

Dependencies: includes regulator consumer but relies on source files for regmap, SoundWire, and ASoC definitions before using the struct. It is tightly coupled to the custom HDA/SoundWire translation in `rt715-sdw.c`; address macro changes must be kept in sync with the readable/volatile lists and defaults table.

Risks: stale or incorrect register encodings can affect many controls at once because the macros compose verb and NID bits. Several fields (`codec`, debug IDs) appear unused in modern ASoC component code. The header exposes no compile-time validation that high/low gain macro pairs match hardware channel semantics.

Test signals: compile-test both source files that include this header; runtime smoke tests should verify every macro-backed control path: pin setup, stream ID setup, ADC format writes, gain/mute controls, mux selection, and private vendor index access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt715.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt721-sdca-sdw.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt721-sdca-sdw.c

Purpose: SoundWire bus driver for the RT721 SDCA codec. It supplies normal and MBQ regmap configurations, SoundWire slave properties, SDCA interrupt handling, attach-driven component initialization, device ID binding, and PM behavior for the ASoC component in `rt721-sdca.c`.

Important APIs and functions: `rt721_sdca_sdw_probe()` creates a 16-bit MBQ regmap with `devm_regmap_init_sdw_mbq()` and an 8-bit SDCA regmap with `devm_regmap_init_sdw()`, then calls `rt721_sdca_init()`. Readable/volatile filters are split between `rt721_sdca_readable_register()`/`volatile_register()` for normal SDCA/HID registers and `rt721_sdca_mbq_readable_register()`/`mbq_volatile_register()` for 16-bit vendor/volume controls. `rt721_sdca_read_prop()` advertises source ports 2 and 6, sink ports 1 and 3, full data-port behavior, paging, wake capability, lane control, parity/bus-clash masks, and a long clock-stop timeout.

Control flow: `rt721_sdca_update_status()` clears `hw_init` on unattach, restores SDCA interrupt masks on attach when a jack is registered, and calls `rt721_sdca_io_init()` only for first attach after reset. `rt721_sdca_interrupt_callback()` cancels pending jack detection work, captures SDCA interrupt status registers, clears cascade/status bits with up to three retries, preserves pending status if work was canceled, and schedules `jack_detect_work` unless system suspend has set `disable_irq`. It uses `disable_irq_lock` to coordinate with suspend.

PM and state persistence: runtime suspend cancels jack work and marks both regmaps cache-only. System suspend first disables SDCA interrupt masks under lock and sets `disable_irq`, then uses the runtime suspend path. Resume waits up to 5 seconds for SoundWire initialization if the slave detached, re-enables interrupt masks when appropriate, clears `unattach_request`, disables cache-only mode, and syncs both regmaps. Remove cancels work, disables runtime PM after first init, and destroys mutexes.

Dependencies and integration points: integrates with SoundWire `sdw_slave_ops`, SDCA interrupt registers, regmap cache, runtime PM, and shared helpers from `rt-sdw-common.h` through the component source. Device ID is Realtek `0x025d`, part `0x721`, SDW v3 class tuple `(0x3,0x1,0)`.

Risks: interrupt clearing depends on SoundWire SDCA cascade semantics and races with delayed work and system suspend. Readable/volatile allowlists must include every register touched by the component; missing entries can break regcache or debug access. Resume sync of both regmaps can replay stale values if initialization presets and cache dirtiness are not coordinated.

Test signals: build and probe RT721 SDCA, inspect advertised DP1/DP2/DP3/DP6 ports, trigger headset insertion and button interrupts, run runtime and system suspend/resume during jack work, validate interrupt mask restoration after detach/re-attach, and confirm cached volume/mute/routing controls survive resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt721-sdca-sdw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt721-sdca-sdw.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt721-sdca-sdw.h

Purpose: regmap default header for the RT721 SDCA SoundWire driver. It defines reset/default values for the normal 8-bit SDCA regmap and the 16-bit MBQ/vendor regmap used by `rt721-sdca-sdw.c`.

Important data: `rt721_sdca_reg_defaults[]` includes SDW/SDCA control defaults for sample-frequency indices, PDE request power states, mute defaults for jack, mic-array, and amplifier functions, vendor controls, and HID-related low register defaults. `rt721_sdca_mbq_defaults[]` includes vendor HDA-float, analog, jack, gain, and volume defaults, including SDCA FU volume/ch-gain registers for jack codec, mic array, and amp functions.

Control flow and integration: no functions are defined. The arrays are wired into `rt721_sdca_regmap` and `rt721_sdca_mbq_regmap` with `REGCACHE_MAPLE`. They define software cache baseline before the device is attached and help resume sync determine what changed from default.

State and persistence: defaults are static module data. Runtime state is maintained by regcache after writes from `rt721-sdca.c`; these arrays only seed initial cache contents. Because RT721 has two cached regmaps, defaults must be correct for both 8-bit and 16-bit address/value domains.

Dependencies: includes regmap and SoundWire register macros and relies on RT721 function/entity/control/channel constants from `rt721-sdca.h` being available in the include order used by the SDW source.

Risks: omissions in this table can lead to incorrect restore after SoundWire reset, while defaults for registers later treated as volatile may be misleading. The MBQ defaults contain many vendor literal addresses, making drift from hardware presets hard to see in review. Any mismatch between default value width and the owning regmap can corrupt cache behavior.

Test signals: verify runtime suspend/resume preserves mute, power-state, sample-rate, volume, and gain settings; compare regcache dumps before/after resume; run jack and audio playback/capture after detach/re-attach; review any added component register access against the readable/volatile filters and defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt721-sdca-sdw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt721-sdca.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt721-sdca.c

Purpose: ASoC component implementation for the RT721 SDCA SoundWire codec. It supports headphone playback, headset-mic capture, speaker playback, digital-mic capture, headset jack/button detection, DAPM power sequencing, mixer controls, SoundWire DAI stream setup, and hardware preset programming.

Important APIs and functions: `rt721_sdca_init()` allocates private state, stores normal/MBQ regmaps, initializes mutexes and delayed work, initializes mute state, and registers the component with three DAIs. `rt721_sdca_io_init()` enables regcache I/O on attach, sets up runtime PM on first attach, optionally bypasses cache on reinit, runs `rt721_sdca_dmic_preset()`, `rt721_sdca_amp_preset()`, and `rt721_sdca_jack_preset()`, then marks hardware initialized. `rt721_sdca_probe()` parses `realtek,jd-src`, stores the component pointer, and resumes PM. `rt721_sdca_set_jack_detect()` stores the ASoC jack, resumes the device, and enables jack interrupt behavior through `rt721_sdca_jack_init()`.

Control flow: jack detection is workqueue-based. `rt721_sdca_jack_detect_handler()` reacts to SDCA status bits captured by the bus driver, calls shared `rt_sdca_headset_detect()` and `rt_sdca_button_detect()`, reports headset/buttons, and schedules button rechecks for release polling. `rt721_sdca_btn_check_handler()` rereads HID message data and reports button state. Mixer controls convert ALSA gain values to 16-bit SDCA volume/boost encodings, maintain combined DAPM/mixer mute state for FU0F and FU1E, and expose DMIC gain arrays. ADC mux helpers route analog and digital mic sources through SDCA HDA-float mux registers.

DAPM and PCM: DAPM widgets model HP, SPK, MIC/LINE/DMIC inputs, PDE supplies, DAC/ADC function units, muxes, and DP1/DP2/DP3/DP6 endpoints. Event handlers write request-power states and mute/unmute FU/PDE controls. `rt721_sdca_pcm_hw_params()` maps AIF1 playback to port 1 and capture to port 2, AIF2 playback to port 3, AIF3 capture to port 6, adds the SoundWire slave, validates channel count, and writes sample-frequency indices for the relevant SDCA clock selectors.

State and persistence: `rt721_sdca_priv` tracks jack state, SDCA interrupt status, delayed work, DAPM/mixer mute booleans, regmaps, mutexes, and init flags. Regcache persists user controls across runtime/system suspend; preset functions run after attach and mark cache dirty on reinit to force a coherent restore.

Dependencies and integration points: depends on ASoC, SoundWire stream helpers, runtime PM, regmap, SDCA macros, and `rt-sdw-common.h` for shared RT SDCA jack/button/index helpers. It is paired with `rt721-sdca-sdw.c` for interrupts, PM, and regmap creation.

Risks: jack/button handling depends on component/card instantiation checks and delayed-work races coordinated by the bus layer. Many vendor preset writes ignore errors. Some DAPM event sequences use fixed sleeps or unverified writes. Source inspection shows an extra closing brace near one PDE event in this snapshot, so compile coverage is important. If `sdw_stream_add_slave()` succeeds and later validation fails, stream cleanup is not performed in this function.

Test signals: build-test, enumerate all three DAIs, play HP and speaker streams, capture headset and DMIC streams, exercise headset insertion/removal and four button codes, test all mixer and mux controls, validate DAPM power transitions through debug logs/register traces, and suspend/resume during audio and jack events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt721-sdca.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt721-sdca.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt721-sdca.h

Purpose: shared RT721 SDCA definitions for the ASoC component and SoundWire transport. It describes private state, custom DMIC-control metadata, vendor node/index constants, SDCA function/entity/control/channel IDs, sample-frequency codes, HID IDs, DAI IDs, and public init entry points.

Important types and APIs: `struct rt721_sdca_priv` carries the normal and MBQ regmaps, component and slave pointers, SoundWire bus params, init flags, calibration and interrupt mutexes, suspend interrupt gating (`disable_irq`), SDCA interrupt snapshots, ASoC jack pointer, delayed works, jack type/source, and DAPM/mixer mute state for headset capture and DMIC capture. `struct rt721_sdca_dmic_kctrl_priv` provides register base, count, max, and invert parameters for custom controls. Public functions are `rt721_sdca_io_init()` and `rt721_sdca_init()`.

Control and integration role: register constants organize vendor NIDs for analog power, DAC, jack detect, combo jack, class-D amp, boost, calibration, efuse, analog control, and HDA SDCA float controls. SDCA function/entity/control constants construct addresses for jack codec, mic array, HID, and amp functions. Sample-rate constants map ALSA rates to SDCA frequency indices. `RT721_BUF_ADDR_HID*` and `RT721_SDCA_HID_ID` support HID button-message reads.

State and persistence behavior: header-defined fields are the authoritative in-memory persistence for jack state, pending SDCA interrupt status, and user mute settings. Regcache persistence is implemented by source files, but the header's split between `regmap` and `mbq_regmap` is central to cache restore. `first_hw_init` and `hw_init` separate probe-time allocation from attach-time programming.

Dependencies: includes Linux PM, regmap, SoundWire, SoundWire type, ASoC, and workqueue headers. It is also implicitly coupled to `rt-sdw-common.h` helper semantics used by the implementation, though that common header is included in the `.c` file.

Risks: large macro surface can drift from vendor datasheet or SDCA address construction. Generic names such as `CH_L` and `FUNC_NUM_*` can collide if included in broader compilation scopes. Fields such as `params` and `jd_src` are lightly used or only parsed, so future behavior may require clearer validation.

Test signals: compile all RT721 users; validate all DAI IDs route to expected ports; test sample-rate index writes; verify HID button paths use the correct buffer/report ID; exercise jack state and mute-state persistence across detach, runtime suspend, and system suspend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt721-sdca.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt722-sdca-sdw.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt722-sdca-sdw.c

Purpose: SoundWire bus driver for the RT722 SDCA codec. It creates a single 16-bit MBQ-capable SDCA regmap with per-register MBQ width selection, publishes SoundWire properties, handles SDCA interrupts, coordinates attach-time initialization, and implements PM for the RT722 ASoC component.

Important APIs and functions: `rt722_sdca_mbq_size()` is the core register classifier; it returns 1 for one-byte SDCA/HID/control registers, 2 for two-byte vendor/volume/gain registers, and 0 for inaccessible registers. `rt722_mbq_config` passes that classifier to `devm_regmap_init_sdw_mbq_cfg()` in `rt722_sdca_sdw_probe()`. `rt722_sdca_readable_register()` uses the same classifier, while `rt722_sdca_volatile_register()` marks live status, power-state, HID, and selected vendor registers. `rt722_sdca_read_prop()` configures source ports 2/6, sink ports 1/3, full data ports, paging, wake capability, lane control, and clock-stop timeout.

Control flow: `rt722_sdca_update_status()` clears `hw_init` on unattach, restores interrupt masks when a jack exists and the slave reattaches, and calls `rt722_sdca_io_init()` when needed. `rt722_sdca_interrupt_callback()` mirrors RT721: cancel pending jack work, snapshot SDCA interrupt status, clear SDCA cascade bits with retries, preserve pending status after canceled work, and schedule `jack_detect_work` unless suspended. System suspend sets `disable_irq` and masks SDCA interrupt bits under `disable_irq_lock`; resume restores masks when no detach occurred or waits up to 5 seconds for reinitialization after detach, then syncs regcache.

State and persistence: the bus driver owns no separate state beyond the `rt722_sdca_priv` allocated by the component. Regcache is marked cache-only on suspend and synced on resume. `hw_init`, `first_hw_init`, `disable_irq`, and `scp_sdca_stat*` are the key state variables shared with component jack/work handlers.

Dependencies and integration points: depends on SoundWire SDCA registers, regmap SDW MBQ configuration, runtime PM, delayed work coordination in `rt722-sdca.c`, and constants/defaults from `rt722-sdca.h` and `rt722-sdca-sdw.h`. Device ID is Realtek `0x025d`, part `0x722`, SDW v3 class tuple `(0x3,0x1,0)`.

Risks: correctness hinges on the large `rt722_sdca_mbq_size()` allowlist. A missing register can make valid component access fail; a wrong width can corrupt transactions. Interrupt clearing is retry-limited and races with suspend/workqueue scheduling. As with RT721, resume can replay stale cached state if initialization flags and cache dirtiness are not aligned.

Test signals: build and probe RT722 SDCA, verify MBQ widths using regmap debug or bus traces, test DP1/DP2/DP3/DP6 audio paths, trigger jack/button SDCA interrupts, suspend/resume with pending delayed work, detach/re-attach the slave, and confirm cached controls and interrupt masks are restored.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt722-sdca-sdw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt722-sdca-sdw.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt722-sdca-sdw.h

Purpose: RT722 SDCA regmap-default header. It supplies `rt722_sdca_reg_defaults[]` for the single MBQ-configured SDCA regmap created by `rt722-sdca-sdw.c`.

Important data: the defaults include low SDCA/vendor registers (`0x2f*`, `0x200*`, `0x581*`, `0x610*`) plus constructed SDCA control addresses for jack codec, mic array, HID-adjacent function controls, amp controls, sample-frequency indices, request-power states, mute defaults, volume defaults, and function-unit channel gains. Defaults put major paths in muted or PS3-like safe states and set 48 kHz-style sample-frequency indices (`0x09`) initially.

Control flow and integration: the header has no functions. `rt722-sdca-sdw.c` plugs this array into `rt722_sdca_regmap` using `REGCACHE_MAPLE`; the same source determines whether each register is one or two bytes with `rt722_sdca_mbq_size()`. The component source later updates these cached values during preset, DAPM, mixer, and PCM operations.

State and persistence: static defaults seed software regcache before attach and after allocation. Runtime persistence comes from regcache mutations, dirty marking, and resume sync. Since RT722 uses one width-aware regmap rather than separate normal/MBQ regmaps, the defaults must match the width classifier exactly.

Dependencies: includes Linux regmap and SoundWire registers and relies on RT722 SDCA constants from `rt722-sdca.h` in the including source. It is coupled to both the MBQ classifier and the component register writes.

Risks: a default address absent from the MBQ-size allowlist will not be readable/writable through the configured regmap as expected. Width mismatches are particularly risky because a 1-byte default for a 2-byte control, or vice versa, can produce incorrect cache sync. Defaults may become stale relative to the guarded function-initialization presets in `rt722-sdca.c`.

Test signals: run regcache sync tests across runtime/system suspend, compare default and live values for mute/power/sample-rate controls, validate that every default address has a nonzero MBQ size classifier, and exercise audio/jack paths after detach/re-attach.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt722-sdca-sdw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt722-sdca.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt722-sdca.c

Purpose: ASoC component implementation for the RT722 SDCA SoundWire codec. It supports headphone playback, headset capture, speaker playback, digital-mic capture, combo-jack and button handling, SDCA mixer controls, DAPM power sequencing with power-state polling, SoundWire stream setup, and guarded hardware preset initialization.

Important APIs and functions: `rt722_sdca_init()` allocates private state, stores the regmap/slave, starts regcache cache-only, initializes mutexes/delayed works and default mute booleans, then registers three DAIs. `rt722_sdca_io_init()` enables cache I/O after attach, configures runtime PM on first init, reads hardware version from `RT722_JD_PRODUCT_NUM`, runs `rt722_sdca_dmic_preset()`, `rt722_sdca_amp_preset()`, and `rt722_sdca_jack_preset()`, marks cache dirty on reinit, and sets `hw_init`. `rt722_sdca_index_write/read()` expose vendor NID/register access and are declared in the header.

Control flow: jack detection is local rather than using `rt-sdw-common.h`. `rt722_sdca_headset_detect()` reads SDCA detected mode, maps it to headphone/headset jack bits, and writes selected mode. `rt722_sdca_button_detect()` reads HID owner/offset/message bytes, decodes button bits, and returns ownership to the device. Delayed workers report jack/button state and poll button release. `rt722_sdca_jack_init()` enables SDCA interrupt masks and configures unsolicited/HID behavior under `calibrate_mutex`.

Mixer/DAPM/PCM: gain controls convert ALSA integer values to SDCA 16-bit volume/boost encodings; FU0F and FU1E capture controls combine mixer mutes with DAPM mutes. DAPM widgets model HP, SPK, MIC/LINE/DMIC, PDE supplies, DAC/ADC FUs, muxes, and DP1/DP2/DP3/DP6 endpoints. PDE event handlers request PS0/PS3 and call `rt722_pde_transition_delay()` to poll actual power state. `rt722_sdca_pcm_hw_params()` maps AIF1 playback/capture to ports 1/2, AIF2 speaker playback to port 3, AIF3 DMIC capture to port 6, adds the SoundWire slave, validates channels/rates, and writes sample-frequency indices.

State and persistence: `rt722_sdca_priv` tracks regmap, component/slave, init flags, jack state, interrupt snapshots, delayed work, mutexes, hardware version, and combined mute booleans. Preset functions check SDCA function status `FUNCTION_NEEDS_INITIALIZATION` so some programming is skipped unless the hardware reports the need or this is first init. Regcache is the persistence layer across PM.

Dependencies and integration points: paired with `rt722-sdca-sdw.c` for probe, PM, interrupts, and MBQ sizing. Depends on ASoC, SoundWire, runtime PM, regmap, SDCA macros, and jack reporting APIs.

Risks: many preset writes ignore errors; jack calibration loops can wait up to about one second and only debug-log timeout. `rt722_sdca_pcm_hw_params()` can leave a SoundWire slave added if validation after `sdw_stream_add_slave()` fails. Some source text shows duplicated `SND_JACK_BTN_0/1` in a report mask, probably harmless but noisy. Header declares `rt722_sdca_jack_detect()` but this file provides internal detection helpers, so external declaration drift should be reviewed.

Test signals: build-test, run HP and speaker playback, headset and DMIC capture, exercise jack insertion modes and four button codes, validate function-status guarded presets on first boot and after reset, test DAPM power-state polling, verify hardware-version-specific branches, and suspend/resume during active streams and pending jack work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt722-sdca.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt722-sdca.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt722-sdca.h

Purpose: shared RT722 SDCA definitions for the component and SoundWire bus driver. It defines the private state structure, custom control metadata, vendor nodes/registers, SDCA function/entity/control/channel IDs, sample-rate indices, function-status flags, jack-detect and hardware-version enums, and public init/index APIs.

Important types and APIs: `struct rt722_sdca_priv` stores the single MBQ-aware regmap, component and slave pointers, bus params, init flags, calibration and interrupt mutexes, suspend interrupt gating, SDCA interrupt snapshots, ASoC jack pointer, delayed works, jack type/source, FU0F/FU1E mute booleans, and `hw_vid`. `struct rt722_sdca_dmic_kctrl_priv` supplies register base/count/max/invert for custom mixer controls. Public functions include `rt722_sdca_init()`, `rt722_sdca_io_init()`, `rt722_sdca_index_write()`, `rt722_sdca_index_read()`, and a declared `rt722_sdca_jack_detect()`.

Control and integration role: constants cover RT722 vendor NIDs (`RT722_VENDOR_REG`, calibration, efuse, IMS/DRE, analog, HDA control), index registers for bias, combo-jack auto detect, calibration, HID/UMP controls, floating power controls, mixer controls, EAPD, and SDCA function controls. SDCA function/entity/control IDs are used in `SDW_SDCA_CTL(...)` address construction across both source files. `FUNCTION_NEEDS_INITIALIZATION` gates preset writes. Enums define DAI IDs and RT722 hardware variants VA/VB.

State and persistence behavior: the header captures all runtime state required for jack handling and PM coordination. Unlike RT721, RT722 has one regmap, so all persistent control state relies on that single cache plus the driver's booleans for mixer/DAPM mute composition. `hw_vid` persists the detected hardware variant for variant-specific initialization.

Dependencies: includes Linux PM, regmap, SoundWire, SoundWire type, ASoC, and workqueue headers. It is coupled to `rt722-sdca-sdw.c`'s MBQ-width classifier and to the component's preset/control code.

Risks: the declared `rt722_sdca_jack_detect()` is not the primary local helper name in the implementation viewed here, suggesting stale API surface. Generic macro names (`FUNC_NUM_*`, `CH_*`) can collide. Hardware constants are numerous and vendor-specific; mistakes are hard to validate without hardware traces.

Test signals: compile all users, verify every public prototype has a matching definition or intentional external provider, validate DAI IDs/port mapping, exercise function-status initialization paths, run jack/button tests, and confirm VA/VB-specific branches are covered on representative hardware or emulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt722-sdca.h -->
