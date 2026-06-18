<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/inspur-ipsps.c -->
## sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/inspur-ipsps.c

### Purpose
`inspur-ipsps.c` is a PMBus hwmon driver for Inspur Power System power supplies. It exposes the standard PMBus voltage, current, power, fan, temperature, and status sensors for one page, and adds vendor-specific sysfs attributes for identity strings, firmware version, hardware version, part/serial numbers, and supply operating mode.

### Important APIs, types, and functions
The file defines vendor registers `IPSPS_REG_VENDOR_ID`, `IPSPS_REG_MODEL`, `IPSPS_REG_FW_VERSION`, `IPSPS_REG_PN`, `IPSPS_REG_SN`, `IPSPS_REG_HW_VERSION`, and `IPSPS_REG_MODE`. `enum ipsps_index` and `ipsps_regs[]` map hwmon sensor attributes to those SMBus registers. `ipsps_string_show()` reads block strings and terminates at `#`; `ipsps_fw_version_show()` validates the six-byte firmware payload; `ipsps_mode_show()` renders active/standby/redundancy state; `ipsps_mode_store()` writes only active or standby values. `ipsps_info` declares the PMBus sensor surface and `ipsps_pdata` sets `PMBUS_SKIP_STATUS_CHECK`.

### Control flow
Probe stores `ipsps_pdata` in `client->dev.platform_data` and calls `pmbus_do_probe()`. The PMBus core creates the standard hwmon attributes from `ipsps_info.func[0]`; `ATTRIBUTE_GROUPS(ipsps)` adds the vendor attributes. Mode writes are string-matched through `sysfs_streq()` and translated to byte writes.

### State and persistence behavior
The driver has no allocated private data. Persistent state lives on the PSU and includes the vendor identity fields and writable mode register. The platform-data pointer is a static object. The mode sysfs attribute can persistently alter PSU behavior depending on device firmware.

### Dependencies and integration points
It depends on the PMBus core, Linux hwmon sensor-device-attribute helpers, I2C SMBus byte/block operations, optional OF matching through `inspur,ipsps1`, and the I2C id `ipsps1`.

### Risks
`ipsps_string_show()` uses `memscan()` and writes `*p = '\0'`; if no `#` appears, `p` points at `data + rc`, which is safe only because the buffer has one extra byte and `rc` is bounded by SMBus block length. Firmware parsing rejects any length other than six bytes. `PMBUS_SKIP_STATUS_CHECK` avoids probe failures on status reads but can hide broken status behavior.

### Test signals
Useful tests include successful probe with standard PMBus sensors, sysfs reads for every vendor attribute, malformed firmware block returning `-EPROTO`, unknown mode rendering `unspecified`, active/standby writes changing the mode byte, invalid mode writes returning `-EINVAL`, OF and I2C modalias binding, and behavior when status checks would otherwise fail.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/inspur-ipsps.c -->
