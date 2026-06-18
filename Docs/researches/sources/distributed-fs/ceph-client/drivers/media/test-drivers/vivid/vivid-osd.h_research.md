# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-osd.h

Purpose: declares OSD framebuffer helpers and provides no-OSD stubs when framebuffer overlay support is disabled.

Important APIs and types: `vivid_fb_init`, `vivid_fb_deinit`, `vivid_fb_clear`, and `vivid_fb_green_bits`. In non-OSD builds, init returns `-ENODEV`, cleanup/clear are no-ops, and green bits default to 5.

Control flow: core device initialization can call `vivid_fb_init` unconditionally when OSD support is desired, while compile-time configuration selects real or stub behavior.

State and persistence: the header owns no state. Real implementation manages framebuffer state in `struct vivid_dev`.

Dependencies and integration points: depends on `CONFIG_VIDEO_VIVID_OSD` and the including context providing `struct vivid_dev` and `-ENODEV`.

Risks: callers must tolerate `-ENODEV` in stub builds. The fallback `vivid_fb_green_bits` value influences RGB555/RGB565 behavior in code that may run without a real framebuffer.

Test signals: compile and runtime coverage of both config paths validate the stubs and real declarations.
