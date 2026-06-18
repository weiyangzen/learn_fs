# sources/distributed-fs/ceph-client/sound/soc/intel/boards/skl_hda_dsp_generic.c

Purpose: Generic machine driver for Skylake and later HDA DSP platforms with optional iDisp HDMI, external HDA codecs, DMICs, and Bluetooth offload.

Important APIs, types, and functions: `skl_hda_get_board_quirk()` derives BT offload quirk bits from a single `bt_link_mask`. `skl_hda_add_dai_link()` marks HDMI PCM links ignored when iDisp is absent. `skl_hda_audio_probe()` allocates a card, obtains a `sof_card_private` via `sof_intel_board_get_ctx()`, sets `hda_codec_present` and HDMI flags from `mach_params.codec_mask`, overrides link order and BE ids with `HDA_LINK_ORDER` and `HDA_LINK_IDS`, then asks `sof_intel_board_set_dai_link()` to synthesize the BE links. `skl_set_hda_codec_autosuspend_delay()` finds the first external HDA codec component and sets bus power-save delay to 1000 ms.

Control flow and integration: This driver is a thin policy layer over `sof_board_helpers.c`. It sets card metadata, link ordering, optional `cfg-dmics` component strings, platform-name fixups, card drvdata, and then registers the card. HDMI/HDA controls are handled by the helper late-probe path.

State and persistence: All state is devm-managed card/context data. No persistent state exists.

Dependencies: SOF board helpers, HDA codec private data, HDA DSP platform component names, ACPI mach params, and ASoC PM ops.

Risks: BE id/order constants must match SOF topology files. Autosuspend delay lookup depends on codec component name containing `ehdaudio0D0`. Test signals include generated DAI links for each codec-mask combination, HDMI FE ignore behavior without iDisp, HDA analog/digital controls, DMIC component strings, BT link creation, and HDA codec autosuspend timing.
