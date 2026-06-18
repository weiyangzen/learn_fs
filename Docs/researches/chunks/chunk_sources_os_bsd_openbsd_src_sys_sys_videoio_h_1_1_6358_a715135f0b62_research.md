# Chunk Research: sources/os/bsd/openbsd-src/sys/sys/videoio.h lines 1-6358

## Scope

This chunk covers lines 1-6358 of OpenBSD's `sys/sys/videoio.h`, a public V4L2-compatible video device ABI header. The full file has 6403 lines; this chunk includes the license/header guard, inlined Linux V4L2 common/control definitions, most public V4L2 data structures, format IDs, state/control flags, helper macros, the single inline timestamp helper, and ioctl command definitions through `VIDIOC_TRY_ENCODER_CMD`. Lines after 6358 continue the ioctl list and close the header.

## Purpose and API Surface

The header exposes a user/kernel ABI for video, radio, SDR, touch, metadata, codec, and media-control style devices. It is declaration-heavy: it defines constants, enums, structure layouts, unions, packed ABI payloads, and ioctl request numbers rather than implementing driver logic.

Major exported areas in this chunk:

- Selection and EDID API: `V4L2_SEL_TGT_*`, `V4L2_SEL_FLAG_*`, compatibility aliases, and `struct v4l2_edid`.
- Control classes and IDs: user, codec, camera, FM TX/RX, flash, JPEG, image source/processing, DV, RF tuner, detection, stateless codec, and colorimetry control namespaces.
- Codec control payloads: stateful MPEG/H.26x/VPx/HEVC/AV1 controls and stateless decode parameter structs for H.264, FWHT, VP8, MPEG-2, HEVC, VP9, and AV1.
- Core V4L2 stream model: buffer types, memory types, fields, colorspace/transfer/YCbCr/HSV/quantization enums, capability flags, pixel format structures, buffer queue structures, and stream parameter structures.
- Format identifiers: a large catalog of `v4l2_fourcc()` and `v4l2_fourcc_be()` pixel/data format constants for RGB, greyscale, YUV, Bayer, tiled, compressed codec streams, vendor formats, SDR, touch, and metadata payloads.
- Device discovery and configuration structs: capability, format enumeration, frame size/interval enumeration, standards, DV timings/caps, input/output descriptors, tuning/modulator/frequency structs, audio/audioout structs, VBI and sliced VBI structs.
- Event/debug/buffer-management structs: event payloads/subscription, debug chip/register payloads, create/remove buffer payloads.
- Ioctl request definitions through line 6358: query capability, enum/get/set/try format, buffer queueing, streaming, standards, controls, tuner/audio, EDID, crop/selection, extended controls, frame size/intervals, encoder commands, and the start of the advanced-debug ioctl section.

## Dependencies and ABI Assumptions

The header includes OpenBSD system headers `sys/time.h`, `sys/types.h`, and `sys/ioccom.h`. It depends on OpenBSD integer typedefs such as `u_int8_t`, `u_int16_t`, `u_int32_t`, and `u_int64_t`, `struct timeval`, `struct timespec`, ioctl encoding macros `_IO`, `_IOR`, `_IOW`, `_IOWR`, and compiler support for `__attribute__((packed))`.

The file inlines material from Linux `v4l2-common.h` and `v4l2-controls.h`, but adapts it to OpenBSD-style public headers. `__user` is defined empty when not already present, so user-pointer annotations remain syntactically available without requiring Linux headers. Several payload structs use raw user pointers, for example `struct v4l2_ext_control`, `struct v4l2_buffer`, `struct v4l2_clip`, and `struct v4l2_window`; kernel ioctl handlers must validate/copy those addresses.

Macros such as `_BITUL()` and `GENMASK()` are referenced in the FWHT flag block. They are not defined in this chunk, so consumers must receive them from other OpenBSD headers or from earlier compatibility definitions in the effective include graph. This is a visible dependency risk if the header is compiled standalone outside its intended environment.

## Control Flow and State

There is almost no executable control flow. The only function body in this chunk is:

- `static inline u_int64_t v4l2_timeval_to_ns(const struct timeval *tv)`, which converts seconds and microseconds to nanoseconds.

All other behavior is encoded as ABI state machines and ioctl payload contracts:

- Buffer lifecycle state is represented by `struct v4l2_requestbuffers`, `struct v4l2_buffer`, `struct v4l2_plane`, `struct v4l2_exportbuffer`, `struct v4l2_create_buffers`, and `struct v4l2_remove_buffers`, plus flags such as `V4L2_BUF_FLAG_MAPPED`, `QUEUED`, `DONE`, `ERROR`, `IN_REQUEST`, `PREPARED`, `LAST`, and timestamp/source masks.
- Streaming control is exposed by `VIDIOC_REQBUFS`, `QUERYBUF`, `QBUF`, `DQBUF`, `EXPBUF`, `STREAMON`, `STREAMOFF`, `PREPARE_BUF`, and `CREATE_BUFS`; actual queue transitions are implemented by drivers, not this header.
- Control state is represented by scalar `struct v4l2_control`, compound `struct v4l2_ext_control`, batches in `struct v4l2_ext_controls`, query descriptors, control IDs, control types, and flags like disabled/read-only/write-only/volatile/dynamic-array.
- Codec decode state is represented in userspace-supplied parameter structs: H.264 SPS/PPS/scaling/prediction/slice/decode params, DPB entries, HEVC SPS/PPS/slice/decode/RPS params, VP8/VP9 segmentation/filter/probability structs, MPEG-2 sequence/picture/quantisation structs, FWHT params, AV1 sequence/tile/frame/film grain structs.
- Device signal/input/output state is represented by standards bitmasks, input/output status/capability bits, tuner/modulator frequency ranges, RDS blocks, DV timing capabilities, events, and debug register payloads.

## Data Model Highlights

The ABI is heavily union-based. `struct v4l2_format` dispatches on `type` to image, multi-plane image, overlay window, VBI, sliced VBI, SDR, metadata, or raw data layouts. `struct v4l2_streamparm` dispatches capture vs output timing parameters. `struct v4l2_ext_control` dispatches scalar, string, raw pointer, and many codec/control-specific payload pointers.

Several structures are explicitly packed to preserve Linux-compatible layouts across compilers and platforms, including many codec/control/query/VBI/timing payloads. Reserved arrays are common and comments repeatedly require applications and drivers to zero them; this is central to forward compatibility.

Pixel and metadata formats are represented by FourCC constants. This chunk defines the helper macros `v4l2_fourcc()` and `v4l2_fourcc_be()` and then enumerates many formats. The big-endian helper sets bit 31, so code comparing or serializing FourCC values must preserve that flag.

Colorimetry defaults are specified by mapping macros:

- `V4L2_MAP_COLORSPACE_DEFAULT`
- `V4L2_MAP_XFER_FUNC_DEFAULT`
- `V4L2_MAP_YCBCR_ENC_DEFAULT`
- `V4L2_MAP_QUANTIZATION_DEFAULT`

These macros are simple nested conditional expressions and do not validate enum values.

## Risks and Edge Cases

- ABI layout risk: this is a public ioctl ABI header. Changes to field sizes, ordering, packing, or enum/control IDs can break existing userland or driver compatibility.
- Pointer-width risk: structures contain `unsigned long` and pointers in ioctl payload unions. Compatibility layers for 32-bit userland on 64-bit kernels must translate them carefully; a comment after this chunk's boundary explicitly reminds maintainers to update Linux compat ioctl handling when adding ioctls.
- User pointer risk: `__user` is empty here, so static analysis cannot rely on the annotation in OpenBSD builds. Kernel code must still treat all user pointers as untrusted.
- Reserved-field risk: many structs require reserved fields to be zero. Drivers should reject or ignore nonzero reserved bits consistently to avoid ABI ambiguity and future-extension conflicts.
- Bitmask collision risk: aliases and deprecated definitions are intentionally retained, for example MPEG-to-codec control aliases, old selection aliases, tuner language/SAP aliases, deprecated colorspace names, and later compatibility capabilities. Consumers should avoid interpreting aliases as independent capabilities.
- Macro dependency risk: `_BITUL()` and `GENMASK()` appear in this header region but are not defined in this chunk. If not supplied by included headers, FWHT flag definitions will not compile.
- Range/array risk: stateless codec structs contain large fixed arrays and dynamic-array control comments. Drivers must validate `size`, `count`, dimensions, and control type before trusting user payloads.
- Time conversion risk: `v4l2_timeval_to_ns()` performs unchecked arithmetic; extreme `tv_sec` values can overflow `u_int64_t`, though normal V4L2 timestamps should not approach that range.

## Cross-Chunk References

This is chunk 1 and ends at line 6358 after `VIDIOC_TRY_ENCODER_CMD` and before the remaining ioctl definitions. The next chunk or merge step must account for the continuation of the ioctl block: debug register ioctls, hardware frequency seek, DV timing/event subscription/ioctl definitions, create/prepare/selection/decoder/frequency-band/chip-info/query-ext/remove-buffer ioctls, `BASE_VIDIOC_PRIVATE`, deprecated compatibility aliases, `V4L2_CAP_ASYNCIO`, and the closing header guard.

Within this chunk, comments reference external implementation files and Linux/OpenBSD driver layers not present here, including V4L2 core ioctl compatibility handling, codec specifications, device-tree SDTV standard bindings, media controller/subdevice conventions, and driver-specific control namespaces. Those are integration references rather than local definitions.

## Research Notes

Read scope: complete line range 1-6358. This report is intentionally a chunk report only and does not create or replace the merged per-file report at `Docs/researches/sources/os/bsd/openbsd-src/sys/sys/videoio.h_research.md`.