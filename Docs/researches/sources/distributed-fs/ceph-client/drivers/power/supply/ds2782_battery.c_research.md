# sources/distributed-fs/ceph-client/drivers/power/supply/ds2782_battery.c

Purpose: implements an I2C fuel-gauge driver for Maxim/Dallas DS2782 and DS2786 chips, exposing status, capacity, voltage, current, and temperature through the power-supply class.

Important APIs/types/functions: `struct ds278x_info` holds I2C client, battery descriptor, selected ops table, delayed work, sense resistor value for DS2786, cached capacity, and cached status. `struct ds278x_battery_ops` selects chip-specific current/voltage/capacity conversion functions. `ds278x_read_reg()` and `ds278x_read_reg16()` wrap SMBus register reads.

Control flow: probe allocates a unique IDA number for the supply name, validates DS2786 platform data, selects the ops table from the I2C ID, initializes default full status/capacity, registers the battery, initializes delayed work, and starts one-second polling. Polling recomputes status/capacity and emits `power_supply_changed()` on change. Suspend cancels polling; resume restarts it.

State and persistence: cached `status` and `capacity` are volatile. No writable properties or persistent driver-managed calibration are exposed. DS2786 requires platform `rsns` to convert current.

Dependencies and integration: depends on I2C SMBus byte/word reads, IDA allocation, optional platform data from `linux/ds2782_battery.h`, delayed-work autocancel, and power-supply registration.

Risks and test signals: this source snapshot duplicates `POWER_SUPPLY_PROP_VOLTAGE_NOW` in the property list. Conversion constants and integer division should be checked for DS2782 and DS2786 separately, especially sense resistor handling. Test missing DS2786 platform data, IDA cleanup on probe failures, SMBus read errors, polling notifications, suspend/resume, and boundary capacity values.
