# subset-b-006443 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max98090.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/max98090.c

Purpose: I2C ASoC codec driver for Maxim MAX98090/MAX98091, covering stereo playback/capture, analog and digital microphone inputs, headphone/speaker/receiver outputs, sidetone/loopback paths, DSP EQ/biquad coefficient controls, TDM, jack detection, PLL unlock recovery, MCLK handling, and runtime/system power transitions.

Important APIs and data: `max98090_reg` defines sparse register defaults for regmap. `max98090_volatile_register()` and `max98090_readable_register()` define reset/status/revision volatility and the readable register ranges. Mixer controls are registered from `max98090_snd_controls`, with MAX98091-only DMIC3/4 controls in `max98091_snd_controls`. DAPM topology is split between base `max98090_dapm_widgets`/`max98090_dapm_routes` and MAX98091 extensions. The DAI surface is `max98090_dai_ops`: `startup`, `set_sysclk`, `set_fmt`, `set_tdm_slot`, `hw_params`, `mute_stream`, and `trigger`. Public integration is exported through `max98090_mic_detect()`.

Control flow: I2C probe allocates `struct max98090_priv`, selects the device type from match data, reads `maxim,dmic-freq`, builds the I2C regmap, requests the threaded IRQ, and registers the ASoC component and one `HiFi` DAI. Component probe obtains optional `mclk`, resets the codec, initializes clock/DAI/TDM/jack state, reads the revision to distinguish MAX98090 vs MAX98091, initializes delayed work, enables jack detection, sets high-performance defaults and micbias from `maxim,micbias`, then adds controls/routes. DAI setup stores format state, configures master/consumer mode, I2S/left/right/DSP_A formats, inversion, and TDM slots. `hw_params` derives BCLK/LRCLK, accepts only 16-bit runtime programming after startup constraints, adjusts filter/sample-rate modes, and programs DMIC clock compensation. Trigger handling enables or disables deferred PLL-unlock interrupt detection only in consumer mode.

State and persistence: `struct max98090_priv` persists sysclk/pclk/bclk/lrclk, selected DAI format, TDM slots, last mic boost/sidetone values, jack state, work items, and master/SHDN flags. Regmap uses `REGCACHE_RBTREE`; runtime suspend switches to cache-only and runtime resume resets then syncs. System resume marks the cache dirty, resets, clears IRQ status, and syncs. Bias transitions enable/disable `mclk` around `SND_SOC_BIAS_PREPARE`, sync regcache when leaving OFF, and mark cache dirty in OFF. Shutdown writes volume smoothing and then powers the device down.

Dependencies and integration points: depends on I2C, regmap, clocks, ASoC controls/DAPM/DAI, threaded IRQs, delayed work, PM, `sound/max98090.h` platform data, and the local register header. Board integration supplies compatible strings, optional `mclk`, IRQ, `maxim,dmic-freq`, and `maxim,micbias`; machine drivers call `set_sysclk`, `set_fmt`, optional TDM setup, and `max98090_mic_detect()`.

Risks: IRQ request is unconditional against `i2c->irq`, so boards without a valid IRQ can fail probe. DAI startup suppresses 24-bit support unless right-justified, while `hw_params` rejects non-16-bit widths, so advertised `S24_LE` is fragile. PLL unlock recovery toggles SHDN while active, which can create audible artifacts. TDM validation only limits slot count and width, then uses first/last set bits; sparse masks may not match machine-driver intent. Jack detection uses delayed work and pull-up changes, so suspend/remove ordering and stale jack pointers are important. `max98090_configure_dmic()` return is ignored in `hw_params`.

Test signals: successful probe should log MAX98090/MAX98091 revision, expose expected controls/routes, and register the `HiFi` DAI. Exercise 8-96 kHz playback/capture, master and consumer clocking, I2S/left/right/DSP_A format setup, TDM slots, DMIC clocks from `maxim,dmic-freq`, headphone/headset/button reporting through IRQ, runtime suspend/resume with audio restart, and shutdown mute ramp behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max98090.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max98090.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/max98090.h

Purpose: local register and private-state header for the MAX98090/MAX98091 ASoC driver. It maps codec register addresses, bit masks, shifts, field widths, revision IDs, coefficient block sizes, jack-state constants, the driver-private structures, and the exported mic-detect prototype used by machine drivers.

Important APIs and types: `MAX98090_DEFAULT_DMIC_FREQ` supplies the fallback digital-mic clock target. `M98090_REG_*` constants cover status/interrupt, quick setup, inputs, ADC/DAC paths, clocking, interface/TDM, mixers, output controls, DRC, jack detection, DSP filter coefficients, DMIC3/4, sample-rate, and revision registers. Bitfield macros define masks/shifts for clock divisors, DAI format, TDM slots, routing mixers, volume fields, EQ/biquad enables, jack status/interrupt bits, and MAX98091 DMIC34 fields. `enum max98090_type`, `struct max98090_cdata`, and `struct max98090_priv` describe device variant, DAI runtime data, and all persistent driver state. `max98090_mic_detect()` is declared for external ASoC card integration.

Control flow relevance: the `.c` file uses these macros in every regmap update, DAPM route, ALSA control, DAI callback, IRQ handler, and PM transition. Revision constants `M98090_REVA` and `M98091_REVA` drive runtime variant detection. TDM and DMIC macros configure DAI format registers and MAX98091-only capture paths. Jack constants are used by the delayed jack state machine.

State and persistence: the header defines the shape of state persisted across callbacks: regmap/component handles, platform data, optional `mclk`, clock rates, DMIC target frequency, one DAI cache, delayed work, `snd_soc_jack`, DAI/TDM settings, cached analog gain selections, `master`, and `shdn_pending`. These fields are restored through regcache sync and reinitialized only at component probe.

Dependencies and integration points: depends conceptually on Linux regmap, ASoC component/jack, clock, workqueue, and platform-data types included by the C file. It also bridges to public platform definitions from `sound/max98090.h`. Consumers should include this header only inside the codec driver; external users use the exported mic-detect symbol.

Risks: the header contains a very large hand-maintained register map, so off-by-one masks and duplicate/incorrect widths can silently corrupt hardware programming. One suspicious macro, `M98090_DMIC34_ZEROPAD_NUM`, derives from `M98090_DIGMIC4_WIDTH` rather than its own width. Private-state layout couples PM, IRQ, DAI, and DAPM behavior tightly, which increases regression risk when adding fields or variant support.

Test signals: compile coverage catches missing macros, but hardware validation is needed for every register field family: DAI clocking, TDM, mixer routes, EQ/biquad byte controls, jack detection bits, and MAX98091 DMIC3/4 controls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max98090.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max98095.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/max98095.c

Purpose: I2C ASoC driver for MAX98095, a multi-DAI audio codec with stereo HiFi playback/capture, mono Aux and Voice playback DAIs, analog microphone/line inputs, headphone/speaker/receiver/line outputs, platform-data-driven EQ and biquad coefficient loading, jack detection, and bias-level clock/power management.

Important APIs and data: private state `struct max98095_priv` stores regmap, platform data, optional MCLK, sysclk, three DAI runtime records, dynamically built EQ/BQ enum text arrays, line/mic cached state, jack pointers, and a mutex protecting segmented coefficient writes. `max98095_reg_def` and regmap callbacks define the cache surface and volatile host/status areas. `m98095_eq_band()` and `m98095_biquad_band()` write coefficient words into DAI1/DAI2 coefficient windows. `max98095_snd_controls`, `max98095_dapm_widgets`, and `max98095_audio_map` expose controls and power graph. Public jack integration is `max98095_jack_detect()`.

Control flow: I2C probe allocates state, initializes the mutex and regmap, stores platform data, and registers the component with three DAIs. Component probe gets optional `mclk`, performs a software-style reset sequence, initializes all three DAI state records, requests the IRQ if present, reads revision ID, writes default routing and power registers, applies platform data for digital mic mode and EQ/BQ controls, then takes the codec out of shutdown. Each DAI has separate `set_fmt` and `hw_params` functions but shares `set_sysclk`; format callbacks support consumer/provider clocking, I2S/left-justified, and clock inversion. `hw_params` maps width and sample rate, writes sample-rate mode, and computes NI for provider mode using `sysclk`.

State and persistence: regmap uses `REGCACHE_RBTREE`; readable/writeable/volatile callbacks separate cached control registers from host/status and revision registers. Bias-level transitions enable/disable `mclk`, sync cache when leaving OFF, and toggle mic-bias enables. EQ and BQ selections are cached per DAI and reloaded from platform data by closest sample rate. Suspend disables jack detection and forces bias OFF; resume forces STANDBY and re-enables/report jacks.

Dependencies and integration points: depends on I2C, regmap, ASoC, platform data from `sound/max98095.h`, optional clock, IRQ, and jack APIs. Board files or machine drivers provide EQ/BQ coefficient arrays, digital mic flags, jack detect pin/delay options, DAI format/sysclk configuration, and jack objects. The driver exports `max98095_jack_detect()` for card code.

Risks: platform-data EQ/BQ text arrays are allocated with `krealloc()` and are not freed in remove. If an EQ/BQ control is used before the DAI rate has been set, closest-rate selection sees `(unsigned)-1` as `fs`. DAI2 and DAI3 share mono playback paths, and DAPM mixer controls for mono DAC2/DAC3 reuse the same register bit in some speaker mixers. `max98095_jack_detect_enable()` dereferences `max98095->pdata`, so calling jack detection without platform data can crash. IRQ is requested with raw `request_threaded_irq()` in component probe and freed manually, unlike devm resources.

Test signals: verify revision read, DAI1 duplex and DAI2/DAI3 mono playback at 8-96 kHz, 16/24-bit operation, provider-mode NI programming with valid sysclk, optional MCLK bias transitions, EQ/BQ mode controls with multiple platform coefficient rates, line input shared-PGA state, jack insertion/removal with separate and shared jack objects, suspend/resume jack re-report, and remove-time IRQ cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max98095.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max98095.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/max98095.h

Purpose: local register definition header for the MAX98095 codec driver. It enumerates host/status, DAI, mixer, level, ALC, jack, power, revision, EQ, and biquad registers plus the bit masks needed by `max98095.c`.

Important APIs and data: `M98095_000_HOST_DATA` through `M98095_0FF_REV_ID` name the register map, with `M98095_REG_MAX_CACHED` marking the cached range. Bitfield macros cover jack auto status and interrupt enable, host segmented access (`M98095_SEG`), DAI format/master/clock bits, DAC mixer routes, mic preamp masks, output mute bits, digital mic mode, EQ/BQ enables, jack detection options, power enables, shutdown/run, coefficient byte extraction, and coefficient base windows. `M98095_COEFS_PER_BAND`, `M98095_BYTE1()`, and `M98095_BYTE0()` support coefficient writes. The header declares exported `max98095_jack_detect()`.

Control flow relevance: the C file uses this header for regmap access policy, default reset rewriting, sample-rate and DAI format programming, DAPM power bits, jack status reporting, platform-data EQ/BQ loading, and bias-level power management. Coefficient base registers intentionally overlap the normal 8-bit register address space after setting the `SEG` host bit.

State and persistence: no state is stored here directly, but constants define which register values can be cached and restored by regmap. Fields such as `M98095_SHDNRUN`, `M98095_MBEN`, EQ/BQ enables, DAI clock mode, and jack detection bits persist across regcache sync and are manipulated in suspend/resume and bias transitions.

Dependencies and integration points: ties local driver logic to `sound/max98095.h` platform data and ASoC machine-driver calls. The external jack-detect prototype is the header-level contract for board code that wants codec IRQ-based headphone/mic reporting.

Risks: because the header is a dense hand-written hardware map, incorrect bit definitions directly affect audio routing or power. `M98095_045_DSP_CFG` in the comment does not match the C file's use of `M98095_045_CFG_DSP`, which is harmless for compilation but a documentation trap. Coefficient-window macros use low byte addresses under segmented access, so misuse without `M98095_SEG` would write ordinary control registers.

Test signals: compile coverage plus hardware checks for DAI format bits, jack status masks, EQ/BQ segmented coefficient programming, power enable masks, and digital mic configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max98095.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max98357a.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/max98357a.c

Purpose: minimal platform ASoC codec driver for MAX98357A/MAX98360A I2S class-D amplifiers. The hardware has no register bus; the driver exposes a playback-only DAI and optionally controls an `sdmode` GPIO for shutdown/mute sequencing.

Important APIs and data: `struct max98357a_priv` stores optional `sdmode` GPIO, `sdmode-delay`, and whether DAPM has enabled SD_MODE. `max98357a_daiops_trigger()` toggles the GPIO on PCM start/stop family commands. `max98357a_sdmode_event()` records DAPM SD_MODE state. DAPM contains an output `Speaker` and an output driver `SD_MODE`. The single DAI `HiFi` supports 1-2 channel playback, 8-96 kHz, and 16/24/32-bit formats.

Control flow: platform probe allocates state, gets optional `sdmode` GPIO initialized low, reads optional `sdmode-delay`, stores driver data, and registers the component/DAI. During a playback route power-up, DAPM marks `sdmode_switch`; the next trigger start waits the configured delay and drives GPIO high. Stop/suspend/pause-push drives GPIO low. If no GPIO is provided, trigger handling is a no-op.

State and persistence: there is no regmap or hardware cache. Persistent state is only the GPIO descriptor, delay, and DAPM-derived switch flag. Device-managed allocation and GPIO ownership clean up automatically on remove.

Dependencies and integration points: depends on platform bus, OF/ACPI match tables, optional GPIO consumer property named `sdmode`, optional device property `sdmode-delay`, and ASoC DAPM/DAI registration. Compatible strings include `maxim,max98357a` and `maxim,max98360a`; ACPI IDs are `MX98357A` and `MX98360A`.

Risks: `mdelay()` is busy-waiting in trigger context, so large `sdmode-delay` values can be harmful. DAPM and trigger ordering controls whether start drives GPIO high; if a machine route never powers `SD_MODE`, `sdmode_switch` remains false. The driver cannot validate actual amplifier state because there is no readback.

Test signals: probe with and without `sdmode`, playback trigger GPIO transitions, route power sequencing from `HiFi Playback` to `Speaker`, all advertised sample rates/formats, and suspend/stop ensuring GPIO low.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max98357a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max98363.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/max98363.c

Purpose: SoundWire ASoC amplifier driver for MAX98363. It registers a mono playback DAI, exposes volume/tone/monitor controls, configures SoundWire properties and stream ports, and manages regmap cache through runtime PM and SoundWire attach status.

Important APIs and data: `max98363_reg` supplies defaults for monitor, tone, volume, gain, and DSP config registers. Regmap uses 32-bit register addresses, 8-bit values, single read/write, and RBTREE cache. `max98363_read_prop()` advertises one sink port, paging support, clock-stop capabilities, and data-port properties. DAI operations are `max98363_sdw_dai_hw_params()`, `max98363_pcm_hw_free()`, and `max98363_set_sdw_stream()`. `max98363_update_status()` initializes hardware once the SoundWire slave attaches.

Control flow: SoundWire probe creates the regmap and calls `max98363_init()`, which allocates private state, puts the regmap into cache-only mode, registers the component and DAI, and enables autosuspend without marking the device active. When the bus reports `SDW_SLAVE_ATTACHED`, `max98363_io_init()` disables cache-only mode, optionally bypasses cache during first hardware init, marks runtime PM active on first attach, reads revision ID, sets `first_hw_init` and `hw_init`, and releases autosuspend. PCM `hw_params` obtains the SoundWire stream from DAI DMA data, rejects capture, builds stream and port configs for RX port 1, and calls `sdw_stream_add_slave()`. `hw_free` removes the slave from the stream.

State and persistence: `struct max98363_priv` stores regmap, `sdw_slave`, `hw_init`, and `first_hw_init`. Runtime suspend switches regmap to cache-only and marks it dirty. Resume waits for SoundWire initialization if an unattach request is pending, clears `unattach_request`, disables cache-only mode, and syncs. `SDW_SLAVE_UNATTACHED` clears `hw_init`, forcing reinitialization on the next attach.

Dependencies and integration points: depends on SoundWire core, SoundWire register/type helpers, runtime PM, regmap SoundWire transport, and ASoC. Match table uses SoundWire manufacturer/device IDs `0x019F/0x8363`. Controls include digital/speaker volume, tone generator, ramp, clock monitor, speaker monitor threshold/duration. DAPM routes `HiFi Playback` through `AIFIN` to `BE_OUT`.

Risks: `stream_config.ch_count` is hardcoded to 1 instead of using requested channels, which matches the mono DAI but makes stereo requests impossible. Resume can return `-ETIMEDOUT` if SoundWire initialization does not complete within 5 seconds. The readable-register macro references `MAX98363_R2005_INTR_FALG`, likely a typo preserved in the ABI of this header. There is no remove callback disabling runtime PM, relying on devm/SoundWire cleanup.

Test signals: SoundWire enumeration and revision log, attach/detach transitions, runtime suspend/resume after clock-stop, mono playback stream add/remove, 16/24-bit rates from 8-192 kHz, ALSA controls for volume/tone/monitor bits, and timeout behavior when a slave fails to reattach.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max98363.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max98363.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/max98363.h

Purpose: local register and private-state header for the MAX98363 SoundWire amplifier driver.

Important APIs and data: register macros cover software reset, interrupt raw/state/flag/enable/clear, error monitor control, speaker monitor threshold/duration, tone generator config/enable, amplifier volume/gain, DSP config, and revision ID. Bit shifts define speaker monitor, clock monitor, and ramp fields. `struct max98363_priv` stores the regmap, SoundWire slave pointer, and hardware initialization flags.

Control flow relevance: the C file uses the register constants for regmap defaults, access policy, ALSA controls, revision readback, and runtime PM cache sync. The private flags control whether attach status should perform I/O initialization and whether resume must wait for SoundWire reinitialization.

State and persistence: `hw_init` is cleared on SoundWire unattach and set after successful revision read. `first_hw_init` distinguishes first enumeration from subsequent cache syncs. These flags protect ASoC/runtime PM from accessing a not-yet-enumerated slave.

Dependencies and integration points: intended only for `max98363.c`; types come from regmap and SoundWire headers included in the C file. The register map aligns with SoundWire 32-bit addressing.

Risks: `MAX98363_R2005_INTR_FALG` appears misspelled and should be treated carefully because both header and C file use the same token. The header exposes minimal state, so adding controls needing more persistent configuration requires extending this struct and reviewing PM paths.

Test signals: compile use of all register tokens, revision read at `MAX98363_R21FF_REV_ID`, ALSA controls writing monitor/tone/ramp fields, and attach/resume paths toggling `hw_init` and `first_hw_init` as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max98363.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max98371.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/max98371.c

Purpose: I2C ASoC driver for the MAX98371 stereo class-D amplifier. It exposes playback-only DAI configuration, speaker and digital volume controls, dynamic headroom tracking controls, monomix and HPF enums, DAPM speaker enable routing, and regmap-backed revision probing.

Important APIs and data: `max98371_reg` holds register defaults. `max98371_volatile_register()` marks IRQ clear and version registers volatile; `max98371_readable_register()` blocks soft reset reads. ALSA controls include speaker gain, digital gain, DHT max/min/rotation gain, DHT attack step/rate, monomix select, and HPF cutoff. DAI ops are `max98371_dai_set_fmt()` and `max98371_dai_hw_params()`.

Control flow: I2C probe allocates `struct max98371_priv`, initializes regmap, reads `MAX98371_VERSION`, logs it, and registers the component and `max98371-aif1` DAI. `set_fmt` only accepts codec consumer clocking and supports I2S, right-justified, and left-justified modes. `hw_params` maps sample format to channel size, programs BCLK/LRCLK ratio for 32/48/64 only, maps sample rate for 32/44.1/48/88.2/96 kHz, enables both RX channels in monomix source, and enables both DAI channels.

State and persistence: state is only the regmap pointer. Register state persists via `REGCACHE_RBTREE`; there are no explicit suspend/resume callbacks. DAPM powers the `DAC`, `Global Enable`, and `SPK_OUT` route using `MAX98371_SPK_ENABLE` and `MAX98371_GLOBAL_ENABLE`.

Dependencies and integration points: depends on I2C, regmap, ASoC, and local register macros. Device tree compatible is `maxim,max98371`; I2C ID is `max98371`. Machine drivers must provide a consumer-clock DAI format and compatible PCM params.

Risks: advertised `MAX98371_RATES` is 8-48 kHz, but `hw_params` accepts 88.2/96 kHz and rejects 8/16/22.05/24 kHz; advertised formats are big-endian bits, while `hw_params` checks little-endian formats, creating a likely format negotiation mismatch. Only BCLK ratios 32/48/64 work. No explicit PM means boards rely on DAPM/regcache defaults and external power handling.

Test signals: probe revision read, playback at actually supported rates and BCLK ratios, validation of endian format negotiation, DAPM enabling `SPK_OUT`, monomix channel selection, HPF/DHT controls, and error paths for unsupported rates/formats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max98371.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max98371.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/max98371.h

Purpose: local register-map header for the MAX98371 amplifier driver.

Important APIs and data: register macros cover IRQ clear registers, DAI clock/BSEL, speaker sample rate, DAI channel enable, monomix source/config, HPF, digital gain, speaker gain, format/mode/channel-size fields, DHT controls, speaker/global enable, soft reset, and version. Constants define supported BSEL values, sample-rate encodings, monomix RX source, channel-size fields, and output enables. `struct max98371_priv` stores only the regmap pointer.

Control flow relevance: `max98371.c` uses these constants in regmap defaults, readable/volatile callbacks, ALSA controls, DAI format/clock/rate setup, DAPM power widgets, and revision probing.

State and persistence: this header defines the fields cached by regmap and the lone private pointer needed for register access. No PM fields or runtime flags exist, so all persistent behavior is register-cache based.

Dependencies and integration points: private to the MAX98371 I2C driver and ASoC component registration. Machine-driver-visible behavior is indirect through DAI names and supported register programming in the C file.

Risks: format macros use shifted values that must match `MAX98371_FMT_MASK` and `MAX98371_FMT_MODE_MASK`; incorrect shifts would break all playback format setup. The header lists 88.2/96 kHz sample-rate encodings even though the DAI advertises only up to 48 kHz, reflecting the mismatch seen in the C file.

Test signals: compile use of macros, regmap access to `MAX98371_VERSION`, DAI format writes to `MAX98371_FMT`, rate writes to `MAX98371_SPK_SR`, and DAPM writes to speaker/global enable bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max98371.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max98373-i2c.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/max98373-i2c.c

Purpose: I2C transport ASoC driver for MAX98373 smart amplifier. It provides PCM/TDM DAI setup, I2C regmap defaults and access policy, sleep PM cache handling, revision probing, interleave-mode handling, feedback readback caching, and component registration through common MAX98373 support.

Important APIs and data: `max98373_reg` defines a large 16-bit register map for interrupts, PCM/ICC/SoundWire control, amplifier path/gain/DSP, IV sense, measurement ADCs, BDE, DHT, limiter, auto-restart, global shutdown, and revision. `max98373_i2c_cache_reg` lists volatile feedback/readback registers cached before suspend. DAI ops are `max98373_dai_set_fmt()`, `max98373_dai_hw_params()`, and `max98373_dai_tdm_slot()`. Regmap callbacks list readable and volatile register ranges. The component driver itself is supplied by common `soc_codec_dev_max98373` from the shared MAX98373 code.

Control flow: probe allocates `struct max98373_priv`, reads `maxim,interleave_mode`, initializes 16-bit I2C regmap, allocates feedback cache entries, calls `max98373_slot_config()` for voltage/current slots and GPIO configuration, reads revision ID, then registers the component and one DAI. `set_fmt` supports normal and inverted BCLK, and I2S/left-justified/DSP_A/DSP_B data formats. `hw_params` maps 16/24/32-bit widths, maps sample rates 8-96 kHz, writes both PCM sample-rate registers, adjusts IV ADC sample rate for interleave mode, and sets BCLK ratio when not in TDM mode. `set_tdm_slot` toggles TDM mode, validates BCLK ratio and slot width, selects up to two RX slots for speaker mono mix, and writes TX Hi-Z masks.

State and persistence: private state includes regmap, optional reset GPIO/common fields, voltage/current/spk feedback slots, interleave mode, channel size, TDM mode, feedback cache, SoundWire fields shared with common code, and masks. Suspend reads selected volatile feedback registers into `max98373->cache`, switches regmap cache-only, and marks it dirty. Resume disables cache-only, calls `max98373_reset()`, and syncs the cache.

Dependencies and integration points: depends on I2C, ACPI/OF matching, regmap, ASoC, PM, local `max98373.h`, and common MAX98373 functions/controls not in this file. Device properties include `maxim,interleave_mode` and whatever `max98373_slot_config()` consumes for feedback slots/GPIO. Compatible is `maxim,max98373`; ACPI ID is `MX98373`.

Risks: `set_tdm_slot()` treats an all-zero request as disabling TDM but still computes `slots * slot_width` and will return `-EINVAL`, so the common ASoC "clear TDM" call may fail. TDM RX slot parsing silently uses only the first two set bits. Non-TDM BCLK ratio depends on `max98373->ch_size` from `hw_params`; ordering is fine in normal PCM setup but fragile if reused elsewhere. Suspend caches volatile readbacks but this file does not restore those `cache[i].val` values directly, so correctness depends on common code/control read paths. Reset and slot configuration behavior is delegated to shared code and must remain compatible with I2C regcache.

Test signals: I2C revision read, DAI format programming for I2S/LJ/DSP_A/DSP_B, BCLK ratios from 32 to 512/320, rates 8-96 kHz, 16/24/32-bit formats, interleave-mode IV ADC rate adjustment, TDM slot masks including one and two RX slots, TX Hi-Z masks, suspend/resume with regcache sync and reset, and component controls provided by common MAX98373 code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max98373-i2c.c -->
