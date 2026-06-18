<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/video_gx.c -->
## sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/video_gx.c

Purpose: implements Geode GX video processor operations for dot-clock programming, CRT/TFT output configuration, and blanking.

Important APIs, types, and functions: `struct gx_pll_entry` and the 48 MHz/14 MHz PLL tables map pixclock to divider bits and dot PLL values. `gx_set_dclk_frequency()` chooses the correct table by CPU stepping, programs `MSR_GLCP_DOTPLL` and `MSR_GLCP_SYS_RSTPLL`, and waits for lock. `gx_configure_tft()` configures pad select, flat-panel timing, dither control, FP power/data, and panel power. `gx_configure_display()` programs VP display config, sync polarity, DAC power, gamma, CRT enables, and calls TFT setup when CRT is disabled. `gx_blank_display()` maps fbdev blank modes to DAC, sync, CRT enable, and panel power.

Control flow: `gx_set_mode()` from the GX display controller path calls these exported functions to set clock and display output. Blanking is called from fbdev callbacks. CRT mode and flat-panel mode diverge primarily through `par->enable_crt`.

State and persistence: uses `struct gxfb_par` MMIO pointers and `enable_crt`. Persistent hardware state is in MSRs, VP registers, and FP registers; no private heap state is maintained here.

Dependencies and integration points: depends on `gxfb.h`, x86 CPU stepping data, MSR helpers, CS5535 MSR definitions, and fbdev sync/blank fields. It is paired with `gxfb_core.c` and `suspend_gx.c`.

Risks: the `PREDIV2` macro appears to alias the post-divider bit by definition, which may be intentional legacy behavior or a typo carried into PLL setup. PLL lock wait has a timeout counter but no error return if lock is never observed. Comments indicate undocumented TFT bits and hardware-specific magic values. Flat-panel configuration is limited and not EDID-driven.

Test signals: dot-clock programming on stepping-1 and later GX CPUs, register traces for common VESA modes, CRT versus flat-panel output validation, all DPMS blank modes, and suspend/resume interaction with TFT panel power bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/video_gx.c -->
