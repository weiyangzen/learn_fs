# sources/distributed-fs/ceph-client/drivers/rtc/rtc-mt2712.c

Purpose: implements the MediaTek MT2712 SoC RTC with protected write-trigger semantics, full date/time alarm matching, power-loss detection, and suspend wake support.

Important APIs/types/functions: `struct mt2712_rtc` tracks RTC device, base, IRQ, wake-enabled state, and `powerlost`. `mt2712_rtc_write_trigger()` writes `WRTGR` and waits for `BBPU_CBUSY` to clear. `mt2712_rtc_writeif_unlock()` performs the two-step protection unlock. Time functions are `__mt2712_rtc_read_time()`, `mt2712_rtc_read_time()`, and `mt2712_rtc_set_time()`. Alarm functions program `MT2712_AL_*`, `MT2712_AL_MASK`, and `MT2712_IRQ_EN`. `mt2712_rtc_hw_init()` programs BBPU, CII, power keys, CON registers, and detects lost backup state.

Control flow: probe allocates private data, maps MMIO, calls hardware init before fetching the IRQ or allocating the RTC, requests a low-triggered threaded alarm IRQ, enables wake capability, sets the RTC range to 2000-2127, and registers. Reads reject access while `powerlost` is true and repeat field reads if seconds carried. Set-time writes all time fields, triggers the write, and clears `powerlost`. Set-alarm updates masked alarm fields, masks day-of-week matching, triggers, then enables/disables the alarm IRQ.

State and persistence: persistent state includes RTC time/alarm registers, power keys, BBPU, CON0/CON1, protection state, IRQ enable/status, and alarm mask. The driver caches only `powerlost` and suspend wake state. Alarm interrupt status is read in the threaded handler but not explicitly cleared there beyond framework/event handling via hardware semantics.

Dependencies and integration: depends on MMIO platform resource, IRQ 0, OF compatible `mediatek,mt2712-rtc`, PM sleep hooks, and MediaTek RTC write-trigger/protection conventions.

Risks and test signals: `mt2712_rtc_hw_init()` uses `mt2712_rtc->rtc` for debug messages before the RTC device is allocated, which is hazardous if those debug paths execute. `mt2712_rtc_write_trigger()` logs timeout but returns void, so callers cannot fail writes. Read consistency loop compares a second read against `tm_sec` and relies on wrap direction. Test power-key lost-power path, write-trigger timeout, protection unlock sequencing, alarm IRQ status handling, wake enable/disable failure paths, range endpoints, and probe ordering under dynamic debug.
