# sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6dsp-common.c

Purpose: `q6dsp-common.c` provides shared audio channel helper functions used by QDSP6 drivers.

Important APIs and types: `q6dsp_map_channels` fills an eight-entry PCM channel map for 1, 2, 3, 4, 5, 6, or 8 channels using QDSP6 channel position constants. `q6dsp_get_channel_allocation` returns HDMI CEA-861-E channel allocation values for 2 through 8 channels.

Control flow: both functions are simple switch tables. Unsupported channel counts return `-EINVAL`. `q6dsp_map_channels` clears the map before filling supported entries.

State and persistence: no state. Outputs are caller-provided arrays or return values.

Dependencies and integration points: exports are used by ASM media-format setup and APM/HDMI DAI setup. The implementation depends on constants from `q6dsp-common.h` and Linux errno/string helpers.

Risks: 7-channel PCM mapping is unsupported while HDMI allocation accepts 7 channels. The 6/8-channel map orders LFE before FC, matching this DSP expectation but potentially surprising to generic ALSA users. HDMI allocation table is fixed to the comment's CEA mapping and does not include every possible speaker layout.

Test signals: unit-style tests for every supported channel count, unsupported channel counts, zeroed trailing channel map entries, and expected HDMI allocation bytes.
