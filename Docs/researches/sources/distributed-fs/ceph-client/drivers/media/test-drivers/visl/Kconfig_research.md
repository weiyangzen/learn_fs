# sources/distributed-fs/ceph-client/drivers/media/test-drivers/visl/Kconfig

## Purpose
`visl/Kconfig` exposes the Virtual Stateless Decoder Driver and its optional debugfs support.

## Important APIs, Types, and Functions
`CONFIG_VIDEO_VISL` is a tristate depending on `VIDEO_DEV` and selecting `FONT_SUPPORT`, `FONT_8x16`, `VIDEOBUF2_VMALLOC`, `V4L2_MEM2MEM_DEV`, `MEDIA_CONTROLLER`, and `VIDEO_V4L2_TPG`. `CONFIG_VISL_DEBUGFS` is a bool depending on `VIDEO_VISL` and `DEBUG_FS`, enabling debugfs bitstream dumps.

## Control Flow
When `VIDEO_VISL` is enabled, kbuild builds the VISL module from objects in the Makefile. If `VISL_DEBUGFS=y`, the debugfs object is added.

## State and Persistence
This file stores build configuration only. Runtime decoder and debugfs state are in the VISL source files outside this work item.

## Dependencies and Integration Points
VISL integrates with V4L2 mem2mem, media controller, vb2 vmalloc, TPG, and font support. It is used for stateless codec uAPI development and can run user-space decode loops without hardware.

## Risks and Edge Cases
Enabling debugfs can expose bitstream buffers for diagnostics and should be limited to debug/development kernels. The core driver selects several media facilities, which can enlarge minimal test kernels.

## Test Signals
Build with `VIDEO_VISL=m/y` and with `VISL_DEBUGFS=y/n`. Runtime tests should confirm module load, media/video node creation, mem2mem operation, and debugfs entries only when configured.
