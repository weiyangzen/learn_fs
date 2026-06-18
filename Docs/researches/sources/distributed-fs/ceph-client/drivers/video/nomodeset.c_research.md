# sources/distributed-fs/ceph-client/drivers/video/nomodeset.c

Purpose: global kernel modeset-disabling helper for the `nomodeset` boot parameter. It lets graphics drivers query whether only firmware/system framebuffer drivers should be used.

Important APIs, types, and functions: static `video_nomodeset`, exported `video_firmware_drivers_only`, and `disable_modeset` registered with `__setup("nomodeset", ...)`.

Control flow: early boot parameter parsing calls `disable_modeset`, sets the static boolean, emits a warning, and returns handled. Drivers call `video_firmware_drivers_only()` to check this state.

State and persistence: one boot-lifetime boolean. No runtime toggling or persistence across boots.

Dependencies and integration points: used through `<video/nomodeset.h>` by DRM/fbdev code that wants to avoid native modesetting when the user requested firmware-only graphics.

Risks: global effect is coarse-grained. Drivers that do not check this helper may still bind. The warning text is the only user-facing signal here.

Test signals: boot with `nomodeset`; verify exported helper returns true and native drivers that honor it skip modesetting while system framebuffer remains available.
