# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/hfi_platform_v6.c

This file defines static HFI v6 platform capabilities and frequency hints, and attaches the v6 buffer-requirement calculator. It advertises higher decode limits for H.264/HEVC/VP9, encoder support for H.264/HEVC/VP8, UBWC/10-bit formats where supported, and frequency rows used by PM scaling.

Key data are the `caps[]` table and `codec_freq_data[]`. Key functions mirror v4: `get_capabilities()`, `get_codecs()`, `get_codec_freq_data()`, `codec_vpp_freq()`, `codec_vsp_freq()`, and `codec_lp_freq()`. The exported `hfi_plat_v6` includes `.bufreq = hfi_plat_bufreq_v6`, making this platform responsible for calculated buffer requirements.

Control flow rejects lite cores by returning no capabilities/codecs/frequencies for `is_lite(core)`. For non-lite v6, `get_codecs()` returns fixed encoder and decoder bitmasks and count, while capability parsing copies eight entries into `core->caps`. Frequency lookup is keyed by V4L2 pixel format and session type.

State is immutable static table data copied into `venus_core`; buffer sizing state is delegated to `hfi_plat_bufs_v6.c`. Dependencies include `core.h`, `hfi_platform.h`, V4L2 formats, HFI codec/capability constants, and the v6 buffer calculator.

Risks include the hard-coded codec count, no lite fallback, and tight coupling with calculated buffer sizes. Advertising 8K decode or 10-bit formats without matching buffer formulas and PM votes can cause firmware stream failures. Test signals include v6 codec enumeration, 8K frame-size constraints, v6 `REQBUFS` sizes, PM frequency votes for VP8/VP9 VSP paths, and rejection/alternate handling of lite cores.
