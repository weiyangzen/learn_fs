# sources/distributed-fs/ceph-client/include/video/omapvrfb.h

## Purpose
`omapvrfb.h` exposes the OMAP VRFB rotation-engine interface used to map framebuffer memory at multiple rotation angles.

## Important APIs, Types, and Functions
`OMAP_VRFB_LINE_LEN` is 2048. `struct vrfb` stores context id, four virtual and physical angle views, resolution, offsets, bytes per pixel, and YUV mode. With `CONFIG_OMAP2_VRFB`, APIs include support check, context request/release, size adjustment, minimum physical size, maximum height, setup, angle mapping, and context restore. Without the option, inline stubs return safe defaults or no-op.

## Control Flow
Callers check support, request a VRFB context, adjust dimensions to VRFB alignment, allocate enough physical memory, call setup with physical base and geometry, map a requested rotation angle, use the selected rotated view for display or blit, and release the context during teardown. Resume paths call restore context.

## State and Persistence Behavior
VRFB context state is in `struct vrfb` and hardware mapping registers. It persists while the context is allocated and must be restored after suspend or hardware reset. Stub builds provide no real hardware state.

## Dependencies and Integration Points
It integrates OMAP fbdev/DSS rotation paths with a SoC-specific memory remapping engine. It depends on MMIO pointer types and is often used with overlay rotation settings in OMAP display code.

## Risks and Test Signals
Risks include treating stub success as real rotation support, underallocating physical memory due to alignment, invalid rotation indices, context leaks, and missing restore after resume. Test signals include all four rotation angles, YUV and RGB modes, max-height/min-size calculations, suspend/resume restore, context exhaustion, and builds without `CONFIG_OMAP2_VRFB`.
