<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/cmdline.h -->
# sources/distributed-fs/ceph-client/include/video/cmdline.h

Purpose: declares helpers for retrieving parsed video command-line options for framebuffer/video drivers.

Important APIs and types: `video_get_options(name)` returns option text for a named video device. When `CONFIG_FB_CORE` is enabled, `__video_get_options(name, option, is_of)` is exported for fbdev compatibility.

Control flow: drivers call `video_get_options()` during probe or setup to fetch `video=` command-line configuration; fbdev compatibility code may call the internal helper with Open Firmware matching context.

State and persistence: parsed boot command-line options are global boot-time state maintained elsewhere. This header owns no state.

Dependencies and integration points: depends on kconfig and types. It integrates with fbdev core, boot parameter parsing, platform/of video drivers, and legacy mode option handling.

Risks and test signals: risks include option matching ambiguity, deprecated internal helper use, and behavior differences when `CONFIG_FB_CORE` is disabled. Test `video=` boot options for named devices, OF aliases, and configs with/without fbdev core.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/cmdline.h -->
