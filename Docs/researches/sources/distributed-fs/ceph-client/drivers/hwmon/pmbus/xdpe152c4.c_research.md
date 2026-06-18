# sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/xdpe152c4.c

Purpose: compact PMBus driver for Infineon XDPE152C4/XDPE15284 VR controllers. It exposes two linear-format PMBus pages with voltage, current, power, input, and temperature capabilities.

Important APIs/types/functions: `xdpe152_info` is the driver’s primary contract: two pages, linear formats for all supported classes, page-specific `func[]` masks. `xdpe152_probe()` copies that template and delegates to PMBus core.

Control flow: I2C/OF matching selects the driver, probe allocates a per-client `pmbus_driver_info` copy, and `pmbus_do_probe()` handles all PMBus discovery and sysfs creation.

State and persistence: only PMBus core state persists. The driver does not cache telemetry, write registers, or implement custom read/write hooks.

Dependencies/integration: I2C, OF matching, PMBus core.

Risks: capabilities are static and assume the hardware exposes the listed sensors on both pages. There is no chip-specific runtime validation or format negotiation.

Test signals: successful probe for both IDs, visible two-page PMBus attributes, linear-format value sanity, and error-free module namespace import for PMBus.
