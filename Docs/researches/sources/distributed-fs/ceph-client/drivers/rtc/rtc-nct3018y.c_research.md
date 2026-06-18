# sources/distributed-fs/ceph-client/drivers/rtc/rtc-nct3018y.c

Purpose: implements the Nuvoton NCT3018Y I2C RTC with BCD time registers, hour/min/sec alarm, voltage-low reporting, optional IRQ alarm support, and optional common-clock `clkout` provider.

Important APIs/types/functions: `struct nct3018y` stores the RTC, I2C client, part number, and optional `clk_hw`. `nct3018y_set_alarm_mode()` toggles alarm interrupt enable and clears alarm flag. `nct3018y_get_alarm_mode()` reads enable and pending bits. RTC callbacks cover time, alarm, alarm IRQ enable, and `RTC_VL_READ`. Clock-output callbacks implement recalc, determine, set rate, prepare, unprepare, and is_prepared over `NCT3018Y_REG_CLKO`.

Control flow: probe checks I2C/SMBus functionality, reads control and part ID, applies NCT3018Y-specific 24-hour mode setup, clears status, allocates the RTC, configures 2000-2099 range, requests a falling-edge threaded IRQ if `client->irq` is present, optionally registers clkout, and registers the RTC. Read-time first reads status and returns `-EINVAL` if the voltage/battery mask reports invalid data, then reads a 10-byte block and decodes sparse time offsets. Set-time may temporarily set the TWO bit on NCT3018Y parts, writes seconds/minutes/hours individually and day/month/year as a block, then restores TWO. Alarm ops write/read only sec/min/hour alarm registers and use control/status bits for enabled/pending.

State and persistence: persistent hardware state includes time, alarm, status flags, control bits, part-specific TWO/HF bits, and clkout rate/enable. Driver state tracks part number and optional clkout registration. Alarm feature is cleared when no IRQ is supplied.

Dependencies and integration: depends on I2C with raw I2C, SMBus byte, and block-data support; OF compatible `nuvoton,nct3018y`; optional IRQ; optional common clock framework; and RTC voltage-low ioctl support.

Risks and test signals: `nct3018y_rtc_read_time()` treats status byte zero as invalid, but `probe()` clears the status register to zero, so the first read-time behavior depends on hardware repopulating battery bits. Several block reads request contiguous bytes while only every other alarm/time register is used for sec/min/hour. `nct3018y_clkout_register_clk()` ignores `of_clk_add_provider()` cleanup/error. Test part ID variants, TWO-bit restore on all write errors, voltage-low ioctl, no-IRQ feature clearing, alarm flag clear, clkout rates and enable, status-after-probe behavior, and I2C error propagation.
