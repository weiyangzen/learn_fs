# subset-b-006429 Cirrus Logic ASoC Codec Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs42l42-sdw.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs42l42-sdw.c

## Purpose

`cs42l42-sdw.c` is the SoundWire bus glue for the Cirrus Logic CS42L42 ASoC codec. It adapts the common CS42L42 core in `cs42l42.c` to the SoundWire transport by providing SoundWire register access, SoundWire DAI stream setup, port preparation power hooks, attach/unattach handling, and runtime/system PM behavior. It replaces the normal ASP DAPM routes with SoundWire SRC routes and exports no public APIs of its own beyond the module driver.

## Important APIs, Types, and Functions

- `cs42l42_sdw_dai_startup()` refuses PCM startup until `init_done` is true, preventing ALSA streams before SoundWire enumeration and common codec initialization.
- `cs42l42_sdw_dai_hw_params()` converts ALSA params into `sdw_stream_config` and `sdw_port_config`, chooses DP2 for playback and DP1 for capture, calls `sdw_stream_add_slave()`, caches `sample_rate`, and configures SRC clocks through `cs42l42_src_config()`.
- `cs42l42_sdw_dai_prepare()` validates that both SoundWire-derived `sclk` and `sample_rate` are known, then calls `cs42l42_pll_config()`.
- `cs42l42_sdw_dai_hw_free()` removes the slave from the SoundWire stream and clears `sample_rate`.
- `cs42l42_sdw_port_prep()` powers headphone or ADC blocks around SoundWire port prepare/deprepare using `CS42L42_PWR_CTL1`.
- `cs42l42_sdw_read()` and `cs42l42_sdw_write()` implement custom regmap bus access. Registers are offset by `0x8000`; reads handle both immediate and delayed SoundWire memory-read completion through `MEM_ACCESS_STATUS`.
- `cs42l42_sdw_read_prop()`, `cs42l42_sdw_update_status()`, and `cs42l42_sdw_bus_config()` are the `sdw_slave_ops`.
- `cs42l42_sdw_runtime_suspend()`, `cs42l42_sdw_runtime_resume()`, and `cs42l42_sdw_resume()` manage cache-only regmap mode and SoundWire reattach recovery.
- `cs42l42_sdw_probe()` allocates private state, obtains IRQ from ACPI/DT, clones the shared regmap/component definitions for SoundWire-specific changes, enables runtime PM, and calls `cs42l42_common_probe()`.

## Control Flow

Probe allocates `struct cs42l42_private`, discovers an optional hardware IRQ, clones `cs42l42_regmap`, changes it to 16-bit register addressing with custom SoundWire read/write callbacks, starts in cache-only mode, clones `cs42l42_soc_component`, swaps DAPM routes to the SoundWire map, initializes runtime PM, and delegates resource/power/component registration to `cs42l42_common_probe()`.

SoundWire enumeration drives the real initialization. `update_status(ATTACHED)` ignores stale first attach reports while `sdw_waiting_first_unattach` is set. After a real attach, `cs42l42_sdw_init()` disables cache-only mode, calls `cs42l42_init()`, syncs cache writes that happened before attach, disables conditional clock-stop logic, and releases the probe-time runtime PM reference. `update_status(UNATTACHED)` is used during probe synchronization to release reset after the SoundWire core has seen the device absent.

PCM setup flows through the DAI ops: machine driver supplies an `sdw_stream` via `.set_stream`, `hw_params` adds the slave port, `bus_config` records `sclk` as half the current data rate, and `prepare` configures the shared PLL. Teardown removes the stream and resets `sample_rate`.

## State and Persistence Behavior

The file mutates shared `cs42l42_private` fields: `sdw_peripheral`, `sample_rate`, `sclk`, `sdw_waiting_first_unattach`, `init_done`, and runtime PM state. Regmap cache is the persistence boundary across pre-enumeration, runtime suspend, and system suspend. Cache writes are held until attach, then synced. After a SoundWire bus reset/unattach, `cs42l42_sdw_handle_unattach()` waits for `initialization_complete`, performs a soft reboot through a bypassed regmap write, sleeps for boot time, and marks the cache dirty before restore.

## Dependencies and Integration Points

This file depends on the Linux SoundWire core, ASoC DAI/component APIs, `sound/sdw.h` helpers, regmap custom bus callbacks, runtime PM, ACPI/OF IRQ discovery, and the common CS42L42 core exports in namespace `SND_SOC_CS42L42_CORE`. Build integration is through `CONFIG_SND_SOC_CS42L42_SDW` and `snd-soc-cs42l42-sdw.o`.

## Risks

Register access is timing-sensitive because delayed SoundWire reads poll very short intervals. Incorrect cache-only transitions can lose pre-attach configuration or attempt bus I/O while the manager is suspended. The driver rejects SoundWire clock changes while `stream_use` is nonzero; missing that guard can glitch active audio. Attach/unattach sequencing is subtle because stale ATTACH notifications after reset are explicitly filtered. `cs42l42_sdw_runtime_resume()` has a branch for `ret > 0`, but `cs42l42_sdw_handle_unattach()` currently returns only 0 or negative, so debounce waiting appears unreachable.

## Test Signals

Useful tests include SoundWire enumeration with stale attach conditions, runtime suspend/resume with regcache sync, system suspend while attached and after bus reset, playback and capture on DP2/DP1, unsupported clock/sample-rate combinations returning errors in `prepare`, and jack IRQ handling after SoundWire PM transitions. Build with `CONFIG_SND_SOC_CS42L42_CORE` and `CONFIG_SND_SOC_CS42L42_SDW`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs42l42-sdw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs42l42.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs42l42.c

## Purpose

`cs42l42.c` is the shared ASoC core for the Cirrus Logic CS42L42 codec. It provides the register map, default register cache, ALSA controls, DAPM widgets/routes, ASP DAI implementation, PLL/SRC programming, jack/headset/button detection, IRQ thread, device-property parsing, suspend/resume sequencing, and common probe/remove helpers used by bus-specific drivers.

## Important APIs, Types, and Functions

- `cs42l42_regmap`, `cs42l42_readable_register()`, `cs42l42_volatile_register()`, and `cs42l42_page_range` define the paged 8-bit regmap and cache behavior.
- `cs42l42_soc_component` exposes controls, DAPM widgets/routes, and `.set_jack`.
- `cs42l42_dai` exposes the non-SoundWire ASP DAI with playback/capture, supported formats, and `cs42l42_ops`.
- `cs42l42_pll_config()` selects a table entry for SCLK and sample rate, configures pass-through or PLL registers, and refuses reconfiguration while a stream is active.
- `cs42l42_src_config()` sets ASRC clock selection and 96 kHz enable bits when no stream is active.
- `cs42l42_pcm_hw_params()`, `cs42l42_set_dai_fmt()`, `cs42l42_set_sysclk()`, and `cs42l42_set_bclk_ratio()` implement ASP clocking, channel placement, LRCLK, and format setup.
- `cs42l42_mute_stream()` is the stream start/stop power-clock transition point. It starts/stops PLL, switches between SCLK and oscillator, tracks `stream_use`, and mutes/unmutes headphone output.
- `cs42l42_irq_thread()` handles tip-sense, automatic headset type detection, unplug, and button press/release reports.
- `cs42l42_common_probe()`, `cs42l42_init()`, and `cs42l42_common_remove()` are the exported lifecycle helpers used by I2C and SoundWire front ends.

## Control Flow

Common probe stores driver data, initializes `irq_lock`, gets regulators, powers supplies, obtains optional reset GPIO, holds SoundWire devices in reset until an UNATTACH synchronization point, optionally requests a threaded IRQ, and registers the ASoC component/DAI. Bus-specific drivers later call `cs42l42_init()` once registers are accessible.

Initialization reads and validates the device ID, logs revision, powers up the core while leaving functional blocks DAPM-controlled, parses device properties, applies SoundWire SRC override if needed, configures headset detection, sets `init_done`, and programs interrupt masks.

ASP PCM setup calculates BCLK from machine-provided ratio, explicit SCLK, or ALSA params, configures capture/playback channel resolution and placement, then applies PLL, LRCLK, and SRC settings. Muting controls the active clock source: first unmute starts PLL if needed, selects PLL/SCLK, and marks stream active; final mute switches back to the internal oscillator, disconnects/stops PLL, and clears stream state.

Jack detection starts with tip-sense. On plug, `cs42l42_init_hs_type_detect()` powers HS bias and starts automatic type detection. On auto-detect completion, `cs42l42_process_hs_type_detect()` may run manual fallback, configures CTIA/OMTP switches or headphone behavior, enables button detection for headset types, and reports the jack type. Button interrupts are debounced, bias thresholds are swept, and reports map to `SND_JACK_BTN_0` through `BTN_3`.

## State and Persistence Behavior

`struct cs42l42_private` persists register map, supplies, reset GPIO, IRQ, jack pointer, SoundWire pointer, PLL selection, SCLK, sample rate, BCLK ratio, plug/headset state, debounce/property values, stream bitmap, suspend flag, and init status. Regmap defaults/cache hold most hardware configuration. Suspend saves registers overwritten by the shutdown sequence, writes a datasheet power-down sequence, waits for PDN_DONE, puts regmap in cache-only mode, resets and disables regulators, then restores saved values into cache. Resume powers supplies and reset, marks cache dirty, syncs `MIC_DET_CTL1` first for VP-domain correctness, syncs the full cache, and clears `suspended`.

## Dependencies and Integration Points

The core depends on ASoC component/DAI/DAPM/control APIs, ALSA jack reporting, regmap with paged ranges, regulator bulk APIs, GPIO reset, runtime PM callers, firmware/device properties, and `cirrus_read_device_id()`. It exports symbols in `SND_SOC_CS42L42_CORE` for I2C/SoundWire bus modules.

## Risks

Clock programming is fragile: unsupported SCLK/sample-rate combinations return `-EINVAL`, while changes during active streams return `-EBUSY`. `stream_use` is a bitmap keyed by ALSA stream direction, so changes must preserve capture/playback independence. Headset detection uses many sleeps, debounce parameters, sticky interrupt reads, and hardware switch states; races with suspend and jack registration are guarded by `irq_lock`. Regmap cache ordering matters on resume because VP-domain registers require `MIC_DET_CTL1` sync first. IRQ requests use a non-devm `request_threaded_irq()` and must be freed on init errors and remove.

## Test Signals

Test build coverage for the core plus I2C/SoundWire users, codec probe with good/bad device IDs, regulator/reset error unwinds, ASP playback/capture at 44.1 to 96 kHz and common word widths, SCLK/BCLK ratio edge cases, PLL lock timeout warnings, system suspend/resume with jack inserted, plug/unplug/type-detect/button events, and ALSA control read/write for ADC/DAC/filter/slow-start controls.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs42l42.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs42l42.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs42l42.h

## Purpose

`cs42l42.h` is the private shared header for CS42L42 ASoC bus drivers and the common core. It centralizes the per-device state structure and declares the regmap, component driver, DAI driver, register classification helpers, clock/audio helpers, IRQ entry point, PM helpers, and common lifecycle functions.

## Important APIs, Types, and Functions

- `struct cs42l42_private` is the central driver state. It contains the regmap, device, supplies, reset GPIO, power-down completion, ALSA jack pointer, SoundWire peripheral pointer, IRQ lock, device/IRQ identifiers, PLL/SCLK/sample-rate/BCLK state, headset debounce/property state, button thresholds, stream bitmap, and booleans for DAPM delay, suspend, SoundWire attach synchronization, and initialization completion.
- External data symbols include `cs42l42_page_range`, `cs42l42_regmap`, `cs42l42_soc_component`, and `cs42l42_dai`.
- Shared helpers include `cs42l42_pll_config()`, `cs42l42_src_config()`, `cs42l42_mute_stream()`, `cs42l42_irq_thread()`, `cs42l42_suspend()`, `cs42l42_resume()`, `cs42l42_resume_restore()`, `cs42l42_common_probe()`, `cs42l42_init()`, and `cs42l42_common_remove()`.

## Control Flow

The header defines the contract followed by transport front ends. A bus driver allocates and fills `struct cs42l42_private` with at least `dev`, `regmap`, `irq`, `devid`, and any bus pointer, then calls `cs42l42_common_probe()`. Once register access is possible, the bus path calls or triggers `cs42l42_init()`. During audio operation, bus DAIs can reuse `cs42l42_pll_config()`, `cs42l42_src_config()`, and `cs42l42_mute_stream()`. During teardown they call `cs42l42_common_remove()`.

## State and Persistence Behavior

The state is intentionally shared across core and bus modules. Several fields act as persistence across asynchronous contexts: `jack` is used by the IRQ thread after `.set_jack`, `stream_use` prevents clock reconfiguration while active, `plug_state` and `hs_type` hold jack state across IRQs and resume, `suspended` filters IRQ processing during PM, and `sdw_waiting_first_unattach` coordinates SoundWire reset synchronization.

## Dependencies and Integration Points

The header includes DT binding constants, GPIO, mutex, regmap, regulator, SoundWire, ALSA jack, CS42L42 sound definitions, and ASoC component/DAI declarations. It is included by `cs42l42.c` and SoundWire/I2C bus code. The namespace exports in the `.c` file match these declarations.

## Risks

Because this is a shared internal ABI, adding fields or changing meaning affects all bus drivers. Locking expectations are implicit: jack/IRQ/suspend-sensitive fields must be touched under `irq_lock` where the core does so. SoundWire fields are compiled in unconditionally via included SoundWire types, so build coverage must include configurations where SoundWire support is modular or disabled.

## Test Signals

Compile tests for CS42L42 core, I2C, and SoundWire configurations are the main header-level signal. Runtime signals are matching initialization state, no NULL `jack` reports during IRQs, correct stream-use transitions, and successful suspend/resume after both bus front ends use the shared helpers.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs42l42.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs42l43-jack.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs42l43-jack.c

## Purpose

`cs42l43-jack.c` implements CS42L43 accessory detection. It configures DT/firmware-defined jack detection parameters, controls headset bias, performs tip/ring/type/load detection, handles button press/release and bias-clamp interrupts, supports manual jack override controls, and reports ALSA jack states.

## Important APIs, Types, and Functions

- `cs42l43_set_jack()` stores the `snd_soc_jack`, parses properties such as button resistance thresholds, detect time, bias ramp/sense, tip/ring debounce/inversion/pullups, programs detection registers, and enables optional ring sense.
- `cs42l43_start_hs_bias()` and `cs42l43_stop_hs_bias()` control headset bias and clamp settings.
- `cs42l43_button_press()` reads the hardware DC detect result, converts it to resistance, maps it against up to six button thresholds, and reports `SND_JACK_BTN_0` through `BTN_5`.
- `cs42l43_button_release()` clears button reports.
- `cs42l43_bias_sense_timeout()` restores automatic bias clamp behavior after a clamp interrupt.
- `cs42l43_start_load_detect()`, `cs42l43_stop_load_detect()`, and `cs42l43_run_load_detect()` temporarily reconfigure ADC/headphone/load-detect hardware to classify headset, headphone, or line-out loads.
- `cs42l43_run_type_detect()` runs automatic CTIA/OMTP/3-pole/open-circuit detection, then invokes load detection when needed.
- `cs42l43_tip_sense_work()` is the delayed worker that performs insertion/removal processing and ALSA jack reporting.
- `cs42l43_jack_get()` and `cs42l43_jack_put()` implement the "Jack Override" ALSA control.

## Control Flow

Jack setup resumes the device, takes `jack_lock`, parses firmware properties, writes debounce/type-detect/bias registers, and stores the jack pointer. Tip-sense IRQs cancel pending work and queue `tip_sense_work` after configured debounce. The worker resumes the device, takes `jack_lock`, reads debounced tip/ring status, and branches between insertion and removal.

On insertion, SoundWire systems keep a runtime PM reference while the jack is present. Ring-sense absence can report optical. Otherwise the worker starts type detection: it enables bias, starts automatic type detect, waits for the `type_detect` completion, disables the mode, and classifies the result. CTIA/OMTP and some type values run load detection as a microphone-bearing headset; 3-pole runs load detection without mic and maps impedance to headphone or line-out; open circuit reports extension. Headsets start bias and button detection before reporting.

On removal, override state is cleared, button/bias and manual switch state are reset through `cs42l43_clear_jack()`, all jack bits are reported cleared, and the SoundWire jack-present PM reference is dropped.

## State and Persistence Behavior

Persistent jack state lives in `struct cs42l43_codec`: `jack_hp`, `use_ring_sense`, debounce/bias/detect properties, button thresholds, delayed work objects, completions for type/load detection, booleans for load/button/jack presence, `jack_override`, and `suspend_jack_debounce`. Load detection temporarily changes headphone, ADC, bias, clamp, volume ramp, adaptive power, and load-detect registers and then restores cached `adc_ena`/`hp_ena`.

## Dependencies and Integration Points

The file depends on the CS42L43 MFD core/regmap, ASoC component/jack/control APIs, runtime PM, firmware properties, completions supplied by IRQ handlers in `cs42l43.c`, and delayed work queues. Its public functions are declared in `cs42l43.h` and used by the main codec component.

## Risks

This code is highly timing-sensitive. Type and load detection depend on completions arriving before fixed timeouts; false insertions after suspend are mitigated by extra debounce. Button resistance conversion can divide around small hardware values and maps thresholds with a first-less-than rule, so malformed `cirrus,buttons-ohms` can misclassify buttons. Load detection temporarily powers down headphones and changes DAPM-protected hardware while holding the DAPM mutex. Manual override bypasses automatic detection and must restore all switch/bias/clamp state on exit. Runtime PM references on SoundWire jack presence must remain balanced.

## Test Signals

Test property parsing with valid, missing, malformed, and too-many button thresholds; plug/unplug debounce including resume; CTIA, OMTP, headphone, line-out, optical, extension, and removal reports; button press/release thresholds; bias clamp recovery; manual jack override modes; load-detect timeout handling; and SoundWire runtime PM reference balance while a jack is inserted.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs42l43-jack.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs42l43-sdw.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs42l43-sdw.c

## Purpose

`cs42l43-sdw.c` is the small SoundWire stream helper module for the CS42L43 codec component. Unlike CS42L42, CS42L43 appears as an MFD child codec whose parent can be a SoundWire device; this file only connects ASoC DAI stream operations to SoundWire stream add/remove and stream-pointer storage.

## Important APIs, Types, and Functions

- `cs42l43_sdw_add_peripheral()` obtains the `sdw_stream_runtime` from DAI DMA data, converts ALSA params to SoundWire stream and port configs, chooses the SoundWire data port from `dai->id`, and calls `sdw_stream_add_slave()`.
- `cs42l43_sdw_remove_peripheral()` gets the same stream and parent SoundWire slave, then calls `sdw_stream_remove_slave()`.
- `cs42l43_sdw_set_stream()` stores the stream pointer in DAI DMA data for the selected direction.

## Control Flow

The main codec driver wires these helpers into SoundWire DAI ops. A machine driver calls `.set_stream`, `hw_params` calls `cs42l43_sdw_add_peripheral()` and then sample-rate programming in `cs42l43.c`, and `hw_free` calls `cs42l43_sdw_remove_peripheral()`. The parent SoundWire slave is recovered with `dev_to_sdw_dev(priv->dev->parent)`.

## State and Persistence Behavior

This file persists no independent state. It reads `struct cs42l43_codec` from component drvdata and relies on DAI DMA data to hold the `sdw_stream_runtime`. The active stream association is owned by ASoC/SoundWire core state.

## Dependencies and Integration Points

It depends on `CONFIG_SND_SOC_CS42L43_SDW`, the SoundWire core, `sound/sdw.h`, ASoC DAI/component APIs, and `cs42l43.h`. The functions are exported in namespace `SND_SOC_CS42L43` and are compiled as `snd-soc-cs42l43-sdw.o`.

## Risks

The helper assumes the codec device parent is a SoundWire slave. Calling it for a non-SoundWire parent would miscast device state. The data port number is exactly `dai->id`, so DAI table changes in `cs42l43.c` must remain aligned with SoundWire DP numbering. Missing `.set_stream` causes `-EINVAL` at `hw_params`/`hw_free`.

## Test Signals

Exercise each CS42L43 SoundWire DAI DP1 through DP7, verify capture/playback port numbering, confirm no stream leaks after `hw_free`, test missing stream pointer failures, and compile both reachable and non-reachable `CONFIG_SND_SOC_CS42L43_SDW` paths because `cs42l43.h` supplies stubs when this module is absent.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs42l43-sdw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs42l43.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs42l43.c

## Purpose

`cs42l43.c` is the main ASoC codec driver for CS42L43/CS42L43B MFD devices. It registers the component and DAIs, builds the common and variant-specific control/DAPM graph, implements ASP and SoundWire DAI operations, programs sample rates and PLL, handles power-event completions, requests codec IRQs, integrates jack helper functions, and manages runtime/system PM.

## Important APIs, Types, and Functions

- DAI operations: `cs42l43_startup()`, `cs42l43_asp_hw_params()`, `cs42l43_asp_set_fmt()`, `cs42l43_asp_set_tdm_slot()`, `cs42l43_sdw_hw_params()`, and `cs42l43_sdw_ops`.
- DAI table `cs42l43_dais[]` exposes one ASP DAI and SoundWire DP1-DP7 DAIs.
- Control helpers include DAPM-locked getters/setters, EQ coefficient storage, speaker VU sync, shutter-aware decimator/speaker switches, and `cs42l43_spk_put()`.
- PLL path: `cs42l43_set_pll()`, `cs42l43_enable_pll()`, `cs42l43_disable_pll()`, and `cs42l43_pll_ev()`.
- Power event helpers include `cs42l43_dapm_wait_completion()`, speaker/headphone event handlers, ADC/mic event handlers, and EQ startup programming.
- `cs42l43_component_probe()` initializes regmap, default TDM slots, variant-specific controls/widgets/routes, and component state.
- `cs42l43_codec_probe()` allocates `struct cs42l43_codec`, initializes locks/completions/work, maps/request IRQs, obtains optional MCLK, and registers the ASoC component.

## Control Flow

Platform probe gets the parent MFD `struct cs42l43`, finds its IRQ domain, initializes codec private state, enables runtime PM, requests all codec IRQs, configures optional shutter notification IRQs from `SHUTTER_CONTROL`, gets optional `mclk`, and registers the ASoC component with all DAIs. Component probe then initializes the ASoC regmap, resets TDM slot maps, stores the component pointer, and adds CS42L43 or CS42L43B-specific controls/routes.

ASP `hw_params` determines slot count/width from explicit TDM setup or PCM params, balances non-DSP frames to even slots, computes BCLK, programs provider-mode BCLK divisors using GCD against the internal 24.576 MHz sysclk, writes channel width/slot/phase registers, and programs sample rate 1. `set_fmt` configures DSP_A/DSP_B/I2S/left-justified formats, provider/consumer mode, clock inversion, and dynamically adds or removes the DAPM BCLK-from-FSYNC route. SoundWire `hw_params` delegates stream setup to `cs42l43-sdw.c` and then sets sample rate.

DAPM powers the PLL as a supply. PLL enable chooses MCLK or SoundWire refclk, normalizes supported reference frequencies through dividers, waits for `pll_ready`, marks SoundWire PLL active, and switches MCLK source under regmap lock. Headphone and speaker widgets wait for hardware completion IRQs. ADC/mic widgets cache decimator mute/ramp registers before power-up and restore after. EQ power-up writes cached coefficients, waits for initialize done, and unmutes EQ input.

## State and Persistence Behavior

`struct cs42l43_codec` persists device/core pointers, IRQ domain, shutter IRQ mappings, MCLK, TDM slots, EQ coefficients, PLL source/frequency, completions, ADC/HP enable caches, DAPM-related locks, jack state, delayed work, current-limit state, and cached control pointers. Runtime resume only toggles speaker VU sync. System suspend sets jack debounce, disables mapped IRQs, cancels delayed works, clears jack state, and force-suspends runtime PM; resume force-resumes and reenables IRQs.

## Dependencies and Integration Points

The driver depends on the CS42L43 MFD core and register definitions, IRQ domain mappings, regmap, clocks, runtime PM, ASoC component/DAI/DAPM/control APIs, SoundWire helpers via optional `cs42l43-sdw.c`, and jack helpers in `cs42l43-jack.c`. Build integration uses `snd-soc-cs42l43.o` for `cs42l43.o cs42l43-jack.o`.

## Risks

Variant-specific routing is macro-heavy; CS42L43 and CS42L43B differ in decimators, DP channels, mixer values, and controls. DAI ID values must match SoundWire port numbers. PLL changes are refused while active and are protected by the parent `pll_lock`; incorrect ordering can break SoundWire register reads. Completion-based power events can timeout and leave DAPM with partially powered hardware. Shutter controls deliberately drop a mixed volatile/nonvolatile register from cache before read. Current-limit handling temporarily disables headphones and later restores them only if not in load detect.

## Test Signals

Build and boot both CS42L43 and CS42L43B variants. Test ASP formats, provider/consumer clocking, TDM slot masks, all supported sample rates, SoundWire DP streams, PLL MCLK and SoundWire sources, DAPM power-up/down timeouts, EQ coefficient writes, shutter notifications, speaker/headphone current limit, system suspend/resume with pending jack work, and variant-specific mixer route availability.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs42l43.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs42l43.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs42l43.h

## Purpose

`cs42l43.h` is the internal header shared by the CS42L43 codec core, jack helper, and optional SoundWire helper. It defines driver constants, the private codec state object, SoundWire helper declarations or stubs, jack helper declarations, IRQ handler declarations, and the jack override enum symbol.

## Important APIs, Types, and Functions

- Constants define internal sysclk, default TDM slots, timeout values for PLL/speaker/headphone/load detection, headphone current-limit backoff/decay/count, maximum ASP channels, EQ coefficient count, and button count.
- `struct cs42l43_codec` is the per-codec ASoC state. It stores parent MFD/core pointers, component pointer, IRQ domain, shutter IRQs, MCLK, TDM slot maps, EQ coefficients, PLL refclk state, completions, decimator/ADC/HP caches, locks, jack detection settings and work, button thresholds, current-limit state, and cached ALSA controls.
- SoundWire declarations are conditional on `IS_REACHABLE(CONFIG_SND_SOC_CS42L43_SDW)`. Otherwise inline/stub values make non-SoundWire builds fail stream setup cleanly.
- Jack and IRQ declarations connect `cs42l43.c` and `cs42l43-jack.c`.

## Control Flow

The main codec driver owns allocation and initialization of `struct cs42l43_codec`. It passes the state to IRQ handlers and work functions. Jack setup and DAPM/DAI operations mutate fields inside this object to coordinate hardware power, route configuration, stream setup, and delayed detection.

## State and Persistence Behavior

This header defines the state that survives across component probe/remove, runtime PM, IRQs, delayed work, and DAPM events. Notable persistent fields are TDM slot arrays, EQ coefficient cache, PLL source/frequency, completion objects, ADC/HP enable masks used during load detect, jack configuration/override, and current-limit counters.

## Dependencies and Integration Points

It depends on Linux completions, mutexes, workqueues, ALSA PCM types, ASoC component/jack forward declarations, and the MFD `struct cs42l43` forward declaration. The conditional SoundWire stubs are important integration points because `cs42l43.c` can compile whether the helper module is reachable or not.

## Risks

Changes to `struct cs42l43_codec` affect multiple asynchronous users. Locking expectations are embedded in implementation code: `jack_lock` protects jack paths, `spk_vu_lock` protects volume update toggles, and the parent core `pll_lock` protects PLL state. Stubbed SoundWire helpers return `-EINVAL` or NULL; DAI tables must not expose unusable SoundWire behavior in configurations where the helper cannot be loaded unless that failure is intended.

## Test Signals

Header-level tests are mostly compile matrix checks for `CONFIG_SND_SOC_CS42L43` with `CONFIG_SND_SOC_CS42L43_SDW` built-in, modular, and disabled. Runtime signals include correct completion wiring, no workqueue use after component remove, and stable jack/PLL/DAPM state through suspend/resume.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs42l43.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs42l51-i2c.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs42l51-i2c.c

## Purpose

`cs42l51-i2c.c` is the I2C transport wrapper for the CS42L51 ASoC codec core. It binds I2C/OF device IDs, creates an I2C regmap from the shared `cs42l51_regmap`, delegates probe/remove to `cs42l51.c`, and wires system sleep PM to the common suspend/resume helpers.

## Important APIs, Types, and Functions

- `cs42l51_i2c_id[]` matches legacy I2C device name `"cs42l51"`.
- `cs42l51_of_match[]` matches DT compatible `"cirrus,cs42l51"`.
- `cs42l51_i2c_probe()` copies the shared regmap config to a stack local, creates `devm_regmap_init_i2c()`, and calls `cs42l51_probe()`.
- `cs42l51_i2c_remove()` calls `cs42l51_remove()`.
- `cs42l51_pm_ops` maps system sleep to `cs42l51_suspend()` and `cs42l51_resume()`.
- `cs42l51_i2c_driver` is registered through `module_i2c_driver()`.

## Control Flow

I2C probe is thin: create bus regmap, pass `&i2c->dev` plus the regmap to the common codec probe, and return its result. Remove delegates to the common remove path. Suspend/resume are invoked by the driver core and only call the core regcache helpers.

## State and Persistence Behavior

This file owns no persistent codec state. All private state is allocated by `cs42l51_probe()` and stored as device drvdata. The I2C regmap is devm-managed and uses the common register access policy from `cs42l51.c`.

## Dependencies and Integration Points

It depends on Linux I2C, module APIs, ASoC headers, and the shared CS42L51 core exports. It integrates with DT binding `cirrus,cs42l51` and the build target `snd-soc-cs42l51-i2c.o`.

## Risks

Because regmap initialization is directly passed into `cs42l51_probe()`, regmap errors are handled by the common probe through `IS_ERR()`. Any future transport-specific regmap changes must modify the local copy before initialization. PM only covers system sleep, not runtime PM.

## Test Signals

Test I2C device and OF matching, probe deferral/error handling from regmap, successful chip ID validation through the common probe, remove regulator/reset cleanup, and suspend/resume regcache sync over I2C.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs42l51-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs42l51.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs42l51.c

## Purpose

`cs42l51.c` is the shared ASoC codec core for the Cirrus Logic CS42L51. It provides controls, DAPM routes/widgets, DAI setup, MCLK handling, register access policy, common probe/remove, and suspend/resume regcache behavior. The code is transport-neutral and currently used by the I2C wrapper.

## Important APIs, Types, and Functions

- `struct cs42l51_private` persists MCLK frequency/clock handle, audio format, master/slave mode, regulators, reset GPIO, and regmap.
- ALSA controls expose PCM/analog/ADC/PGA volumes, mute switches, deemphasis, automute, ramp/zero-cross controls, mic/ADC boost, bass/treble, and a custom PCM channel mixer.
- DAPM widgets model mic bias, PGAs, ADCs, DACs, analog inputs, mic preamps, headphone outputs, and muxes. Optional MCLK supply widget is added when an MCLK clock exists.
- `cs42l51_set_dai_fmt()` records I2S/left/right-justified format and master/slave-auto mode.
- `cs42l51_set_dai_sysclk()` records MCLK frequency.
- `cs42l51_hw_params()` chooses an MCLK/LRCLK ratio table for master, slave, or slave-auto mode, programs speed mode, MCLK divide, master bit, ADC/DAC serial format, and rejects unsupported ratios or word widths.
- `cs42l51_dai_mute()` toggles DAC A/B mute bits.
- `cs42l51_component_probe()` optionally adds the MCLK DAPM supply and programs default DAC behavior.
- `cs42l51_regmap` defines readable/writeable/volatile registers and maple cache.
- `cs42l51_probe()`, `cs42l51_remove()`, `cs42l51_suspend()`, and `cs42l51_resume()` are exported for bus wrappers.

## Control Flow

Common probe validates the provided regmap, allocates private state, gets optional `"MCLK"`, requests and enables VL/VD/VA/VAHP regulators, gets optional reset GPIO, releases reset, reads `CHIP_REV_ID`, validates revision A or B, logs revision, and registers the ASoC component/DAI. Errors assert reset and disable regulators.

Component probe programs DAC defaults: signal processor path, automute enabled, immediate volume changes, and no deemphasis. PCM `hw_params` then depends on prior machine-driver calls to set format and sysclk. It derives `ratio = mclk / sample_rate`, finds that ratio in the selected mode table, programs interface and mic-power/speed bits, and configures right-justified width-specific DAC format if needed.

DAPM power-down events implement the datasheet sequence by setting global PDN before individual channel power-down, then clearing PDN after. Optional MCLK DAPM supply enables the clock before use and delays 20 ms before disabling it after power-down.

## State and Persistence Behavior

The driver stores software DAI settings (`mclk`, `audio_mode`, `func`) in private state between `set_fmt`/`set_sysclk` and `hw_params`. Regmap cache persists register values across system suspend. Suspend marks the cache dirty and cache-only; resume disables cache-only and syncs. Regulators stay managed by probe/remove rather than suspend/resume in this file.

## Dependencies and Integration Points

The core depends on ASoC component/DAI/DAPM/control APIs, regmap, clk, GPIO, regulator bulk APIs, and the CS42L51 register definitions in `cs42l51.h`. It exports symbols for the I2C bus module. DT integration is via the wrapper and `cirrus,cs42l51`.

## Risks

The file comment says master mode was originally not supported, but the current code has a master-mode ratio table and programming path; hardware validation is important. `mclk` must be set before `hw_params`, or ratio calculation can fail or divide by zero if machine drivers omit sysclk setup. Slave-auto and manual slave ratio tables differ in MCLK divide behavior. `SOC_SINGLE("Zero Cross Switch", ..., max 0)` appears unusual and should be treated carefully if controls are changed. Reset polarity uses `GPIOD_OUT_LOW` and remove sets the GPIO high.

## Test Signals

Test I2C probe with valid revision A/B and invalid IDs, regulator/reset error unwinds, DAI formats I2S/left/right justified, right-justified 16/18/20/24-bit widths, master/slave-auto ratio coverage, missing or invalid MCLK handling, DAPM power sequencing, optional MCLK clock enable/disable, DAC mute, channel mixer modes, and suspend/resume regcache sync.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs42l51.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs42l51.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs42l51.h

## Purpose

`cs42l51.h` is the shared header for the CS42L51 codec core and transport wrappers. It declares the exported regmap and lifecycle/PM helpers and defines the chip ID, revision, register addresses, bit masks, format values, speed modes, status bits, and register-range constants.

## Important APIs, Types, and Functions

- Declarations: `cs42l51_regmap`, `cs42l51_probe()`, `cs42l51_remove()`, `cs42l51_suspend()`, and `cs42l51_resume()`.
- Chip identity macros include `CS42L51_CHIP_ID`, revision A/B constants, `CS42L51_CHIP_REV_MASK`, `CS42L51_CHIP_REV_ID`, and `CS42L51_MK_CHIP_REV()`.
- Register definitions cover power control, mic power/speed modes, serial interface format/master bits, mic/ADC/DAC controls, gain/attenuation/volume, beep/tone/mixer/limiter/ALC/noise, status, and charge frequency.
- `CS42L51_LASTREG` intentionally stops at `0x20` even though `CHARGE_FREQ` is `0x21`, with a comment documenting an SMBus block-read size workaround.

## Control Flow

Transport drivers include this header to create a regmap and call the common probe/remove/PM helpers. The core implementation uses the register/mask constants to implement DAI format, power sequencing, DAPM controls, and chip ID validation.

## State and Persistence Behavior

The header itself stores no state, but its constants define the persistent register contract used by regmap cache and ASoC controls. The `FIRSTREG/LASTREG/NUMREGS` definitions document a cache/register-window boundary that intentionally excludes one register from the legacy bulk range.

## Dependencies and Integration Points

It forward-declares `struct device` and relies on users including appropriate regmap/device headers in implementation files. It is consumed by `cs42l51.c` and `cs42l51-i2c.c`, and forms the local ABI for any future SPI/I2C transport.

## Risks

Bit macros use raw shifts and small constants; changing them changes hardware programming directly. The workaround around `CS42L51_LASTREG` is easy to miss because `cs42l51_regmap.max_register` in the core is `CS42L51_CHARGE_FREQ`. New bulk-cache or defaults work must respect why only 32 registers were historically grouped.

## Test Signals

Compile coverage of the core and I2C wrapper validates declarations. Runtime signals include correct chip revision recognition, register read/write allow-lists matching these constants, DAI format programming, status volatility, and suspend/resume cache sync across the declared register range.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs42l51.h -->
