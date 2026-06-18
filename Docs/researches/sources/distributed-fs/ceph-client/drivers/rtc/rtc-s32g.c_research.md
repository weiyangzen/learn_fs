<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-s32g.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-s32g.c

Purpose: implements the NXP S32G2/S32G3 RTC alarm/wakeup block as an RTC class device. It does not maintain calendar time in hardware; it derives read_time from system real time plus accumulated sleep seconds and uses the hardware API counter for alarms.

Important APIs/types/functions: `struct rtc_priv` stores RTC device, MMIO base, IPG and selected source clocks, SoC data, computed RTC frequency, accumulated `sleep_sec`, IRQ, and selected clock source index. `rtc_soc_data` defines clock divisor and reserved clock sources. Core functions are `rtc_clk_dts_setup()`, `rtc_clk_src_setup()`, `s32g_rtc_set_alarm()`, `s32g_rtc_read_time()`, suspend/resume hooks, and `s32g_rtc_handler()`.

Control flow: probe maps registers, enables wakeup, gets `ipg` and the first usable source clock, allocates RTC, configures source/dividers with counter disabled, computes effective RTC Hz, requests the alarm IRQ, and registers. Alarm set converts requested wall time to a positive offset from current real time minus accumulated sleep, bounds it by 32-bit APIVAL cycles, waits for API synchronization, and writes APIVAL. IRQ clears APIVAL/status and reports AF. Suspend adds remaining APIVAL-derived seconds to `sleep_sec`; resume reconfigures registers because suspend-to-RAM may reset them.

State and persistence: APIVAL, RTCC, RTCS, clock source/divider, and accumulated software `sleep_sec` drive behavior. No set_time op exists, and calendar state is not persisted in the RTC block.

Dependencies and integration points: depends on platform MMIO, OF match `nxp,s32g2-rtc`, named clocks `ipg` and `source0..source3`, RTC core, system time via `ktime_get_real_seconds()`, and PM sleep callbacks.

Risks and test signals: `rtc_clk_dts_setup()` returns `-EOPNOTSUPP` immediately when it sees a reserved source index, which prevents trying later valid sources. `alarm_irq_enable()` ignores its `enabled` argument and always enables API interrupt bits. Test clock-source selection, reserved source handling, divider math, APIVAL overflow/range, synchronization timeout, suspend/resume accumulation, system-time jumps, IRQ clear/report, and wakeup behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-s32g.c -->
