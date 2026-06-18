# subset-b-006511 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/board_selection.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/board_selection.c

Purpose: AVS board enumeration for the Intel cAVS/AVS PCI driver. It translates detected firmware/hardware capabilities, NHLT endpoints, ACPI codec IDs, DMI quirks, HDA codec discovery, and module parameters into platform devices for ASoC machine drivers and AVS CPU components.

Important APIs, types, and data: exports `avs_register_all_boards()` and `avs_unregister_all_boards()`. The file builds arrays of `struct snd_soc_acpi_mach` for SKL/KBL/APL/GLK/CNL/ICL/TGL/MBL-class platforms, using `.id`, `.uid`, `.drv_name`, `.mach_params.i2s_link_mask`, optional `.machine_quirk`, optional `.pdata` TDM masks, and topology filenames. `struct avs_acpi_boards` maps PCI device IDs to those arrays. Module parameters are `i2s_test` and `obsolete_card_names`; the latter is copied into `struct avs_mach_pdata`.

Control flow: `avs_register_all_boards()` conditionally registers a probe board when debugfs is enabled, then DMIC, I2S test boards from the module parameter, ACPI/NHLT-driven I2S boards, and finally one HDAudio board per probed HDA codec. `avs_register_board()` uses `platform_device_register_data()` and registers a devm cleanup action so platform devices are removed with the AVS PCI device. `avs_register_board_pdata()` allocates AVS-specific platform data, attaches codec/TDM/card-name metadata to the ACPI machine descriptor, and passes a copied machine object as platform data to the board driver.

State and persistence: board platform devices are transient kernel devices tied to the AVS device lifetime by devm actions. `mach->pdata` is mutated before registration, so static `snd_soc_acpi_mach` entries are shared state; this is acceptable for a single AVS controller path but worth noticing for re-probe and concurrent assumptions. Firmware topology filename selection is persisted in the platform data consumed by later ASoC registration.

Dependencies and integration points: depends on ACPI NHLT (`acpi_nhlt_find_endpoint()`), ACPI codec presence (`acpi_dev_present()`), HDA codec lists, DMI matching, `avs_register_*_component()` from the PCM/probe layers, and board modules with platform names such as `avs_rt286`, `avs_dmic`, and `avs_hdaudio`. Topology names must match firmware topology files and backend DAI names used by board drivers.

Risks: stale or missing ACPI/DMI entries can select the wrong codec driver or topology. `i2s_test` parsing allocates an integer array and rejects more SSPs than hardware reports, but invalid TDM masks can still create multiple loopback boards. Several static machine entries carry compound-literal pdata/TDM arrays, so lifetime is static but mutation of `.pdata` later can obscure original defaults. HDA/DMIC/I2S registration warns but generally continues, so partial cards are expected on mixed endpoint systems.

Test signals: boot logs for "enumerate ... endpoints failed", visible platform devices/cards for each endpoint, topology filename loading, `i2s_test=` loopback card creation, DMI-specific KBL/KBL-R RT286/RT298 selection, and ACPI NHLT systems with no endpoints returning quietly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/board_selection.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/Kconfig -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/Kconfig

Purpose: Kconfig menu for Intel AVS ASoC machine drivers. It exposes per-board tristate options and the compatibility option for obsolete card names.

Important APIs, types, and functions: no C APIs are defined. Symbols include `SND_SOC_INTEL_AVS_CARDNAME_OBSOLETE` and `SND_SOC_INTEL_AVS_MACH_*` entries for DA7219, DMIC, ES8336, HDAudio, I2S test, MAX98927/MAX98357A/MAX98373, NAU8825, PCM3168A, PROBE, RT274/RT286/RT298/RT5514/RT5640/RT5663/RT5682, and SSM4567.

Control flow: each machine driver is selectable only when `SND_SOC_INTEL_AVS` is enabled. I2C-based codecs depend on `I2C` and `MFD_INTEL_LPSS || COMPILE_TEST`; codec symbols are selected so the matching codec driver is available. Debug probe support depends on `DEBUG_FS` and selects `SND_HWDEP`.

State and persistence: configuration choices persist in the built kernel/module set. `SND_SOC_INTEL_AVS_CARDNAME_OBSOLETE` influences runtime behavior through the global `obsolete_card_names` module parameter default in `board_selection.c`.

Dependencies and integration points: integrates kernel build selection with `boards/Makefile` object names and with platform devices created by `board_selection.c`. The selected codec symbols must match codec component names hard-coded in the board source files.

Risks: missing a machine config causes board platform devices to have no binding driver even if ACPI detects the endpoint. `select` pulls codecs but dependency coverage is still board-specific; unusual test builds rely on `COMPILE_TEST`. Obsolete card naming helps userspace UCM compatibility but risks diverging from new long names.

Test signals: `scripts/config` or `.config` contains expected `SND_SOC_INTEL_AVS_MACH_*` values, `modinfo` shows generated modules, and a detected endpoint binds to a matching platform driver instead of remaining unbound.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/Makefile

Purpose: build glue for Intel AVS machine driver modules.

Important APIs, types, and functions: defines per-module object variables such as `snd-soc-avs-da7219-y := da7219.o` and maps Kconfig symbols to module objects through `obj-$(CONFIG_SND_SOC_INTEL_AVS_MACH_*)`.

Control flow: Kbuild includes each module object only when its corresponding Kconfig symbol is enabled. Each source currently builds as a single-object module with the `snd-soc-avs-*` module name.

State and persistence: no runtime state. The persistent output is kernel objects/modules named according to the Makefile variables.

Dependencies and integration points: must stay aligned with `boards/Kconfig`, platform driver names inside each `.c` file, and platform devices registered by `board_selection.c`.

Risks: adding a board only in `Kconfig` or only in this Makefile silently prevents the expected module from building. Case sensitivity matters for `MAX98357A` Kconfig versus `snd-soc-avs-max98357a` object naming.

Test signals: `make M=sound/soc/intel/avs/boards` builds the expected modules, and enabled configs produce matching `snd-soc-avs-*.ko` artifacts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/da7219.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/da7219.c

Purpose: ASoC machine driver binding AVS SSP/I2S CPU DAIs to a Dialog DA7219 headset codec.

Important APIs, types, and functions: platform driver `avs_da7219`; probe `avs_da7219_probe()`; link factory `avs_create_dai_link()`; codec hooks `avs_da7219_codec_init()` and `avs_da7219_codec_exit()`; BE fixup `avs_da7219_be_fixup()`; DAPM clock event `platform_clock_control()`.

Control flow: probe obtains `snd_soc_acpi_mach` and `avs_mach_pdata`, validates a singular SSP/TDM slot through `avs_mach_get_ssp_tdm()`, builds a backend link named from `AVS_STRING_FMT()`, allocates a card and jack, sets card names based on obsolete-name policy, installs controls/widgets/routes, and registers a deferrable card. Codec init sets DA7219 sysclk to 19.2 MHz on APL or 24.576 MHz on KBL, creates headset jack pins/buttons, and connects the jack to the codec component. DAPM "Platform Clock" starts/stops codec PLL around active routes.

State and persistence: `snd_soc_jack` is card drvdata and lives with devm allocations. The DAI link hard-codes codec component `i2c-DLGS7219:00` and codec DAI `da7219-hifi`. BE params are forced to 48 kHz, stereo, S24_LE.

Dependencies and integration points: depends on `SND_SOC_DA7219`, ACPI ID `DLGS7219`, topology `da7219-tplg.bin`, AVS I2S component DAI name `SSP<n>[:tdm] Pin`, and codec clock definitions from `da7219.h`.

Risks: duplicated assignment to `dl->name` is harmless but confusing. Clock-rate selection relies on `soc_intel_is_apl()` with KBL as the fallback. Wrong TDM platform data or topology backend naming prevents link binding. Jack cleanup depends on `exit` being called.

Test signals: card "AVS I2S DA7219" or legacy `avs_da7219`, headset button events, route power causing PLL changes, and hw_params constrained to 48 kHz stereo S24_LE on the backend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/da7219.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/dmic.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/dmic.c

Purpose: generic AVS DMIC machine driver for Intel PCH digital microphone endpoints.

Important APIs, types, and functions: platform driver `avs_dmic`; `avs_dmic_probe()`; `avs_create_dai_links()`; DAI definitions for `DMIC Pin` and `DMIC WoV Pin`.

Control flow: board selection first creates a `dmic-codec` platform device and passes its device name in `avs_mach_pdata.codec_name`. Probe creates two capture-only backend links sharing the DMIC codec: normal DMIC and wake-on-voice DMIC. The WoV link sets `ignore_suspend` so it can stay available across suspend. The card then registers with DMIC widget/routes and either modern or obsolete names.

State and persistence: no private runtime state beyond the card and link allocations. The codec name is copied from platform data and must remain stable for component matching.

Dependencies and integration points: depends on `SND_SOC_DMIC`, `avs_register_dmic_component()` CPU DAIs, NHLT PDM endpoint detection, and topology `dmic-tplg.bin`.

Risks: the two links share a single allocated codec component descriptor; that is intentional but means both links assume identical codec endpoint. If board selection fails to create `dmic-codec`, probe cannot bind to a codec. WoV suspend behavior must match firmware topology support.

Test signals: two backend links named `DMIC` and `DMIC WoV`, capture works on the normal path, WoV path survives suspend, and no card is created when NHLT has no PDM endpoint.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/dmic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/es8336.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/es8336.c

Purpose: AVS I2S machine driver for ESS ES8336/ES8316-style codec systems with speaker GPIO power control.

Important APIs, types, and functions: platform driver `avs_es8336`; private `struct avs_card_drvdata` containing jack and GPIO; `avs_es8336_codec_init()`/`exit()`; `avs_es8336_hw_params()`; `avs_es8336_be_fixup()`; suspend/resume jack hooks; DAPM speaker power event.

Control flow: probe validates SSP/TDM, creates a backend link to `i2c-ESSX8336:00` DAI `ES8316 HiFi`, allocates drvdata and card, assigns suspend/resume hooks, DAPM controls/routes, and registers the card. Codec init creates a headset jack, registers ACPI GPIO mapping for `speaker-enable`, obtains an optional GPIO, maps play/pause button, connects the jack, and disables idle bias. DAPM speaker supply toggles the active-low GPIO. `hw_params()` selects 24 MHz sysclk on Kaby Lake and 19.2 MHz otherwise.

State and persistence: private drvdata stores the jack and GPIO descriptor; `codec_exit()` disconnects jack and releases GPIO. Backend params are fixed to 48 kHz, stereo, S24_3LE.

Dependencies and integration points: depends on ACPI ID `ESSX8336`, `SND_SOC_ES8316`, ACPI GPIO resources, CPU VFM identification, topology `es8336-tplg.bin`, and AVS SSP CPU DAIs.

Risks: GPIO mapping failures only warn, but a failing GPIO request aborts probe. The active-low GPIO inversion is subtle and route-dependent. The codec DAI name uses ES8316 naming although the board is exposed as ES8336, so codec driver naming must match.

Test signals: speaker power follows DAPM route activation, jack detection is restored after resume, KBL versus non-KBL sysclk selection appears in codec configuration, and backend format is S24_3LE at 48 kHz stereo.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/es8336.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/hdaudio.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/hdaudio.c

Purpose: generic ASoC machine driver for HDA codecs discovered by the AVS HDA bus, including HDMI/display codecs.

Important APIs, types, and functions: platform driver `avs_hdaudio`; `avs_hdaudio_probe()`; dynamic link creator `avs_create_dai_links()`; probing binder link `probing_link`; `avs_probing_link_init()`; HDMI mapping helpers `avs_card_hdmi_pcm_at()` and `avs_card_late_probe()`.

Control flow: board selection creates one platform device per HDA codec with `avs_mach_pdata.codec`. Probe checks the codec device is still registered, creates a temporary "probing-LINK" against `codec-probing-DAI`, and registers the card. During link init, the codec's `pcm_list_head` is counted and converted into real backend DAI links, one per `hda_pcm`. For display codecs, late probe maps HDA HDMI converter PCMs to topology FE PCMs named with the `HDMI` prefix and then completes codec probing.

State and persistence: `hda_pcm->pcm` and `hda_pcm->device` are updated for HDMI codecs during late probe. Card naming is either legacy `hdaudioB%dD%d` or modern `AVS HDMI`/`AVS HD-Audio`.

Dependencies and integration points: depends on HDA codec core, AVS HDA component registration, topology FE naming convention (`HDMI%d`), codec PCM list population, and display power/i915 integration from the core driver.

Risks: dynamic `snd_soc_add_pcm_runtimes()` depends on codec PCM list stability. HDMI topology indexing is 1-based and string parsed; missing topology PCMs produce warnings and invalid devices. Codec removal before deferred card probe is explicitly handled with `-ENODEV`.

Test signals: HDA codec cards bind after codec configure, HDMI converter mapping logs show converter-to-PCM assignment, missing HDMI topology entries warn, and non-display HDA codecs register as "AVS HD-Audio".
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/hdaudio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/i2s_test.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/i2s_test.c

Purpose: test/loopback machine driver for manually selected AVS SSP/TDM I2S paths.

Important APIs, types, and functions: platform driver `avs_i2s_test`; `avs_i2s_test_probe()`; `avs_create_dai_link()`.

Control flow: board selection parses the `i2s_test=` module parameter, creates one platform device per selected SSP/TDM slot, and sets topology names like `i2s<ssp>[:tdm]-test-tplg.bin`. Probe validates exactly one SSP and one TDM slot, creates a single no-PCM backend link with a dummy codec, chooses either legacy loopback naming or modern "AVS I2S TEST-..." naming, and registers the card.

State and persistence: no persistent private state. The selected SSP/TDM mask is carried in `avs_mach_pdata.tdms` and `mach_params.i2s_link_mask`.

Dependencies and integration points: depends on `avs_register_i2s_component()` CPU DAI creation and firmware/topology support for loopback test paths. It intentionally uses `snd_soc_dummy_dlc` instead of a real codec.

Risks: this bypasses ACPI codec matching, so invalid module parameters can create cards that topology or hardware cannot use. It rejects multi-SSP/multi-TDM cards, matching the one-link implementation.

Test signals: passing `i2s_test=...` creates loopback cards, dummy codec links bind, invalid multi-slot data returns `-EINVAL`, and test topology files load for the requested SSP/TDM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/i2s_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/max98357a.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/max98357a.c

Purpose: AVS I2S machine driver for MAX98357A speaker amplifier boards.

Important APIs, types, and functions: platform driver `avs_max98357a`; `avs_max98357a_probe()`; `avs_create_dai_link()`; `avs_max98357a_be_fixup()`.

Control flow: probe reads AVS machine platform data, validates one SSP/TDM, creates a single playback-only backend link to codec `MX98357A:00` DAI `HiFi`, configures I2S codec-bitclock/frameclock consumer format, and registers a card with a single speaker DAPM route.

State and persistence: no private runtime state. Backend params are forced to 48 kHz, stereo, S16_LE.

Dependencies and integration points: depends on ACPI ID `MX98357A`, `SND_SOC_MAX98357A`, topology `max98357a-tplg.bin`, and AVS I2S CPU component naming.

Risks: hard-coded codec component name lacks `i2c-` prefix unlike many I2C boards, so it must match the codec driver's ACPI-created component name. Playback-only means capture paths are not exposed even if topology attempted them.

Test signals: card "AVS I2S MAX98357A", playback-only backend link, speaker DAPM switch, and 48 kHz stereo S16_LE hardware params.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/max98357a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/max98373.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/max98373.c

Purpose: AVS I2S/TDM stereo amplifier machine driver for two MAX98373 codecs.

Important APIs, types, and functions: platform driver `avs_max98373`; codec conf prefixes for `i2c-MX98373:00` and `:01`; `avs_max98373_hw_params()`; `avs_max98373_be_fixup()`; `avs_create_dai_link()`.

Control flow: probe validates SSP/TDM, builds one backend link with two codec components using DSP_B format, installs left/right codec name prefixes and speaker routes, and registers the card. `hw_params()` assigns TDM slots based on codec component name: right/DEV0 uses mask `0x30`, left/DEV1 uses `0xC0`, with 8 slots of 16 bits.

State and persistence: no private state. Backend params are fixed to 48 kHz, stereo, S16_LE; codec-specific TDM slot settings are pushed at stream setup.

Dependencies and integration points: depends on ACPI ID `MX98373`, two enumerated codec instances, `SND_SOC_MAX98373`, topology `max98373-tplg.bin`, and DSP_B-format SSP backend compatibility.

Risks: both codec instances must exist with exact names. Slot masks encode board wiring; swapping DEV0/DEV1 or prefixes can invert channels. Failure on either codec aborts hw_params.

Test signals: two codec components appear with left/right DAPM prefixes, TDM slot programming succeeds for both devices, and stereo playback routes to both speaker widgets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/max98373.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/max98927.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/max98927.c

Purpose: AVS I2S/TDM stereo amplifier machine driver for two MAX98927 codecs.

Important APIs, types, and functions: platform driver `avs_max98927`; `card_codec_conf`; `avs_max98927_hw_params()`; `avs_max98927_be_fixup()`; `avs_create_dai_link()`.

Control flow: probe creates a one-CPU/two-codec backend link in DSP_B mode. The card adds left/right speaker DAPM controls and codec prefixes. During `hw_params()`, the driver iterates codec DAIs and programs DEV0 with TDM mask `0x30` and DEV1 with `0xC0`.

State and persistence: no private state. Backend params are fixed to 48 kHz stereo S16_LE, and TDM slot configuration is applied per stream setup.

Dependencies and integration points: depends on ACPI ID `MX98927`, codec components `i2c-MX98927:00` and `:01`, `SND_SOC_MAX98927`, and topology `max98927-tplg.bin`.

Risks: exact component names and two-codec enumeration are required. TDM mask errors affect channel routing. The driver returns the first TDM programming error, so a missing codec DAI blocks the stream.

Test signals: successful hw_params logs no TDM errors, DAPM routes `Left/Right Spk` to prefixed `BE_OUT`, and stereo playback uses both amps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/max98927.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/nau8825.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/nau8825.c

Purpose: AVS I2S machine driver for Nuvoton NAU8825 headset codec systems.

Important APIs, types, and functions: platform driver `avs_nau8825`; clock DAPM handler `avs_nau8825_clock_control()`; codec init/exit; BE fixup; trigger op `avs_nau8825_trigger()`; suspend/resume jack hooks.

Control flow: probe validates SSP/TDM, creates a backend link to `i2c-10508825:00` DAI `nau8825-hifi`, allocates jack/card, installs controls/widgets/routes, and registers the card. Codec init creates headset jack pins and button mappings. DAPM platform clock switches codec sysclk between 24 MHz MCLK and internal clock. Trigger start/resume programs FLL based on the runtime sample rate. Resume restores FLL sysclk if playback is still active and reconnects jack detection.

State and persistence: `snd_soc_jack` is stored as card drvdata. Backend params are forced to 48 kHz stereo S24_LE. Codec clock state follows DAPM and stream trigger events.

Dependencies and integration points: depends on ACPI ID `10508825`, `SND_SOC_NAU8825`, topology `nau8825-tplg.bin`, codec clock constants, and AVS SSP DAI naming.

Risks: clock sequencing spans DAPM, trigger, and resume; regressions can break jack detection or playback resume. The resume helper assumes codec DAI exists and checks widget activity before restoring FLL source.

Test signals: headset button events, DAPM clock toggles, trigger start sets FLL to `rate * 256`, suspend/resume keeps jack reporting, and backend params are 48 kHz stereo S24_LE.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/nau8825.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/pcm3168a.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/pcm3168a.c

Purpose: AVS machine driver for PCM3168A codec boards with separate DAC and ADC links.

Important APIs, types, and functions: platform driver `avs_pcm3168a`; DAI definitions for PCM3168A DAC/ADC and CPU `SSP0 Pin`/`SSP2 Pin`; `avs_create_dai_links()`; `avs_pcm3168a_be_fixup()`.

Control flow: probe receives platform data, creates two backend links: `SSP0-Codec-dac` to codec DAI `pcm3168a-dac` and `SSP2-Codec-adc` to `pcm3168a-adc`. Both links share platform data, I2S format, codec bit/frame provider flags, and S24_LE fixup. Card routes expose multiple CPB headphones, line out, microphones, and line in.

State and persistence: no private state. Unlike most single-link boards, this file does not derive SSP ports from `mach->mach_params`; it hard-codes SSP0 for DAC and SSP2 for ADC, matching board selection masks.

Dependencies and integration points: depends on ACPI ID `PCM3168A`, codec `i2c-PCM3168A:00`, `SND_SOC_PCM3168A_I2C`, topology `pcm3168a-tplg.bin`, and AVS CPU DAIs for SSP0/SSP2.

Risks: hard-coded SSP allocation must match board wiring and `board_selection.c`; topology or ACPI changes need coordinated edits. The fixup only constrains format, leaving rate/channel constraints to topology/codec.

Test signals: two backend links bind, DAC playback and ADC capture function independently, S24_LE is accepted, and all CPB DAPM routes are visible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/pcm3168a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/probe.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/probe.c

Purpose: debug/probing machine driver exposing a compress capture DAI for AVS runtime data extraction.

Important APIs, types, and functions: platform driver `avs_probe_mb`; `avs_probe_mb_probe()`; `avs_create_dai_links()`.

Control flow: when debugfs is enabled, board selection registers `avs_probe_mb` and then `avs_register_probe_component()`. Probe creates one DAI link named `Compress Probe Capture` with CPU DAI `Probe Extraction CPU DAI`, dummy codec, platform set to the board device, and registers card "AVS PROBE".

State and persistence: no private state in the board driver. Probe stream state is owned by the AVS probe component/debug layer.

Dependencies and integration points: depends on `CONFIG_DEBUG_FS`, `SND_HWDEP`, probe component registration from `probes.c`, and compress operations used to extract data from firmware probes.

Risks: debug-only feature must not be registered when debugfs is off. A mismatch between CPU DAI name and probe component breaks compress capture binding.

Test signals: card "AVS PROBE" appears under debug builds, compress capture opens on the probe DAI, and `probe_points` debugfs control can connect extraction points.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/probe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/rt274.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/rt274.c

Purpose: AVS I2S/TDM machine driver for Realtek ALC274 codec boards.

Important APIs, types, and functions: platform driver `avs_rt274`; clock handler `avs_rt274_clock_control()`; codec init/exit; BE fixup; suspend/resume jack hooks; `avs_create_dai_link()`.

Control flow: probe validates SSP/TDM, creates one DSP_A backend link to `i2c-INT34C2:00` DAI `rt274-aif1`, allocates jack/card, installs DAPM routes and registers the card. Codec init creates headset jack, attaches it to the component, programs four-slot 24-bit TDM masks, and disables idle bias. DAPM "Platform Clock" sets codec sysclk and, on power-up, programs BCLK ratio and PLL2 for 24 MHz output.

State and persistence: jack pointer is card drvdata and is disconnected on suspend and exit, restored on resume. Backend params are fixed to 48 kHz stereo S24_LE.

Dependencies and integration points: depends on ACPI ID `INT34C2`, `SND_SOC_RT274`, topology `rt274-tplg.bin`, and codec clock/TDM support.

Risks: DAPM clock handler always sets sysclk even on off events and only enables PLL on on events; codec driver must tolerate that sequence. TDM slot settings must match topology and SSP format.

Test signals: headset jack reports after init/resume, TDM setup succeeds, DAPM clock events do not fail, and streams run at 48 kHz stereo S24_LE.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/rt274.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/rt286.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/rt286.c

Purpose: AVS I2S machine driver for Realtek ALC286 codec boards.

Important APIs, types, and functions: platform driver `avs_rt286`; codec init/exit; `avs_rt286_be_fixup()`; `avs_rt286_hw_params()`; suspend/resume jack hooks.

Control flow: probe validates one SSP/TDM, creates I2S link to `i2c-INT343A:00` DAI `rt286-aif1`, allocates a jack/card, installs headphone/mic/speaker routes, and registers. Codec init creates a headset jack with one button flag and attaches it to the component. `hw_params()` programs codec sysclk from PLL at 24 MHz. Backend fixup forces 48 kHz stereo S24_LE.

State and persistence: jack is card drvdata and is disconnected before suspend and reattached after resume. No other private state.

Dependencies and integration points: depends on ACPI ID `INT343A`, `SND_SOC_RT286`, topology `rt286-tplg.bin`, and AVS board selection DMI quirks that choose RT286 versus RT298 on KBL-family systems.

Risks: ACPI ID overlaps RT298 on some platforms, so DMI selection in `board_selection.c` is critical. Button key codes are not explicitly mapped here, relying on defaults/userspace.

Test signals: correct RT286 card selected on SKL/KBL DMI systems, jack reconnects on resume, sysclk programming succeeds, and backend params are fixed to 48 kHz stereo S24_LE.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/rt286.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/rt298.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/rt298.c

Purpose: AVS machine driver for Realtek ALC298 codec boards, including Kaby Lake-R DMI-specific format/clock handling.

Important APIs, types, and functions: platform driver `avs_rt298`; local `kblr_dmi_table`; codec init/exit; BE fixup; `avs_rt298_hw_params()`; suspend/resume hooks; link factory.

Control flow: probe validates SSP/TDM, creates a backend link to `i2c-INT343A:00` DAI `rt298-aif1`, then registers a routed card with jack drvdata. Link creation chooses I2S format on Kaby Lake-R DDR4 RVP and DSP_A otherwise. `hw_params()` sets sysclk to 24 MHz on that DMI match or 19.2 MHz otherwise. Codec init creates the headset jack and attaches it.

State and persistence: jack is card drvdata and is disconnected/restored across PM. Backend params are 48 kHz stereo S24_LE.

Dependencies and integration points: depends on ACPI ID `INT343A` or `10EC0298` selection, `SND_SOC_RT298`, DMI platform identity, topology `rt298-tplg.bin`, and board selection tables.

Risks: DMI-specific behavior duplicates platform selection logic and must remain synchronized with board tables. Wrong format selection can produce silent audio even when the card registers.

Test signals: KBL-R RVP selects I2S/24 MHz, other RT298 paths select DSP_A/19.2 MHz, jack works after resume, and 48 kHz stereo S24_LE backend params are enforced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/rt298.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/rt5514.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/rt5514.c

Purpose: AVS capture-only machine driver for Realtek RT5514 DMIC/voice codec.

Important APIs, types, and functions: platform driver `avs_rt5514`; `avs_rt5514_codec_init()`; `avs_rt5514_be_fixup()`; `avs_rt5514_hw_params()`; link factory.

Control flow: probe validates SSP/TDM, creates a DSP_B capture-only backend link to `i2c-10EC5514:00` DAI `rt5514-aif1`, installs DMIC routes, and registers. Codec init marks DMIC DAPM route to ignore suspend. `hw_params()` programs TDM slot mask `0xF`, 8 slots, 16-bit width and sets sysclk to 24.576 MHz MCLK. BE fixup forces 48 kHz, 4 channels, S16_LE.

State and persistence: no private state. The route ignore-suspend state persists in DAPM for low-power capture behavior.

Dependencies and integration points: depends on ACPI ID `10EC5514`, board selection TDM mask pdata, `SND_SOC_RT5514`, topology `rt5514-tplg.bin`, and AVS SSP capture CPU DAI.

Risks: capture-only channel count is four, unlike most stereo boards; topology must match. TDM mask and clock programming are board-specific. Missing ignore-suspend would break wake/low-power mic use.

Test signals: capture stream exposes four channels at 48 kHz S16_LE, DMIC path remains available across suspend, and RT5514 TDM/sysclk programming succeeds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/rt5514.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/rt5640.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/rt5640.c

Purpose: AVS I2S machine driver for Realtek ALC5640 codec instances, including ACPI UID-based instance naming.

Important APIs, types, and functions: platform driver `avs_rt5640`; codec init/exit; `avs_rt5640_be_fixup()`; `avs_rt5640_hw_params()`; suspend/resume hooks; `avs_create_dai_link()` that accepts `snd_soc_acpi_mach`.

Control flow: probe validates SSP/TDM, creates a link to `i2c-10EC5640:0<uid-1>` DAI `rt5640-aif1`, allocates jack/card, sets card name with UID suffix when present, installs routes, and registers. Codec init creates headset jack and disables idle bias. `hw_params()` derives PLL/sysclk from MCLK 19.2 MHz and stream rate, then enables ASRC sources. BE fixup maps S32_LE to S24_LE because HDA and I2S align 24/32-bit samples differently.

State and persistence: jack is card drvdata. UID conversion produces stable codec component names for multi-instance ACPI entries. Clock/ASRC state is programmed per stream.

Dependencies and integration points: depends on ACPI ID `10EC5640` with UID values from board selection, `SND_SOC_RT5640`, topology `rt5640-tplg.bin`, and Realtek ASRC helper.

Risks: UID parsing is sensitive: UID is decremented to produce zero-based codec suffixes. Unlike most boards, this driver does not use obsolete-name pdata and always uses modern naming. The S32-to-S24 fixup is narrow and assumes topology format negotiation.

Test signals: UID 1/2/3 boards bind to `i2c-10EC5640:00/01/02`, jack resumes correctly, ASRC setup succeeds, and S32_LE FE use does not break I2S backend alignment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/rt5640.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/rt5663.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/rt5663.c

Purpose: AVS I2S machine driver for Realtek ALC5663 headset codec boards.

Important APIs, types, and functions: platform driver `avs_rt5663`; private `struct rt5663_private`; codec init/exit; BE fixup; `avs_rt5663_hw_params()`; suspend/resume hooks.

Control flow: probe validates SSP/TDM, creates I2S link to `i2c-10EC5663:00` DAI `rt5663-aif`, allocates private jack/card, installs controls/routes, and registers. Codec init creates headset jack with four button mappings and attaches it. `hw_params()` selects ASRC for DAC/ADC filters and sets 24.576 MHz MCLK sysclk. BE fixup forces 48 kHz stereo S24_LE.

State and persistence: private drvdata stores the jack. Jack is disconnected on suspend and restored on resume.

Dependencies and integration points: depends on ACPI ID `10EC5663`, `SND_SOC_RT5663`, topology `rt5663-tplg.bin`, and codec ASRC helper.

Risks: `avs_card_resume_post()` retrieves card drvdata as `struct snd_soc_jack *`, but probe stores `struct rt5663_private *`; because the jack is the first member this works by layout but is fragile and type-obscuring. ASRC/sysclk failure handling returns codec errors directly.

Test signals: headset buttons map to play/pause, voice, volume up/down; resume restores jack reporting; sysclk/ASRC setup succeeds; backend params are 48 kHz stereo S24_LE.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/rt5663.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/rt5682.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/rt5682.c

Purpose: AVS I2S machine driver for Realtek ALC5682 codec boards with DMI-controlled MCLK and SSP quirks.

Important APIs, types, and functions: platform driver `avs_rt5682`; quirk macros and global `avs_rt5682_quirk`; DMI callback/table; codec init/exit; `avs_rt5682_hw_params()`; BE fixup; suspend/resume hooks.

Control flow: probe applies driver-data quirk if present, runs DMI matching, validates SSP/TDM from platform data, creates an I2S backend link to `i2c-10EC5682:00` DAI `rt5682-aif1`, creates card/jack, and registers. Codec init optionally enables ASRC for 24 MHz MCLK, creates headset jack with four button mappings, and attaches it. `hw_params()` chooses PLL source/frequency from MCLK or BCLK, sets sysclk to `rate * 512`, and sets TDM slot width to the PCM width. BE fixup forces 48 kHz stereo S24_LE.

State and persistence: global quirk state affects all instances of this module. Jack is card drvdata and is disconnected/restored across PM.

Dependencies and integration points: depends on ACPI ID `10EC5682`, DMI product names for WhiskeyLake/Ice Lake clients, `SND_SOC_RT5682_I2C`, topology `rt5682-tplg.bin`, and common Intel quirks headers.

Risks: the quirk macro encodes SSP bits but link creation uses platform-data SSP from board selection; mismatches can confuse future maintenance. Global quirk state is not per-device. PLL source selection must match board MCLK availability.

Test signals: DMI systems set expected quirk value, jack buttons work, PLL/sysclk/TDM setup succeeds for both 19.2 MHz and 24 MHz MCLK variants, and resume restores jack reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/rt5682.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/ssm4567.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/ssm4567.c

Purpose: AVS I2S/TDM stereo speaker machine driver for two Analog Devices SSM4567 amplifiers.

Important APIs, types, and functions: platform driver `avs_ssm4567`; codec conf prefixes; `avs_ssm4567_codec_init()`; `avs_ssm4567_be_fixup()`; link factory.

Control flow: probe validates SSP/TDM, creates one DSP_A backend link with inverted bitclock format to two codec instances `i2c-INT343B:00` and `:01`, installs left/right speaker prefixes/routes, and registers. Codec init programs slot 1 for left codec and slot 2 for right codec with two 48-bit slots. BE fixup forces 48 kHz stereo S24_LE.

State and persistence: no private state. TDM slot assignment is applied during DAI init and persists for stream use.

Dependencies and integration points: depends on ACPI ID `INT343B`, `SND_SOC_SSM4567`, topology `ssm4567-tplg.bin`, and exact two-codec ACPI instance naming.

Risks: left/right slot mapping and codec index order are hard-coded. The include of `nau8825.h` appears unnecessary and can mislead maintainers. Missing one codec prevents full link creation.

Test signals: two codec components bind with left/right prefixes, slot programming succeeds, and speaker playback routes to both `OUT` endpoints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/ssm4567.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/cldma.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/cldma.c

Purpose: code-loader DMA implementation for AVS platforms with CLDMA, used primarily by SKL-style firmware and module loading.

Important APIs, types, and functions: internal `struct hda_cldma`; global `code_loader`; exported helpers `hda_cldma_init()`, `free()`, `setup()`, `set_data()`, `transfer()`, `fill()`, `start()`, `stop()`, `reset()`, and `interrupt()`. Register helpers target stream descriptor registers and software position based FIFO (SPIB) registers.

Control flow: `hda_cldma_init()` allocates SG data buffer and BDL buffer, records DSP base and stream address. `hda_cldma_setup()` builds BDL entries over the circular buffer, writes BDL/CBL/LVI/stream tag registers, and enables SPIB. `hda_cldma_transfer()` initializes completion state, fills the first chunk, and schedules delayed work. The work function starts DMA, waits for IOC completions, checks stream status, refills data until `remaining` reaches zero, and re-enables CLDMA interrupts between chunks. IRQ handling disables CLDMA interrupt, captures SD status, and completes the wait.

State and persistence: `code_loader` is a singleton with a fixed stream tag. Runtime transfer state is `position`, `remaining`, and `sd_status`; DMA buffers persist until `hda_cldma_free()`. Completion and delayed work coordinate process context and interrupt context.

Dependencies and integration points: called from `loader.c` for base firmware, libraries, and modules; interrupt path is expected from platform DSP interrupt handlers; uses HDA stream and ADSP register helpers plus `BDL_SIZE`.

Risks: singleton state means only one CLDMA transfer may be active. Pointer arithmetic on `void *position` relies on compiler extension common in kernel C. Timeout or non-IOC status logs errors but higher layers must stop/reset appropriately. BDL IOC is set only on the last entry of the circular buffer, affecting refill cadence.

Test signals: firmware load reaches ROM/basefw status transitions, CLDMA IOC timeouts are absent, `SD_INT_COMPLETE` appears in status, and `hda_cldma_stop()` cleanly cancels delayed work on errors/removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/cldma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/cldma.h -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/cldma.h

Purpose: public interface for the AVS CLDMA code-loader helper.

Important APIs, types, and functions: declares opaque `struct hda_cldma`, external singleton `code_loader`, default buffer size `AVS_CL_DEFAULT_BUFFER_SIZE`, and all lifecycle/control functions implemented in `cldma.c`.

Control flow: callers initialize the singleton, set transfer data, call setup/start/transfer as needed, feed interrupts into `hda_cldma_interrupt()`, then stop/reset/free during error handling and teardown.

State and persistence: hides the CLDMA object internals, so state is owned by `cldma.c`. The singleton declaration makes the loader globally shared within the AVS module.

Dependencies and integration points: included by `core.c` for free/init and by `loader.c` for firmware transfer. Requires HDA bus types via function signatures but avoids exposing register details.

Risks: opaque singleton API does not enforce serialization at compile time. Call order matters: data/setup/interrupt handling must be coordinated by loader/core code.

Test signals: compile-time users include only the header, and runtime firmware loading succeeds on CLDMA-attributed platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/cldma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/cnl.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/cnl.c

Purpose: Cannon Lake-class DSP interrupt handling and DSP operation table.

Important APIs, types, and functions: `avs_cnl_dsp_interrupt()` is exported; internal `avs_cnl_ipc_interrupt()` handles CNL HIPC registers; `avs_cnl_dsp_ops` wires generic power/reset/stall, CNL interrupting, HDA firmware loading, APL log/status/coredump/D0ix helpers, and APL log enabling.

Control flow: DSP interrupt reads ADSPIS and, if IPC is pending, calls the IPC handler. The handler masks DONE/BUSY interrupts, reads ack and response registers, completes `done_completion` when DSP acknowledges a host request, processes response/notification payloads via `avs_dsp_process_response()`, acknowledges response registers, waits briefly for DONE clearing, then re-enables DONE/BUSY interrupts.

State and persistence: updates IPC completions and relies on `adev->ipc` state. No file-local persistent state.

Dependencies and integration points: used by `core.c` CNL/CML/RKL platform specs and by ICL/TGL-derived ops through reuse. Integrates with `ipc.c` response parsing and register constants in `registers.h`.

Risks: incorrect ack ordering can wedge IPC. The poll after response ack ignores return value, so hardware clock-gating propagation failures are not fatal but can affect later interrupts.

Test signals: IPC request/reply completions occur without timeouts on CNL-class devices, notifications are processed, and no interrupt storms occur after ack/re-enable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/cnl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/control.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/control.c

Purpose: ALSA control callbacks for topology-defined AVS volume and mute controls backed by active DSP peak-volume/gain modules.

Important APIs, types, and functions: `avs_control_volume_get/put/info()`, `avs_control_mute_get/put/info()`, helper `avs_get_kcontrol_adev()`, and `avs_get_volume_module()`.

Control flow: get callbacks find the AVS device from the DAPM kcontrol, lock `path_mutex`, search active AVS paths/pipelines/modules for a peakvol or gain module with the topology control ID, fetch current DSP volume/mute through IPC when active, update cached `avs_control_data.values`, and copy values to userspace. Put callbacks validate inputs against mixer min/max, compare with cached values, lock path construction, update the active DSP module when present, cache the new values, and return `1` for changed controls. Info callbacks describe integer/boolean ranges and channel counts.

State and persistence: `struct avs_control_data` attached to topology dobj stores control ID and last values. If a module is inactive, get/put operate on cached values only, preserving desired state until the path exists.

Dependencies and integration points: depends on topology private data, `path.c` runtime module lists, `messages.c` IPC wrappers for peak-volume get/set, and ALSA SoC mixer control structures.

Risks: `avs_get_volume_module()` drops `path_list_lock` before returning a module pointer; `path_mutex` is intended to protect construction/destruction, but misuse elsewhere could invalidate pointers. Mute values are inverted relative to DSP mute booleans (`values[i] = !mute`), so UI semantics must stay consistent. Validation loop handles `num_channels == 0` by checking one value.

Test signals: mixer get reflects live DSP state while streams run, put updates active streams immediately, cached values survive inactive paths, invalid ranges return `-EINVAL`, and topology controls expose correct counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/control.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/control.h -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/control.h

Purpose: header for AVS topology control private data and ALSA control callbacks.

Important APIs, types, and functions: defines `struct avs_control_data` with topology control ID and per-channel cached values up to `SND_SOC_TPLG_MAX_CHAN`; declares volume and mute get/put/info callbacks.

Control flow: topology parsing and control registration can reference these callbacks; runtime operations are implemented in `control.c`.

State and persistence: `avs_control_data.values` is the persistent cache for inactive or last-known DSP control values.

Dependencies and integration points: includes ALSA control and UAPI ASoC topology limits. Used by topology/control registration code and by `control.c`.

Risks: value array size is fixed to topology maximum; callers must not copy more DSP channels than that. The ID must match module template `ctl_id` for live lookup to work.

Test signals: topology controls allocate private data of this shape and callback function pointers resolve during build/link.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/control.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/core.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/core.c

Purpose: main Intel AVS PCI/HDA driver: probes the controller, initializes HDA/extended links, IRQs, codecs, firmware, boards, runtime/system PM, and platform descriptors.

Important APIs, types, and functions: PCI driver `avs_pci_driver`; probe/remove/shutdown; bus/chip helpers; IRQ handlers for HDA streams and DSP IPC; codec probing; async `avs_hda_probe_work()`; PM helpers; platform `avs_spec` descriptors and PCI ID table. Also exports HDA power/clock/L1SEN helpers used by loader code.

Control flow: PCI probe honors `snd_intel_dsp_driver_probe()`, enables PCI, allocates `avs_dev`, initializes HDA extended bus and IPC, maps BAR0 and DSP BAR4, parses capabilities, configures DMA, initializes streams, requests two shared IRQ handlers on one vector, initializes i915 audio component, and schedules probe work. Probe work powers display, initializes the HDA chip, probes codecs, powers down links, enables processing-pipe capability and interrupts, initializes debugfs, first-boots firmware, obtains NHLT, registers all boards, and enables autosuspend. IRQ top half masks global interrupts and wakes a thread; stream thread handles HDA stream/RIRB events, while DSP thread dispatches platform IPC interrupt handling. Remove reverses board/debugfs/NHLT/CLDMA/streams/codecs/links/firmware/IRQ/mapping state.

State and persistence: `struct avs_dev` owns bus, IPC, firmware cache, module info, component/path lists, PM counters, trace state, and work item. Runtime PM transitions may either full-suspend DSP or enter a standby path when low-power paths are active. PCI config power/clock gating masks are module parameters.

Dependencies and integration points: integrates PCI, HDA codec core, HDA extended bus, i915 display audio, ACPI NHLT, debugfs, firmware loader, board selection, PCM components, DSP ops from platform files, and sysfs attributes. PCI ID descriptors choose firmware version minimums, SRAM/HIPC register layouts, boot masks, and attributes such as CLDMA/IMR/ACE/ALTHDA.

Risks: probe is split between PCI probe and async work, so remove/shutdown must cancel work and tolerate partial initialization. Two `pci_request_irq()` calls share the same vector with different dev_ids; cleanup must match both. PM paths rely on firmware IPC unless recovery has blocked IPC. Platform descriptors must stay aligned with firmware locations and register layouts. Error unwinding differs before and after scheduled work.

Test signals: successful firmware boot, HDA codec enumeration, board cards appearing, runtime suspend/resume cycles, shared IRQ handling without lost stream periods or IPC timeouts, and removal after deferred probe without leaks or use-after-free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/debug.h -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/debug.h

Purpose: debug/logging interface declarations and log buffer helpers for AVS.

Important APIs, types, and functions: log buffer macros `avs_log_buffer_size()`, `avs_log_buffer_addr()`, APL log layout helpers, locked status helper `avs_log_buffer_status_locked()`, debugfs/probe function declarations under `CONFIG_DEBUG_FS`, and no-op stubs when debugfs is disabled. `AVS_SET_ENABLE_LOGS_OP(name)` populates DSP ops conditionally.

Control flow: platform DSP ops call through enable-log hooks only when debugfs is compiled. Log buffer address computation asks the platform op for a per-core offset and maps it into the debug SRAM window.

State and persistence: no state owned by the header; it coordinates access to `adev->trace_lock`, firmware config, and debug window.

Dependencies and integration points: used by platform ops, `debugfs.c`, `board_selection.c` probe-board registration, and firmware notification handling.

Risks: `avs_log_buffer_size()` divides by `adev->hw_cfg.dsp_cores`; callers need valid hardware config. Stubs make debug-only registration return `-EOPNOTSUPP`, so callers should treat that as optional.

Test signals: debugfs-disabled builds compile with stubs, debugfs-enabled builds expose trace/probe APIs, and log buffer offset failures return NULL rather than invalid SRAM pointers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/debugfs.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/debugfs.c

Purpose: debugfs support for AVS firmware trace collection, SRAM/register dumps, and runtime probe-point control.

Important APIs, types, and functions: `avs_debugfs_init()/exit()`, `avs_logging_fw()`, `avs_dump_fw_log()`, `avs_dump_fw_log_wakeup()`, file operations for `strace`, `trace_control`, `fw_regs`, `debug_window`, `probe_points`, and `probe_points_disconnect`.

Control flow: init creates `avs` debugfs directory, default trace timer periods, trace/probe files, and dump files. `strace_open()` pins the module and allocates a PAGE_SIZE kfifo, `strace_read()` blocks until data is available then copies FIFO data to userspace, and release flushes remaining firmware log buffers before freeing. `trace_control_write()` parses integer arrays: one mask disables resources, mask plus priorities enables logging after forcing DSP out of D0ix and setting firmware time. Probe files query, connect, and disconnect firmware probe points via IPC. Register/window reads copy SRAM windows to temporary buffers for userspace.

State and persistence: trace FIFO, waitqueue, spinlock, aging/full timer periods, and `logged_resources` live in `avs_dev`. Logging keeps runtime PM active and D0ix disabled until all resources are disabled. Probe point connections are firmware state controlled through IPC.

Dependencies and integration points: depends on debugfs, kfifo, AVS IPC probe/log messages, platform `enable_logs` and `log_buffer_status` ops, runtime PM, and firmware notification `AVS_NOTIFY_LOG_BUFFER_STATUS`.

Risks: `strace_open()` returns `-EBUSY` if already initialized but does not drop the module reference on that path, which is a subtle resource-risk signal. User input for probe point arrays is binary-layout-sensitive and must align with descriptor sizes. Logging power-state bookkeeping must unwind on IPC failures.

Test signals: reading `strace` receives firmware log bytes after enabling `trace_control`; disabling last resource allows autosuspend; `fw_regs` and `debug_window` return expected sizes; `probe_points` lists and modifies firmware probe state; open/close cycles do not leak module refs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/dsp.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/dsp.c

Purpose: common DSP core power/reset/stall helpers plus runtime module and pipeline instance lifecycle for AVS firmware paths.

Important APIs, types, and functions: core ops `avs_dsp_core_power/reset/stall/enable/disable()`, module lifecycle `avs_dsp_init_module()` and `avs_dsp_delete_module()`, pipeline lifecycle `avs_dsp_create_pipeline()` and `avs_dsp_delete_pipeline()`, private core reference helpers.

Control flow: core power/reset/stall update ADSPCS bits and poll matching acknowledge bits, with tracepoints and hardware propagation delays. Enabling a core powers it, exits reset, and unstalls; disabling stalls, resets, and powers down. Non-main DSP cores are reference-counted: first get disables D0ix then powers and sets D0, last put deletes D0 and re-enables D0ix. Module init allocates an instance ID, finds module metadata, gets the target core, loads module code if it is the first instance of an unloaded loadable module, sends IPC init-instance, and returns instance ID. Delete optionally sends delete-instance, frees ID, unloads module code when last instance goes away, and puts the core. Pipeline creation/deletion wrap firmware IPC with an IDA-backed pipeline ID.

State and persistence: `adev->core_refs`, module IDAs, pipeline IDA, and firmware module load state are persistent driver state. Module code may be loaded into DSP memory while at least one instance exists.

Dependencies and integration points: depends on platform DSP ops, IPC wrappers, module info from `utils.c/messages.c`, firmware transfer ops from `loader.c`, D0ix management in `ipc.c`, and path construction code.

Risks: error path in `avs_dsp_init_module()` after `avs_dsp_get_core()` but before successful IPC can jump to `err_mod_entry` without putting the core for some failures before `err_ipc`, so changes need close audit. Core ref underflow is not guarded in put. Firmware load/unload decisions rely on module IDA emptiness and module metadata accuracy.

Test signals: tracepoints show expected ADSPCS transitions, creating/deleting pipelines frees IDs, loadable module binaries transfer only for first instance and unload after last, and D0ix is disabled while secondary cores are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/dsp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/icl.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/icl.c

Purpose: Ice Lake-specific DSP operations for firmware logging, debug-window slot lookup, D0ix policy, and a firmware-load workaround.

Important APIs, types, and functions: debugfs-only `avs_icl_enable_logs()`, packed debug-window slot descriptors, `avs_icl_log_buffer_offset()`, `avs_icl_d0ix_toggle()`, `avs_icl_set_d0ix()`, `avs_icl_load_basefw()`, and `avs_icl_dsp_ops`.

Control flow: log enabling builds a variable-sized `avs_icl_log_state_info` with priorities for selected resources and sends it by IPC. Log buffer offset reads MEMWND2 slot descriptors from debug SRAM and finds a slot whose type/resource matches debug log for the requested core. D0ix toggle requests full power for pipeline-running IPCs and for payload-carrying IPCs. Base firmware loading allocates a dummy HDA capture stream, temporarily raises VS_LTRP.GB to 95 us, starts the stream to avoid low-power link entry, calls the generic HDA basefw loader, then stops/cleans the stream and restores VS_LTRP.

State and persistence: no file-local persistent state. Firmware logging state is sent to firmware; VS_LTRP is saved and restored.

Dependencies and integration points: used by ICL/JSL specs in `core.c`; reuses CNL interrupt handling, APL log status/coredump, and HDA loader. Depends on MEMWND2 layout agreed with firmware.

Risks: debug-window packed structures must match firmware exactly. `avs_icl_enable_logs()` validates resource mask against `max_libs_count`; wrong firmware config can reject logging. Firmware load workaround must always release stream and restore LTRP on all exits.

Test signals: ICL firmware boots reliably with dummy capture workaround, debug log offsets resolve for active cores, D0ix transitions do not occur during running pipeline IPCs, and logging priorities reach firmware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/icl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/ipc.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/ipc.c

Purpose: AVS host-DSP IPC transport, response/notification handling, D0ix transition orchestration, timeout recovery, and IPC context lifecycle.

Important APIs, types, and functions: `avs_ipc_init()`, `avs_ipc_block()`, `avs_dsp_process_response()`, send variants `avs_dsp_send_msg*_timeout()`, ROM send variants, PM send variants, `avs_dsp_interrupt_control()`, D0ix helpers, and recovery work.

Control flow: send path optionally wakes DSP to D0i0 based on platform `d0ix_toggle`, serializes requests with `msg_mutex`, initializes RX/completions under `rx_lock`, writes payload to downlink SRAM and HIPC request registers, waits for BUSY/reply completion while tolerating interleaved notifications, copies reply payload back, and schedules delayed D0ix when allowed. ROM send path writes request while the main core is stalled and then unstalls it before waiting for DONE. Interrupt processing classifies headers as replies or notifications; replies fill `ipc->rx`, notifications handle FW_READY, log-buffer status, exception caught, and other payload types. Timeouts synthesize exception handling, disconnect streams, disable DSP cores, reboot firmware, and re-enable runtime PM.

State and persistence: `struct avs_ipc` tracks readiness, RX buffer, completions, recovery work, D0ix delayed work, disable depth, and current D0ix state. Firmware ready completion lives in `avs_dev`.

Dependencies and integration points: depends on platform HIPC register specs, DSP ops for D0ix/coredump/log handling, mailbox SRAM helpers, ALSA PCM stop paths, component list, firmware boot in `loader.c`, and tracepoints.

Risks: IPC readiness gates most operations with `-EPERM`; callers must distinguish blocked recovery from real failures. Notification interleaving retry loop is bounded but complex. `avs_dsp_enable_d0ix()` uses `atomic_dec_and_test`; unbalanced enable/disable calls can underflow policy. Recovery forcibly disconnects streams, so userspace sees PCM disconnects on firmware faults.

Test signals: ordinary IPCs complete within 300 ms, payload replies are copied for large config gets, FW_READY completes first boot, log notifications drain buffers, IPC timeout triggers recovery once, and runtime D0ix transitions occur after idle delay but not while disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/ipc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/lnl.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/lnl.c

Purpose: Lunar Lake/Future Core link-interrupt routing adjustment layered on Meteor Lake core stall behavior.

Important APIs, types, and functions: `avs_lnl_core_stall()`.

Control flow: calls `avs_mtl_core_stall()` for the actual core stall/unstall operation. After successful unstall, iterates HDA extended links and sets `AZX_ML_LCTL_OFLEN` so link interrupts are routed to DSP firmware.

State and persistence: modifies ML link control registers after unstall; no file-local state.

Dependencies and integration points: depends on MTL core stall implementation, HDA extended bus link list, and register definitions. Used indirectly by platform ops for LNL/PTL-style descriptors.

Risks: if hlink list is incomplete or link register writes fail silently, firmware may miss offload link interrupts. Behavior only runs on unstall, so later link additions would need separate routing.

Test signals: after DSP unstall, each multi-link control register has OFLEN set and firmware receives link interrupts on LNL-class hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/lnl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/loader.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/loader.c

Purpose: AVS firmware, library, and module loading framework for CLDMA, HDA DMA, and IMR boot paths.

Important APIs, types, and functions: manifest structs and stripping/verification helpers; CLDMA loaders `avs_cldma_load_basefw/load_library/transfer_modules`; HDA/IMR helpers `avs_hda_init_rom()`, `avs_hda_load_basefw()`, `avs_hda_load_library()`, `avs_hda_transfer_modules()`; library loader `avs_dsp_load_libraries()`; boot entry points `avs_dsp_boot_firmware()` and `avs_dsp_first_boot_firmware()`; resource allocator `avs_dsp_alloc_resources()`.

Control flow: base firmware is requested from `intel/avs/<platform>/dsp_basefw.bin`, optional extended manifest is stripped, manifest magic/offset is validated, minimum version is enforced unless `ignore_fw_version=1`, then platform `load_basefw` is called and waits for FW_READY. CLDMA base loading powers/resets/unstalls main core, waits for ROM init, streams firmware through CLDMA, and waits for ROM status. HDA loading assigns a host playback stream, prepares DMA, enables SPIB, copies firmware, initializes ROM with boot config and purge, triggers DMA, and polls ROM-entered status. IMR boot first tries to start from retained memory when purge is false. Libraries are deduplicated by manifest name and loaded into firmware library slots. First boot initializes CLDMA when needed, disables main core, boots firmware with purge, and queries/allocates hardware, firmware, library, core, and pipeline resources.

State and persistence: firmware objects are cached through `avs_request_firmware()` and `adev->fw_list` so later suspend/resume is insulated from filesystem changes. `adev->lib_names` tracks loaded library slots; slot 0 is `BASEFW`. `adev->core_refs`, `ppl_ida`, and module info are allocated after first boot.

Dependencies and integration points: depends on firmware files declared in `core.c`, CLDMA helper, HDA stream DMA helpers, IPC boot/load-library/module messages, topology library names, power/clock/L1SEN gating controls, and platform attributes CLDMA/IMR/ALTHDA.

Risks: firmware manifest parsing mutates a local firmware copy by advancing data/size, so callers must pass copies when preserving original firmware cache. Library slot capacity check uses `id + num_libs >= max_libs_count`, which rejects filling the last nominal slot; verify intent before changing. Loading failures after caching libraries can require full driver reload. Power/clock gating must be restored on all error paths.

Test signals: minimum firmware version warnings/errors, successful FW_READY within 3 seconds, IMR resume path works when purge is false, HDA/CLDMA transfer status reaches expected ROM codes, library deduplication avoids duplicate loads, and module info initializes after boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/loader.c -->
