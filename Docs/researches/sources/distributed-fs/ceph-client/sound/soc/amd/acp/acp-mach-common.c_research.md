# sources/distributed-fs/ceph-client/sound/soc/amd/acp/acp-mach-common.c

## Purpose
`acp-mach-common.c` is the shared machine-driver construction layer for AMD ACP legacy and SOF cards. It translates `struct acp_card_drvdata` endpoint and codec selections into ASoC DAI links, widgets, controls, routes, jack setup, clocking, and codec-specific `hw_params` handling for RT5682/RT5682S, RT1019, MAX98360A, MAX98388, NAU8825, NAU8821, DMIC, and ES83xx-extension cards.

## Important APIs, Types, and Functions
The exported entry points are `acp_sofdsp_dai_links_create()` and `acp_legacy_dai_links_create()`, plus exported DMI quirk table `acp_quirk_table`. Important local callbacks include codec init functions such as `acp_card_rt5682_init()`, `acp_card_rt5682s_init()`, `acp_card_rt1019_init()`, `acp_card_maxim_init()`, `acp_card_max98388_init()`, `acp_card_nau8825_init()`, and `acp_8821_init()`, and runtime ops such as `acp_card_rt5682_hw_params()`, `acp_card_rt5682s_hw_params()`, `acp_card_rt1019_hw_params()`, `acp_card_maxim_hw_params()`, `acp_max98388_hw_params()`, `acp_nau8825_hw_params()`, and `acp_nau8821_hw_params()`. `acp_rtk_set_bias_level()` manages Realtek bit-clock enable ordering.

## Control Flow
Machine probe code in companion files fills `acp_card_drvdata`, then calls one of the two DAI-link creation functions. Both count enabled endpoints, allocate `snd_soc_dai_link` arrays with devm allocation, and then append headset, amplifier, Bluetooth, and DMIC links based on CPU endpoint IDs. The SOF path uses `acp-sof-*` CPU DAIs and the PCI SOF component, while the legacy path uses ACP I2S/PDM CPU DAIs and SoC-revision-specific platform component names. Per-link codec IDs select the codec component array, init callback, ops table, playback/capture flags, and codec-conf name prefixes.

Runtime control flows through ASoC callbacks. Startup constrains channels/rates and sets codec DAI formats. `hw_params` programs PLLs, sysclks, BCLK ratios, TDM slots, and optional ACP-supplied word/bit clocks. DMI quirks can enable TDM mode or remap SOF BT/DMIC backend IDs. Jack init creates ALSA jack pins and button mappings and registers codec jack callbacks. DAPM routes and card controls are added during codec init.

## State and Persistence
State is volatile kernel/device-managed memory attached to the `snd_soc_card` and `acp_card_drvdata`. Clock handles, `tdm_mode`, `soc_mclk`, codec IDs, and codec-conf pointers persist for the card lifetime. Static jack objects are module-global. No disk persistence exists; DMI and ACPI matching drive runtime topology.

## Dependencies and Integration Points
The file depends on ASoC card, DAI, DAPM, jack, and codec APIs; Realtek/Nuvoton/Maxim codec headers; `acp-mach.h`; DMI matching; and ACP platform component names created by PCI/SoC drivers. It integrates with `acp-sof-mach.c`, legacy machine drivers, ES83xx ops, SOF topology BE IDs, and ACP platform DMA/I2S/PDM drivers.

## Risks
DAI-link selection is table-like but hand-coded; new boards can silently get dummy codecs, wrong platform components, or wrong BE IDs if `acp_card_drvdata` is inconsistent. Clock enable/disable is split across startup, `hw_params`, shutdown, and bias transitions, so imbalance can cause audio pops or leaks. TDM slot masks are codec-specific and fragile. Static jack objects limit assumptions about multiple simultaneous cards.

## Test Signals
Useful signals are successful card registration for each board ID, visible ALSA links/widgets/routes, jack button reporting, 48 kHz constraints, TDM-mode playback/capture on Google Skyrim-like systems, BT/DMIC remap on Steam Deck OLED, and suspend/resume with Realtek clock bias transitions. Runtime tests should exercise headset, speaker, DMIC, Bluetooth, and no-codec/dummy-codec link combinations.
