# Research: subset-b-006540

This grouped report covers the requested ASoC SoundWire utility and core ASoC support files. Each section preserves the source path in its title and is wrapped for deterministic reconciliation into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sdw_utils/soc_sdw_cs42l45.c -->
## sources/distributed-fs/ceph-client/sound/soc/sdw_utils/soc_sdw_cs42l45.c

Purpose: provides CS42L45 SoundWire machine-driver runtime initialization helpers for headset and digital microphone endpoints. The file is intentionally small and is consumed through `codec_info_list` entries in `soc_sdw_utils.c`.

Important APIs and data: `soc_jack_pins[]` maps codec DAPM pin names to `SND_JACK_HEADPHONE` and `SND_JACK_MICROPHONE`; `asoc_sdw_cs42l45_hs_rtd_init()` appends `hs:cs42l45`, creates the shared `ctx->sdw_headset` jack with mechanical/headset/lineout capabilities, and registers it with the codec component through `snd_soc_component_set_jack()`; `asoc_sdw_cs42l45_dmic_rtd_init()` appends `mic:cs42l45-dmic`.

Control flow and state: both helpers are runtime init callbacks. They mutate `card->components` using devm-managed strings. The headset path allocates/initializes the shared jack and binds it to the first codec component; the DMIC path only updates user-space component metadata.

Dependencies and integration: depends on ASoC card/component/jack helpers and `asoc_sdw_mc_private` from `sound/soc_sdw_utils.h`. Integrated by CS42L45/CS42L49 entries in `codec_info_list`.

Risks: exact DAPM pin strings must match the codec topology; failure to allocate the growing `card->components` string returns `-ENOMEM`. Multiple init calls would recreate the jack, so the central `rtd_init_done` guard in `soc_sdw_utils.c` is important.

Test signals: probe logs for jack creation/registration failures, UCM visibility of `hs:cs42l45` and `mic:cs42l45-dmic`, jack detect/button behavior, and DAPM routes exposing the listed pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sdw_utils/soc_sdw_cs42l45.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sdw_utils/soc_sdw_cs47l47.c -->
## sources/distributed-fs/ceph-client/sound/soc/sdw_utils/soc_sdw_cs47l47.c

Purpose: mirrors the CS42L45 helper pattern for CS47L47 SoundWire headset and DMIC runtime initialization.

Important APIs and data: `soc_jack_pins[]` describes CS47L47 headphone/headset/microphone pins. `asoc_sdw_cs47l47_hs_rtd_init()` appends `hs:cs47l47`, creates `ctx->sdw_headset` via `snd_soc_card_jack_new_pins()`, and passes the jack to the codec driver with `snd_soc_component_set_jack()`. `asoc_sdw_cs47l47_dmic_rtd_init()` appends `mic:cs47l47-dmic`.

Control flow and state: the headset init path is allocation, jack creation, codec callback registration, and error return on any failure. The DMIC path is metadata-only. Persistent state is devm-owned `card->components` plus the shared jack object in card private data.

Dependencies and integration: exported in namespace `SND_SOC_SDW_UTILS`; referenced from the CS47L47 entry in `codec_info_list`. Relies on the generic ASoC card jack and component APIs.

Risks: duplicated logic with CS42L45 means any semantic change in CS SDCA jack behavior must be kept in sync. Component strings and pin labels are user-space/topology contracts. `snd_soc_rtd_to_codec(rtd, 0)` assumes the expected codec position.

Test signals: card registration should show `hs:cs47l47`/`mic:cs47l47-dmic`; jack reports should include headphone and microphone bits; failures should be visible through `Failed to create jack` or `Failed to register jack`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sdw_utils/soc_sdw_cs47l47.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sdw_utils/soc_sdw_cs_amp.c -->
## sources/distributed-fs/ceph-client/sound/soc/sdw_utils/soc_sdw_cs_amp.c

Purpose: handles Cirrus CS35L56 SoundWire amplifier setup for generic machine drivers, including playback speaker routing, volume limiting, feedback capture slot allocation, and amplifier counting.

Important APIs: `asoc_sdw_cs35l56_volume_limit()` caps the prefixed `Speaker Volume` control at `CS35L56_SPK_VOLUME_0DB`. `asoc_sdw_cs_spk_rtd_init()` finds CS35L56 codec DAIs, limits volume, and routes `Speaker` to `<prefix> SPK`. `asoc_sdw_cs_spk_feedback_rtd_init()` divides four TX feedback channels across amps sharing each CPU bus and calls `snd_soc_dai_set_tdm_slot()`. `asoc_sdw_cs_amp_init()` increments `info->amp_num` only on playback links.

Control flow and state: playback runtime init iterates codec DAIs and adds one DAPM route per matching amp. Feedback init derives `amps_per_bus` from `num_codecs / num_cpus`, computes a per-CPU slot cursor, and assigns masks from `ch_maps`. State persists in DAPM graph, mixer limits, TDM slot configuration, and `info->amp_num`.

Dependencies and integration: entries for CS35L56 part IDs in `soc_sdw_utils.c` bind playback and capture DAIs to these helpers. Depends on ASoC DAPM, DAI TDM APIs, and dai-link channel maps.

Risks: feedback allocation assumes divisible codec/CPU topology and max four channels per amp; invalid aggregate layouts return `-EINVAL`. Small stack buffers rely on short name prefixes. Route names must match codec component prefixes.

Test signals: speaker playback route appears, volume cap is applied, feedback capture exposes non-overlapping TDM slots, and invalid multi-amp topology logs `Illegal num_codecs`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sdw_utils/soc_sdw_cs_amp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sdw_utils/soc_sdw_dmic.c -->
## sources/distributed-fs/ceph-client/sound/soc/sdw_utils/soc_sdw_dmic.c

Purpose: provides generic SoC DMIC DAPM initialization for SoundWire machine drivers.

Important APIs and data: `dmic_widgets[]` declares `SoC DMIC`; `dmic_map[]` routes `DMic` from `SoC DMIC`; `asoc_sdw_dmic_init()` installs both on the card DAPM context.

Control flow and state: the function adds the widget first, returns immediately if widget creation fails, then adds routes. It has no static mutable state; all persistent effects are DAPM widgets/routes owned by the card.

Dependencies and integration: uses `snd_soc_dapm_new_controls()` and `snd_soc_dapm_add_routes()`. It is a generic helper for boards that need a non-codec digital microphone path in addition to SoundWire endpoints.

Risks: route endpoint names must match the machine/card topology. The helper does not check if the controls already exist, so callers must avoid duplicate initialization. Failure is logged but only the returned error tells callers to abort.

Test signals: DAPM should include `SoC DMIC` and a `DMic` route; card probe should fail cleanly on widget/route allocation errors; capture path tests should confirm the DAPM source powers as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sdw_utils/soc_sdw_dmic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sdw_utils/soc_sdw_maxim.c -->
## sources/distributed-fs/ceph-client/sound/soc/sdw_utils/soc_sdw_maxim.c

Purpose: supports Maxim MAX98363/MAX98373 SoundWire speaker amplifiers in generic ASoC SoundWire machine drivers.

Important APIs and data: `max_98373_dapm_routes[]` connects `Left Spk`/`Right Spk` to backend outputs. `asoc_sdw_maxim_spk_rtd_init()` installs those routes. `max_98373_sdw_ops` wraps common SoundWire stream ops but overrides prepare/hw_free to enable/disable speaker pins. `asoc_sdw_mx8373_sdw_late_probe()` disables speaker pins after boot. `asoc_sdw_maxim_init()` increments amp count, switches on `info->part_id`, and for MAX98373 installs late probe and custom ops.

Control flow and state: prepare calls `asoc_sdw_prepare()` then enables per-prefix speaker pins for playback; hw_free deprepares then disables. Late probe initializes pins disabled. `maxim_part_id` is static but only used during init selection.

Dependencies and integration: tied to Maxim entries in `codec_info_list`; uses ASoC DAPM, SoundWire stream helper wrappers, and card late-probe plumbing.

Risks: helper silently returns 0 from pin toggling even if the last pin operation failed, so hardware pin-state failures may be hidden. Prefix-derived pin names must match DAPM widgets. Unsupported part IDs abort with `-EINVAL`.

Test signals: boot leaves speakers disabled, playback prepare enables the correct left/right pins, hw_free disables them, and MAX98363 keeps default stream ops while MAX98373 uses custom ops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sdw_utils/soc_sdw_maxim.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sdw_utils/soc_sdw_rt5682.c -->
## sources/distributed-fs/ceph-client/sound/soc/sdw_utils/soc_sdw_rt5682.c

Purpose: initializes Realtek RT5682 SoundWire headset runtime state for generic machine drivers.

Important APIs and data: `rt5682_map[]` adds headphone and headset microphone routes; `rt5682_jack_pins[]` maps `Headphone` and `Headset Mic` to jack bits. `asoc_sdw_rt5682_rtd_init()` appends `hs:rt5682`, adds routes, creates `Headset Jack` with headset plus four button bits, maps buttons to media/voice/volume keys, and registers the jack with the codec component.

Control flow and state: the helper returns immediately on component string allocation, route addition, or jack creation failures. Persistent state is DAPM routing, shared `ctx->sdw_headset`, key mapping in the ALSA jack object, and codec jack callback state.

Dependencies and integration: referenced by RT5682 entry in `codec_info_list`; depends on ASoC DAPM, card jack, input key definitions, and component `set_jack`.

Risks: route names are tightly coupled to codec widget names. Only one shared headset jack is supported per card context. Button mapping assumes codec driver reports `SND_JACK_BTN_0..3` consistently.

Test signals: UCM card components include `hs:rt5682`; jack insertion reports headset bits; headset buttons emit play/pause, voice command, volume up, and volume down input events; route-add failures are visible in logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sdw_utils/soc_sdw_rt5682.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sdw_utils/soc_sdw_rt700.c -->
## sources/distributed-fs/ceph-client/sound/soc/sdw_utils/soc_sdw_rt700.c

Purpose: handles RT700 SoundWire headset/speaker runtime initialization.

Important APIs and data: `rt700_map[]` routes `Headphones`, `Speaker`, and `AMIC` to RT700 codec widgets. `rt700_jack_pins[]` maps headphone and microphone pins. `asoc_sdw_rt700_rtd_init()` appends `hs:rt700`, adds routes, creates a headset jack with four button bits, maps button key codes, and binds the jack to the codec component.

Control flow and state: all work happens in the runtime init callback. It mutates `card->components`, the DAPM graph, `ctx->sdw_headset`, the ALSA input key map, and the codec driver's jack callback pointer.

Dependencies and integration: linked from RT700 `codec_info_list` entry. Uses standard ASoC DAPM and jack APIs.

Risks: RT700 uses plural `Headphones` and `AMIC` names unlike some other Realtek helpers; mismatched topology strings would leave paths disconnected. Duplicate runtime init would recreate jacks, relying on the central `rtd_init_done` flag.

Test signals: DAPM graph contains RT700 headphone/speaker/AMIC routes, jack reports headset and button events, and card components expose `hs:rt700`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sdw_utils/soc_sdw_rt700.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sdw_utils/soc_sdw_rt711.c -->
## sources/distributed-fs/ceph-client/sound/soc/sdw_utils/soc_sdw_rt711.c

Purpose: supports pre-SDCA RT711 SoundWire headset setup, including optional jack-detect source software-node properties.

Important APIs: `rt711_add_codec_device_props()` adds `realtek,jd-src` from `SOC_SDW_JACK_JDSRC(quirk)` before card registration. `asoc_sdw_rt711_init()` runs once on playback, finds the SoundWire device by codec name, adds properties, and stores a referenced device in `ctx->headset_codec_dev`. `asoc_sdw_rt711_exit()` removes the software node and drops the reference. `asoc_sdw_rt711_rtd_init()` adds routes, creates the shared headset jack, maps buttons, and calls `snd_soc_component_set_jack()`.

Control flow and state: init is early device-property setup; rtd init is DAPM/jack setup; exit cleans software-node state. Persistent state includes software-node properties on the SDW device and `ctx->headset_codec_dev`.

Dependencies and integration: selected by RT711 version 2 `codec_info_list` entry. Depends on SoundWire bus lookup, Linux software nodes, ASoC jack/DAPM APIs, and quirk macros.

Risks: property setup must occur before codec component probe. Missing SoundWire device returns `-EPROBE_DEFER`. Exit does not clear `ctx->headset_codec_dev`, so caller ordering must avoid reuse after cleanup.

Test signals: JD source quirks appear in codec driver properties, probe defers until SDW device exists, headset jack/buttons work, and driver remove path releases software node/device reference.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sdw_utils/soc_sdw_rt711.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sdw_utils/soc_sdw_rt_amp.c -->
## sources/distributed-fs/ceph-client/sound/soc/sdw_utils/soc_sdw_rt_amp.c

Purpose: supports Realtek RT1308/RT1316/RT1318/RT1320 SoundWire amplifiers, including DMI-specific BQ coefficient injection, DAPM speaker routing, RT1308 I2S clock setup, and lifecycle cleanup.

Important APIs and data: DMI table entries map Dell SKUs to coefficient arrays from `soc_sdw_rt_amp_coeff_tables.h`. `rt_amp_add_device_props()` installs `realtek,bq-params` and count properties. Route arrays map one or two amps per codec family. `asoc_sdw_rt_amp_spk_rtd_init()` selects the route map from DAI name and adds routes based on `name_prefix` suffix `-1` or `-2`. `soc_sdw_rt1308_i2s_ops` sets PLL/sysclk in `rt1308_i2s_hw_params()`. `asoc_sdw_rt_amp_init()` counts playback amps and, once two are present, applies software-node properties to both SDW devices. `asoc_sdw_rt_amp_exit()` removes those nodes and drops references.

Control flow and state: amp count is accumulated in `info->amp_num`; device refs are stored in `ctx->amp_dev1/2`; software nodes persist until exit. DAPM routes persist for the card lifetime.

Dependencies and integration: used by Realtek amp entries in `codec_info_list`; depends on DMI, SoundWire bus lookup, software nodes, ASoC DAPM/DAI clock APIs, and RT1308 codec constants.

Risks: if second device lookup fails, the first reference/property may already be held. Route selection defaults unknown codec names to RT1320. Prefix parsing supports only `-1`/`-2`, so larger arrays rely on other helpers.

Test signals: Dell SKU systems expose BQ properties to codec drivers, two-amp cards add both left/right routes, RT1308 I2S sets PLL at `rate * 512`, and remove unloads software nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sdw_utils/soc_sdw_rt_amp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sdw_utils/soc_sdw_rt_amp_coeff_tables.h -->
## sources/distributed-fs/ceph-client/sound/soc/sdw_utils/soc_sdw_rt_amp_coeff_tables.h

Purpose: provides static Realtek amplifier biquad/BQ coefficient payloads for specific Dell platforms used by `soc_sdw_rt_amp.c`.

Important data: defines `RT1308_MAX_BQ_REG` and `RT1316_MAX_BQ_REG`, then two `static const u8 __maybe_unused` arrays: `dell_0a5d_bq_params[]` and `dell_0b00_bq_params[]`. Each array is a packed byte stream of register address/data triplets or related codec parameter bytes, consumed as a firmware-node `realtek,bq-params` u8 array.

Control flow and state: no executable code. State is compile-time immutable data included into the Realtek amp helper. Runtime copies the relevant array into a stack buffer before creating a software node.

Dependencies and integration: included only by `soc_sdw_rt_amp.c`. DMI matches choose one of these arrays and pass its length via `realtek,bq-params-cnt`.

Risks: values are opaque hardware tuning data; incorrect length or ordering can cause poor audio response or codec misconfiguration. `RT_AMP_MAX_BQ_REG` in the C file is chosen from max register counts and must be large enough for every table. Because arrays are static in a header, including this header from multiple C files would duplicate data.

Test signals: compile-time array size matches DMI platform metadata; runtime codec driver receives the property with expected count; platform audio validation should compare speaker tuning/response on each listed Dell SKU.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sdw_utils/soc_sdw_rt_amp_coeff_tables.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sdw_utils/soc_sdw_rt_dmic.c -->
## sources/distributed-fs/ceph-client/sound/soc/sdw_utils/soc_sdw_rt_dmic.c

Purpose: updates card component metadata for Realtek SoundWire DMIC endpoints, with special handling for RT1320/RT1321 SDCA SmartMic counts.

Important API: `asoc_sdw_rt_dmic_rtd_init()` derives a user-space microphone name from `component->name_prefix`, translating `rt714` to `rt715-sdca` for compatibility. If the component device is an RT1320/RT1321 SoundWire slave, it iterates all card components, counts same-part peripherals that expose an SDCA SmartMic function, and appends `cfg-mics:<count>` to `card->components`.

Control flow and state: runtime init builds a devm string, optionally scans card components and SDCA function tables, then appends either `mic:<name>` or `mic:<name> cfg-mics:<n>`. Persistent state is only `card->components`.

Dependencies and integration: used by multiple Realtek DMIC DAI entries in `codec_info_list`; depends on SoundWire slave helpers and `sdca_function.h` type constants.

Risks: correctness depends on codec drivers registering SDCA function data before this callback. The component iterator reuses the `component` variable, so later code must not assume it still points to the original. User-space UCM naming compatibility is encoded in string special cases.

Test signals: card components contain expected mic names, RT1320/RT1321 cards include accurate `cfg-mics`, and SDCA SmartMic devices are discovered from `sdca_data.function[]`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sdw_utils/soc_sdw_rt_dmic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sdw_utils/soc_sdw_rt_mf_sdca.c -->
## sources/distributed-fs/ceph-client/sound/soc/sdw_utils/soc_sdw_rt_mf_sdca.c

Purpose: provides speaker DAPM route initialization for Realtek multifunction SDCA codecs RT712, RT721, and RT722.

Important APIs and data: route arrays connect generic `Speaker` to codec-specific `SPK` or `SPOL`/`SPOR` endpoints. `struct codec_route_map` binds codec names to route arrays and sizes. `get_codec_route_map()` does exact string lookup. `asoc_sdw_rt_mf_sdca_spk_rtd_init()` truncates/copies `dai->name` into a six-byte codec name buffer, looks up routes, and adds them to card DAPM.

Control flow and state: runtime init is lookup then route addition. No static mutable state exists; DAPM routes are the persistent side effect.

Dependencies and integration: used by RT712/RT721/RT722 amplifier DAI entries in `soc_sdw_utils.c`. Depends on ASoC DAPM and codec DAI names matching the route map keys.

Risks: `CODEC_NAME_SIZE` is tight and relies on short names like `rt712`; future longer codec names would be truncated and fail lookup. Unsupported names return `-EINVAL`. Route names must match codec driver widgets.

Test signals: RT712 creates two routes while RT721/RT722 create one; unsupported DAI names log `failed to get codec name and route map`; playback powers the expected speaker widget.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sdw_utils/soc_sdw_rt_mf_sdca.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sdw_utils/soc_sdw_rt_sdca_jack_common.c -->
## sources/distributed-fs/ceph-client/sound/soc/sdw_utils/soc_sdw_rt_sdca_jack_common.c

Purpose: common jack helper for Realtek SDCA headset codecs RT711/RT712/RT713/RT721/RT722.

Important APIs: `rt_sdca_jack_add_codec_device_props()` optionally installs `realtek,jd-src` before codec probe. `asoc_sdw_rt_sdca_jack_init()` ensures one headset device reference per card, finds the SDW device, adds properties, and stores `ctx->headset_codec_dev`. `asoc_sdw_rt_sdca_jack_exit()` removes software node and drops the reference when a JD source quirk was used. `asoc_sdw_rt_sdca_jack_rtd_init()` appends `hs:<prefix>`, adds `-sdca` suffix for RT711/RT713 UCM compatibility, installs codec-specific headphone/mic DAPM routes, creates shared headset jack with four button bits, maps keys, and registers the jack.

Control flow and state: early init handles software-node property state; runtime init handles card routes/jack; exit cleans property state. Persistent state includes `ctx->headset_codec_dev`, card components, DAPM routes, and jack callback state.

Dependencies and integration: used by SDCA Realtek jack entries in `codec_info_list`; depends on SoundWire bus lookup, ASoC DAPM/jack, input keys, and machine quirks.

Risks: exit returns without clearing references if no JD source quirk is set, matching property ownership but relying on lifecycle assumptions. String matching with `strstr()` can match prefixes broadly. UCM suffix rules are compatibility-sensitive.

Test signals: each supported codec adds the correct routes, card components include the expected `-sdca` suffix for RT711/RT713, JD source property is visible when quirked, and remove path clears `ctx->headset_codec_dev`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sdw_utils/soc_sdw_rt_sdca_jack_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sdw_utils/soc_sdw_ti_amp.c -->
## sources/distributed-fs/ceph-client/sound/soc/sdw_utils/soc_sdw_ti_amp.c

Purpose: initializes TI TAS2783 SoundWire amplifier speaker routes and volume limits.

Important APIs: `asoc_sdw_ti_amp_initial_settings()` limits `<prefix> Speaker Volume` to `TIAMP_SPK_VOLUME_0DB`. `asoc_sdw_ti_spk_rtd_init()` iterates codec DAIs named `tas2783`, maps prefixes `tas2783-1` through `tas2783-4` to `Left Spk`, `Right Spk`, `Left Spk2`, and `Right Spk2`, applies volume limits, and adds DAPM routes from the selected speaker widget to `<prefix> SPK`. `asoc_sdw_ti_amp_init()` increments `info->amp_num` only for playback.

Control flow and state: runtime init loops over all codec DAIs in a link and returns on unhandled prefix, volume-limit failure, or route-add failure. Persistent state is mixer limit, DAPM route, and amp count.

Dependencies and integration: TAS2783 entry in `codec_info_list` supplies four-speaker widgets and controls and binds these helpers. Uses ASoC DAPM and mixer volume limiting.

Risks: `asoc_sdw_ti_amp_initial_settings()` logs volume-limit errors but returns 0, so route init may proceed after a failed limit. Prefix parsing is hard-coded to four amps. Buffers assume short prefixes/widget names.

Test signals: four-speaker systems expose all left/right speaker pins, each TAS2783 volume control is capped, unrecognized prefixes produce `unhandled prefix`, and playback DAPM routes target the right physical speaker.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sdw_utils/soc_sdw_ti_amp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sdw_utils/soc_sdw_utils.c -->
## sources/distributed-fs/ceph-client/sound/soc/sdw_utils/soc_sdw_utils.c

Purpose: central SoundWire ASoC helper library. It defines the codec capability registry, generic widgets/controls, codec lookup helpers, runtime initialization, SoundWire stream operation wrappers, DAI-link construction helpers, endpoint counting/parsing, and card cleanup/late-probe hooks.

Important APIs and data: `codec_info_list[]` maps SoundWire vendor/part/version IDs and ACPI IDs to `asoc_sdw_codec_info` entries, DAI descriptors, widgets, controls, init/exit/rtd callbacks, quirks, auxiliary components, and optional card late probes. Lookup exports include `asoc_sdw_find_codec_info_part()`, `_acpi()`, and `_dai()`. `asoc_sdw_rtd_init()` installs controls/widgets once per runtime, calls codec-specific `rtd_init`, constructs speaker component metadata, and marks DAI init complete. Stream exports `asoc_sdw_startup()`, `prepare()`, `trigger()`, `hw_params()`, `hw_free()`, and `shutdown()` wrap SoundWire stream APIs and channel-map setup. Link helpers create `snd_soc_dai_link` objects. Endpoint helpers count and parse ACPI SoundWire endpoint descriptions into internal endpoint/dailink structures.

Control flow and state: machine creation first counts endpoints, parses links, builds DAI links, then runtime init executes per codec DAI. Static `codec_info_list` contains mutable fields such as `amp_num`, `rtd_init_done`, and late-probe callbacks; `asoc_sdw_mc_dailink_exit_loop()` resets `rtd_init_done` and calls registered exits. Endpoint parsing handles aux components, sidecar amps, quirks, SDCA function presence, aggregation groups, and per-stream link masks.

Dependencies and integration: depends on Linux SoundWire bus/slave APIs, ACPI SoundWire descriptors, SDCA function metadata, and many codec-specific helper files exported under `SND_SOC_SDW_UTILS`. Generic machine drivers use this as their discovery and setup layer.

Risks: mutable global codec registry state must be reset on card teardown and may be sensitive to multiple cards. Endpoint filtering mixes quirks and BIOS SDCA data; wrong quirk polarity can drop endpoints. `asoc_sdw_get_codec_name()` depends on exact generated SoundWire device names and unique-ID rules. Channel-map logic requires capture channels divisible by codec count.

Test signals: mockup entries exercise parsing; real boards should validate endpoint counts, aggregated DAI grouping, card component strings, DAPM controls/widgets, SDCA endpoint filtering, SoundWire prepare/trigger/deprepare sequences, and teardown cleanup of software nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sdw_utils/soc_sdw_utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/soc-ac97.c -->
## sources/distributed-fs/ceph-client/sound/soc/soc-ac97.c

Purpose: implements ASoC AC97 component allocation/registration, optional AC97 GPIO exposure, and generic GPIO/pinctrl-based AC97 reset operation setup.

Important APIs and data: `soc_ac97_bus` is the shared AC97 bus with ops set by `snd_soc_set_ac97_ops()`. `snd_soc_alloc_ac97_component()` allocates and initializes an `snd_ac97` device under the card. `snd_soc_new_ac97_component()` optionally resets/checks codec ID, registers the device, and initializes GPIOs. `snd_soc_free_ac97_component()` removes GPIOs/device and releases the ref. Under `CONFIG_GPIOLIB`, `snd_ac97_gpio_priv` and `snd_soc_ac97_gpio_chip` map AC97 GPIO register access to gpiolib callbacks. `snd_soc_set_ac97_ops_of_reset()` parses pinctrl states and GPIOs, installs warm/cold reset callbacks, and stores `snd_ac97_rst_cfg`.

Control flow and state: AC97 creation is allocate, optional reset, `device_add`, GPIO registration. Free reverses those steps. Reset config is a single static global and includes pinctrl state handles and GPIO descriptors. AC97 bus ops are also global and protected only by busy checks.

Dependencies and integration: uses ALSA AC97 core, ASoC component register read/write helpers, gpiolib, pinctrl, platform device resources, and device-tree named `ac97` GPIOs/states.

Risks: global `soc_ac97_ops` and reset config limit concurrent differing controllers. Error path after GPIO init failure calls `put_device()` without `device_del()` after successful `device_add()`, which is a lifecycle-sensitive path to audit. GPIO direction debug strings include a likely typo for input.

Test signals: AC97 device appears with card-derived name, reset toggles expected pins/states, GPIO chip exposes 8 AC97 GPIOs when enabled, and `snd_soc_set_ac97_ops()` returns `-EBUSY` when replacing active ops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/soc-ac97.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/soc-acpi.c -->
## sources/distributed-fs/ceph-client/sound/soc/soc-acpi.c

Purpose: provides ASoC ACPI and SoundWire enumeration helpers for machine-driver selection and ACPI package extraction.

Important APIs: `snd_soc_acpi_find_machine()` scans a machine table, tests primary `id` or composite codec IDs, applies optional `machine_quirk`, and returns the selected entry. `snd_soc_acpi_find_package_from_hid()` walks ACPI devices for a HID and extracts a typed package into caller-provided state. `snd_soc_acpi_codec_list()` validates that every codec in a quirk-provided list is present. `snd_soc_acpi_sdw_link_slaves_found()` verifies that all ACPI-described SoundWire slaves for a link are reported in the live peripheral list, including duplicate part-count and unique-ID handling.

Control flow and state: helpers are stateless except `snd_soc_acpi_id_present()` may copy a matching composite codec ID into `machine->id`. Package search terminates early when a valid package is found. SoundWire matching compares link ID, manufacturer, part, version, duplicate count, and unique ID when needed.

Dependencies and integration: uses ACPI device presence/evaluation APIs, `soc-acpi.h` machine descriptors, and SoundWire ID macros. Exported functions are used by platform machine drivers during probe.

Risks: mutating `machine->id` for composite matches can affect later table use. Duplicate SoundWire parts require exact expected/reported counts before unique IDs are considered. Package extraction ignores malformed/nonmatching devices and returns false rather than detailed errors.

Test signals: ACPI tables with single and composite codec IDs select expected machines; quirk rejection continues scanning; package extraction validates count/format; SoundWire duplicate slave configurations only pass when all unique IDs are present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/soc-acpi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/soc-card-test.c -->
## sources/distributed-fs/ceph-client/sound/soc/soc-card-test.c

Purpose: KUnit coverage for `snd_soc_card_get_kcontrol()` lookup behavior.

Important APIs and data: `test_card_controls[]` defines twelve dummy mixer controls with distinct shift values and left/right-prefixed names. `test_snd_soc_card_get_kcontrol()` adds controls to a test card, looks each up by exact name, checks the returned `soc_mixer_control->shift`, and verifies misses for unrelated, partial, and NULL names. Fixture setup allocates `soc_card_test_priv`, registers a KUnit device, creates an ASoC card, and calls `snd_soc_register_card()`.

Control flow and state: per-test init builds and registers a card; the test adds controls and performs lookups; exit unregisters the card and drops the device reference. State is isolated through KUnit allocations.

Dependencies and integration: depends on KUnit, `kunit/device.h`, ASoC card registration, and control helper macros. It directly exercises `soc-card.c`.

Risks: because the fixture registers a minimal card, future ASoC registration prerequisites could break the test before the lookup logic runs. The test validates exact control name lookup but not component-prefixed lookup from `soc-component.c`.

Test signals: the KUnit suite name is `soc-card`; expected pass means every added control is found with matching private shift and invalid names return NULL.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/soc-card-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/soc-card.c -->
## sources/distributed-fs/ceph-client/sound/soc/soc-card.c

Purpose: wraps core ASoC card-level operations: mixer control lookup, jack creation, card lifecycle callbacks, bias callbacks, and dynamic DAI-link add/remove hooks.

Important APIs: `snd_soc_card_get_kcontrol()` returns a mixer kcontrol by exact name, guarding NULL. `jack_new()` initializes `snd_soc_jack` lists/mutex/notifier and calls `snd_jack_new()`. `snd_soc_card_jack_new()` and `_jack_new_pins()` export jack creation with optional pin attachment. Lifecycle wrappers include suspend/resume pre/post, probe, late_probe, remove, bias-level hooks, `snd_soc_card_add_dai_link()`, and `snd_soc_card_remove_dai_link()`.

Control flow and state: wrapper callbacks call optional function pointers on `struct snd_soc_card` and normalize return logging through `soc_card_ret()`. Probe/late_probe manage `card->probed`: if `probe` exists it sets probed after probe, and late_probe sets it after late probe; remove calls `card->remove` only when probed and then clears the flag. Jack creation initializes caller-owned jack structs.

Dependencies and integration: used broadly by ASoC core and machine drivers, including SoundWire helpers that create headset jacks. Depends on ALSA control and jack core plus card callback conventions.

Risks: lifecycle correctness hinges on `card->probed`; callback ordering changes can skip remove or call it too early. Jack helpers assume caller storage remains valid. `snd_soc_card_get_kcontrol()` performs exact lookup only, so callers must format names correctly.

Test signals: `soc-card-test.c` validates kcontrol lookup; runtime tests should cover jack creation with pins, probe/late_probe/remove ordering, and dynamic dai-link callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/soc-card.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/soc-component.c -->
## sources/distributed-fs/ceph-client/sound/soc/soc-component.c

Purpose: implements ASoC component-level dispatch for driver callbacks, jack/control helpers, compressed stream component operations, register I/O, PCM component operations, runtime PM, and rollback markers.

Important APIs: clock and PLL wrappers (`snd_soc_component_set_sysclk()`, `_set_pll()`), jack/control helpers (`snd_soc_component_set_jack()`, `_get_kcontrol()`, `_notify_control()`), module/open/close wrappers, suspend/resume/probe/remove callbacks, regmap helpers, compressed ops dispatchers, register read/write/update/field helpers, PCM callbacks (`pointer`, `delay`, `ioctl`, `copy`, `page`, `mmap`, `new`, `free`, `prepare`, `hw_params`, `hw_free`, `trigger`, `ack`), and runtime PM get/put.

Control flow and state: most functions test for an optional driver callback, call it, then wrap/log return values. Marker macros store the current stream in fields such as `mark_open`, `mark_hw_params`, `mark_trigger`, `mark_pm`, and `mark_compr_open`; rollback cleanup skips components without a matching mark. Register I/O serializes legacy read/write paths with `component->io_mutex`, while regmap paths use regmap APIs. Compressed and PCM dispatch usually iterate all runtime components, except first-provider APIs such as pointer/copy/page/mmap.

Dependencies and integration: sits under ASoC PCM/compress/card code and is called by codec/platform/component drivers. Depends on regmap, pm_runtime, ALSA PCM/compress structures, and ASoC runtime iterators.

Risks: single marker fields mean overlapping streams of the same component require careful ordering. Some get_caps/copy paths return through a `component` pointer after loops and assume at least one component. First-provider behavior may hide later component implementations. Async register updates require explicit `snd_soc_component_async_complete()`.

Test signals: component callback order and rollback paths during failed open/hw_params, register I/O with and without regmap, runtime PM reference balance, compressed op dispatch, and PCM trigger rollback should be covered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/soc-component.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/soc-compress.c -->
## sources/distributed-fs/ceph-client/sound/soc/soc-compress.c

Purpose: creates and operates ALSA compressed audio devices for ASoC, covering both normal codec-to-CPU links and dynamic front-end/back-end DPCM compressed paths.

Important APIs and data: `soc_compr_ops` handles static compressed streams; `soc_compr_dyn_ops` handles dynamic FE streams. Open/free paths call DAI/component/link startup and shutdown helpers with rollback handling. Trigger, set/get params, ack, pointer, metadata, caps, and optional copy are dispatched across CPU DAI, components, machine link, DPCM BEs, and DAPM as appropriate. `snd_soc_new_compress()` validates unidirectional single CPU/codec support, allocates `snd_compr`, creates optional internal BE PCM for dynamic links, selects ops, enables copy when any component supports it, and registers the compressed device.

Control flow and state: static open gets runtime PM, locks DPCM mutex, starts CPU DAI/components/link, and activates runtime; failure calls `soc_compr_clean()` with rollback. Dynamic FE open computes DPCM paths under card lock, starts BEs, then FE CPU/component/link. Dynamic set_params prepares BEs with empty FE hw_params before programming compressed params. Trigger updates DPCM state and DAPM stream events. Persistent state includes `rtd->compr`, `compr->private_data`, `rtd->fe_compr`, `rtd->pcm` for dynamic links, delayed close work function, DPCM states, and active runtime flags.

Dependencies and integration: depends on ALSA compress core, ASoC DPCM, DAPM, component and DAI compress helpers, and card/runtime locks.

Risks: compressed devices reject multi-CPU or multi-codec links. Dynamic FE correctness depends on lock ordering and DPCM state transitions. Partial drain bypasses BE trigger and only hits components. Error rollback must keep PM/module/component marks balanced.

Test signals: static and dynamic compressed playback/capture open/free, invalid bidirectional or multi-codec rejection, DPCM BE startup/params/trigger ordering, drain commands, metadata/ack/pointer propagation, and copy callback exposure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/soc-compress.c -->
