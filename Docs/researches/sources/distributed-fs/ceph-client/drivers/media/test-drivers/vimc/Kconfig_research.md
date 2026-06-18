# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vimc/Kconfig

## Purpose
`vimc/Kconfig` exposes the Virtual Media Controller driver as `CONFIG_VIDEO_VIMC`.

## Important APIs, Types, and Functions
The option is a tristate named "Virtual Media Controller Driver (VIMC)". It depends on `VIDEO_DEV` and selects `FONT_SUPPORT`, `FONT_8x16`, `MEDIA_CONTROLLER`, `VIDEO_V4L2_SUBDEV_API`, `VIDEOBUF2_VMALLOC`, `VIDEOBUF2_DMA_CONTIG`, and `VIDEO_V4L2_TPG`.

## Control Flow
When enabled as built-in or module, the Makefile builds `vimc.o`, whose init path registers a virtual platform device and platform driver. The selected dependencies ensure the media graph, subdev active-state APIs, font-backed OSD, vb2 allocators, and test pattern generator are available.

## State and Persistence
Kconfig state persists in the kernel build configuration only. It does not create runtime state by itself.

## Dependencies and Integration Points
The dependency and select list matches the implementation: VIMC needs video device core, media controller topology, V4L2 subdev nodes, vmalloc or DMA-contig capture queues, and TPG/font support for sensor frames.

## Risks and Edge Cases
Because it selects features, enabling VIMC can pull in media-controller and buffer allocator code that test kernels might not otherwise include. The help text notes the topology is hard coded, so enabling it is primarily for testing and development.

## Test Signals
Build tests should verify `CONFIG_VIDEO_VIMC=m` and `=y`. Runtime smoke tests should confirm the module loads, creates a media device and video nodes, and exposes the expected hard-coded topology.
