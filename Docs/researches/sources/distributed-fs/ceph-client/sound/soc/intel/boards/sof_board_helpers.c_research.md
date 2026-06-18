# sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_board_helpers.c

Purpose: Shared topology builder for Intel SOF I2S/HDA board drivers. It converts detected codec/amp types and packed board quirk bits into a card's BE DAI-link table.

Important APIs, types, and functions: `sof_intel_board_get_ctx()` allocates `struct sof_card_private`, detects headset codec and amp types through ACPI helper APIs, decodes SSP ports, HDMI count, BT offload, and HDMI capture masks. `sof_intel_board_set_dai_link()` calculates link count, allocates links, applies default or caller-supplied link order/ids, and dispatches to helper builders. Builders include `set_ssp_codec_link()`, `set_dmic_link()`, `set_idisp_hdmi_link()`, `set_ssp_amp_link()`, `set_bt_offload_link()`, `set_hdmi_in_link()`, and `set_hda_codec_link()`. `sof_intel_board_card_late_probe()` builds HDMI controls through `hda_dsp_hdmi_build_controls()`.

Control flow and integration: Machine drivers first get a context, optionally override fields, call `sof_intel_board_set_dai_link()`, and then patch `ctx->codec_link` and/or `ctx->amp_link` with codec-specific component arrays, init callbacks, ops, and codec_conf. DAPM init callbacks add shared DMIC or HDA widgets/routes. HDMI init stores the HDMI component for late probe.

State and persistence: State lives in devm-managed context and DAI-link arrays. The shared `platform_component` object is static but its name is later fixed by ASoC platform-name fixup.

Dependencies: ASoC core, SOF topology conventions, Intel SoC legacy BYT/CHT naming quirks, ACPI codec detection helpers, HDA DSP HDMI helper.

Risks: Link count and generated order must exactly match topology expectations; mismatch returns `-EINVAL` or causes topology failures. Static component arrays are reused across cards. HDMI link id overrides increment across multi-link groups. Test signals include unit-style link count/order inspection, all supported codec/amp quirk combinations, DMIC/HDA DAPM routes, HDMI controls, and legacy SSP dai names.
