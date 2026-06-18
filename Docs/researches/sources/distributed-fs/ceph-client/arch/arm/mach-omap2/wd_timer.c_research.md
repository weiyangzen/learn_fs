<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/wd_timer.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-omap2/wd_timer.c

### Purpose
`wd_timer.c` provides OMAP2+ watchdog timer reset and disable helpers for hwmod initialization.

### Important APIs, Types, And Functions
Public APIs are `omap2_wd_timer_disable(struct omap_hwmod *oh)` and `omap2_wd_timer_reset(struct omap_hwmod *oh)`. Important watchdog offsets are `OMAP_WDT_WPS` and `OMAP_WDT_SPR`.

### Control Flow
Disable obtains the watchdog runtime virtual base and writes the required `0xAAAA` then `0x5555` sequence to SPR, polling WPS after each write. Reset performs an OCP softreset, polls SYSS reset-done with `omap_test_timeout()`, honors any reset delay, logs the reset result, and disables the watchdog unless reset timed out.

### State, Persistence, And Dependencies
Persistent effects are watchdog register state and hwmod reset state. The file depends on OMAP hwmod accessors, watchdog platform semantics, and PRM/SYSS reset bits.

### Integration Points
OMAP hwmod/device init can call these helpers to avoid an enabled watchdog rebooting the system after reset.

### Risks
Disable polling has no timeout, so a stuck WPS bit can hang. Reset behavior differs between OMAP2/3 and OMAP4, and the helper is written around the rearm-after-softreset behavior.

### Test Signals
Boot should reset and disable watchdog without spontaneous reboot. Fault-injection or hardware tests should verify timeout logging for failed softreset and WPS behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/wd_timer.c -->
