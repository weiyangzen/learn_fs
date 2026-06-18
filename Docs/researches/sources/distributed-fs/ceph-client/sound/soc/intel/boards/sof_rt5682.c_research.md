# sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_rt5682.c

Purpose: Broad SOF machine driver for Intel platforms with Realtek RT5682, RT5682S, or RT5650 headset codecs and many optional speaker amp families.

Important APIs, types, and functions: Quirk bits include MCLK enable and common board-helper SSP/amp/BT/HDMI fields. DMI and module parameters can override quirks. `sof_rt5682_codec_init()` handles optional legacy PMC MCLK setup, enables ASRC for 24 MHz MCLK on supported codecs, creates headset jacks, and registers codec jack callbacks. `sof_rt5682_hw_params()` chooses PLL source from MCLK or BCLK, handles RT5682S PLL1/PLL2 selection, sets sysclk, and configures two-slot TDM. `sof_card_dai_links_create()` patches headset codec links for RT5650/RT5682/RT5682S and amp links for Maxim, Realtek, RT5650 AIF2, and TI TAS2563.

Control flow and integration: Probe combines platform id, DMI, and module quirks; gets common context; handles RT5650 card-name/speaker-link special case; adjusts legacy BYT/CHT and GLK behavior; acquires/enables PMC MCLK for legacy systems; creates links; installs amp codec_conf; fixes platform names; and registers the card.

State and persistence: Module-global quirk, static card/component arrays, devm context, optional clock handle, and jack state. No persistent storage.

Dependencies: SOF board helpers, Realtek headset codec APIs, Realtek/Maxim/TI amp helpers, common clock framework, ASoC jack/input, SOF topology clock metadata, DMI, and Intel SoC quirks.

Risks: Clock path selection is complex and codec-specific. Legacy MCLK is enabled in probe and hw_params and must be balanced by platform lifetime behavior. Module quirk override can create topology mismatches. Test signals include all headset codec variants, MCLK and BCLK PLL paths, RT5682S high-rate cases, jack/button events, amp family playback, HDMI/BT links, legacy no-DMIC/no-HDMI behavior, and suspend/resume audio noise regressions.
