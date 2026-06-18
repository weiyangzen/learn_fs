# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/mtk_vcodec_dec.h

## Purpose
This decoder public header defines decoder limits, buffer-private structures, exported V4L2 ops, platform pdata symbols, and shared decoder helper prototypes.

## Important APIs, Types, And Functions
Constants define default/min/max dimensions, 4K capability flags, and decode success IRQ bit. `struct vdec_fb` describes a decoded frame buffer with Y and C plane memory and framebuffer status. `struct mtk_video_dec_buf` extends `v4l2_m2m_buffer` with state flags for capture-buffer ownership, queued state, errors, and a union of frame buffer or bitstream buffer. Externs expose ioctl/m2m/media ops and platform data for MT8173, MT8183, LAT single-core, and single-core variants. Helper prototypes cover hardware locking, queue initialization, default params, release, and vb2 callbacks.

## Control Flow
The header does not execute control flow. It defines the shared structures passed among the parent driver, common ioctl layer, stateful/stateless queue callbacks, and codec implementations.

## State, Persistence, And Dependencies
Buffer state is per-vb2 buffer and in memory only. Dependencies include vb2 core, V4L2 mem2mem, and decoder driver state.

## Integration Points
Used throughout decoder files and codec-specific `vdec` implementations. The platform-data externs are selected by OF match in the driver.

## Risks
`mtk_video_dec_buf`'s union means source and capture buffers interpret the same storage differently; queue type must be respected. Ownership flags are central to stateful reference-buffer recycling and are protected by context locks in call sites.

## Test Signals
Buffer lifecycle tests, stateful reference-buffer requeue tests, codec platform matching, and compile coverage of exported ops.
