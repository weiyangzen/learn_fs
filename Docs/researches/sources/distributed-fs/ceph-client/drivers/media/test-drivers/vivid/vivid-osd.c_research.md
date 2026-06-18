# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-osd.c

Purpose: implements optional framebuffer-backed on-screen display/overlay support for Vivid. It allocates a small 16-bit framebuffer, registers it with fbdev, initializes display mode/fix information, provides color maps and simple ioctls, and supplies helpers used by video loopback overlay blending.

Important APIs and functions: exported APIs are `vivid_fb_init`, `vivid_fb_deinit`, `vivid_fb_clear`, and `vivid_fb_green_bits`. Internal framebuffer operations include `vivid_fb_ioctl`, `vivid_fb_check_var`, `vivid_fb_set_par`, `vivid_fb_setcolreg`, `vivid_fb_pan_display`, and `vivid_fb_blank`. Initialization helpers are `vivid_fb_init_vidmode` and `vivid_fb_release_buffers`.

Control flow: `vivid_fb_init` allocates `video_vbase`, stores a physical address via `virt_to_phys`, initializes a 720x576 16-bit mode, clears the framebuffer with color bars, registers the framebuffer, and applies parameters. The fbdev callbacks validate/normalize mode requests, update stride and fixed info, manage pseudo-palette entries, handle `FBIOGET_VBLANK`, and ignore blanking. `vivid_fb_deinit` unregisters fbdev and frees the cmap, palette, and backing buffer.

State and persistence: framebuffer memory and fbdev state are volatile per device. `video_vbase`, `video_pbase`, display dimensions, byte stride, `fb_info`, `fb_defined`, and `fb_fix` live in `struct vivid_dev`. Pixel contents persist until cleared or overwritten by fbdev userspace.

Dependencies and integration points: depends on Linux fbdev APIs, V4L2 device logging, Vivid core, and video loopback code that reads `video_vbase` for OSD blending. Header stubs make this optional under `CONFIG_VIDEO_VIVID_OSD`.

Risks: fbdev is optional and legacy; configurations without `CONFIG_VIDEO_VIVID_OSD` use stubs. `virt_to_phys` on kmalloc memory is only suitable for this synthetic test use and is not a real hardware mapping. The code only supports 16-bit RGB555/RGB565 and ignores most mode changes and blanking requests. `vivid_fb_deinit` assumes the framebuffer was registered.

Test signals: build with and without `CONFIG_VIDEO_VIVID_OSD`, framebuffer registration/removal, fbset/fbdev mmap or write tests, clear-framebuffer control, overlay loopback rendering, palette updates, and unload leak checks validate the module.
