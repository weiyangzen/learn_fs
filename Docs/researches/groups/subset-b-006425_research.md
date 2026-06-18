# subset-b-006425 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cpcap.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cpcap.c

## Purpose
This file is the ALSA SoC codec driver for the Motorola CPCAP PMIC audio block. It exposes two DAIs, `cpcap-hifi` for stereo playback and `cpcap-voice` for mono voice playback plus mono/stereo capture, and maps the PMIC register-level audio routing into ASoC controls, DAPM widgets, DAPM routes, jack detection, and headset button reporting.

## Important APIs, types, and functions
The central private type is `struct cpcap_audio`, which holds the component, parent MFD regmap, vendor ID, cached voice codec clock/format settings, the `VAUDIO` regulator, headset and mic-bias IRQ numbers, and the `snd_soc_jack` object. `struct cpcap_reg_info` plus `cpcap_default_regs[]` define the reset/default register programming applied at probe.

Important control helpers are `cpcap_output_mux_get_enum()`, `cpcap_output_mux_put_enum()`, `cpcap_input_right_mux_get_enum()`, `cpcap_input_right_mux_put_enum()`, `cpcap_input_left_mux_get_enum()`, and `cpcap_input_left_mux_put_enum()`. They implement non-linear mux layouts that cannot be described by simple `SOC_ENUM` controls. Clock and stream setup are handled by `cpcap_set_sysclk()`, `cpcap_set_samprate()`, `cpcap_hifi_hw_params()`, `cpcap_hifi_set_dai_fmt()`, `cpcap_voice_hw_params()`, `cpcap_voice_set_dai_fmt()`, and `cpcap_voice_set_tdm_slot()`. `cpcap_voice_call()` programs modem-to-codec routing for a special voice-call mode inferred from TDM slot arguments. Probe/remove and power hooks are `cpcap_soc_probe()`, `cpcap_soc_remove()`, `cpcap_codec_probe()`, and `cpcap_set_bias_level()`. Headset state is handled by `cpcap_hs_irq_thread()` and `cpcap_mb2_irq_thread()`.

## Control flow
The platform probe locates the parent device-tree `audio-codec` child and registers the component with two DAI drivers. Component probe allocates `struct cpcap_audio`, gets the `VAUDIO` regulator, creates an ALSA jack with headset and button capability, initializes the component regmap from the parent CPCAP MFD regmap, reads the CPCAP vendor, requests threaded `hs` and `mb2` IRQs, resets audio registers through `cpcap_audio_reset()`, performs an initial headset-detection pass, and enables wake on both IRQs.

Audio reset writes the default register table, selects the default DAI mux mapping, sets HiFi and Voice clocks to 26 MHz, and programs both sample-rate generators to 48 kHz. HiFi `hw_params` only updates sample rate. HiFi format setup enforces codec bit/frame provider mode and accepts I2S specially, falling back to 4-slot network mode for other formats. Voice `hw_params` updates sample rate and capture time slots for mono/stereo capture. Voice format setup similarly configures provider mode, clock/frame inversion, and I2S versus network mode. Voice TDM setup writes TX/RX slot masks, derives a sample rate from `slot_width * 1000`, and toggles the modem voice-call register route if the slot pattern matches the driver heuristic.

DAPM controls power the VAUDIO supply, DAI clocks, microphone bias, ADCs, DACs, PGAs, output amplifiers, headset charge pump, loopback, mono mixers, and playback/capture muxes. Output mux changes update three separate register banks, ensuring only one source among Off/Voice/HiFi/Ext is enabled for each physical output.

## State and persistence behavior
Runtime state is in CPCAP hardware registers, the parent MFD regmap cache, `struct cpcap_audio`, regulator mode, and the ALSA jack status. The driver does not persist settings across reboots. It does preserve selected voice clock ID, voice clock frequency, and voice format in memory, but those cached fields are not a durable store. Bias-level transitions switch `VAUDIO` between normal and standby unless a microphone is present, because mic/PTT detection needs `VAUDIO` in normal mode. IRQ wake enables headset and mic-bias events to wake the system.

## Dependencies and integration points
This file depends on the CPCAP MFD interface from `<linux/mfd/motorola-cpcap.h>`, the parent regmap, CPCAP vendor detection via `cpcap_get_vendor()`, Linux regulators, threaded IRQs, input key reporting, ALSA jack support, and ASoC component/DAI/DAPM APIs. It integrates with machine drivers through the DAI names `cpcap-hifi` and `cpcap-voice`, the component name `cpcap-codec`, device-tree child node `audio-codec`, and platform IRQ names `hs` and `mb2`.

## Risks and test signals
Key risks are the custom mux setters touching multiple registers, voice-call detection based on a primitive TDM-slot heuristic, sample-rate reset self-clear failures, ST-vendor-specific DAC workaround sequencing, and headset/PTT detection races while bias and charge pump settle. The HiFi DAI format mask includes `SNDRV_PCM_FORMAT_S24_LE` rather than the usual `SNDRV_PCM_FMTBIT_S24_LE`, which is worth checking in build or runtime validation because `.formats` expects a bitmask. The voice format function logs unsupported provider/inversion cases but does not always return `-EINVAL`, which could leave partially accepted bad formats.

Useful test signals are successful component registration from a CPCAP MFD parent, `VAUDIO` regulator mode transitions during playback/capture/jack states, working 8 kHz through 48 kHz HiFi and Voice streams, correct output source selection for every physical route, voice capture in one- and two-channel modes, modem-call TDM mode toggling the expected register bits, headset/headphone/mic/button reports from IRQs, wake from headset IRQs, and no register update errors when the ST workaround runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cpcap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cq93vc.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cq93vc.c

## Purpose
This file is a compact ALSA SoC codec driver for the Texas Instruments CQ0093 voice codec used on DaVinci platforms. It binds to a platform device named `cq93vc-codec`, attaches to a regmap supplied by the DaVinci voice codec MFD/platform data, and exposes simple playback/capture controls and one DAI.

## Important APIs, types, and functions
The exported driver surface is the platform driver `cq93vc_codec_driver` and one ASoC DAI named `cq93vc-hifi`. Mixer controls are `PGA Capture Volume` and `Mono DAC Playback Volume`. `cq93vc_mute()` toggles `DAVINCI_VC_REG09_MUTE`, `cq93vc_set_dai_sysclk()` accepts only the supported master-clock frequencies 22.5792 MHz, 27 MHz, and 33.8688 MHz, and `cq93vc_set_bias_level()` writes `DAVINCI_VC_REG12_POWER_ALL_ON` or `DAVINCI_VC_REG12_POWER_ALL_OFF` according to ASoC bias state. `cq93vc_probe()` initializes the component regmap from `struct davinci_vc`.

## Control flow
Platform probe registers the component and DAI. Component probe expects `component->dev->platform_data` to point to a valid `struct davinci_vc` containing a regmap; it then calls `snd_soc_component_init_regmap()`. Stream setup is intentionally minimal: the DAI constrains playback and capture to 8 kHz or 16 kHz, unsigned 8-bit or signed 16-bit little-endian samples, and one or two channels. Mute and bias callbacks directly update codec power and DAC mute registers through the component regmap.

## State and persistence behavior
The driver stores no private runtime object. Its state is the hardware register state behind the DaVinci voice codec regmap and ASoC bias state. There is no suspend/resume implementation, no regcache management here, and no durable persistence.

## Dependencies and integration points
The file depends on `<linux/mfd/davinci_voicecodec.h>` for register definitions and `struct davinci_vc`, platform-device binding, and ASoC component/DAI registration. It is integrated into the codec Makefile as `snd-soc-cq93vc.o` under `CONFIG_SND_SOC_CQ0093VC`. Machine drivers integrate through the DAI name `cq93vc-hifi`.

## Risks and test signals
The largest risk is the implicit platform-data contract: `cq93vc_probe()` dereferences `component->dev->platform_data` without a null check. Wrong or missing MFD setup will fail badly rather than gracefully. The sysclk callback validates frequency but does not program a local clock source, so clock correctness depends on the platform. Test signals are successful platform probe with a valid DaVinci voice-codec regmap, register writes on bias transitions, DAC mute/unmute behavior, mixer get/put round trips, and playback/capture operation at both supported rates and formats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cq93vc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cros_ec_codec.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cros_ec_codec.c

## Purpose
This file is the ChromeOS Embedded Controller audio codec driver. It does not program a local hardware codec directly; instead it uses ChromeOS EC host commands to control EC audio functions: digital microphone gain, an EC I2S RX capture path, wake-on-voice enablement, hotword model loading, and a software PCM stream fed from EC audio data.

## Important APIs, types, and functions
The central type is `struct cros_ec_codec_priv`, shared by both registered ASoC components. It stores the EC device, capability bits, EC and AP shared-memory windows, DMIC probe state, I2S bit-clock ratio, wake-on-voice state, mapped WoV shared-memory pointers, an in-kernel circular audio queue, PCM DMA offset, a delayed work item, and a ChromeOS EC notifier.

All EC communication funnels through `send_ec_host_command()`. DMIC controls use `dmic_get_gain()`, `dmic_put_gain()`, and `dmic_probe()`. I2S capture setup uses `i2s_rx_hw_params()`, `i2s_rx_set_bclk_ratio()`, `i2s_rx_set_fmt()`, and the DAPM event `i2s_rx_event()`. Wake-on-voice support is implemented by `wov_map_shm()`, `wov_read_audio_shm()`, `wov_read_audio()`, `wov_copy_work()`, `wov_enable_get()`, `wov_enable_put()`, `wov_hotword_model_put()`, `wov_host_event()`, `wov_probe()`, `wov_remove()`, and PCM callbacks `wov_pcm_open()`, `wov_pcm_hw_params()`, `wov_pcm_hw_free()`, `wov_pcm_pointer()`, and `wov_pcm_new()`.

## Control flow
Platform probe allocates `cros_ec_codec_priv`, discovers optional EC and AP shared-memory ranges from device tree, sends `EC_CODEC_GET_CAPABILITIES`, resets EC I2S RX using `EC_CODEC_I2S_RX_RESET`, and registers two ASoC components. The I2S RX component provides the `EC Codec I2S RX` DAI and DAPM path from `DMIC` to `I2S RX`; its probe also adds EC mic gain controls if the EC supports max-gain querying. The WoV component provides the `Wake on Voice` capture DAI, the `Wake-on-Voice Switch`, and the `Hotword Model` bytes control.

For I2S capture, `hw_params` accepts only 48 kHz with 16- or 24-bit samples, sends sample depth to the EC, then computes and sends BCLK either from the stored ratio or ALSA parameters. DAPM PRE_PMU sends EC enable and PRE_PMD sends EC disable. For wake-on-voice, probe registers an EC event notifier and maps optional language/audio shared memory according to EC capabilities. A WoV host event schedules delayed copy work. The copy worker reads audio either through shared memory offsets or repeated host commands, enqueues bytes into a 64 KiB ring, drains full periods to ALSA's vmalloc DMA buffer, advances the PCM pointer, and calls `snd_pcm_period_elapsed()`.

Hotword model updates arrive as a bytes TLV control. The driver skips the TLV header, copies the model from userspace, hashes it with SHA-256, compares the current EC model hash, and sends the new model either through shared memory or chunked host commands.

## State and persistence behavior
State is volatile and split between the kernel private object, EC firmware state, and optional shared memory. `wov_enabled` mirrors EC wake-on-voice state after successful enable/disable commands. `ap_shm_last_alloc` is a monotonic allocator within the reserved AP shared-memory region during driver lifetime. WoV PCM state uses `wov_rp`, `wov_wp`, and `wov_dma_offset`; `wov_burst_read` causes initial larger reads after `hw_params`. The hotword model is persisted, if at all, by EC firmware, not by this driver. The driver has no explicit suspend/resume callbacks, but EC host events can be queued during suspend through the notifier API argument.

## Dependencies and integration points
The file depends on ChromeOS EC protocol definitions in `cros_ec_commands.h` and `cros_ec_proto.h`, EC parent driver data from `dev_get_drvdata(pdev->dev.parent)`, optional OF reserved-memory mappings, ACPI ID `GOOG0013`, OF compatible `google,cros-ec-codec`, ASoC component/DAI/PCM APIs, SHA-256 hashing, delayed work, and the EC event notifier chain. User-visible integration is through the I2S capture DAI, WoV capture DAI, mic gain control, wake-on-voice switch, and hotword model bytes control.

## Risks and test signals
Risks include EC firmware capability mismatches, shared-memory size or type errors, host-command latency in audio paths, ring-buffer overrun during WoV bursts, TLV model size assumptions, and synchronization between `wov_copy_work()` and PCM teardown. `wov_hotword_model_put()` subtracts the TLV header from `size`, so malformed or too-small control payload handling should be validated through ALSA control paths. `wov_pcm_hw_free()` drains queued bytes before clearing the substream, which can emit period elapsed during teardown and should be checked against ALSA expectations.

Useful test signals are successful capability query and I2S reset, optional graceful handling of old EC firmware returning `-ENOPROTOOPT` for reset, DMIC max-gain control creation, EC gain get/set commands for both channels, I2S capture at 48 kHz 16/24-bit with expected BCLK, DAPM enable/disable commands, WoV enable/disable, hotword model upload with unchanged-hash short-circuit, EC and AP shared-memory mapping paths, host-event-triggered audio capture, pointer monotonicity across ring wrap, no overrun logs under expected EC burst rates, and clean component removal unregistering the notifier.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cros_ec_codec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs-amp-lib-test.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs-amp-lib-test.c

## Purpose
This file is the KUnit test suite for `cs-amp-lib.c`, the Cirrus Logic smart-amplifier helper library. It validates firmware calibration coefficient access, EFI calibration read/write behavior, vendor speaker ID detection, Dell SSIDExV2 variant parsing, and the KUnit static-stub hook surface exported by the library.

## Important APIs, types, and functions
The suite private state is `struct cs_amp_lib_test_priv`, which owns a faux amp device, a mutable fake `struct cirrus_amp_efi_data` blob, a list of fake firmware-control writes, and captured EFI attributes. `struct cs_amp_lib_test_param` drives parameterized tests over amplifier counts, amplifier indices, and vendor strings. Static-stub replacements simulate EFI get/set calls, firmware coefficient reads/writes, write-protected EFI storage, zero-filled BIOS-reserved blobs, HP/Cirrus calibration variables, Lenovo and HP speaker-ID variables, and Dell SSIDExV2 variables.

The tested library APIs are `cs_amp_get_efi_calibration_data()`, `cs_amp_set_efi_calibration_data()`, `cs_amp_write_cal_coeffs()`, `cs_amp_read_cal_coeffs()`, `cs_amp_write_ambient_temp()`, `cs_amp_get_vendor_spkid()`, and `cs_amp_devm_get_vendor_specific_variant_id()`. `cs_amp_lib_test_case_init()` creates per-test state and a faux device. `cs_amp_lib_test_cases[]` lists all KUnit cases, and `kunit_test_suite(cs_amp_lib_test_suite)` registers the suite as `snd-soc-cs-amp-lib-test`.

## Control flow
Each test initializes private state, activates one or more static stubs through `kunit_activate_static_stub()`, invokes a public `cs-amp-lib` API, and checks returned errors plus mutated fake state. Calibration read tests cover truncated headers, declared counts larger than the file, missing variables, HP variable preference, UID lookup, unchecked index lookup, UID-checked fallback to index, zero UID handling, out-of-range index handling, and ignored entries whose timestamp is zero.

Firmware coefficient tests replace low-level coefficient reads/writes and verify that calibration writes emit ambient, calR, status, and checksum controls in the expected order, that reads populate ambient/calR/status plus a non-zero timestamp, and that ambient-only writes touch only the ambient control. EFI write tests cover creating a new calibration variable, indexed placement, unspecified maximum size, appending while growing, writing into zero-filled preallocated EFI space without shrinking it, replacing by index or UID, deduplicating duplicate calibration targets by clearing timestamps, finding empty slots, rejecting zero calTarget writes, preserving EFI attributes, respecting HP vendor-variable updates, and preserving old fake storage when writes are denied.

Speaker-ID tests simulate absent, valid, invalid, and oversize Lenovo/HP EFI byte variables. Dell variant tests parse valid SSIDExV2 strings, reject invalid second fields, reject non-Dell callers, and report `-ENOENT` when no variant variable exists.

## State and persistence behavior
The suite itself has no durable state. It models EFI persistence with an in-memory `cal_blob` that fake `set_efi_variable` replaces after successful writes. Empty calibration entries are represented the same way as the library, by zeroing both `calTime` words. The faux device is created per test and destroyed through a KUnit action. Randomized calibration payloads exercise copy/replace behavior while assertions focus on structural invariants.

## Dependencies and integration points
The test depends on KUnit, KUnit static stubs, faux devices, kernel list helpers, random bytes, EFI GUID/status definitions, Cirrus DSP/control structures, and `<sound/cs-amp-lib.h>`. It imports the `SND_SOC_CS_AMP_LIB` namespace and requires `CONFIG_SND_SOC_CS_AMP_LIB_TEST_HOOKS` so `cs_amp_test_hooks` is non-null and the library redirects static helper calls. It is the primary in-tree test signal for the EFI calibration code in `cs-amp-lib.c`.

## Risks and test signals
The suite gives strong coverage for calibration storage edge cases, but it does not exercise real EFI runtime services, real cs_dsp firmware controls, concurrent writers contending on the library mutex, debugfs creation, or full integration with an actual ASoC amplifier driver. Several tests use randomized payloads, so failures should print enough structural context to diagnose which invariant changed. Passing this suite is a high-signal indication that calibration lookup/update semantics, UID/index behavior, vendor variable preference, and speaker/variant parsing remain compatible with the library contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs-amp-lib-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs-amp-lib.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs-amp-lib.c

## Purpose
This file provides common helper code for Cirrus Logic smart amplifiers. It bridges amplifier drivers to firmware calibration controls, EFI-stored calibration blobs, vendor speaker identifiers, Dell variant strings, and a Cirrus-specific debugfs root.

## Important APIs, types, and functions
Public exported APIs are `cs_amp_write_cal_coeffs()`, `cs_amp_read_cal_coeffs()`, `cs_amp_write_ambient_temp()`, `cs_amp_get_efi_calibration_data()`, `cs_amp_set_efi_calibration_data()`, `cs_amp_get_vendor_spkid()`, `cs_amp_devm_get_vendor_specific_variant_id()`, `cs_amp_create_debugfs()`, and `cs_amp_test_hooks`. Internal firmware-control helpers are `cs_amp_write_cal_coeff()`, `cs_amp_read_cal_coeff()`, `_cs_amp_write_cal_coeffs()`, and `_cs_amp_read_cal_coeffs()`. EFI helpers include `cs_amp_get_efi_variable()`, `cs_amp_set_efi_variable()`, `cs_amp_convert_efi_status()`, `cs_amp_alloc_get_efi_variable()`, `cs_amp_get_cal_efi_buffer()`, `cs_amp_set_cal_efi_buffer()`, `_cs_amp_get_efi_calibration_data()`, and `_cs_amp_set_efi_calibration_data()`.

The file knows several EFI variables: Cirrus and HP calibration variables, Lenovo and HP one-byte speaker-ID variables, and Dell `SSIDexV2Data`. `cs_amp_efi_cal_write_lock` serializes calibration EFI updates. `cs_amp_test_hooks` exposes static helper entry points to KUnit when test hooks are enabled.

## Control flow
Firmware calibration writes first verify that DSP firmware controls exist, then write ambient, calR, status, and checksum (`calR + 1`) as big-endian control values under `dsp->pwr_lock`. Reads retrieve ambient, calR, and status, convert from big endian, and stamp the returned `cirrus_amp_cal_data` with current wall-clock time converted to Windows 100 ns time.

EFI calibration reads search the HP variable first and then the Cirrus variable. The code performs a size query, allocates a buffer, reads the variable, verifies the header and flexible-array count against the actual byte size, and treats a zero `size` header as BIOS-preallocated storage whose size is the EFI variable size. Lookup prefers a non-empty entry with non-zero calTarget matching `target_uid`; if none is found, a valid `amp_index` can return an entry whose calTarget is zero or when target matching is intentionally disabled.

EFI calibration writes reject zero calTarget, read the existing HP or Cirrus variable if present, create the Cirrus variable if none exists, initialize zero-filled preallocated blobs, choose a slot by explicit index, matching target, first empty entry, or array growth, deduplicate other active entries with the same calTarget when an explicit index is used, then writes the resized blob back with preserved EFI attributes. The public setter wraps the update in `cs_amp_efi_cal_write_lock`.

Speaker ID lookup checks vendor byte variables in order and maps Lenovo `0xd0/0xd1` or HP `0x30/0x31` to speaker IDs 0/1. Dell variant lookup reads `SSIDexV2Data`, parses underscore-delimited fields, and returns a devm-managed two-character audio hardware ID only for Dell or unknown PCI vendor callers.

## State and persistence behavior
DSP coefficient state lives in firmware controls and is not durable by this file. EFI calibration data is durable platform firmware state and is written through EFI runtime services when available. The code preserves EFI attributes from an existing variable and uses nonvolatile boot/runtime access defaults for newly created Cirrus variables. Empty calibration slots are represented by zero `calTime`; calTarget must be non-zero for writes. Debugfs state is the `cirrus_logic/<dev_name>` directory created under the global debugfs root.

## Dependencies and integration points
The library depends on `FW_CS_DSP` for real DSP coefficient access, EFI runtime services for persistent calibration and vendor IDs, PCI vendor IDs for Dell gating, debugfs, KUnit static stubs, and public data structures from `<sound/cs-amp-lib.h>`. It exports symbols in namespace `SND_SOC_CS_AMP_LIB` and imports `FW_CS_DSP`. Consumer amplifier drivers are expected to pass their `struct cs_dsp`, `struct cirrus_amp_cal_controls`, silicon UID, amp index, and optional PCI SSID details.

## Risks and test signals
Risks include corrupt EFI variable layouts, firmware-reserved zero-filled buffers, target UID collisions, write failures after in-memory mutation, EFI runtime unavailability, endian mistakes in DSP controls, and concurrent writers racing without the global mutex. The current implementation reads the entire calibration variable into memory and bounds count at 128, limiting malformed flexible-array damage. High-value test signals are the KUnit suite in `cs-amp-lib-test.c`, real platform EFI read/write tests on HP and Cirrus variable names, speaker-ID detection on Lenovo/HP systems, Dell SSIDExV2 parsing, DSP firmware-control read/write smoke tests, and verification that failed EFI writes do not corrupt persistent calibration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs-amp-lib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l32.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l32.c

## Purpose
This file is the ALSA SoC I2C codec/monitor driver for the Cirrus Logic CS35L32 boosted class-D amplifier. It registers a capture-only monitor DAI for current/voltage/power monitor data, exposes amplifier controls and DAPM routes, parses platform/device-tree configuration, applies a datasheet monitor patch, and manages regulators, reset GPIO, regmap cache, and runtime power.

## Important APIs, types, and functions
The private type is `struct cs35l32_private`, holding the regmap, component pointer, `VA` and `VP` regulators, platform data, and optional reset GPIO. Register metadata is provided by `cs35l32_reg_defaults[]`, `cs35l32_readable_register()`, `cs35l32_volatile_register()`, `cs35l32_precious_register()`, and `cs35l32_regmap`. ASoC controls and routes are in `cs35l32_snd_controls[]`, `cs35l32_dapm_widgets[]`, and `cs35l32_audio_map[]`.

DAI/component callbacks are `cs35l32_set_dai_fmt()`, `cs35l32_set_tristate()`, and `cs35l32_component_set_sysclk()`. Configuration and lifecycle functions are `cs35l32_handle_of_data()`, `cs35l32_i2c_probe()`, `cs35l32_i2c_remove()`, `cs35l32_runtime_suspend()`, and `cs35l32_runtime_resume()`. The I2C driver matches OF compatible `cirrus,cs35l32` and I2C ID `cs35l32`.

## Control flow
I2C probe allocates private state, initializes an 8-bit register/8-bit value regmap with maple cache, copies platform data or parses device-tree properties, gets and enables `VA`/`VP` supplies, obtains the optional reset GPIO and deasserts reset, reads the multi-register device ID via `cirrus_read_device_id()`, verifies `CS35L32_CHIP_ID`, reads revision ID, applies `cs35l32_monitor_patch`, writes platform configuration for boost manager, SDOUT sharing, SDOUT data layout, battery recovery, and battery threshold, powers down the amplifier by setting `PDN_AMP`, clears the initial MCLK error status by reading interrupt status, and registers the ASoC component plus `cs35l32-monitor` DAI.

The DAI supports two-channel 48 kHz capture with 16/24/32-bit little-endian samples. DAI format setup only toggles whether the serial port is clock/frame provider or consumer. Tristate setup controls SDOUT high impedance. Component sysclk setup accepts 6.000, 12.000, 6.144, and 12.288 MHz and writes MCLK divide/ratio bits.

Runtime suspend marks the regmap cache-only and dirty, asserts reset, and disables regulators. Runtime resume re-enables regulators, deasserts reset, exits cache-only mode, and syncs the regcache.

## State and persistence behavior
Runtime state is held in hardware registers, regmap cache, regulator state, reset GPIO state, and the copied platform data. No settings are persisted by the driver. During runtime suspend, register state is preserved in regcache and replayed after resume. Remove asserts reset but does not explicitly disable regulators; regulator disable is handled in probe error paths and runtime PM paths.

## Dependencies and integration points
The file depends on I2C, regmap, regulator bulk APIs, optional GPIO descriptors, OF property parsing, ASoC component/DAI/DAPM APIs, CS35L32 register definitions from `cs35l32.h`, device-tree binding constants from `<dt-bindings/sound/cs35l32.h>`, and `cirrus_read_device_id()` from `cirrus_legacy.h`. Kbuild includes it as `snd-soc-cs35l32.o` under `CONFIG_SND_SOC_CS35L32`.

## Risks and test signals
Risks include invalid DT values silently falling back after logging errors, omitted platform-data defaults when neither platform data nor OF data is present, power sequencing around reset/regulator timing, regcache sync after reset, and interrupt-status registers marked precious because reads can clear state. The runtime resume path ignores the return value of `regcache_sync()`, so sync failures would not propagate. Test signals are successful I2C probe and chip-ID match, regulator enable/disable behavior, reset GPIO transitions, monitor patch writes, correct fallback/default property values, sysclk rejection for unsupported rates, DAI capture at 48 kHz with each supported sample width, DAPM power of monitor ADC paths, runtime suspend/resume preserving configured registers, and clean failure unwinding when ID or patch application fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l32.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l32.h

## Purpose
This header defines the local register map, bit masks, platform-data structure, supported rates, and supported formats for the CS35L32 ASoC driver in `cs35l32.c`.

## Important APIs, types, and definitions
The only type is `struct cs35l32_platform_data`, containing low-battery threshold/recovery, LED/audio gain management, boost management, SDOUT data configuration, and SDOUT sharing fields. Register definitions cover device ID, power control, clock control, battery threshold, monitor/status, boost/current-protection, serial-port control, class-D control, interrupt masks/status, LED status, and LED flash/movie/timer/inhibit registers. Bit definitions include MCLK divide/ratio, power-down bits, ADSP master/share/data config, SDOUT tristate, battery masks, boost mask, and gain manager mask. `CS35L32_RATES` restricts the DAI to 48 kHz, and `CS35L32_FORMATS` allows 16-, 24-, and 32-bit little-endian samples.

## Control flow
There is no executable control flow in the header. `cs35l32.c` uses these constants during regmap setup, DT/platform configuration, sysclk programming, DAI format programming, DAPM control definitions, and runtime power management.

## State and persistence behavior
The header stores no state. It defines the symbolic contract for hardware register state and for platform data passed into the driver. Any persistence comes from the caller's platform data, device tree, regmap cache, and CS35L32 hardware registers.

## Dependencies and integration points
The header is private to the CS35L32 codec driver and is included by `cs35l32.c`. It assumes ALSA PCM format/rate macros are available from the including translation unit. Device-tree constants for property values live separately in `<dt-bindings/sound/cs35l32.h>`, while this header owns register addresses and masks.

## Risks and test signals
Incorrect register offsets or masks would directly misprogram the amplifier, especially power-down, MCLK, SDOUT, boost, and battery-management fields. Because the header uses plain macros, compiler type checking is minimal. Test signals are indirect: successful chip identification, correct sysclk bit programming, SDOUT tristate behavior, valid monitor capture formats, DT property application landing in the expected masked bits, and stable suspend/resume regcache replay.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l32.h -->
