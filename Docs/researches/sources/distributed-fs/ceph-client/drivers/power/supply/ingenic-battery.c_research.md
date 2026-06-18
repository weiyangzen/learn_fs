# sources/distributed-fs/ceph-client/drivers/power/supply/ingenic-battery.c

## Purpose
This platform driver exposes the Ingenic JZ47xx battery voltage ADC as a Linux power-supply battery. It is intentionally small: it reads a single IIO channel named `battery`, consumes design voltage limits from the power-supply battery-info binding, reports current voltage, min/max design voltage, and derives `HEALTH` from whether the sampled voltage is below or above those design limits.

## Important APIs, Types, and Functions
The central state is `struct ingenic_battery`, holding the `struct device`, IIO channel, mutable `power_supply_desc`, registered `power_supply`, and `power_supply_battery_info`. `ingenic_battery_get_property()` implements `POWER_SUPPLY_PROP_HEALTH`, `VOLTAGE_NOW`, `VOLTAGE_MIN_DESIGN`, and `VOLTAGE_MAX_DESIGN`. `ingenic_battery_set_scale()` queries `iio_read_max_channel_raw()` plus available `IIO_CHAN_INFO_SCALE` entries and programs the smallest fractional-log2 scale that can cover the configured maximum battery voltage. `ingenic_battery_probe()` wires the platform device to the power-supply core and validates the mandatory battery-info voltage fields.

## Control Flow
Probe allocates state, gets the `battery` IIO channel, builds a descriptor named `jz-battery`, registers the power supply with `drv_data` and fwnode, reads battery info, validates design min/max voltage, then calls `ingenic_battery_set_scale()`. Property reads are synchronous IIO reads. Health first reads voltage in microvolts, then rewrites the same integer field to a power-supply health enum.

## State and Persistence
The only persistent driver state is the battery-info pointer and selected ADC scale. The ADC scale write persists in the backing IIO provider until changed elsewhere. Runtime voltage and health are not cached.

## Dependencies and Integration Points
The driver depends on an IIO provider that supports processed reads, max raw reads, available scale enumeration, and optional scale writes using `IIO_VAL_FRACTIONAL_LOG2`. It integrates with DT via `ingenic,jz4740-battery` and with the power-supply battery-info parser through the monitored battery fwnode.

## Risks
Scale selection assumes the available scale list is ordered as numerator/exponent pairs and that `max_raw * scale` fits the `u64` calculation. If design voltages are absent or wrong, probe fails or health classification is misleading. `get_property()` returns the IIO read status after using `val->intval`, so callers see an error if the read failed, but any temporary value in `val` is not meaningful.

## Test Signals
Useful checks are successful probe with valid battery-info DT, correct ADC scale selection for several maximum voltages, `VOLTAGE_NOW` matching the IIO channel conversion, and health transitions below min, inside range, and above max. Negative tests should cover missing IIO channel, missing design voltage properties, unsupported scale formats, and scale write failures.
