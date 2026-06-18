# sources/distributed-fs/ceph-client/drivers/regulator/tps6524x-regulator.c

Purpose: SPI regulator driver for TPS6524x PMICs, exposing three DCDCs, two LDOs, USB switch, and LCD switch.

Important APIs/types/functions: `struct tps6524x` owns SPI device, mutex, and generated descriptors. `struct supply_info` describes each rail’s voltage table, current-limit table, enable field, voltage field, and current-limit field. Low-level SPI helpers perform nonstandard 12/16/4-bit read/write transactions and status validation. Regulator ops manually implement enable, disable, is-enabled, voltage selector, and current limit.

Control flow: probe requires an array of platform `regulator_init_data`, allocates state, initializes mutex, creates descriptors from `supply_info`, and registers seven regulators. Writes go through `rmw_protect`, which sets write-enable, performs a locked RMW, then clears write-enable. Voltage/current ops validate fixed rails and selector bounds before writing encoded fields.

State and persistence: all rail state is in PMIC SPI registers. Driver state is descriptor metadata and lock only. Write-enable is explicitly toggled around protected updates.

Dependencies and integration points: SPI core, regulator framework, platform data, and PMIC-specific SPI framing/status bits. There is no OF parser in this file.

Risks: no regulator can probe without platform data. SPI transaction bit widths are unusual and controller-dependent. `rmw_protect` may leave write-enable set if the protected RMW fails before the final clear. Fixed rails reject set-voltage/current-limit requests.

Test signals: SPI status error decoding, write-enable set/clear sequencing under failures, all rail voltage/current tables, fixed rail behavior, mutex serialization, and platform-data array ordering.
