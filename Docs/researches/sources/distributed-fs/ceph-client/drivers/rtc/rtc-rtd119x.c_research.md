<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-rtd119x.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-rtd119x.c

Purpose: implements the built-in Realtek RTD1295/RTD119x RTC as a platform driver backed by MMIO registers and a clock.

Important APIs/types/functions: `struct rtd119x_rtc` stores the MMIO base, clock, RTC device, and fixed base year. `rtd119x_rtc_reset()`, `rtd119x_rtc_set_enabled()`, `rtd119x_rtc_read_time()`, and `rtd119x_rtc_set_time()` implement the hardware operations. RTC ops expose only `read_time` and `set_time`.

Control flow: probe maps the register resource, enables the input clock, powers the RTC if needed, resets and zeroes calendar registers on first power-up, enables the counter with the magic `0x5a` value, and registers the RTC. Reads sample seconds before and after reading all date fields, retrying up to three times if a rollover is detected. The hardware stores day-of-year count since `base_year` 2014; reads convert that day count to year/month/day, and writes convert `tm_yday` back to the 15-bit day counter.

State and persistence: hardware registers hold seconds, minutes, hours, day count, power state, reset control, and enable state. The driver has no alarm or NVRAM state and disables the RTC and clock on remove.

Dependencies and integration points: depends on platform resources, OF compatible `realtek,rtd1295-rtc`, `of_clk_get()`, MMIO accessors, RTC core, and leap-year/month helpers.

Risks and test signals: seconds are stored shifted left by one, limiting resolution interpretation to hardware format. Set-time correctness depends on a valid `tm_yday` supplied by the RTC core. Supported range is limited by a 15-bit day counter relative to 2014. Test first-boot RTCPWR initialization, clock enable failure cleanup, rollover retry behavior, dates before 2014, far-future day overflow, leap years, and remove-time disable/clock release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-rtd119x.c -->
