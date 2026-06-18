# sources/distributed-fs/ceph-client/sound/soc/intel/boards/hsw_rt5640.c

Purpose: Haswell Lynx Point ASoC machine driver for systems using the Realtek RT5640 codec through SSP0.

Important APIs, types, and functions: Static widgets/routes expose `Headphones` and `Mic` plus SSP0 codec BE connections. `codec_link_hw_params_fixup()` constrains the BE to 48 kHz, stereo, 16-bit samples because the ADSP performs FE conversion. `codec_link_hw_params()` sets the codec sysclk to 12.288 MHz MCLK and updates codec register `0x83` to select the expected filter mode. The DAI-link array contains four dynamic FE links (`System`, two offload playback links, and `Loopback`) plus one no-PCM SSP0 codec BE.

Control flow and integration: Probe obtains `snd_soc_acpi_mach`, assigns the platform component name with `snd_soc_fixup_dai_links_platform_name()`, and registers the static card. Runtime DPCM connects FEs to the codec BE, with trigger mode set to post-trigger for FE links.

State and persistence: The driver uses static card/link tables and no private drvdata. It has no persistent state.

Dependencies: ASoC DPCM, Haswell PCM platform name from ACPI mach data, RT5640 codec definitions, and standard `snd_soc_pm_ops`.

Risks: The raw register update is codec-version sensitive and deserves regression attention. The platform and codec component names are hard coded except platform fixup. Test signals include card registration, all FE PCMs appearing, 48 kHz stereo BE constraints, headphone/mic DAPM routing, offload playback, and suspend/resume with PM ops.
