<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/fbio.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/fbio.h

## Purpose
This header defines SPARC framebuffer ioctl constants and structures.

## Important APIs, Types, and Functions
It exposes framebuffer type, video mode, cursor/color-map, and device-specific ioctl data layouts used by SPARC framebuffer drivers and userspace.

## Control Flow
Userspace issues ioctls; framebuffer drivers copy these structures and apply display configuration or report state.

## State and Persistence Behavior
Persistent state is in framebuffer device settings and userspace ABI; the header has no state.

## Dependencies and Integration Points
It integrates SPARC framebuffer drivers, console support, and legacy userspace tools.

## Risks
This is ABI-facing; layout changes break existing tools. Copying unchecked structures can affect display stability.

## Test Signals
Run framebuffer ioctl smoke tests, console mode changes, color-map/cursor operations, and ABI structure-size checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/fbio.h -->
