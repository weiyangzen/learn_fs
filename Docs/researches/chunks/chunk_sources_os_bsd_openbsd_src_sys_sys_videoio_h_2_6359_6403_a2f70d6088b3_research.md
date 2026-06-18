# Chunk Research: sources/os/bsd/openbsd-src/sys/sys/videoio.h lines 6359-6403

## Scope

This chunk covers the final 45 lines of OpenBSD's `sys/sys/videoio.h`. It completes the public V4L2-compatible ioctl request-number block, reserves the private ioctl range, keeps two deprecated pixel-format aliases for source compatibility, defines a deprecated/unimplemented capability bit, and closes the `_SYS_VIDEOIO_H_` header guard.

The chunk is declaration-only. It does not implement driver behavior, but it is ABI-significant because these macros encode ioctl command numbers, direction bits, and payload structure types.

## APIs and ABI Surface

The exported ioctl macros in this chunk all use OpenBSD ioctl encoding macros from `sys/ioccom.h` with ioctl group `'V'`:

- Advanced debug register access: `VIDIOC_DBG_S_REGISTER` uses `_IOW('V', 79, struct v4l2_dbg_register)`, while `VIDIOC_DBG_G_REGISTER` uses `_IOWR('V', 80, struct v4l2_dbg_register)`.
- Hardware frequency seek: `VIDIOC_S_HW_FREQ_SEEK` writes `struct v4l2_hw_freq_seek`.
- Digital video timings: `VIDIOC_S_DV_TIMINGS`, `VIDIOC_G_DV_TIMINGS`, `VIDIOC_ENUM_DV_TIMINGS`, `VIDIOC_QUERY_DV_TIMINGS`, and `VIDIOC_DV_TIMINGS_CAP`.
- Event queue API: `VIDIOC_DQEVENT`, `VIDIOC_SUBSCRIBE_EVENT`, and `VIDIOC_UNSUBSCRIBE_EVENT`.
- Buffer lifecycle extensions: `VIDIOC_CREATE_BUFS`, `VIDIOC_PREPARE_BUF`, and `VIDIOC_REMOVE_BUFS`.
- Selection/cropping replacement API: `VIDIOC_G_SELECTION` and `VIDIOC_S_SELECTION`.
- Decoder command API: `VIDIOC_DECODER_CMD` and `VIDIOC_TRY_DECODER_CMD`.
- Frequency band enumeration: `VIDIOC_ENUM_FREQ_BANDS`.
- Debug chip discovery: `VIDIOC_DBG_G_CHIP_INFO`, marked experimental/debug/internal.
- Extended control query: `VIDIOC_QUERY_EXT_CTRL`.

The chunk also exports `BASE_VIDIOC_PRIVATE` as `192`, documenting that ioctl numbers `192-255` are private. `V4L2_PIX_FMT_HM12` maps to `V4L2_PIX_FMT_NV12_16L16`, and `V4L2_PIX_FMT_SUNXI_TILED_NV12` maps to `V4L2_PIX_FMT_NV12_32L32`. `V4L2_CAP_ASYNCIO` is kept at `0x02000000`, but the comment says this capability was never implemented.

## Control Flow and State

There is no executable control flow in this chunk. The visible behavior is encoded as ioctl ABI contracts:

- `_IOW` commands represent userland-to-kernel input payloads.
- `_IOR` commands represent kernel-to-user output payloads.
- `_IOWR` commands represent bidirectional payloads.

The state surfaces named here are owned by V4L2 drivers or core ioctl handling: debug register state, tuner seek state, DV timing state, event subscriptions and event queue contents, buffer allocation/preparation/removal state, selection rectangles, decoder command state, frequency band inventory, debug chip metadata, and extended-control metadata.

## Dependencies

These macros depend on definitions earlier in the same header and on included system headers:

- `_IO`, `_IOR`, `_IOW`, and `_IOWR` from `sys/ioccom.h`.
- Payload structs such as `struct v4l2_dbg_register`, `struct v4l2_hw_freq_seek`, `struct v4l2_dv_timings`, `struct v4l2_event`, `struct v4l2_create_buffers`, `struct v4l2_buffer`, `struct v4l2_selection`, `struct v4l2_decoder_cmd`, `struct v4l2_frequency_band`, `struct v4l2_dbg_chip_info`, and `struct v4l2_query_ext_ctrl`.
- Alias targets `V4L2_PIX_FMT_NV12_16L16` and `V4L2_PIX_FMT_NV12_32L32`, defined earlier as tiled NV12 FourCC values.

The comment at lines 6389-6390 references Linux's `drivers/media/v4l2-core/v4l2-compat-ioctl32.c`; this OpenBSD header preserves that imported-maintenance warning even though the file is not local to this header.

## Risks and Edge Cases

- ABI stability risk: ioctl numbers, directions, and payload structure types are public ABI.
- Compatibility-layer risk: 32-bit ioctl compatibility handling matters because many V4L2 payload structs contain pointers, `unsigned long`, unions, or layout-sensitive reserved fields.
- Debug ioctl exposure risk: debug register and chip-info ioctls are experimental/internal and require privilege checks in handlers.
- Private ioctl collision risk: `BASE_VIDIOC_PRIVATE` reserves `192-255`; private driver commands outside that range can collide with public ABI.
- Deprecated alias risk: `V4L2_PIX_FMT_HM12` and `V4L2_PIX_FMT_SUNXI_TILED_NV12` are aliases, not distinct formats.
- Dead capability risk: `V4L2_CAP_ASYNCIO` has a bit value but is documented as never implemented.

## Cross-Chunk References

This chunk continues directly from chunk 1, which defined the required payload structs, FourCC constants, capability bits, and ioctl commands through `VIDIOC_TRY_ENCODER_CMD` at line 6352. The advanced-debug comment that governs `VIDIOC_DBG_S_REGISTER` and `VIDIOC_DBG_G_REGISTER` begins in chunk 1 at lines 6354-6358 and terminates immediately before this chunk's first macro.

The final merged per-file report should connect this tail section to the earlier buffer, event, selection, DV timing, frequency, debug, and extended-control structure definitions. This chunk intentionally does not create or replace the per-file report at `Docs/researches/sources/os/bsd/openbsd-src/sys/sys/videoio.h_research.md`.

## Research Notes

Read scope: complete line range 6359-6403, with adjacent context from lines 6320-6358 used only to confirm ioctl-list continuity and the comment applying to the debug register ioctls. Scope is within `Docs/research_subset_a.md`.