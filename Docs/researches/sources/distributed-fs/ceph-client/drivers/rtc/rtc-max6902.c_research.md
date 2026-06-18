# sources/distributed-fs/ceph-client/drivers/rtc/rtc-max6902.c

Purpose: supports the Maxim MAX6902 SPI RTC with burst BCD time reads, individual field writes, separate century register, and write-protect control.

Important APIs and functions: `max6902_set_reg()` and `max6902_get_reg()` wrap one-byte register access. `max6902_read_time()` and `max6902_set_time()` implement RTC class operations. Probe configures SPI mode 3 and tests the seconds register.

Control flow: reading performs burst read command `0xbf`, decodes seconds through year, reads the century register separately, and normalizes `tm_year`. Setting converts `tm_year` to absolute year, clears write-protect, writes each time register and century, then restores write-protect.

State and persistence: all state is in the SPI chip registers; software state is only the registered RTC pointer.

Dependencies and integration: SPI mode 3, 8-bit words, BCD helpers, RTC class, and SPI write/read command bit conventions.

Risks: `max6902_set_time()` mutates the caller's `rtc_time` by adding 1900 to `tm_year`, which is surprising and can leak back to caller state. Individual writes ignore return values, so failed writes can still return success. No alarm or validation.

Test signals: SPI setup/probe read failure, write failure injection on individual fields, caller `tm_year` mutation, century rollover, and write-protect behavior.
