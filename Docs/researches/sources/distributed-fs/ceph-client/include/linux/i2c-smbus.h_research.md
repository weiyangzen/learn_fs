# sources/distributed-fs/ceph-client/include/linux/i2c-smbus.h

## Purpose
Declares SMBus-specific helper devices and alert/host-notify support layered on the I2C core.

## APIs, Control Flow, and State
`struct i2c_smbus_alert_setup` optionally passes an IRQ to the SMBus alert client. `i2c_new_smbus_alert_device()` creates the alert response address client, and `i2c_handle_smbus_alert()` handles alerts. If both SMBus and I2C slave support are enabled, host-notify slave helpers create/free a host-notify device; otherwise they return `ERR_PTR(-ENOSYS)` or no-op. If SMBus and DMI are enabled, SPD write-protect registration helpers expose platform policy; otherwise they are no-ops.

## Dependencies, Integration, Risks, and Tests
Depends on I2C core, spinlocks, and workqueues. Integrates with SMBus alert protocol, host notify, DIMM SPD write-protection policy, and adapter interrupt/polling implementations. Risks include assuming IRQ handling exists when `irq` is omitted, failing to free host-notify clients, not checking `ERR_PTR`, and SPD policy being compiled out. Test signals include SMBALERT# events, host-notify slave callbacks, alert polling fallback, SPD write enable/disable registration, and config combinations for SMBus/slave/DMI.
