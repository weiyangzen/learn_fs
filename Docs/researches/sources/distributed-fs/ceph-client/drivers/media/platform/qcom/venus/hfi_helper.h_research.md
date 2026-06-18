# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/hfi_helper.h

## Purpose
`hfi_helper.h` is the shared HFI ABI vocabulary for Venus: error codes, events, buffer flags, flush modes, extradata IDs, property IDs, codec/profile/level constants, buffer types/modes, HFI versions, and payload structures for properties, capabilities, formats, resources, and packet headers.

## Important Constants And Types
- HFI domains, architecture offsets, command/message offsets, and `enum hfi_version`.
- Error codes for system and session failures, plus special stream errors.
- Event IDs for system/session error, sequence changed, property changed, LTR failure, and buffer-reference release.
- Buffer flags such as EOS, sync frame, codec config, readonly, EOSEQ, corruption/drop/discontinuity flags.
- Flush constants, extradata constants, interlace constants, property IDs for common/VDEC/VENC/VPE system, param, and config spaces.
- Codec/profile/level maps for H.264, H.263, MPEG2/4, VC1, VP8/VP9, HEVC, DivX.
- Buffer types and version-sensitive macros for scratch/extradata buffer IDs.
- Property structs for debug, UBWC, enable, frame size/rate, profile/level, bitrate, QP, HDR10, work mode/route, raw plane constraints, codec capabilities, buffer requirements, resources, image version, sequence header, color conversion, and packet headers.
- Inline accessors for `struct hfi_buffer_requirements` compensate for HFI 4xx member swaps.

## Control Flow And Integration
This header contains no executable flow beyond inline accessors. It is included by HFI packet builders, message parsers, helpers, platform capability code, and core state definitions. It provides the constants that map V4L2 controls and formats to firmware properties and the structs that are copied into or out of HFI packets.

## State And Persistence
No runtime state. All definitions are compile-time ABI descriptions. The firmware image version string may be carried in `struct hfi_property_sys_image_version_info_type` and later stored in `venus_core`.

## Dependencies
Relies on kernel integer types, flexible arrays, and `__counted_by` annotations. It is tightly coupled to Qualcomm Venus firmware ABI versions.

## Risks And Edge Cases
- Numeric constants are firmware ABI; a single wrong value can make controls, buffers, or events silently misbehave.
- Some property IDs alias by HFI generation, such as QP range and MPEG4 time resolution, so version-specific packet code must choose carefully.
- HFI 4xx buffer-requirement member swaps require using inline accessors; direct field access can be wrong on that generation.
- Many DMA/device addresses in HFI structs are `u32`, requiring SoC DMA masks and firmware memory maps to stay below limits.

## Test Signals
- Compile tests across all HFI versions and platform files.
- Runtime parsing and property setup across generations, especially HFI 4xx buffer requirements and HFI 6xx constraints.
- V4L2 control tests for every mapped profile/level/rate-control/QP/HDR/format property.
