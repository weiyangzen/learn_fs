# sources/distributed-fs/ceph-client/sound/soc/intel/boards/cht_bsw_rt5645.c

## Purpose
This Cherrytrail/Braswell machine driver supports RT5645 and RT5650 codec variants. It selects the correct card based on ACPI HID, handles SSP0/SSP2 and AIF1/AIF2 routing quirks, configures codec PLL/sysclk and ASRC, creates headset jack detection, and exposes codec-specific component metadata.

## Important APIs, Types, and Functions
`struct cht_acpi_card` maps codec HIDs to codec type and card definition. `struct cht_mc_private` stores the headset jack, selected ACPI card, and MCLK. Quirk bits select SSP2 AIF2, SSP0 AIF1, SSP0 AIF2, and `pmc_plt_clk_0`. `platform_clock_control()` enables MCLK for active paths and switches the codec to RC clock before disabling MCLK. `cht_aif1_hw_params()` programs RT5645 PLL from 19.2 MHz MCLK. `cht_codec_init()` selects ASRC clock source, adds DAPM routes for selected SSP/AIF, creates the headset jack, calls `rt5645_set_jack_detect()`, and sets MCLK rate. `cht_codec_fixup()` configures 48 kHz stereo and chooses SSP0 16-bit I2S or SSP2 24-bit DSP/TDM behavior.

## Control Flow and Integration
Probe finds a supported Realtek ACPI HID, chooses RT5645 or RT5650 card, rewrites the codec component name, gets the physical codec device, fills component metadata from `rt5645_components()`, detects BYTCR and reads ACPI CHAN routing, applies DMI quirks, mutates codec/CPU DAI names for AIF2 or SSP0, fixes platform names, gets `pmc_plt_clk_0` or `_3`, sets SOF or legacy names, installs SOF PM ops when needed, and registers the chosen card.

## State, Persistence, and Dependencies
State includes global `cht_rt5645_quirk`, shared mutable `cht_dailink`, two static card objects, card component strings from codec properties, MCLK, and jack state. Dependencies include RT5645 codec helpers, ACPI HID/package lookup, DMI, common clock, Atom SST DPCM, `soc_intel_is_byt()`, and SOF parent detection.

## Risks and Test Signals
Risks include shared DAI link mutation across variants, missed edge cases in ACPI HID matching, quirk combinations selecting impossible SSP/AIF routes, and MCLK clock-source handling on Strago-family systems. Test signals include correct card name for RT5645 versus RT5650, component metadata from codec device, jack detection and buttons on RT5650 paths, SSP0 16-bit or SSP2 24-bit stream format, ASRC source selection matching AIF route, and stable audio across suspend/resume and runtime PM.
