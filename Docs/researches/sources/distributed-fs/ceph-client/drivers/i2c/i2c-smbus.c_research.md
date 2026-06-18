# sources/distributed-fs/ceph-client/drivers/i2c/i2c-smbus.c

Purpose: optional SMBus protocol extensions outside the always-built core helpers. It implements SMBALERT handling, a slave-mode SMBus Host Notify receiver helper, and DMI-based SPD EEPROM auto-instantiation helpers.

Important APIs: `i2c_handle_smbus_alert()` schedules alert work for an ARA client. With slave support, `i2c_new_slave_host_notify_device()` and `i2c_free_slave_host_notify_device()` manage a slave client at address `0x08`. DMI exports are `i2c_register_spd_write_disable()` and `i2c_register_spd_write_enable()`.

Control flow: the `smbus_alert` driver binds an alert response address client, obtains an IRQ from setup data, firmware `smbus_alert`, or `smbalert` GPIO, and requests a threaded IRQ. The handler repeatedly reads ARA bytes, decodes alerting address/data bit, invokes the matching client driver's `alert()` callback, and forces all alert handlers if the same unhandled address repeats. Host-notify support collects the first byte of a 3-byte slave write and calls `i2c_handle_smbus_host_notify()`. SPD registration scans DMI memory devices, validates a common memory type, chooses `spd`, `ee1004`, or `spd5118`, and probes addresses `0x50` upward.

State and persistence: alert state stores work item and ARA client. Host-notify state stores received byte index/address in platform data. SPD-instantiated clients persist until adapter removal.

Dependencies and integration: depends on I2C core, SMBus helpers, IRQ/GPIO firmware properties, DMI memory-device data, optional slave core, and client-driver alert callbacks.

Risks: unhandled alerts can loop, mitigated by repeated-address force handling. Host Notify currently ignores the data parameter beyond the notifying address. DMI SPD instantiation is heuristic and skips mixed memory types or unsupported types. DDR5 SPD is skipped when write-disabled mode requests safety.

Test signals: SMBALERT IRQ and polling helper paths, alert callback dispatch, repeated unhandled alert behavior, host-notify slave writes, DMI slot/type combinations, and SPD client creation logs.
