# sources/distributed-fs/ceph-client/drivers/rtc/rtc-pcf8583.c

Purpose: provides a legacy I2C RTC driver for the PCF8583 RTC/RAM chip. It handles time read/write and uses the chip's RAM area to maintain full year and checksum data because the RTC hardware only stores a two-bit year field.

Important APIs/types/functions: `struct pcf8583` stores the RTC and cached control byte; `struct rtc_mem` describes small RAM transactions. `pcf8583_get_datetime()` reads six BCD time/date bytes with an I2C combined transaction. `pcf8583_set_datetime()` stops the clock through the control register, writes time and optional date bytes, then restores control. `pcf8583_read_mem()` and `pcf8583_write_mem()` access RAM from offset 8 upward. `pcf8583_rtc_read_time()` reconciles the two-bit hardware year with RAM year bytes; `pcf8583_rtc_set_time()` updates the RAM year and checksum.

Control flow: probe checks plain I2C support, allocates per-client state, and registers an RTC with read/set time only. Reads clear STOP/HOLD if set, read hardware time plus RAM year bytes, then derive `tm_year`. Writes program RTC time/date, read checksum and year bytes, adjust checksum for changed year bytes, and write both RAM locations.

State and persistence: the chip stores time in BCD registers, a two-bit year in the day register, and full year/checksum in battery-backed RAM locations `CMOS_YEAR` and `CMOS_CHECKSUM`. The driver's cached control byte is runtime-only and initialized as zero before first use.

Dependencies and integration: uses the I2C core directly rather than regmap, BCD helpers, RTC core, and devm allocation/registration. It has no OF table, IRQ, alarm, or nvmem integration despite using RAM internally.

Risks: cached control state may not reflect hardware after probe, so restoring control can overwrite existing mode bits. RAM checksum handling assumes a preexisting PCF8583 CMOS layout. The hardware year correction is subtle around four-year wraps and century bytes. Test signals include STOP/HOLD recovery, read/write around year modulo-four transitions, RAM checksum preservation, invalid RAM contents, and I2C short transfer error paths.
