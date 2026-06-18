<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-rx8111.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-rx8111.c

Purpose: implements a minimal Epson RX8111 I2C RTC driver exposing time read/write and voltage-low reporting, while defining register fields for broader chip functionality.

Important APIs/types/functions: `struct rx8111_data` stores regmap, an array of allocated `regmap_field` objects, device, and RTC pointer. `rx8111_regfields[]` maps extension, flag, control, power-switch, and status bits. `rx8111_read_time()`, `rx8111_set_time()`, `rx8111_ioctl()`, and `rx8111_read_vl_flag()` implement the current RTC surface.

Control flow: probe allocates state, initializes I2C regmap, allocates all regmap fields, allocates an RTC, sets 2000-2099 range, clears alarm feature, and registers. Read-time checks XST, VLF, and STOP before bulk-reading seven BCD time registers. Set-time clears XST/VLF, sets STOP, bulk-writes the time, then clears STOP. Voltage ioctl reports `RTC_VL_DATA_INVALID` from VLF and `RTC_VL_BACKUP_LOW` from the VLOW status monitor.

State and persistence: hardware keeps time, alarms, timer, timestamp, power-switch, flag, and status registers. The driver currently persists no local runtime state beyond regmap/regfields and does not expose alarms, IRQs, timestamps, power-switch configuration, or nvmem.

Dependencies and integration points: depends on I2C regmap, regmap fields, RTC core, OF compatible `epson,rx8111`, BCD helpers, and userspace `RTC_VL_READ`.

Risks and test signals: probe uses `devm_kmalloc()` rather than zeroed allocation, leaving unused members such as `data->rtc` uninitialized. If set-time fails after STOP is set, the driver intentionally leaves the clock stopped and future reads fail until a successful set-time. `FIELD_GET()` is used with single-bit masks on a raw flag value; current definitions work but are unusual. Test XST/VLF/STOP rejection, VLOW ioctl composition, set-time failure recovery, invalid weekday masks, all regmap_field allocations, and alarm feature absence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-rx8111.c -->
