# sources/distributed-fs/ceph-client/drivers/hid/hid-ft260.c

Implements the FTDI FT260 USB HID-to-I2C host bridge as a HID driver that registers an `i2c_adapter`. It translates Linux I2C and SMBus operations into FT260 HID feature/output/input reports, exposes bridge configuration through sysfs, and handles USB HID lifecycle for the FT260 I2C interface only.

Important structures are `struct ft260_device` and the packed FT260 report structs for chip/system/status, I2C read/write requests, and input data reports. Key APIs are `ft260_hid_feature_report_get()`, `ft260_hid_feature_report_set()`, `ft260_hid_output_report()`, `ft260_i2c_write()`, `ft260_i2c_read()`, `ft260_i2c_write_read()`, `ft260_i2c_xfer()`, `ft260_smbus_xfer()`, and `ft260_raw_event()`.

Probe validates USB transport, parses/opens HID hardware, reads chip version and system config, rejects unsupported UART-only/interface-1 modes, initializes adapter metadata, checks/resets bus status, adds the I2C adapter, and creates sysfs attributes. I2C callers take `dev->lock`, force full HID power, issue writes and/or reads, poll status, and return to normal power. Reads wait on a completion that `ft260_raw_event()` completes after assembling input reports.

State is volatile: adapter state, transfer mutex, completion, read buffer/index/length, cached clock, and `need_wakeup_at`. Sysfs writes modify live FT260 settings such as I2C enable, UART mode, clock, and reset. Dependencies include HID core, USB HID, I2C core, completions, sysfs attributes, and `hid-ids.h`.

Risks center on transfer timing, status polling, multi-report read length accounting, and narrow combined write/read support where first-message length above two bytes returns `-EOPNOTSUPP`. Test signals include real FT260 I2C scans, plain and combined transfers, SMBus variants, idle wakeup, sysfs clock/reset paths, suspend/resume power hints, and malformed input reports.
