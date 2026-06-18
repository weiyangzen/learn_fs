<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/video_cs5530.h -->
## sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/video_cs5530.h

Purpose: declares the CS5530 video operation table and register offsets/bit masks used by `video_cs5530.c` and GX1 code.

Important APIs, types, and functions: exports `cs5530_vid_ops`. Defines register offsets for video config, display config, video position/scale/color-key, palette address/data, dot-clock config, and CRC. Defines bit masks for video input formats, line size, filter enable, display enable, sync enable, DAC and flat-panel power/data, sync polarity, power sequence delay, DDC pins, and 16-bit mode.

Control flow: this header is consumed by the CS5530 implementation; it does not execute. Its constants determine which bits are preserved, cleared, or set during display configuration and blanking.

State and persistence: all state represented here is hardware-resident in CS5530 registers. There is no C storage except users of the constants.

Dependencies and integration points: depends on `struct geode_vid_ops` being visible in including source contexts. Integrates CS5530 display control with GX1 fbdev operations.

Risks: incorrect masks here directly affect hardware programming. Several DDC and video overlay definitions are present even though this worker-read implementation uses only display/PLL/blanking bits, so future users need separate validation.

Test signals: compile coverage with `video_cs5530.c`, register-level tests that compare expected display config masks, and hardware smoke tests for palette, PLL, and DPMS behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/video_cs5530.h -->
