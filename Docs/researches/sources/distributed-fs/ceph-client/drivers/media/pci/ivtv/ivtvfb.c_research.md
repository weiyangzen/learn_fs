# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtvfb.c

## Purpose
This file implements the `ivtvfb` fbdev driver for cx23415 on-screen display memory. It exposes decoder OSD memory as a Linux framebuffer, manages display modes, color maps, panning, blanking, vsync ioctls, large DMA writes, write-combining setup, and restore after firmware restart.

## Important APIs, Types, and Functions
Important structures are `struct osd_info` and `struct ivtv_osd_coords`. Key functions include framebuffer API wrappers for OSD coordinates and framebuffer memory, `ivtvfb_write`, `ivtvfb_ioctl`, `ivtvfb_set_var`, `_ivtvfb_check_var`, `ivtvfb_pan_display`, `ivtvfb_set_par`, `ivtvfb_setcolreg`, `ivtvfb_blank`, `ivtvfb_restore`, `ivtvfb_init_vidmode`, `ivtvfb_init_io`, `ivtvfb_init_card`, callback init/cleanup, and module init/exit.

## Control Flow
Module init finds the ivtv PCI driver and initializes eligible decoder-output cards. Card init checks PAT/write-combining policy, allocates `osd_info`, initializes ivtv firmware, obtains OSD framebuffer base, maps the framebuffer region, sets a default mode, registers fbdev, enables OSD output, allocates UDMA resources, and advertises V4L2 overlay capability. Writes use CPU copy for small/unaligned data and UDMA for large aligned transfers. Mode changes validate fb var settings, program pixel format/flicker/coordinates/window registers, and force YUV register updates.

## State and Persistence Behavior
It stores per-card OSD state in `itv->osd_info`, including physical/virtual framebuffer addresses, write-combining cookie, current mode, palette, blank state, pan offset, fb_info/fix/var data, and display geometry. It updates shared ivtv state such as `osd_video_pbase`, `osd_rect`, V4L2 overlay caps, `ivtvfb_restore`, and `yuv_info` OSD tracking fields.

## Dependencies and Integration Points
It depends on fbdev APIs, ivtv firmware/mailbox/UDMA/card infrastructure, SAA7127 video output, decoder memory mappings, arch write-combining helpers, V4L2 device iteration through the ivtv driver, and YUV overlay state.

## Risks
Mode validation must match hardware limits and TV standard timing. UDMA writes pin userspace pages and share the decoder DMA engine. Cleanup assumes `osd_info` exists for output-capable cards. PAT/write-combining policy can block initialization on x86_64. Framebuffer size is hardcoded to avoid overlap, so firmware/layout changes could invalidate assumptions.

## Test Signals
Test module load/unload with multiple ivtv cards, fbcon/fbset mode changes, 8/16/32 bpp color maps, panning, blank/unblank/powerdown, `FBIOGET_VBLANK`, `FBIO_WAITFORVSYNC`, large aligned and small unaligned writes, firmware restart restore, PAT policy, and V4L2 overlay capability toggling.
