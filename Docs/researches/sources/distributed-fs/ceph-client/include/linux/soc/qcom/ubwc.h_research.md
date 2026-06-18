# sources/distributed-fs/ceph-client/include/linux/soc/qcom/ubwc.h

Purpose: This header defines Qualcomm Universal Bandwidth Compression configuration data and helpers for multimedia clients.

Important APIs/types/functions: `struct qcom_ubwc_cfg_data` stores UBWC mode flags, version, swizzle, macrotile, bank spread, and minimum access length data. Constants define swizzle enable levels and UBWC versions 1.0 through 6.0. Inline helpers return global config data and test individual fields such as UBWC mode, 64-byte min access length, macrotile mode, bank spread, and swizzle.

Control flow: Display, GPU, camera, or video drivers obtain config data and use helpers to select register programming for compressed buffers.

State and persistence: Config data is static SoC capability information. Hardware register programming in consumers persists until changed.

Dependencies and integration: Integrates with Qualcomm DRM, camera, video codecs, GPU/display memory format negotiation, and SoC data tables.

Risks and test signals: Wrong UBWC version or swizzle causes memory layout corruption. Test compressed framebuffer/video formats, SoC-specific config retrieval, fallback when no data is present, and cross-IP consistency.
