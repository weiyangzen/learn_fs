# sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_nau8825.c

Purpose: SOF machine driver for Intel platforms with a Nuvoton NAU8825 headset codec and optional RT1019P, RT1015P, MAX98360A, MAX98373, or NAU8318 speaker amps.

Important APIs, types, and functions: `sof_nau8825_codec_init()` creates a headset jack with four buttons, maps input keys, and calls `snd_soc_component_set_jack()`. `sof_nau8825_hw_params()` obtains topology BCLK, selects NAU8825 FLL BCLK clocking, and sets PLL output to sample_rate * 256. `sof_card_late_probe()` disables MAX98373 speaker pins after boot and then delegates HDMI control setup. `sof_card_dai_links_create()` builds common links and patches the headset codec and selected amp link.

Control flow and integration: Probe applies board id quirks, creates a shared SOF context, marks iDisp presence from ACPI, builds/paches links, installs codec_conf for MAX98373 or no-op amp families, fixes platform names, stores drvdata, and registers the card.

State and persistence: Uses static card/component data and devm `sof_card_private` state. No persistent storage.

Dependencies: NAU8825 codec, SOF board helpers, Realtek/Maxim/Nuvoton amp helpers, ASoC jack/input, and ACPI mach params.

Risks: Only selected amp types are accepted. BCLK must be present in topology or hw_params fails. Speaker DAPM disabling is MAX98373-specific. Test signals include jack/button behavior, FLL/PLL setup, all platform id quirk combinations, optional BT/HDMI links, and amp-specific playback.
