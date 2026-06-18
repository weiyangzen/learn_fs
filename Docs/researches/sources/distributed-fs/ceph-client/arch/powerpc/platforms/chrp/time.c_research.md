# sources/distributed-fs/ceph-client/arch/powerpc/platforms/chrp/time.c

Purpose: CHRP CMOS/RTC access fallback for systems not using RTAS time-of-day services.

Important APIs and control flow: `chrp_time_init` looks for `pnpPNP,b00` or `ds1385-rtc`, remaps default NVRAM index/data ports to the OF resource base, and leaves legacy ports otherwise. `chrp_cmos_clock_read`/`chrp_cmos_clock_write` drive the indexed RTC registers. `chrp_set_rtc_time` locks `rtc_lock`, sets `RTC_SET`, resets the prescaler, converts to BCD if needed, writes time/date fields, then restores control registers in DS12887-safe order. `chrp_get_rtc_time` loops until seconds are stable, converts from BCD, and normalizes post-2000 years.

State, dependencies, and risks: state is the selected RTC port triplet and shared `rtc_lock`. Dependencies include MC146818-compatible register semantics, OF RTC resources, BCD helpers, and PowerPC time hooks. Risks include two-digit year interpretation, port I/O ordering sensitivity, and reliance on stable seconds reads instead of UIP polling. Test signals are correct RTC read/write across reboot, no register corruption on DS12887 clones, and fallback behavior when no RTC node exists.
