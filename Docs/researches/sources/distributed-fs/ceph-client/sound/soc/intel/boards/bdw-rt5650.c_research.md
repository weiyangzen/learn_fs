# sources/distributed-fs/ceph-client/sound/soc/intel/boards/bdw-rt5650.c

## Purpose
This is the Intel Broadwell machine driver for boards using the Realtek RT5650 codec. It describes the ASoC card, DAPM topology, DPCM FE/BE links, jack handling, and codec clock/TDM setup for the Broadwell DSP connected to the codec through SSP0.

## Important APIs, Types, and Functions
`struct bdw_rt5650_priv` stores private card data, mainly the codec component pointer. Static DAPM widgets/routes expose `Headphone`, `Speaker`, `Headset Mic`, and two DMIC pairs. `broadwell_ssp0_fixup()` forces the back end to 48 kHz, 2 to 4 channels, and S24_LE. `bdw_rt5650_hw_params()` programs RT5645 PLL/sysclk from MCLK. `bdw_rt5650_fe_startup()` constrains capture to stereo or quad. `bdw_rt5650_init()` enables RT5645 ASRC filters, sets four 24-bit TDM slots, creates headphone and mic jacks, and calls `rt5645_set_jack_detect()`.

## Control Flow and Integration
Probe receives `struct snd_soc_acpi_mach` platform data, patches DAI platform names with `snd_soc_fixup_dai_links_platform_name()`, selects SOF or legacy card names through `snd_soc_acpi_sof_parent()`, stores private data with `snd_soc_card_set_drvdata()`, and registers the card with `devm_snd_soc_register_card()`. The card has one dynamic FE (`System PCM`) and one no-PCM BE (`Codec`) connected to `haswell-pcm-audio`, `ssp0-port`, and `i2c-10EC5650:00`/`rt5645-aif1`.

## State, Persistence, and Dependencies
Runtime state is limited to private card data and static jack objects. Persistent hardware state includes codec PLL/sysclk, ASRC source selection, TDM slot configuration, and jack detect registration. Dependencies include ASoC core, DPCM, ACPI machine data, `haswell-pcm-audio`, RT5645 codec helpers, and Broadwell/SOF platform matching.

## Risks and Test Signals
Risks include hard-coded codec ACPI name, incorrect 24 MHz versus 24.576 MHz clock assumptions, global jack objects if multiple cards were ever instantiated, and failures when `mach->mach_params.platform` is missing. Test signals include successful card registration, visible DAPM pins, jack events, 48 kHz playback/capture through SSP0, four-channel capture constraints, and suspend/resume without codec clock or jack regressions.
