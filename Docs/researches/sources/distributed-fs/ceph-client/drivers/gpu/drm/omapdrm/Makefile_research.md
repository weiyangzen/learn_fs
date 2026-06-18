# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/Makefile

## Purpose
Defines the OMAP DRM composite object and conditionally included DSS/output components.

## Important APIs, Types, And Functions
`omapdrm-y` lists core DRM, IRQ, CRTC, plane, overlay, encoder, framebuffer, GEM, DMM/TILER, TCM, and common DSS objects. Conditional entries add fbdev, DPI, VENC, SDI, DSI, HDMI common, HDMI4, CEC, and HDMI5 pieces.

## Control Flow
The kernel build links the selected objects into `omapdrm.o` when `CONFIG_DRM_OMAP` is enabled and adds `-DDEBUG` when OMAP DSS debug is configured.

## State, Persistence, And Dependencies
No runtime state exists here.

## Integration Points
Integrated with OMAP Kconfig options and the DRM driver build.

## Risks
Missing conditional dependencies can produce unresolved references. Optional outputs compile only when their Kconfig symbols are enabled.

## Test Signals
Builds across common OMAP configurations and compile-test variants are the main signal.
