# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/hda.h

Purpose: declares HDMI/HDA audio format data used by Tegra HDMI and the HDA parser.

Important APIs/types: `struct tegra_hda_format` contains sample rate, channel count, bit depth, and PCM flag. `tegra_hda_parse_format()` is exported to HDMI code.

Control flow and state: the structure is embedded in `struct tegra_hdmi` and is updated by codec callbacks or HDA scratch IRQs.

Dependencies/integration: includes Linux types and is consumed by `hda.c` and `hdmi.c`.

Risks: no validity flags are included, so users infer validity from fields such as nonzero sample rate.

Test signals: compile coverage and HDMI audio configuration tests that verify struct contents after format parsing.
