# sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_da7219.c

Purpose: SOF machine driver for Intel platforms with a Dialog DA7219 headset codec and optional Maxim speaker amplifiers.

Important APIs, types, and functions: Driver-specific quirk bits identify GLK/CML/JSL boards and MCLK availability. `platform_clock_control()` starts/stops DA7219 PLL SRM mode through a DAPM supply unless PLL bypass is active. `da7219_codec_init()` obtains topology MCLK, sets codec sysclk, optionally uses PLL bypass for 12.288/24.576 MHz MCLK, creates headset/lineout jack pins and button mappings, and registers the jack callback. `card_late_probe()` disables MAX98373 speaker pins after boot and delegates HDMI control setup. `sof_card_dai_links_create()` uses common board helper links and attaches DA7219 plus supported Maxim amp helpers.

Control flow and integration: Probe decodes platform id quirks, detects iDisp, applies board-specific link-order overrides and legacy card names, enables DA7219 MCLK policy, creates links, sets amp codec_conf, fixes platform names, binds context, and registers the card.

State and persistence: State is in `sof_card_private`, especially `da7219.mclk_en` and `da7219.pll_bypass`. Card name and link order are changed per probe. No persistence exists.

Dependencies: DA7219 codec APIs, SOF board helpers, Maxim helpers, SOF topology clock metadata, ASoC DAPM/jack, and ACPI platform data.

Risks: PLL bypass requires topology MCLK to match expected frequencies. DAPM clock callback depends on `DIALOG_CODEC_DAI` lookup. Link-order/card-name compatibility with old topologies is sensitive. Test signals include MCLK/PLL modes, headset and lineout detection, speaker amp DAPM, HDMI controls, and all platform id variants.
