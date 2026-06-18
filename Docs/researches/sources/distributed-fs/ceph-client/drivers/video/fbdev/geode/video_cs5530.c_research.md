<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/video_cs5530.c -->
## sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/video_cs5530.c

Purpose: implements the `geode_vid_ops` backend for the CS5530 video/display block used by the GX1 framebuffer driver.

Important APIs, types, and functions: `struct cs5530_pll_entry` maps fbdev pixclock values to CS5530 PLL register values. `cs5530_set_dclk_frequency()` chooses the closest table entry and writes `CS5530_DOT_CLK_CONFIG` through reset and bypass sequencing. `cs5530_configure_display()` programs display configuration bits for CRT, flat panel, default sync skew, power sequence delay, palette bypass, and sync polarity. `cs5530_blank_display()` maps fbdev blank modes to DAC/panel power, data, and sync bits. `cs5530_vid_ops` exports these three functions.

Control flow: GX1 mode programming calls `set_dclk` and `configure_display` through the video ops table; blanking calls `blank_display`. The code reads existing display config, masks old mode bits, writes updated output policy, and uses delays during PLL programming.

State and persistence: no private state is allocated here. It consumes `geodefb_par` from `fb_info->par`, especially `vid_regs`, `enable_crt`, and `panel_x`. Hardware display state persists in CS5530 registers.

Dependencies and integration points: depends on `geodefb.h` for `struct geodefb_par` and `struct geode_vid_ops`, `video_cs5530.h` for register bits, and fbdev blank/mode fields. Integrated only by GX1 core in this work item.

Risks: PLL selection is nearest-match only; there is no bounds rejection if the requested pixclock is far from the table. Register writes assume `vid_regs` is valid. Panel blanking powers the panel only when both hsync and vsync are active, which may not match all panels' power sequencing requirements.

Test signals: unit-style table selection for common VESA pixclocks, register trace validation for reset/bypass sequence, CRT-only, panel-only, and combined output configuration, and all five fbdev blank modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/video_cs5530.c -->
