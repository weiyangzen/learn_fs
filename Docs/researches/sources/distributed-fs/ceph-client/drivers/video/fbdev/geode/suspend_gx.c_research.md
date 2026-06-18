<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/suspend_gx.c -->
## sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/suspend_gx.c

Purpose: implements Geode GX suspend and resume helpers used by `gxfb_core.c` PM callbacks.

Important APIs, types, and functions: `gx_save_regs()` waits for BLT idle, saves pad select and dot PLL MSRs, unlocks DC, copies GP/DC/VP/FP register blocks, and saves the DC palette. `gx_set_dotpll()` restores dot PLL with reset/lock sequencing. `gx_restore_gfx_proc()`, `gx_restore_display_ctlr()`, and `gx_restore_video_proc()` restore register groups while deliberately skipping volatile/status or enable-sensitive registers. `gx_disable_graphics()` shuts off VP, flat panel, and DC enables. `gx_enable_graphics()` restores panel power state and re-enables VP/DC in order. `gx_powerdown()` and `gx_powerup()` are the exported idempotent entry points.

Control flow: powerdown returns early if already powered down, saves state, disables graphics, and sets `powered_down`. Powerup returns early if not powered down, restores PLL and registers, enables graphics, and clears `powered_down`. Restore order is PLL, graphics processor, display controller, video processor, flat-panel registers, then final enables.

State and persistence: state is persisted in `struct gxfb_par`: MSRs, GP/DC/VP/FP arrays, palette, and powered-down flag. Framebuffer contents are not saved here; the driver relies on mapped VRAM retention or higher-level redraw.

Dependencies and integration points: uses `gxfb.h` register helpers, x86 MSR access, CS5535 MSR definitions, and delay helpers. Called under console lock by `gxfb_core.c` suspend/resume.

Risks: BLT wait and PLL wait are bounded inconsistently: BLT wait has no timeout, while PLL lock has a short loop. Register save uses `memcpy()` from MMIO pointers rather than explicit `memcpy_fromio()`, which is legacy style and may be architecture-sensitive. Restore intentionally skips multiple registers, so features outside the normal fbdev mode path may not survive suspend.

Test signals: suspend/resume cycles while in CRT and panel mode, palette preservation, BLT-active suspend, PLL lock timeout behavior, and regression tests that compare visible mode after resume with mode before suspend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/suspend_gx.c -->
