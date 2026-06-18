# sources/distributed-fs/ceph-client/drivers/rtc/rtc-tps65910.c

Purpose: RTC driver for TI TPS65910 PMICs. It supports BCD time/alarm registers, alarm IRQ, RTC digital power enable, 2000..2099 range, and crystal compensation exposed through the RTC offset API.

Important APIs/types/functions: `struct tps65910_rtc` stores RTC and IRQ. `tps65910_rtc_read_time()` latches counting registers with `GET_TIME` then bulk reads BCD fields. `tps65910_rtc_set_time()` stops RTC, writes BCD registers, and restarts. Alarm ops bulk read/write alarm BCD registers and control `TPS65910_RTC_INTERRUPTS_IT_ALARM`. Calibration helpers write/read two compensation bytes and convert to/from ppb with sign inversion. The IRQ handler reads status, detects alarm, writes status back to clear, and reports `RTC_AF`.

Control flow/state/persistence: probe clears pending status, powers the RTC domain, writes control to start/enable RTC, requests threaded low-trigger IRQ if possible, marks wakeup or clears alarm feature if IRQ unavailable, sets range, and registers. PM toggles IRQ wake.

Dependencies/integration: TPS65910 MFD/regmap, platform driver `tps65910-rtc`, property `wakeup-source` on parent, RTC core, BCD/math64 helpers, IRQ core.

Risks/test signals: if IRQ request fails, probe continues without alarms but still leaves alarm ops in `rtc_class_ops` while clearing the alarm feature. IRQ handler calls `rtc_update_irq()` even when `events` is zero after a non-alarm status. Test BCD month/year conversion, stop/start sequencing failure, compensation min/max and rounding, IRQ unavailable feature behavior, wakeup-source handling, and status-clear semantics.
