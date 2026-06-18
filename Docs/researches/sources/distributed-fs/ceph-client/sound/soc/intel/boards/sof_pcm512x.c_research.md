# sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_pcm512x.c

Purpose: SOF machine driver for Intel UP/UP2-style boards using a TI PCM512x codec, such as Hifiberry DAC+ HATs, with optional DMIC and HDMI links on non-legacy CPUs.

Important APIs, types, and functions: Quirk bits select SSP port, optional SSP capture, and DMIC enablement. DMI callback overrides quirks for UP-CHT01. `sof_pcm512x_codec_init()`, `aif1_startup()`, and `aif1_shutdown()` program PCM512x GPIO registers to control amplifier/output state. `sof_card_dai_links_create()` manually creates the SSP codec link, optional DMIC links, and optional HDMI links, using `ssp%d-port` for BYT/CHT and `SSP%d Pin` otherwise. HDMI init records codec DAIs for late HDMI control setup.

Control flow and integration: Probe decides legacy versus newer CPU behavior, applies DMI quirks, computes link count, creates links, initializes the HDMI list, fixes platform names, stores drvdata, and registers the card. Remove clears component jack state for the codec.

State and persistence: Module-global quirk and `is_legacy_cpu`, static card data, and devm private HDMI list state. No persistent storage.

Dependencies: PCM512x codec registers, HDA DSP HDMI helper, ACPI/DMI, Intel SoC quirks, ASoC DAPM/DAI, and SOF/HDA platform names.

Risks: HDMI late-probe returns `-EINVAL` if expected HDMI list is empty on non-legacy systems. Manual link generation duplicates patterns from newer helpers and can drift. GPIO register bit assumptions are board-specific. Test signals include UP/UP2 DMI behavior, legacy no-HDMI/no-DMIC path, SSP capture enablement, PCM512x GPIO toggles across playback, DMIC capture, HDMI controls, and platform-name fixup.
