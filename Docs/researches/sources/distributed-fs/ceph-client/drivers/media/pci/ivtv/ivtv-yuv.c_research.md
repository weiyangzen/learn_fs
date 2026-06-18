# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-yuv.c

## Purpose
This file implements YUV playback support for cx23415 output. It manages firmware YUV buffer slots, userspace DMA into decoder memory, frame geometry/lacing decisions, cropping/scaling calculations, hardware register programming, vsync-driven display advancement, and cleanup/restoration.

## Important APIs, Types, and Functions
Public symbols are `yuv_offset`, `ivtv_yuv_filter_check`, `ivtv_yuv_work_handler`, `ivtv_yuv_frame_complete`, `ivtv_yuv_setup_stream_frame`, `ivtv_yuv_udma_stream_frame`, `ivtv_yuv_prep_frame`, and `ivtv_yuv_close`. Important internals include `ivtv_yuv_prep_user_dma`, `ivtv_yuv_filter`, horizontal/vertical register handlers, window setup, initialization, next-free frame selection, frame setup, and per-frame UDMA.

## Control Flow
Frame setup chooses a buffer slot, snapshots source/destination geometry, decides progressive/interlaced treatment, and marks whether register updates are needed. UDMA pins Y and UV user planes, builds an SG list targeting the selected decoder YUV buffer and optional blanking region, starts UDMA, waits for completion, unmaps, and advances fill state. Vsync IRQ code advances displayed frame and queues `ivtv_yuv_work_handler`, which clamps/crops against the OSD-visible window and writes horizontal/vertical scaler registers and filters.

## State and Persistence Behavior
The file mutates `itv->yuv_info`: frame indices, frame info rings, old register snapshots, filter selections, OSD tracking geometry, blanking buffer mapping, lacing thresholds/modes, forced-update flags, and running state. It also changes decoder MMIO registers and restores snapshots on close.

## Dependencies and Integration Points
It depends on UDMA helpers, IRQ vsync/decode data request paths, ioctl/private YUV DMA commands, stream decode setup, OSD/framebuffer geometry, decoder memory offsets, and firmware filter tables.

## Risks
The register programming is hardware-specific and full of rounding/fudge factors. Geometry can become invalid after crop/scale and must blank output safely. Y/UV split and blanking offsets must match firmware buffer layout. Cleanup must restore registers so MPEG playback works afterward. UDMA wait logic must handle signals without leaking pinned pages.

## Test Signals
Test private DMA frames, streaming YUV writes, PAL/NTSC output, progressive/interlaced/auto lacing, OSD tracking and panning, extreme crop/scale ratios, invalid tiny windows, repeated start/close register restoration, filter-table validation, and signal interruption during UDMA.
