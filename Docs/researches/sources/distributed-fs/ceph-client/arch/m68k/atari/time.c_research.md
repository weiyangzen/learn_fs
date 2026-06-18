# sources/distributed-fs/ceph-client/arch/m68k/atari/time.c

Purpose: Atari scheduler clocksource and RTC read/write support.

Important APIs are `atari_sched_init()`, `atari_mste_hwclk()`, `atari_tt_hwclk()`, and exported spinlock `rtc_lock`. Timer C on the ST-MFP supplies scheduler ticks and an `mfp` clocksource. `mfp_timer_c_handler()` updates `last_timer_count`, accumulates `clk_total`, calls `legacy_timer_tick(1)`, and drives heartbeat.

Clocksource flow starts MFP Timer C with `INT_TICKS`, requests `IRQ_MFP_TIMC`, and registers frequency `INT_CLK`. `atari_read_clk()` disables local IRQs, ensures a monotonically decreasing count using `min(st_mfp.tim_dt_c, last_timer_count)`, and returns accumulated ticks.

RTC flow supports MegaSTE RP5C15-style registers through `mste_read()`/`mste_write()` and TT MC146818-style CMOS through `RTC_READ/RTC_WRITE`. `atari_tt_hwclk()` handles UIP polling, `RTC_SET`, BCD/binary mode, 12/24-hour mode, weekday conversion, and `atari_rtc_year_offset`.

State includes `clk_total`, `last_timer_count`, RTC hardware registers, and `rtc_lock` used also by NVRAM. Dependencies include Atari MFP/RTC hardware, bcd helpers, clocksource APIs, and machdep hooks set by `config_atari()`.

Risks and test signals: Timer C wrap handling can momentarily stop but should not go backward; RTC access must avoid UIP windows and coordinate with NVRAM. Test clocksource monotonicity, scheduler ticks, MSTE and TT RTC read/write, 12/24-hour conversion, and concurrent NVRAM access.
