<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10-offsets.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10-offsets.h

## Purpose
`solo6x10-offsets.h` defines the SOLO SDRAM memory map used by display capture, encoder OSD, motion detection, G.723 audio, raw capture pages, encoder reference frames, MPEG4/H.264 output, and JPEG output.

## Important APIs, Types, and Functions
The header is macro-only. Key macros include `SOLO_DISP_EXT_ADDR/SIZE`, `SOLO_EOSD_EXT_ADDR_CHAN()`, `SOLO_MOTION_EXT_ADDR()`, `SOLO_G723_EXT_ADDR()`, `SOLO_CAP_EXT_ADDR()`, `SOLO_CAP_EXT_SIZE()`, `SOLO_EREF_EXT_ADDR()`, `SOLO_MP4E_EXT_ADDR/SIZE()`, `SOLO_JPEG_EXT_ADDR/SIZE()`, and `SOLO_SDRAM_END()`.

## Control Flow
There is no runtime control flow here. Callers evaluate the macros after `solo_dev` has type, channel count, and detected `sdram_size`. `solo_p2m_init()` validates `SOLO_SDRAM_END()` against detected SDRAM before higher-level capture/encode features rely on the map.

## State and Persistence
The layout is deterministic from `solo_dev->type`, `nr_chans`, and `sdram_size`. It does not persist state, but it defines where hardware and software share all frame/audio buffers.

## Dependencies and Integration Points
The macros are consumed by P2M DMA, live V4L2 display, encoder V4L2, G.723 audio, motion detection, and OSD code. They depend on constants from `solo6x10.h` such as `SOLO_DEV_6010` and channel counts.

## Risks and Edge Cases
The map uses `clamp()` to reserve minimum MPEG/JPEG regions, so small SDRAM devices can have constrained encoder space. `__SOLO_JPEG_MIN_SIZE` is defined twice with the same value, which is harmless but easy to trip over during maintenance. Any change to channel count or SDRAM detection can shift later regions and break DMA if not validated.

## Test Signals
Check `solo_p2m_init()` accepts the detected SDRAM size, display/audio/encoder offsets do not overlap, MPEG and JPEG wrap logic handles the computed sizes, and 32 MB cards still reserve a usable capture and encode layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10-offsets.h -->
