# sources/distributed-fs/ceph-client/drivers/staging/media/tegra-video/vi.h

## Purpose
Declares the generic Tegra VI data model, SoC operation interface, channel/buffer structures, image data types, video format descriptors, controls, and cross-module helpers.

## Important APIs, Types, And Functions
`V4L2_CID_TEGRA_SYNCPT_TIMEOUT_RETRY` is a private camera-class control. `struct tegra_vi_ops` abstracts SoC-specific enable, syncpoint, format alignment, queue setup, and stream start/stop. `struct tegra_vi_soc` carries format tables, default format, ops, hardware revision, channel/clock limits, and H/V flip support. `struct tegra_vi_channel` owns the video device, vb2 queue, locks, syncpoints, capture kthreads, active format, offsets, buffer lists, port mapping, controls, format bitmaps, TPG mode, notifier, and flip flags. `struct tegra_channel_buffer` extends vb2 with DMA address and MW_ACK thresholds. `struct tegra_video_format` maps CSI data type/bit width/mbus code/bpp/hardware image format/fourcc.

## Control Flow
This header lets `vi.c` implement common V4L2 behavior while backend files install SoC ops and format tables. CSI and VIP code use helper declarations to find remote subdevices and control streaming.

## State And Persistence
All state is runtime kernel memory tied to channel/video-device lifetimes. Active V4L2 state is visible through ioctls while the node exists.

## Dependencies And Integration Points
Depends on host1x, V4L2, media entity, vb2, controls, waitqueues, spinlocks, and `csi.h`. Used across all Tegra video source files.

## Risks And Test Signals
The structure aggregates many lifetime domains, so cleanup ordering and lock usage matter. Port arrays are bounded by `GANG_PORTS_MAX`. Test signals are compile coverage across SoCs, control registration, ganged capture, and stream start/stop with concurrent queue operations.
