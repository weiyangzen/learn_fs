# Research: subset-b-006514

Grouped research for Intel ASoC/SOF board files. Each section preserves the source path and is bounded for reconciliation into source-tree-aligned per-file documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/cht_bsw_rt5672.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/boards/cht_bsw_rt5672.c

Purpose: ASoC machine driver for Cherry Trail/Braswell and Bay Trail CR platforms using the Realtek RT5672/RT5670 codec. It registers a DPCM sound card with media/deep-buffer front ends and one SSP codec back end, adapting the back end to SSP0 on Bay Trail CR and SSP2 otherwise.

Important APIs, types, and functions: `struct cht_mc_private` stores the headset jack, ACPI-resolved codec name, PMC platform clock, and SSP0 flag. `platform_clock_control()` is a DAPM supply event callback that enables `pmc_plt_clk_3`, programs the codec PLL from 19.2 MHz MCLK, and falls back to RCCLK when idle so jack detection still works. `cht_codec_init()` adds ACPI GPIO mappings, selects RT5670 ASRC sources, adds SSP-specific routes, creates the headset jack, maps button events, configures jack detection, and normalizes MCLK rate. `cht_codec_fixup()` forces the BE to 48 kHz stereo and 16-bit or 24-bit samples depending on SSP. `snd_cht_mc_probe()` resolves the ACPI codec instance, overrides platform names, selects SOF card naming when applicable, and registers the card.

Control flow and integration: Probe allocates private state, rewrites the static DAI link codec name from ACPI, optionally rewrites the CPU DAI to `ssp0-port`, fixes platform components from `snd_soc_acpi_mach`, binds card drvdata, and registers the card. During runtime DAPM clock events and hw_params set PLL/sysclk, while suspend/resume calls Realtek jack suspend/resume helpers.

State and persistence: State is in devm-managed private data and a static card/DAI-link template that probe mutates. No disk persistence exists. The codec name mutation and static card object mean repeated probes would need care, but this platform driver is normally singleton.

Dependencies: Linux ASoC core, ACPI GPIO mapping, common clock framework, RT5670 codec APIs, SST Atom DPCM names, Intel SoC quirks, and optional SOF parent detection.

Risks: MCLK acquisition is mandatory and returns probe failure. Static DAI-link mutation can be fragile if multiple matching devices ever probe. Jack detection depends on the codec keeping RCCLK when idle. SSP0/SSP2 bit-width differences must match firmware topology. Test signals include successful card registration, DAPM route validation, `aplay/arecord` at 48 kHz, jack/button events across suspend/resume, and no clock/PLL errors in dmesg.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/cht_bsw_rt5672.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/ehl_rt5660.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/boards/ehl_rt5660.c

Purpose: ASoC machine driver for Elkhart Lake systems with an RT5660 codec, PCH DMIC capture links, and up to four iDisp HDMI playback back ends.

Important APIs, types, and functions: `struct sof_card_private` tracks HDMI PCM entries and whether the iDisp codec is present. `struct sof_hdmi_pcm` records a codec DAI and PCM device id for late HDMI control creation. `hdmi_init()` appends HDMI runtime information to the list. `card_late_probe()` calls `hda_dsp_hdmi_build_controls()` when the HDA HDMI codec exists. `rt5660_hw_params()` programs RT5660 sysclk to PLL1 and derives PLL input from BCLK at 50fs. `hdmi_link_init()` switches HDMI codec components to `snd_soc_dummy_dlc` when ACPI `codec_mask` lacks `IDISP_CODEC_MASK`.

Control flow and integration: The static DAI-link table defines one SSP0 RT5660 back end, two DMIC capture BEs, and four iDisp BEs. Probe allocates private state, fixes platform component names from `mach->mach_params.platform`, rewrites HDMI links to dummy codecs if display audio is unavailable, and registers the card with normal ASoC PM ops.

State and persistence: Runtime state is a devm-managed HDMI list and an `idisp_codec` boolean. The card and link arrays are static and are modified in place for dummy HDMI codec fallback. There is no persisted state.

Dependencies: ASoC core, RT5660 codec driver, HDA DSP HDMI helper namespace, ACPI machine parameters, and the SOF/HDA platform component named from machine data.

Risks: `card_late_probe()` returns `-ENOENT` if the HDMI list is empty, so topology/link mismatches can prevent normal late-probe completion. The HDMI link loop uses fixed index constants and depends on the static table order. Test signals include card registration with and without iDisp codec support, HDMI mixer controls, DMIC capture, RT5660 playback/capture clock setup, and absence of dummy-codec topology failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/ehl_rt5660.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/hda_dsp_common.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/boards/hda_dsp_common.c

Purpose: Shared Intel HDA DSP helper that wires ASoC HDMI front-end PCMs to legacy HDA HDMI codec converter control structures before building HDA codec controls.

Important APIs, types, and functions: When `CONFIG_SND_SOC_SOF_HDA_AUDIO_CODEC` is enabled, `hda_dsp_hdmi_pcm_handle()` scans card runtimes, skips BE links and non-playback PCMs, and returns the Nth FE PCM whose id contains `HDMI`. `hda_dsp_hdmi_build_controls()` obtains `struct hdac_hda_priv` from the component drvdata, iterates `hcodec->pcm_list_head`, assigns each `struct hda_pcm` to the corresponding FE PCM/device number or marks it invalid, toggles display power, and invokes `snd_hda_codec_build_controls()`.

Control flow and integration: Machine drivers call `hda_dsp_hdmi_build_controls()` from `late_probe` after HDMI BEs have captured the HDA HDMI component. This bridges the SOF topology's FE PCM numbering to the HDA codec layer so ELD/jack/control nodes bind to the right PCM devices.

State and persistence: The helper mutates in-memory `hda_pcm` entries by setting `pcm` and `device`. It has no persistent state and no private allocations.

Dependencies: ASoC card runtime iteration, HDA codec private structures, HD-audio display power helpers, and `hdac_hda` codec integration.

Risks: The PCM match is name-based using substring `HDMI`; topology naming changes can break mapping. Converter order is assumed to match FE HDMI enumeration order. Missing FE PCMs produce warnings and invalid devices, which may be acceptable for absent converters but indicate topology mismatches. Test signals include HDMI PCM ids, HDMI controls/ELD creation, display-power sequencing in dmesg, and successful imports from drivers using `SND_SOC_INTEL_HDA_DSP_COMMON`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/hda_dsp_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/hda_dsp_common.h -->
# sources/distributed-fs/ceph-client/sound/soc/intel/boards/hda_dsp_common.h

Purpose: Header for shared Intel HDA DSP HDMI helpers consumed by machine drivers that need to expose HDA HDMI codec controls from SOF/ASoC topologies.

Important APIs, types, and functions: The header declares `hda_dsp_hdmi_build_controls(struct snd_soc_card *card, struct snd_soc_component *comp)` when `CONFIG_SND_SOC_SOF_HDA_AUDIO_CODEC` is enabled. Otherwise it provides a static inline stub returning `-EINVAL`, allowing callers to compile while still failing predictably when HDA audio codec support is absent.

Control flow and integration: Drivers include this header and call the helper during card `late_probe`. It imports HDA codec and display-power definitions plus `hdac_hda` private types needed by the implementation.

State and persistence: The header defines no state. Its only behavioral impact is compile-time gating of HDMI control support.

Dependencies: ASoC, HDA codec core, HDA i915/display helpers, and `../../codecs/hdac_hda.h`.

Risks: Callers must handle the `-EINVAL` stub path, especially in builds without HDA audio codec support. Test signals include build coverage for both config branches and module namespace imports in callers that use the exported implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/hda_dsp_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/hsw_rt5640.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/boards/hsw_rt5640.c

Purpose: Haswell Lynx Point ASoC machine driver for systems using the Realtek RT5640 codec through SSP0.

Important APIs, types, and functions: Static widgets/routes expose `Headphones` and `Mic` plus SSP0 codec BE connections. `codec_link_hw_params_fixup()` constrains the BE to 48 kHz, stereo, 16-bit samples because the ADSP performs FE conversion. `codec_link_hw_params()` sets the codec sysclk to 12.288 MHz MCLK and updates codec register `0x83` to select the expected filter mode. The DAI-link array contains four dynamic FE links (`System`, two offload playback links, and `Loopback`) plus one no-PCM SSP0 codec BE.

Control flow and integration: Probe obtains `snd_soc_acpi_mach`, assigns the platform component name with `snd_soc_fixup_dai_links_platform_name()`, and registers the static card. Runtime DPCM connects FEs to the codec BE, with trigger mode set to post-trigger for FE links.

State and persistence: The driver uses static card/link tables and no private drvdata. It has no persistent state.

Dependencies: ASoC DPCM, Haswell PCM platform name from ACPI mach data, RT5640 codec definitions, and standard `snd_soc_pm_ops`.

Risks: The raw register update is codec-version sensitive and deserves regression attention. The platform and codec component names are hard coded except platform fixup. Test signals include card registration, all FE PCMs appearing, 48 kHz stereo BE constraints, headphone/mic DAPM routing, offload playback, and suspend/resume with PM ops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/hsw_rt5640.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/skl_hda_dsp_generic.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/boards/skl_hda_dsp_generic.c

Purpose: Generic machine driver for Skylake and later HDA DSP platforms with optional iDisp HDMI, external HDA codecs, DMICs, and Bluetooth offload.

Important APIs, types, and functions: `skl_hda_get_board_quirk()` derives BT offload quirk bits from a single `bt_link_mask`. `skl_hda_add_dai_link()` marks HDMI PCM links ignored when iDisp is absent. `skl_hda_audio_probe()` allocates a card, obtains a `sof_card_private` via `sof_intel_board_get_ctx()`, sets `hda_codec_present` and HDMI flags from `mach_params.codec_mask`, overrides link order and BE ids with `HDA_LINK_ORDER` and `HDA_LINK_IDS`, then asks `sof_intel_board_set_dai_link()` to synthesize the BE links. `skl_set_hda_codec_autosuspend_delay()` finds the first external HDA codec component and sets bus power-save delay to 1000 ms.

Control flow and integration: This driver is a thin policy layer over `sof_board_helpers.c`. It sets card metadata, link ordering, optional `cfg-dmics` component strings, platform-name fixups, card drvdata, and then registers the card. HDMI/HDA controls are handled by the helper late-probe path.

State and persistence: All state is devm-managed card/context data. No persistent state exists.

Dependencies: SOF board helpers, HDA codec private data, HDA DSP platform component names, ACPI mach params, and ASoC PM ops.

Risks: BE id/order constants must match SOF topology files. Autosuspend delay lookup depends on codec component name containing `ehdaudio0D0`. Test signals include generated DAI links for each codec-mask combination, HDMI FE ignore behavior without iDisp, HDA analog/digital controls, DMIC component strings, BT link creation, and HDA codec autosuspend timing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/skl_hda_dsp_generic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_board_helpers.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_board_helpers.c

Purpose: Shared topology builder for Intel SOF I2S/HDA board drivers. It converts detected codec/amp types and packed board quirk bits into a card's BE DAI-link table.

Important APIs, types, and functions: `sof_intel_board_get_ctx()` allocates `struct sof_card_private`, detects headset codec and amp types through ACPI helper APIs, decodes SSP ports, HDMI count, BT offload, and HDMI capture masks. `sof_intel_board_set_dai_link()` calculates link count, allocates links, applies default or caller-supplied link order/ids, and dispatches to helper builders. Builders include `set_ssp_codec_link()`, `set_dmic_link()`, `set_idisp_hdmi_link()`, `set_ssp_amp_link()`, `set_bt_offload_link()`, `set_hdmi_in_link()`, and `set_hda_codec_link()`. `sof_intel_board_card_late_probe()` builds HDMI controls through `hda_dsp_hdmi_build_controls()`.

Control flow and integration: Machine drivers first get a context, optionally override fields, call `sof_intel_board_set_dai_link()`, and then patch `ctx->codec_link` and/or `ctx->amp_link` with codec-specific component arrays, init callbacks, ops, and codec_conf. DAPM init callbacks add shared DMIC or HDA widgets/routes. HDMI init stores the HDMI component for late probe.

State and persistence: State lives in devm-managed context and DAI-link arrays. The shared `platform_component` object is static but its name is later fixed by ASoC platform-name fixup.

Dependencies: ASoC core, SOF topology conventions, Intel SoC legacy BYT/CHT naming quirks, ACPI codec detection helpers, HDA DSP HDMI helper.

Risks: Link count and generated order must exactly match topology expectations; mismatch returns `-EINVAL` or causes topology failures. Static component arrays are reused across cards. HDMI link id overrides increment across multi-link groups. Test signals include unit-style link count/order inspection, all supported codec/amp quirk combinations, DMIC/HDA DAPM routes, HDMI controls, and legacy SSP dai names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_board_helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_board_helpers.h -->
# sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_board_helpers.h

Purpose: Public interface and quirk encoding for the Intel SOF board-helper topology builder.

Important APIs, types, and functions: The header defines packed quirk macros for codec SSP, amp SSP, BT offload SSP, HDMI capture SSP mask, iDisp HDMI count, and BT offload presence. It defines link type constants (`SOF_LINK_CODEC`, `SOF_LINK_DMIC01`, `SOF_LINK_IDISP_HDMI`, `SOF_LINK_HDA`, and others) plus `SOF_LINK_ORDER()` and `SOF_LINK_IDS()` bit packing macros. `struct sof_da7219_private`, `struct sof_rt5682_private`, and `struct sof_card_private` hold shared card state, detected codec/amp type, link counts, port numbers, feature flags, pointers to generated links, optional link order/id overrides, and codec-specific private unions. Exported functions are `sof_intel_board_card_late_probe()`, `sof_intel_board_set_dai_link()`, and `sof_intel_board_get_ctx()`.

Control flow and integration: Machine drivers include this header to define platform-device id `driver_data`, obtain a context, override fields for board policy, and patch generated codec/amp links.

State and persistence: The header defines only structure layout and bit encodings. It does not persist data.

Dependencies: ASoC, ACPI Intel SSP common codec enums, and `sof_hdmi_common.h`.

Risks: Bit allocation reserves low 8 bits for machine-driver-specific quirks; collisions can silently misconfigure ports/features. Link-order packing supports seven entries only. Test signals include compile coverage for all macro users and runtime logging of decoded quirk masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_board_helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_cirrus_common.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_cirrus_common.c

Purpose: Shared helpers for Intel SOF boards using Cirrus Logic CS35L41/CS35L53 smart amplifiers.

Important APIs, types, and functions: `cs35l41_init()` adds four possible speaker widgets, pin controls, and routes for woofer/tweeter left/right positions. `cs35l41_hw_params()` obtains the BCLK from SOF topology with `sof_dai_get_bclk()`, sets each codec DAI/component sysclk to SCLK, and programs per-amplifier RX channel maps. `cs35l41_compute_codec_conf()` enumerates ACPI devices with HID `CSC3541` and UIDs 0 through 3, maps UIDs to prefixes `WL`, `WR`, `TL`, `TR`, fills component and codec_conf arrays, and returns the number of found amps. Exported `cs35l41_set_dai_link()` patches a generated amp link, while `cs35l41_set_codec_conf()` publishes codec prefixes on the card.

Control flow and integration: Machine drivers call these helpers after `sof_board_helpers` creates an amp link. Runtime hw_params configures clocks and channel maps for each active amp.

State and persistence: Static arrays hold component and prefix mapping data and are filled at runtime from ACPI. No persistent storage exists.

Dependencies: ASoC DAPM, SOF BCLK query, Cirrus codec DAI/component clock APIs, and ACPI device enumeration.

Risks: ACPI UID mapping is strict; missing physical nodes return zero codecs. Only two or four amps are expected, but an invalid count only warns before link setup uses that value. Test signals include ACPI enumeration logs, codec prefixes, per-amp channel routing, BCLK-derived sysclk, and playback on all speaker positions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_cirrus_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_cirrus_common.h -->
# sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_cirrus_common.h

Purpose: Header for Intel SOF Cirrus Logic amplifier helpers.

Important APIs, types, and functions: It defines CS35L41 DAI and component-name constants, including `CS35L41_CODEC_DAI` and ACPI-derived `CS35L41_DEV0_NAME` through `CS35L41_DEV3_NAME`. It declares `cs35l41_set_dai_link()` for patching a speaker amplifier DAI link and `cs35l41_set_codec_conf()` for assigning card-level codec prefixes.

Control flow and integration: Machine drivers such as `sof_ssp_amp.c` include this header after `sof_board_helpers` creates an amp link. The helper implementation then fills the generated link with the correct codec component array, init callback, and stream ops.

State and persistence: No state is defined here; the implementation owns static arrays.

Dependencies: ASoC and Intel ACPI SSP codec identifiers.

Risks: Header constants must stay aligned with codec-driver DAI names and ACPI HID definitions. Test signals are compile/link namespace coverage and successful card creation on two-amp and four-amp Cirrus systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_cirrus_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_cs42l42.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_cs42l42.c

Purpose: SOF machine driver for Intel platforms with a Cirrus CS42L42 headset codec and optional Maxim MAX98357A/MAX98360A speaker amplifier.

Important APIs, types, and functions: `sof_cs42l42_init()` creates headset jack pins, maps four buttons to input keys, and registers the jack with the codec component. `sof_cs42l42_exit()` clears jack state. `sof_cs42l42_hw_params()` derives BCLK via `sof_dai_get_bclk()` and programs codec sysclk. `sof_card_dai_links_create()` calls the common board helper, then patches the headset codec link with `cs42l42_component`, init/exit callbacks, and ops; it patches the amp link through Maxim helpers. The `GLK_LINK_ORDER` override handles Gemini Lake topology order.

Control flow and integration: Probe applies platform id quirks, gets a shared SOF context, reduces GLK DMIC links to one and overrides link order when necessary, sets iDisp codec presence, builds links, fixes platform names, binds drvdata, and registers the static card.

State and persistence: Uses static card and component arrays plus devm-managed `sof_card_private`. No persistent state.

Dependencies: SOF board helpers, CS42L42 codec component, Maxim common helpers, ASoC jack/input APIs, and ACPI mach params.

Risks: Platform id names include `cs4242` spellings while the codec is CS42L42, so matching depends on existing platform-device ids. Only two Maxim amp types are accepted. Test signals include jack/button events, sysclk setup from topology BCLK, GLK/JSL/ADL/RPL/MTL link order, optional HDMI controls, and speaker playback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_cs42l42.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_da7219.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_da7219.c

Purpose: SOF machine driver for Intel platforms with a Dialog DA7219 headset codec and optional Maxim speaker amplifiers.

Important APIs, types, and functions: Driver-specific quirk bits identify GLK/CML/JSL boards and MCLK availability. `platform_clock_control()` starts/stops DA7219 PLL SRM mode through a DAPM supply unless PLL bypass is active. `da7219_codec_init()` obtains topology MCLK, sets codec sysclk, optionally uses PLL bypass for 12.288/24.576 MHz MCLK, creates headset/lineout jack pins and button mappings, and registers the jack callback. `card_late_probe()` disables MAX98373 speaker pins after boot and delegates HDMI control setup. `sof_card_dai_links_create()` uses common board helper links and attaches DA7219 plus supported Maxim amp helpers.

Control flow and integration: Probe decodes platform id quirks, detects iDisp, applies board-specific link-order overrides and legacy card names, enables DA7219 MCLK policy, creates links, sets amp codec_conf, fixes platform names, binds context, and registers the card.

State and persistence: State is in `sof_card_private`, especially `da7219.mclk_en` and `da7219.pll_bypass`. Card name and link order are changed per probe. No persistence exists.

Dependencies: DA7219 codec APIs, SOF board helpers, Maxim helpers, SOF topology clock metadata, ASoC DAPM/jack, and ACPI platform data.

Risks: PLL bypass requires topology MCLK to match expected frequencies. DAPM clock callback depends on `DIALOG_CODEC_DAI` lookup. Link-order/card-name compatibility with old topologies is sensitive. Test signals include MCLK/PLL modes, headset and lineout detection, speaker amp DAPM, HDMI controls, and all platform id variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_da7219.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_es8336.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_es8336.c

Purpose: SOF machine driver for Intel platforms using Everest ESSX8336/ES8316/ES8326 style codecs, optional DMICs, HDMI playback, HDMI capture SSPs, and board-specific speaker/headphone GPIO quirks.

Important APIs, types, and functions: Quirk macros encode codec SSP, speaker GPIO selection, DMIC, inverted jack detect, headphone GPIO, headset mic port, and HDMI capture SSPs. `struct sof_es8336_private` stores codec device, speaker/headphone GPIOs, jack, HDMI list, speaker state, and delayed pop-suppression work. `sof_es8316_init()` configures mic routing, creates the headset jack, and registers the codec jack. `sof_es8316_speaker_power_event()` and `pcm_pop_work_events()` coordinate delayed GPIO toggling for speaker/headphone mux behavior. `sof_8336_trigger()` mitigates pop noise on playback stop. `sof_card_dai_links_create()` dynamically builds codec, DMIC, HDMI playback, and optional HDMI capture links.

Control flow and integration: Probe combines platform driver_data, DMI quirks, NHLT-derived SSP info, DMIC counts, and module `quirk` override. It resolves the ACPI codec device, fixes component and DAI names, adds a software node for inverted jack detect, maps ACPI GPIOs according to quirk bits, initializes work/list state, sets component strings, and registers the card. Remove cancels work, releases GPIOs, removes the software node, and drops the codec device reference.

State and persistence: Mutable module-global `quirk`, static card/link fields, devm private data, manually acquired GPIO/device references, and a delayed work item. No disk persistence.

Dependencies: ASoC, HDA DSP HDMI helper, ACPI/DMI, GPIO consumer and ACPI GPIO mapping, software nodes, input jack APIs, and topology platform naming.

Risks: The module quirk override can produce topology-incompatible SSP/DMIC selections. Manual `gpiod_get_optional()` resources require remove/error cleanup. Late HDMI probe assumes HDMI list exists. Test signals include DMI/module quirk logs, GPIO polarity/mux behavior, pop-noise regression, jack detect including inverted property, DMIC/HDMI/HDMI-in link counts, ES8326 DAI-name fixup, and remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_es8336.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_hdmi_common.h -->
# sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_hdmi_common.h

Purpose: Minimal shared HDMI-private-data header for Intel SOF board drivers.

Important APIs, types, and functions: It defines `IDISP_CODEC_MASK` as `0x4`, used against ACPI machine `codec_mask` to identify iDisp HDMI codec presence. `struct sof_hdmi_private` stores the HDMI codec ASoC component pointer and an `idisp_codec` boolean.

Control flow and integration: `sof_board_helpers` and SoundWire helper code embed this struct in their private card contexts. HDMI init callbacks store the component, and late-probe callbacks use the boolean and component pointer to decide whether to invoke HDA HDMI control building.

State and persistence: The header defines in-memory fields only. There is no persistence or allocation behavior.

Dependencies: ASoC component definitions.

Risks: Multiple files define or use the same numeric iDisp mask; drift would break HDMI detection. Test signals include compile coverage and HDMI-present/absent card registration paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_hdmi_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_maxim_common.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_maxim_common.c

Purpose: Shared helpers for Intel SOF boards using Maxim speaker amplifiers: MAX98373, MAX98390, MAX98357A, and MAX98360A.

Important APIs, types, and functions: `get_num_codecs()` counts ACPI devices by HID. MAX98373 support adds left/right speaker widgets/routes, reads `maxim,vmon-slot-no` and `maxim,imon-slot-no` properties to create TX masks, validates TDM slot usage from `sof_dai_get_tdm_slots()`, and enables/disables DAPM speaker pins in `max_98373_trigger()`. MAX98390 support handles two or four amps, woofer/tweeter widgets, fixed four-slot TDM masks, and CML-specific codec prefix ordering. MAX98357A/MAX98360A helpers attach a single simple amplifier component with common DAPM speaker controls.

Control flow and integration: Board drivers call `max_98373_dai_link()`, `max_98390_dai_link()`, `max_98357a_dai_link()`, or `max_98360a_dai_link()` to patch an amp link. Card-level codec prefix helpers are called separately for multi-amp devices.

State and persistence: Static component and codec_conf arrays encode ACPI component names and prefixes. Runtime state is limited to DAPM pin changes and ACPI property reads.

Dependencies: ASoC DAPM/DAI APIs, SOF topology helpers for TDM slots, ACPI device enumeration/properties, Intel SoC quirks for CML detection.

Risks: Unsupported amp counts are logged and can leave incomplete link config. TX masks must not overlap and must fit topology TDM slots. DAPM trigger logic assumes component name prefixes match pin names. Test signals include two-amp/four-amp card prefix layout, TDM mask validation, IV-sense capture, speaker pin enable behavior, and simple amplifier playback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_maxim_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_maxim_common.h -->
# sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_maxim_common.h

Purpose: Header exposing Maxim amplifier constants and helper entry points for Intel SOF board drivers.

Important APIs, types, and functions: It defines codec DAI names and ACPI-derived device names for MAX98373, MAX98390, MAX98357A, and MAX98360A. It declares link patch helpers (`max_98373_dai_link()`, `max_98390_dai_link()`, `max_98357a_dai_link()`, `max_98360a_dai_link()`) and codec-conf helpers for multi-amp prefix setup.

Control flow and integration: Machine drivers call these helpers after the common board helper creates an amp DAI link, selecting the helper by detected `enum snd_soc_acpi_intel_codec` amp type.

State and persistence: No mutable state is declared in the header.

Dependencies: ASoC and Intel ACPI SSP codec identifiers.

Risks: DAI names and ACPI component names must match codec drivers and firmware descriptions. Test signals include compile-time API use across board drivers and runtime detection of each supported Maxim amp family.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_maxim_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_nau8825.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_nau8825.c

Purpose: SOF machine driver for Intel platforms with a Nuvoton NAU8825 headset codec and optional RT1019P, RT1015P, MAX98360A, MAX98373, or NAU8318 speaker amps.

Important APIs, types, and functions: `sof_nau8825_codec_init()` creates a headset jack with four buttons, maps input keys, and calls `snd_soc_component_set_jack()`. `sof_nau8825_hw_params()` obtains topology BCLK, selects NAU8825 FLL BCLK clocking, and sets PLL output to sample_rate * 256. `sof_card_late_probe()` disables MAX98373 speaker pins after boot and then delegates HDMI control setup. `sof_card_dai_links_create()` builds common links and patches the headset codec and selected amp link.

Control flow and integration: Probe applies board id quirks, creates a shared SOF context, marks iDisp presence from ACPI, builds/paches links, installs codec_conf for MAX98373 or no-op amp families, fixes platform names, stores drvdata, and registers the card.

State and persistence: Uses static card/component data and devm `sof_card_private` state. No persistent storage.

Dependencies: NAU8825 codec, SOF board helpers, Realtek/Maxim/Nuvoton amp helpers, ASoC jack/input, and ACPI mach params.

Risks: Only selected amp types are accepted. BCLK must be present in topology or hw_params fails. Speaker DAPM disabling is MAX98373-specific. Test signals include jack/button behavior, FLL/PLL setup, all platform id quirk combinations, optional BT/HDMI links, and amp-specific playback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_nau8825.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_nuvoton_common.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_nuvoton_common.c

Purpose: Shared helper for Intel SOF boards using a Nuvoton NAU8318 speaker amplifier.

Important APIs, types, and functions: The file defines one speaker pin control, one `Spk` widget, a route from `Spk` to codec `Speaker`, and a component array for `NAU8318_DEV0_NAME`/`NAU8318_CODEC_DAI`. `nau8318_init()` adds DAPM widgets, card controls, and routes with error reporting. `nau8318_set_dai_link()` patches a generated amp DAI link with the NAU8318 component array and init callback.

Control flow and integration: A machine driver such as `sof_nau8825.c` selects this helper based on detected amp type after common board-link generation.

State and persistence: Static component and DAPM tables only. No persistent state.

Dependencies: ASoC DAPM/card-control APIs and SOF/Nuvoton header constants.

Risks: The header uses `nau8315-hifi` as the codec DAI for NAU8318, so codec-driver naming must remain compatible. Test signals include successful DAPM route/control creation and speaker playback on NAU8318 boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_nuvoton_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_nuvoton_common.h -->
# sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_nuvoton_common.h

Purpose: Header for Intel SOF Nuvoton amplifier helpers.

Important APIs, types, and functions: It defines `NAU8318_CODEC_DAI` as `nau8315-hifi`, `NAU8318_DEV0_NAME` from the ACPI HID, and declares `nau8318_set_dai_link()`.

Control flow and integration: Machine drivers include this header and call `nau8318_set_dai_link()` when `snd_soc_acpi_intel_detect_amp_type()` reports NAU8318.

State and persistence: No state. The implementation owns static link component data.

Dependencies: ASoC and Intel ACPI SSP codec identifiers.

Risks: Codec DAI aliasing across NAU8315/NAU8318 names must remain valid. Test signals include build coverage and runtime link binding to the Nuvoton codec component.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_nuvoton_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_pcm512x.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_pcm512x.c

Purpose: SOF machine driver for Intel UP/UP2-style boards using a TI PCM512x codec, such as Hifiberry DAC+ HATs, with optional DMIC and HDMI links on non-legacy CPUs.

Important APIs, types, and functions: Quirk bits select SSP port, optional SSP capture, and DMIC enablement. DMI callback overrides quirks for UP-CHT01. `sof_pcm512x_codec_init()`, `aif1_startup()`, and `aif1_shutdown()` program PCM512x GPIO registers to control amplifier/output state. `sof_card_dai_links_create()` manually creates the SSP codec link, optional DMIC links, and optional HDMI links, using `ssp%d-port` for BYT/CHT and `SSP%d Pin` otherwise. HDMI init records codec DAIs for late HDMI control setup.

Control flow and integration: Probe decides legacy versus newer CPU behavior, applies DMI quirks, computes link count, creates links, initializes the HDMI list, fixes platform names, stores drvdata, and registers the card. Remove clears component jack state for the codec.

State and persistence: Module-global quirk and `is_legacy_cpu`, static card data, and devm private HDMI list state. No persistent storage.

Dependencies: PCM512x codec registers, HDA DSP HDMI helper, ACPI/DMI, Intel SoC quirks, ASoC DAPM/DAI, and SOF/HDA platform names.

Risks: HDMI late-probe returns `-EINVAL` if expected HDMI list is empty on non-legacy systems. Manual link generation duplicates patterns from newer helpers and can drift. GPIO register bit assumptions are board-specific. Test signals include UP/UP2 DMI behavior, legacy no-HDMI/no-DMIC path, SSP capture enablement, PCM512x GPIO toggles across playback, DMIC capture, HDMI controls, and platform-name fixup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_pcm512x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_realtek_common.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_realtek_common.c

Purpose: Shared Realtek speaker amplifier helpers for Intel SOF machine drivers, covering RT1011, RT1015P, RT1015, RT1308, and RT1019P.

Important APIs, types, and functions: Common two-speaker and four-speaker widgets/controls are reused across amps. `get_num_codecs()` counts ACPI devices by HID. RT1011 support programs PLL/sysclk from BCLK, sets four-slot TDM masks, and uses different prefix/widget behavior for CML compatibility. RT1015 support obtains BCLK, sets PLL/sysclk, and applies four-slot TDM RX masks. RT1308 support derives MCLK from topology, sets PLL/sysclk to rate*512, and exposes one stereo speaker widget. RT1015P and RT1019P are simpler auto-mode helpers with one component and two speaker routes.

Control flow and integration: Machine drivers choose helper functions to patch generated amp links and, where needed, call codec_conf helpers to install name prefixes. Runtime hw_params configures clocks/TDM slots per codec family.

State and persistence: Static component, route, ops, and codec_conf arrays. Runtime state is limited to codec clock/TDM programming.

Dependencies: Realtek codec headers, SOF topology BCLK/MCLK helpers, ASoC DAPM/DAI, ACPI enumeration, and Intel CML detection.

Risks: Multi-amp layouts depend on ACPI instance counts and fixed component order. TDM masks must match topology and amplifier wiring. CML compatibility prefixes are special cases. Test signals include each amp family, two/four RT1011 counts, TDM slot validation, IV/feedback capture where applicable, and DAPM route/control creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_realtek_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_realtek_common.h -->
# sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_realtek_common.h

Purpose: Header exposing Realtek amplifier DAI names, component names, and link helper APIs for Intel SOF board drivers.

Important APIs, types, and functions: It defines constants for RT1011, RT1015P, RT1015, RT1308, and RT1019P codec DAI names and ACPI-derived device names. It declares DAI-link patch helpers and codec-conf helpers for families needing card-level name prefixes.

Control flow and integration: Machine drivers include this header and switch on detected codec/amp type, using these functions to fill `ctx->amp_link` after common board-link allocation.

State and persistence: No mutable state is declared here.

Dependencies: ASoC and Intel ACPI SSP common codec IDs.

Risks: Component strings and DAI names are cross-file contracts with codec drivers and ACPI match tables. Test signals include compile coverage across all Realtek amp users and runtime link binding for each codec family.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_realtek_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_rt5682.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_rt5682.c

Purpose: Broad SOF machine driver for Intel platforms with Realtek RT5682, RT5682S, or RT5650 headset codecs and many optional speaker amp families.

Important APIs, types, and functions: Quirk bits include MCLK enable and common board-helper SSP/amp/BT/HDMI fields. DMI and module parameters can override quirks. `sof_rt5682_codec_init()` handles optional legacy PMC MCLK setup, enables ASRC for 24 MHz MCLK on supported codecs, creates headset jacks, and registers codec jack callbacks. `sof_rt5682_hw_params()` chooses PLL source from MCLK or BCLK, handles RT5682S PLL1/PLL2 selection, sets sysclk, and configures two-slot TDM. `sof_card_dai_links_create()` patches headset codec links for RT5650/RT5682/RT5682S and amp links for Maxim, Realtek, RT5650 AIF2, and TI TAS2563.

Control flow and integration: Probe combines platform id, DMI, and module quirks; gets common context; handles RT5650 card-name/speaker-link special case; adjusts legacy BYT/CHT and GLK behavior; acquires/enables PMC MCLK for legacy systems; creates links; installs amp codec_conf; fixes platform names; and registers the card.

State and persistence: Module-global quirk, static card/component arrays, devm context, optional clock handle, and jack state. No persistent storage.

Dependencies: SOF board helpers, Realtek headset codec APIs, Realtek/Maxim/TI amp helpers, common clock framework, ASoC jack/input, SOF topology clock metadata, DMI, and Intel SoC quirks.

Risks: Clock path selection is complex and codec-specific. Legacy MCLK is enabled in probe and hw_params and must be balanced by platform lifetime behavior. Module quirk override can create topology mismatches. Test signals include all headset codec variants, MCLK and BCLK PLL paths, RT5682S high-rate cases, jack/button events, amp family playback, HDMI/BT links, legacy no-DMIC/no-HDMI behavior, and suspend/resume audio noise regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_rt5682.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_sdw.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_sdw.c

Purpose: Generic SOF SoundWire machine driver for Intel platforms. It dynamically creates DAI links from ACPI SoundWire endpoint descriptions and augments them with SSP, PCH DMIC, iDisp HDMI, BT offload, and echo-reference links.

Important APIs, types, and functions: Module/DMI/SSID quirks encode jack source, HDMI generation, PCH DMIC, SSP ports, BT offload, sidecar amps, codec speaker/mic policy, and deprecated flags. `create_sdw_dailink()` creates playback/capture links per parsed SoundWire dailink, builds CPU pins and codec components, fills channel maps, adds codec_conf prefixes and sidecar devices, and invokes codec-specific init callbacks. `create_sdw_dailinks()`, `create_ssp_dailinks()`, `create_dmic_dailinks()`, `create_hdmi_dailinks()`, `create_bt_dailinks()`, and `create_echoref_dailink()` synthesize all BE classes. `sof_card_dai_links_create()` parses endpoints through SoundWire utility APIs, counts links/configs/aux devices, allocates card arrays, and builds the full topology. `mc_probe()` builds the card context, applies quirks, resets amp counters, registers the card, and wires cleanup.

Control flow and integration: Probe sets up `asoc_sdw_mc_private` with an Intel-private context, applies PCI SSID and DMI quirks, then delegates to dynamic link creation. Late probe runs generic SoundWire late-probe and HDMI control setup. `add_dai_link` ignores HDMI FE PCMs when iDisp is absent. Remove calls the SoundWire dailink exit loop.

State and persistence: State includes module-global `sof_sdw_quirk`, card context, Intel HDMI/pin-index state, dynamically allocated parsed endpoint arrays freed before return, and devm-managed card arrays. No disk persistence.

Dependencies: `sound/soc_sdw_utils`, SoundWire ACPI metadata, HDA DSP HDMI helper, ASoC, DMI/PCI quirk tables, RT711 jack quirk constants, and SOF topologies expecting generated BE ids.

Risks: This file has a large and evolving quirk matrix. Deprecated quirks log errors but do not implement old behavior. Endpoint parsing and BE id assignment must match topology expectations. HDMI link count is always added to link allocation even if iDisp is absent, with FE ignore used later. Test signals include endpoint parsing on all supported codec mixes, sidecar amp/mic policies, PCH versus SDW DMIC conflict warnings, HDMI controls, BT offload, echo reference link presence, amp count component strings, and cleanup on registration failure/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_sdw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_sdw_common.h -->
# sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_sdw_common.h

Purpose: Shared definitions for the Intel SOF SoundWire machine driver and its HDMI helper.

Important APIs, types, and functions: The header defines HDMI counts, CPU DAI limits, SoundWire bidirectional PDI base, group count, I2S SSP bit masks, deprecated compatibility quirk bits, BT offload quirk encoding, and `struct intel_mc_ctx`. The private context stores `struct sof_hdmi_private` and per-SoundWire-link pin indices. It declares `sof_sdw_hdmi_init()` and `sof_sdw_hdmi_card_late_probe()`.

Control flow and integration: `sof_sdw.c` embeds `intel_mc_ctx` in `asoc_sdw_mc_private->private`; link creation increments `sdw_pin_index` to name SDW CPU pins, while HDMI callbacks use the embedded HDMI state.

State and persistence: Defines in-memory context layout only. No persistent state.

Dependencies: Linux bits/types, ASoC, SoundWire utility interfaces, and shared SOF HDMI private data.

Risks: Quirk bit definitions must not collide with SoundWire utility quirk bits. Deprecated flags still appear in logs and quirk tables, so new behavior must not accidentally rely on removed semantics. Test signals include build coverage and correct pin numbering across multi-link SoundWire cards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_sdw_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_sdw_hdmi.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_sdw_hdmi.c

Purpose: HDMI helper implementation for the generic Intel SOF SoundWire machine driver.

Important APIs, types, and functions: `sof_sdw_hdmi_init()` obtains the SoundWire machine private context, casts its Intel-private payload, and stores the HDMI codec component from the runtime codec DAI. `sof_sdw_hdmi_card_late_probe()` checks `idisp_codec` and the stored component, then calls `hda_dsp_hdmi_build_controls()`.

Control flow and integration: `sof_sdw.c` installs `sof_sdw_hdmi_init()` on the first iDisp HDMI BE link and invokes `sof_sdw_hdmi_card_late_probe()` from its card late-probe path after generic SoundWire late probe succeeds.

State and persistence: It mutates only `intel_ctx->hdmi.hdmi_comp`; no allocation or persistence exists.

Dependencies: ASoC runtime helpers, `asoc_sdw_mc_private`, shared SoundWire context definitions, and HDA DSP HDMI control helper.

Risks: If the first HDMI BE does not initialize or iDisp is absent, HDMI control creation must be skipped or return `-EINVAL` as appropriate. Test signals include HDMI controls on SoundWire+iDisp systems and successful registration without HDMI codec.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_sdw_hdmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_ssp_amp.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_ssp_amp.c

Purpose: SOF machine driver for Intel designs centered on SSP-connected speaker amplifiers, including RT1308 and CS35L41, with optional HDMI capture, HDMI playback, DMIC, and BT offload.

Important APIs, types, and functions: Quirk bit `SOF_HDMI_PLAYBACK_PRESENT` controls iDisp HDMI playback. `SSP_AMP_LINK_ORDER` and `SSP_AMP_LINK_IDS` define topology-compatible ordering and fixed BE ids for HDMI-in capable topologies. `sof_card_dai_links_create()` uses the common board helper and patches the amp link for CS35L41 or RT1308. `sof_ssp_amp_probe()` applies platform id quirks, disables PCH DMIC on non-Chromebook systems with no ACPI DMIC count, controls HDMI playback presence, installs fixed ids when HDMI-in SSP mask is present, updates codec_conf, fixes platform names, and registers the card.

Control flow and integration: The driver is a policy wrapper around `sof_board_helpers.c` and amplifier helper modules. Platform ids describe generic amp-only systems, RT1308 HDMI-in systems, CS35L41 systems, and LT6911 HDMI capture designs across Intel generations.

State and persistence: Module-global quirk and devm `sof_card_private`. Static card data. No persistent storage.

Dependencies: SOF board helpers, Realtek and Cirrus amp helpers, DMI Chromebook detection, ACPI mach params, ASoC PM ops.

Risks: Fixed BE ids must match topology files. DMIC suppression policy differs for Chromebooks. HDMI-in masks can create multiple capture SSP links. Test signals include RT1308 and CS35L41 playback, HDMI capture on specified SSP ports, HDMI playback presence/absence, BT offload, DMIC policy, and card component prefixes for CS35L41.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_ssp_amp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_ti_common.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_ti_common.c

Purpose: Shared helper for Intel SOF boards using Texas Instruments TAS2563 speaker devices.

Important APIs, types, and functions: The file defines a single `Spk` pin switch, speaker widget, and route from `Spk` to codec `OUT`. TAS2563 uses one mounted device to manage multiple physical devices, so the helper exposes one component array entry. `tas2563_init()` adds DAPM widgets, card controls, and routes. `sof_tas2563_dai_link()` patches a generated amp link with the TAS2563 component array and init callback.

Control flow and integration: `sof_rt5682.c` uses this helper when the detected amp type is `CODEC_TAS2563`.

State and persistence: Static DAPM/control/component arrays only. No persistent state.

Dependencies: ASoC DAPM APIs and TI codec ACPI/DAI constants.

Risks: The one-component design relies on the TAS2563 codec driver managing multi-device hardware behind a single component. Test signals include card-control creation and speaker playback on TAS2563 platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_ti_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_ti_common.h -->
# sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_ti_common.h

Purpose: Header for Intel SOF Texas Instruments amplifier helpers.

Important APIs, types, and functions: It defines `TAS2563_CODEC_DAI`, `TAS2563_DEV0_NAME`, and declares `sof_tas2563_dai_link()`.

Control flow and integration: Machine drivers include this header and call the helper when ACPI codec detection reports `CODEC_TAS2563`.

State and persistence: No state is declared.

Dependencies: ASoC and Intel ACPI SSP codec identifiers.

Risks: The DAI/component names must remain aligned with the TI codec driver and firmware. Test signals are compile coverage and successful link binding on TAS2563 systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_ti_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_wm8804.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_wm8804.c

Purpose: SOF machine driver for UP/UP2 boards using WM8804/Hifiberry Digi+ SPDIF hardware on SSP5.

Important APIs, types, and functions: `struct sof_card_private` stores two optional clock-select GPIOs and cached sample rate. DMI quirk `SOF_WM8804_UP2_QUIRK` enables UP2-specific GPIO lookup. `sof_wm8804_hw_params()` computes MCLK frequency/divider from sample rate, selects SPDIF status sampling-frequency bits, toggles 44.1 kHz or 48 kHz oscillator GPIOs, programs WM8804 MCLK divider, PLL, sysclk, and status register. Probe resolves the ACPI codec device name dynamically from `mach->id`, optionally installs a GPIO lookup table and obtains the two GPIOs, sets card drvdata, and registers the one-link card.

Control flow and integration: Static link connects `SSP5 Pin` to `wm8804-spdif`. Runtime hw_params only reprograms when sample rate changes. Remove removes the UP2 GPIO lookup table.

State and persistence: Private cached sample rate and GPIO descriptors are devm-managed except the global lookup table. Static codec name buffer and link component name are mutated at probe. No persistent state.

Dependencies: WM8804 codec APIs/registers, ACPI device lookup, DMI, GPIO lookup/consumer APIs, ASoC DAI ops, and PM ops.

Risks: GPIO lookup uses platform-specific ACPI GPIO controller indices and is mandatory on UP2 quirk systems. Unsupported sample rates fail. Codec-name mutation is static. Test signals include 44.1/48 kHz family oscillator switching, SPDIF sample-rate status bits, all supported rates through 192 kHz, ACPI codec name fixup, and GPIO cleanup on remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_wm8804.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/catpt/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/intel/catpt/Makefile

Purpose: Kbuild fragment for the Intel CATPT ASoC driver object.

Important APIs, types, and functions: It defines `snd-soc-catpt-y` as the object list `device.o dsp.o loader.o ipc.o messages.o pcm.o sysfs.o`, adds `CFLAGS_device.o := -I$(src)` so `define_trace.h` can locate the trace header relative to the source directory, and builds `snd-soc-catpt.o` when `CONFIG_SND_SOC_INTEL_CATPT` is enabled.

Control flow and integration: Kernel Kbuild includes this Makefile from the Intel ASoC subtree. The composite object links the CATPT driver modules into one loadable/built-in object controlled by the Kconfig symbol.

State and persistence: Build metadata only. No runtime state.

Dependencies: Kbuild composite object syntax, the listed CATPT source files, and `CONFIG_SND_SOC_INTEL_CATPT`.

Risks: Missing `-I$(src)` can break trace header inclusion in `device.o`. Object list omissions cause link-time or runtime feature gaps. Test signals include kernel build with CATPT enabled as module and built-in, trace header compilation, and expected `snd-soc-catpt` object contents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/catpt/Makefile -->
