# sources/distributed-fs/ceph-client/drivers/i2c/i2c-core-slave.c

Purpose: common I2C slave-mode support. It registers client callbacks with adapters that can act as slave targets, unregisters them, dispatches slave events with tracing, and detects own-slave-address configuration in firmware.

Important APIs: `i2c_slave_register()`, `i2c_slave_unregister()`, `i2c_slave_event()`, and `i2c_detect_slave_mode()` are GPL exports. The adapter algorithm callbacks `reg_slave` and `unreg_slave` are the integration contract, while `client->slave_cb` holds the active callback.

Control flow: registration validates client/callback, warns if the client lacks `I2C_CLIENT_SLAVE`, performs strict 7-bit address validation for non-10-bit clients, checks adapter support, stores the callback, and calls `reg_slave()` under the root adapter lock. Unregister mirrors this through `unreg_slave()` and clears `slave_cb` only on success. Event dispatch calls the callback and emits the slave tracepoint.

State and persistence: the only framework state is `client->slave_cb` plus adapter hardware state established by the adapter driver. Firmware slave-mode detection scans child `reg` properties for `I2C_OWN_SLAVE_ADDRESS`.

Dependencies and integration: used by slave EEPROM/testunit and SMBus host-notify helpers. Depends on trace events, OF/ACPI fwnodes, and adapter algorithm support.

Risks: missing slave flag may collide with normal clients. Adapter callbacks run under root bus lock and must not recurse incorrectly. ACPI slave detection is explicitly unsupported. Callback return values can cause NACK behavior in controller drivers.

Test signals: strict-address rejection, unsupported-adapter `-EOPNOTSUPP`, register/unregister lock coverage, tracepoint output, DT own-slave detection, and client drivers receiving all event types.
