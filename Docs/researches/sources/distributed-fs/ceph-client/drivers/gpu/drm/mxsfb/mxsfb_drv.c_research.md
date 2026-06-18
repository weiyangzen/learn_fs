# sources/distributed-fs/ceph-client/drivers/gpu/drm/mxsfb/mxsfb_drv.c

## Purpose
`mxsfb_drv.c` is the platform-driver and DRM setup for classic MXS/i.MX LCDIF/eLCDIF controllers. It handles device matching, SoC capability data, DRM allocation/registration, bridge attachment, IRQ installation, fb creation policy, and suspend/resume.

## Important APIs, Types, And Functions
The file defines `enum mxsfb_devtype` and `mxsfb_devdata[]` for V3, V4, and V6 register/capability differences: transfer-count/current/next-buffer offsets, hsync width encoding, overlay, CTRL2, and CRC32 support. Key functions are `mxsfb_probe`, `mxsfb_remove`, `mxsfb_shutdown`, `mxsfb_load`, `mxsfb_unload`, `mxsfb_attach_bridge`, IRQ helpers, and AXI clock wrappers. `mxsfb_fb_create()` rejects framebuffers whose pitch is not exactly width times bytes-per-pixel, matching hardware constraints.

## Control Flow, State, And Integration
Probe allocates a DRM device, loads private state based on `device_get_match_data`, removes conflicting framebuffers, registers the DRM device, and starts client setup. Load maps MMIO, gets clocks, sets a 32-bit DMA mask, enables runtime PM, initializes mode config and KMS, initializes vblank, attaches a panel/bridge, sets mode limits, requests IRQ under runtime PM, initializes polling, and stores driver data. The IRQ reads `LCDC_CTRL1`, handles frame-done vblank, optionally records CRC32 entries, clears the frame-done IRQ, and returns handled.

## State, Dependencies, Risks, And Tests
Private state holds devdata, MMIO, clocks, IRQ, CRTC/planes/encoder/connector/bridge, and `crc_active`. Dependencies include DRM GEM DMA, panel bridge, OF graph helpers, aperture conflict removal, PM runtime, and KMS code in `mxsfb_kms.c`. Risks include strict pitch rejection surprising userspace, connector acquisition as a documented bridge-API hack, IRQ cleanup requiring runtime clocks, and returning from `mxsfb_probe` without `drm_dev_put()` if aperture removal fails. Test signals include all compatible DT probes, simplefb handoff, vblank/CRC tests, panel bridge modesets, and suspend/resume.
