# sources/distributed-fs/ceph-client/drivers/rtc/rtc-lpc24xx.c

Purpose: supports the NXP LPC178x/18xx/408x/43xx RTC block with MMIO time registers, alarm registers, clocks, and a single interrupt line.

Important APIs and functions: `struct lpc24xx_rtc` stores the register base, RTC device, and `rtc`/`reg` clocks. `lpc24xx_rtc_ops` exposes read/set time and alarm plus alarm IRQ enable. `lpc24xx_rtc_interrupt()` handles interrupt status and alarm masking.

Control flow: probe maps registers, fetches/enables the RTC and register clocks, clears pending interrupts, enables counting, requests the IRQ, and registers the RTC. Setting time disables counting with calibration enabled, writes discrete fields, then re-enables. Reading time uses consolidated `CTIME0/1/2` registers. Alarm writes disable matching through `AMR`, program all alarm fields, then optionally clear `AMR` to match all fields.

State and persistence: time and alarm state are hardware-backed. The driver has no persistent software state beyond clock handles and base pointer. Hardware alarm enable state is inferred from `AMR == 0`.

Dependencies and integration: depends on platform MMIO and IRQ resources, named clocks `rtc` and `reg`, OF compatible `nxp,lpc1788-rtc`, RTC class APIs, and standard IRQ handling.

Risks: month/year values appear written/read in hardware encoding rather than normalized Linux conventions; this must match controller documentation. Any failure after enabling clocks must unwind both clocks, which probe and remove mostly handle. The interrupt handler reports `RTC_IRQF` even if no recognized cause is set.

Test signals: clock enable/unwind paths, time set/read normalization, alarm enable/disable through `AMR`, IRQ status clearing, removal masking, and alarm invalid-date validation.
