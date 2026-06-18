# sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_cirrus_common.c

Purpose: Shared helpers for Intel SOF boards using Cirrus Logic CS35L41/CS35L53 smart amplifiers.

Important APIs, types, and functions: `cs35l41_init()` adds four possible speaker widgets, pin controls, and routes for woofer/tweeter left/right positions. `cs35l41_hw_params()` obtains the BCLK from SOF topology with `sof_dai_get_bclk()`, sets each codec DAI/component sysclk to SCLK, and programs per-amplifier RX channel maps. `cs35l41_compute_codec_conf()` enumerates ACPI devices with HID `CSC3541` and UIDs 0 through 3, maps UIDs to prefixes `WL`, `WR`, `TL`, `TR`, fills component and codec_conf arrays, and returns the number of found amps. Exported `cs35l41_set_dai_link()` patches a generated amp link, while `cs35l41_set_codec_conf()` publishes codec prefixes on the card.

Control flow and integration: Machine drivers call these helpers after `sof_board_helpers` creates an amp link. Runtime hw_params configures clocks and channel maps for each active amp.

State and persistence: Static arrays hold component and prefix mapping data and are filled at runtime from ACPI. No persistent storage exists.

Dependencies: ASoC DAPM, SOF BCLK query, Cirrus codec DAI/component clock APIs, and ACPI device enumeration.

Risks: ACPI UID mapping is strict; missing physical nodes return zero codecs. Only two or four amps are expected, but an invalid count only warns before link setup uses that value. Test signals include ACPI enumeration logs, codec prefixes, per-amp channel routing, BCLK-derived sysclk, and playback on all speaker positions.
