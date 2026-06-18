# sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_sdw_common.h

Purpose: Shared definitions for the Intel SOF SoundWire machine driver and its HDMI helper.

Important APIs, types, and functions: The header defines HDMI counts, CPU DAI limits, SoundWire bidirectional PDI base, group count, I2S SSP bit masks, deprecated compatibility quirk bits, BT offload quirk encoding, and `struct intel_mc_ctx`. The private context stores `struct sof_hdmi_private` and per-SoundWire-link pin indices. It declares `sof_sdw_hdmi_init()` and `sof_sdw_hdmi_card_late_probe()`.

Control flow and integration: `sof_sdw.c` embeds `intel_mc_ctx` in `asoc_sdw_mc_private->private`; link creation increments `sdw_pin_index` to name SDW CPU pins, while HDMI callbacks use the embedded HDMI state.

State and persistence: Defines in-memory context layout only. No persistent state.

Dependencies: Linux bits/types, ASoC, SoundWire utility interfaces, and shared SOF HDMI private data.

Risks: Quirk bit definitions must not collide with SoundWire utility quirk bits. Deprecated flags still appear in logs and quirk tables, so new behavior must not accidentally rely on removed semantics. Test signals include build coverage and correct pin numbering across multi-link SoundWire cards.
