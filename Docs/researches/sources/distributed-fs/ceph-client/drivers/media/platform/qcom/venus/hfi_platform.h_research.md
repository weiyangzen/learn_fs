# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/hfi_platform.h

This header defines the platform capability model used by the Venus HFI driver. It provides fixed-size arrays and callback contracts for codec support, format support, capability ranges, profile levels, performance frequencies, and platform-specific buffer requirements.

Important types are `struct raw_formats`, `struct hfi_plat_caps`, `struct hfi_platform_codec_freq_data`, and `struct hfi_platform`. Constants such as `MAX_PLANES`, `MAX_FMT_ENTRIES`, `MAX_CAP_ENTRIES`, `MAX_ALLOC_MODE_ENTRIES`, `MAX_CODEC_NUM`, and `MAX_SESSIONS` bound parser and table storage. Externs declare `hfi_plat_v4` and `hfi_plat_v6`; functions expose platform lookup, frequency lookup, and codec enumeration.

Control flow is callback-driven. `hfi_parser.c` asks the platform for static capabilities; PM code asks for codec frequencies; v6 platform uses the `bufreq` callback to compute requirements. `hfi_plat_caps.valid` is specifically documented as Venus v1xx parser state, while static v4/v6 tables are copied wholesale into `core->caps`.

State ownership is external: the header describes data copied into `venus_core` and read by `venus_inst` helpers. Dependencies include V4L2 pixel formats, `hfi.h`, `hfi_helper.h`, and `hfi_plat_bufs.h`.

Risks include fixed-array truncation and semantic mismatch between V4L2 pixel formats and HFI codec masks. Adding codecs or formats requires updating max constants, parser bounds, and platform tables together. Test signals are complete enum-format output, profile/level controls, frame-size limits, PM frequency scaling, and v6 buffer requirements for all advertised codecs.
