# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/hfi_platform_v4.c

This file defines static Venus HFI v4 platform capabilities and frequency hints. It covers full and lite variants, advertising decode/encode codecs, frame limits, bitrates, profile levels, raw formats, dynamic buffer mode support, and per-codec frequency data.

Important data are the `caps[]` and `caps_lite[]` tables, `codec_freq_data[]`, and `codec_freq_data_lite[]`. Key functions are `get_capabilities()`, `get_codecs()`, `get_codec_freq_data()`, `codec_vpp_freq()`, `codec_vsp_freq()`, and `codec_lp_freq()`. The exported object is `hfi_plat_v4`.

Control flow is table selection by `is_lite(core)`. `get_capabilities()` returns either lite or full tables with entry count. `get_codecs()` walks selected capabilities and builds encoder/decoder bitmasks. Frequency lookup matches V4L2 pixel format and session type to VPP, VSP, and low-power frequency values. `hfi_plat_v4` does not provide a `bufreq` callback, so buffer sizing follows other firmware/helper paths.

The file owns immutable static data only. Its contents become persistent runtime state when copied into `core->caps` by `hfi_platform_parser()`. Dependencies include `core.h`, HFI constants, and V4L2 pixel format constants.

Risks include table incompleteness, lite/full mismatches, and frequency underestimation. If a codec appears in format lists but not frequency data, PM scaling can receive zero. Capability limits directly affect user-visible `TRY_FMT`, `ENUM_FRAMESIZES`, and controls. Test signals include full/lite codec enumeration, HEVC/VP9 10-bit format availability, max-resolution clamping, profile-level controls, and decode/encode throughput without clock under-voting.
