## sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/matroxfb_crtc2.h

Purpose: `matroxfb_crtc2.h` defines the private secondary-head framebuffer state used by `matroxfb_crtc2.c`.

Important APIs and types: the main type is `struct matroxfb_dh_fb_info`. It contains a standalone `struct fb_info`, registration/initialization flags, a pointer to the primary `struct matrox_fb_info`, a video-memory descriptor with physical/virtual base, length, usable length, maximum length, offset from primary VRAM, and borrowed byte count, a shared MMIO descriptor, an `interlaced` bit, and a 16-entry pseudo-palette.

Control flow: no executable flow. The structure layout enables CRTC2 fbops to act like a separate fbdev while delegating lifetime, IRQ, output routing, and hardware access through the primary device.

State and persistence: this header defines all persistent per-secondary-fb software state. The `borrowed` field records how much primary usable VRAM was subtracted so deregistration can restore it. `offbase` is the hardware/programming link between the second fb's virtual screen and the shared physical framebuffer aperture.

Dependencies and integration points: includes `matroxfb_base.h` for `vaddr_t` and primary device state, plus `linux/ioctl.h`. `matroxfb_base.c` stores a pointer to this type opaquely in `minfo->crtc2.info`.

Risks: the structure shares MMIO and parent device lifetime rather than owning its own mappings, so stale secondary state after primary removal would be dangerous. Any layout changes must match `matroxfb_crtc2.c` assumptions around memory accounting, fbdev registration, and interlace panning.

Test signals: build with CRTC2 enabled, register/unregister secondary fb, and verify memory accounting fields through mode changes and module unload. Static checks should ensure no code treats the secondary `vbase` as independently iounmapped.
