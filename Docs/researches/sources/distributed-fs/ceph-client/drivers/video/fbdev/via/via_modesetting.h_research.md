<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_modesetting.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_modesetting.h

Purpose: Public header for the basic VIA modesetting helper layer.

Important APIs/types/functions: Defines pitch alignment constants `VIA_PITCH_SIZE` and `VIA_PITCH_MAX`, `struct via_display_timing`, and prototypes for timing, address, pitch, and color-depth setters for primary and secondary engines.

Control flow and state: No standalone flow. The struct carries logical timing values that callers convert from `fb_var_screeninfo` or `fb_videomode` before register programming.

Dependencies and integration points: Included by `share.h`, `hw.h`, and callers such as `lcd.c` and `viafbdev.c`. Risks are lack of explicit units/range in `struct via_display_timing` and reliance on callers to validate pitch against `VIA_PITCH_MAX`. Test signals are compile coverage and mode-setting tests that exercise each exported setter.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_modesetting.h -->
