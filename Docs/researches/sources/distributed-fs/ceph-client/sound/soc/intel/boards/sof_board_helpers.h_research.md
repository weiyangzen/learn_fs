# sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_board_helpers.h

Purpose: Public interface and quirk encoding for the Intel SOF board-helper topology builder.

Important APIs, types, and functions: The header defines packed quirk macros for codec SSP, amp SSP, BT offload SSP, HDMI capture SSP mask, iDisp HDMI count, and BT offload presence. It defines link type constants (`SOF_LINK_CODEC`, `SOF_LINK_DMIC01`, `SOF_LINK_IDISP_HDMI`, `SOF_LINK_HDA`, and others) plus `SOF_LINK_ORDER()` and `SOF_LINK_IDS()` bit packing macros. `struct sof_da7219_private`, `struct sof_rt5682_private`, and `struct sof_card_private` hold shared card state, detected codec/amp type, link counts, port numbers, feature flags, pointers to generated links, optional link order/id overrides, and codec-specific private unions. Exported functions are `sof_intel_board_card_late_probe()`, `sof_intel_board_set_dai_link()`, and `sof_intel_board_get_ctx()`.

Control flow and integration: Machine drivers include this header to define platform-device id `driver_data`, obtain a context, override fields for board policy, and patch generated codec/amp links.

State and persistence: The header defines only structure layout and bit encodings. It does not persist data.

Dependencies: ASoC, ACPI Intel SSP common codec enums, and `sof_hdmi_common.h`.

Risks: Bit allocation reserves low 8 bits for machine-driver-specific quirks; collisions can silently misconfigure ports/features. Link-order packing supports seven entries only. Test signals include compile coverage for all macro users and runtime logging of decoded quirk masks.
