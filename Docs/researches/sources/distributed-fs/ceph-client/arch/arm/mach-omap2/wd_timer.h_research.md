<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/wd_timer.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-omap2/wd_timer.h

### Purpose
`wd_timer.h` declares OMAP2+ watchdog timer reset and disable helpers.

### Important APIs, Types, And Functions
It declares `omap2_wd_timer_disable()` and `omap2_wd_timer_reset()`, both taking `struct omap_hwmod *`.

### Control Flow
There is no runtime flow. The header provides prototypes for hwmod and platform init code.

### State, Persistence, And Dependencies
The header has no state and depends on `omap_hwmod.h`.

### Integration Points
It bridges watchdog-specific code with OMAP hwmod initialization paths.

### Risks
Callers must pass a valid watchdog hwmod; implementation returns errors for missing base data.

### Test Signals
Build configurations using OMAP watchdog hwmods should compile and boot without undefined symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/wd_timer.h -->
