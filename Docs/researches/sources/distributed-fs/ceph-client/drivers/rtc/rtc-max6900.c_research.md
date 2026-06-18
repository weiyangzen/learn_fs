# sources/distributed-fs/ceph-client/drivers/rtc/rtc-max6900.c

Purpose: implements the Maxim MAX6900 I2C RTC with burst read/write for time registers, separate century handling, and write-protect management.

Important APIs and functions: `max6900_i2c_read_regs()` performs burst plus century read, `max6900_i2c_write_regs()` writes century then burst with required delays, `max6900_i2c_clear_write_protect()` clears control write protect, and `max6900_rtc_read_time()`/`max6900_rtc_set_time()` are RTC callbacks.

Control flow: probe requires raw I2C transfers and registers the RTC. Reading sends burst-read and century-read messages, decodes BCD fields, and computes `tm_year` from century and year bytes. Setting clears write-protect, populates BCD fields including century, sets write-protect in the control byte, writes century first, delays, writes the burst block, and delays again.

State and persistence: hardware RTC registers contain time, control/write-protect, and century. There is no driver-owned persistent state.

Dependencies and integration: raw I2C transfer capability, SMBus byte write for control, BCD helpers, RTC class, and MAX6900-specific command opcodes.

Risks: I2C read/write expects exact message counts; partial transfers become `-EIO`. The driver has no alarm support. Weekday is not normalized by subtracting one. Required idle delay after writes is handled with `msleep(3)` but depends on datasheet timing.

Test signals: I2C capability failure, partial transfer failures, write-protect clear failure, century rollover, write delay timing, and set/read round trip.
