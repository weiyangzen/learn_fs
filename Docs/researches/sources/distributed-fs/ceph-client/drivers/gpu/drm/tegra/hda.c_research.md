# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/hda.c

Purpose: parses Intel HDA format words from HDMI codec scratch registers into Tegra HDMI audio format state.

Important APIs/functions: `tegra_hda_parse_format()` decodes PCM/non-PCM, base sample rate, multiplier/divider, bit depth, and channel count into `struct tegra_hda_format`.

Control flow and state: the function is stateless except for filling the caller-provided format struct. HDMI IRQ handling calls it when HDA scratch0 reports a valid format, then reconfigures HDMI audio.

Dependencies/integration: depends on ALSA HDA verb bit definitions and is included by `hdmi.c`.

Risks: sample-rate calculation uses integer arithmetic in `fmt->sample_rate *= (mul + 1) / (div + 1)`, so divider values greater than multiplier can collapse to zero before multiplication. Invalid bit-depth fields trigger `WARN(1)` and fall back to 8 bits.

Test signals: unit-style tests for known HDA format words, especially 44.1/48 kHz families, non-PCM, multichannel, and invalid bit-depth encodings.
