# sources/distributed-fs/ceph-client/include/uapi/linux/fb.h

This header defines the legacy Linux framebuffer userspace ABI. It exposes framebuffer ioctls, fixed and variable screen information, color maps, console-to-framebuffer mapping, vblank status, drawing helper structures, hardware cursor structures, visual/type/acceleration constants, blanking modes, and backlight constants.

Important exports include ioctls `FBIOGET_VSCREENINFO`, `FBIOPUT_VSCREENINFO`, `FBIOGET_FSCREENINFO`, `FBIOGETCMAP`, `FBIOPUTCMAP`, `FBIOPAN_DISPLAY`, `FBIO_CURSOR`, `FBIOGET_CON2FBMAP`, `FBIOPUT_CON2FBMAP`, `FBIOBLANK`, `FBIOGET_VBLANK`, and `FBIO_WAITFORVSYNC`. Key structures are `struct fb_fix_screeninfo`, `fb_var_screeninfo`, `fb_bitfield`, `fb_cmap`, `fb_con2fbmap`, `fb_vblank`, `fb_copyarea`, `fb_fillrect`, `fb_image`, and `fb_cursor`.

Control flow is character-device ioctl and mmap based: applications open `/dev/fbN`, query fixed and variable mode state, set modes/panning/blanking/colormaps/cursors, optionally wait for vblank, and mmap framebuffer memory for drawing. Runtime state lives in fbdev driver mode objects, hardware registers, console binding, mmapped VRAM, colormaps, and cursor state. Persistence is hardware/display state and fbdev driver lifetime; some settings may persist until mode reset or close but are not durable storage.

Dependencies include `linux/types.h`, `linux/i2c.h`, `linux/vesa.h`, fbdev core, console subsystem, and device-specific framebuffer drivers. Integration points include boot splash, simple graphics, embedded systems, DRM fbdev emulation, and old userspace graphics stacks.

Risks include pointer-bearing UAPI structs (`fb_cmap`, `fb_image`, `fb_cursor`) on compat ABIs, physical-address exposure through fixed info, stale or driver-specific acceleration constants, mode-setting races with console/DRM, and memory corruption if mmap dimensions are mishandled. Test signals include fbdev ioctl tests, 32-bit compat tests, mode set/pan/vblank validation, colormap and cursor rendering checks, mmap bounds tests, and DRM-fbdev emulation coverage.
