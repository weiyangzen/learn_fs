# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/i9xx_display_sr.c

## Purpose
`i9xx_display_sr.c` saves and restores legacy display registers across suspend/resume or display reset paths for i9xx-era hardware. It focuses on display arbitration, GMBUS clock gating config, and SWF scratch registers.

## Important APIs, Types, and Functions
`i9xx_display_save_swf()` reads SWF scratch register banks into `display->restore.saveSWF*` arrays with platform-specific counts: mobile gen2 saves SWF0/SWF1/SWF3, desktop gen2 saves SWF1, and GMCH platforms save larger SWF0/SWF1 plus SWF3 sets. `i9xx_display_restore_swf()` writes those arrays back. `i9xx_display_sr_save()` guards on `HAS_DISPLAY()`, saves `DSPARB` for display versions up to 4, saves PCI config `GCDGMBUS` on gen4, then saves SWF. `i9xx_display_sr_restore()` restores SWF first, then gen4 `GCDGMBUS`, then `DSPARB`.

## Control Flow and State
The module has no local private allocation. It persists hardware snapshots in `display->restore`, which must survive the suspend/resume interval. The save path captures MMIO and PCI config state; the restore path replays them in a conservative order.

## Dependencies and Integration Points
The file depends on DRM device access for `display->drm->dev`, PCI config helpers, GMBUS and watermark/arbitration register definitions, and `intel_de_*()` MMIO access. The header exposes `i9xx_display_sr_save()` and `_restore()` to higher-level power-management code.

## Risks and Test Signals
The main risk is incomplete platform coverage or wrong register counts, which can produce resume regressions on older chipsets. Because it touches PCI config and display arbitration, ordering matters. Test signals include suspend/resume on gen2-gen4 and GMCH systems, preserved GMBUS behavior, no display FIFO/arbitration regressions after resume, and debug comparison of saved/restored SWF values where available.
