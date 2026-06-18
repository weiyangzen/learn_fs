# sources/distributed-fs/ceph-client/drivers/rtc/rtc-mt7622.c

Purpose: implements the MediaTek MT7622/SOC RTC block, including protected initialization magic, 2001-2099 calendar range, alarm handling, clock control, and wake IRQ support.

Important APIs/types/functions: `struct mtk_rtc` holds RTC device, MMIO base, IRQ, and clock. Register helpers `mtk_w32()`, `mtk_r32()`, `mtk_rmw()`, `mtk_set()`, and `mtk_clr()` wrap relaxed MMIO. `mtk_rtc_hw_init()` writes power-check, key, and protection magic values and clears debounce/stop. `mtk_rtc_get_alarm_or_time()` and `mtk_rtc_set_alarm_or_time()` abstract time/alarm register banks. `mtk_rtc_alarmirq()` handles alarm status and disables alarm control.

Control flow: probe maps MMIO, gets and enables the `rtc` clock, requests IRQ 0, initializes hardware, marks wake-capable, and registers the RTC through `devm_rtc_device_register()`. Reads repeatedly sample the seconds register before and after the other fields until stable. Set-time validates the tm_year against 2001-2099, stops the counter, writes all fields rebased by 100, and restarts. Set-alarm validates the year, clears alarm enable, synchronizes with any running IRQ handler, writes alarm fields, then writes `RTC_AL_ALL` to enable all alarm matching and interrupt bits.

State and persistence: hardware persists magic/protection registers, debounce, control stop bit, time/alarm calendar registers, alarm control, and interrupt status. Driver state owns the clock and IRQ only. Remove disables the clock.

Dependencies and integration: depends on OF compatibles `mediatek,mt7622-rtc` and `mediatek,soc-rtc`, a named `rtc` clock, MMIO, IRQ, and PM sleep wake calls.

Risks and test signals: the valid range intentionally excludes year 2000 because hardware mishandles leap-year behavior for relative year zero. Set-alarm ignores `wkalrm->enabled` and always restarts the alarm after programming. No explicit `alarm_irq_enable` callback is provided, so alarm enable control is via set-alarm only. Test year 2000 rejection, 2001/2099 endpoints, stable-read loop around second rollover, alarm pending ack, `synchronize_irq()` path, clock cleanup on probe errors/remove, and wake IRQ enable/disable.
