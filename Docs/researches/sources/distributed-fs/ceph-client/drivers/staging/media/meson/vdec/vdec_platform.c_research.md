# Research: sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/vdec_platform.c

Purpose: defines per-SoC Amlogic VDEC format capability tables and exports `struct vdec_platform` instances for GXBB, GXL, GXLX, GXM, G12A, and SM1 revisions. It is the central source of supported compressed pixelformats, limits, firmware names, decoder engine ops, codec ops, capture formats, and V4L2 flags.

Important APIs/types: static `struct amvdec_format` arrays describe each source codec entry. Each entry sets `.pixfmt`, buffer bounds, max resolution, `.vdec_ops` (`vdec_1_ops` or `vdec_hevc_ops`), `.codec_ops` (`codec_h264_ops`, `codec_mpeg12_ops`, `codec_vp9_ops`), firmware path, capture pixfmt list, and compressed/dynamic-resolution flags. The exported `vdec_platform_*` constants point at those arrays and set `enum vdec_revision`.

Control flow: no executable flow beyond module firmware declarations. Probe code elsewhere selects the platform instance from OF data; format negotiation then iterates the table to expose V4L2 capabilities and choose the engine/backend for sessions.

State and persistence: immutable static tables only. Firmware paths are persistent ABI-like strings because userspace/kernel packaging must provide those blobs.

Dependencies/integration: includes `vdec_platform.h`, `vdec.h`, engine headers, and codec headers. Integrates with firmware packaging through `MODULE_FIRMWARE()` declarations and with runtime power quirks through the revision consumed by `vdec_hevc.c`.

Risks: capability drift is easy because entries duplicate MPEG/H264/VP9 limits and firmware names across SoCs. VP9 uses the HEVC hardware ops while H264/MPEG use `vdec_1_ops`; wrong pairing would fail at firmware or register level. SM1 VP9 points to `sm1_vp9_mmu.bin`, unlike older VP9 firmware. Missing `V4L2_FMT_FLAG_DYN_RESOLUTION` for formats that can change resolution would affect userspace behavior.

Test signals: enumerate formats per compatible SoC, request each firmware named by the table, decode H264/MPEG2/VP9 samples at table max and boundary resolutions, and verify dynamic resolution events for H264/VP9 entries only.
