# sources/distributed-fs/ceph-client/drivers/rtc/rtc-snvs.c

Purpose: Freescale/NXP SNVS low-power secure RTC driver. It provides a seconds counter, one-shot low-power timer alarm, wake IRQ support, and syscon or legacy MMIO regmap access.

Important APIs/types/functions: `struct snvs_rtc_data` stores RTC device, regmap, LP offset, IRQ, and optional clock. `rtc_read_lpsrt()` reads the 64-bit counter registers; `rtc_read_lp_counter()` and `_lsb()` retry until counter deltas are plausible. `rtc_write_sync_lp()` waits for several 32 kHz cycles after writes. `snvs_rtc_enable()` toggles `SRTC_ENV`. RTC ops read/set time by converting the 47-bit counter shifted by 15 fractional bits, manage `SNVS_LPTAR`, and enable alarm/wakeup bits. The IRQ handler clears alarm status, disables the one-shot alarm, and reports `RTC_AF`.

Control flow/state/persistence: probe allocates RTC, obtains regmap from DT `regmap` phandle or legacy MMIO, initializes glitch detect, clears status, enables the RTC, sets wake IRQ, requests a shared IRQ, and registers. Time persists in SNVS LP domain when powered.

Dependencies/integration: OF compatible `fsl,sec-v4.0-mon-rtc-lp`, syscon/regmap, optional `snvs-rtc` clock, PM wakeirq helpers, MMIO fallback, RTC core.

Risks/test signals: several error paths after `clk_enable()` in set-time/set-alarm can return without disabling the clock. Counter-read validity is heuristic and timeout based. Test syscon and legacy bindings, stable counter reads around rollover, alarm one-shot behavior, wake IRQ setup, suspend noirq clock gating, and error cleanup.
