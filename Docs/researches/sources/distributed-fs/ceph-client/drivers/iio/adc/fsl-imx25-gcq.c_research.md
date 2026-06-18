# sources/distributed-fs/ceph-client/drivers/iio/adc/fsl-imx25-gcq.c

## Purpose
`fsl-imx25-gcq.c` is the IIO driver for the i.MX25 TSADC Generic Conversion Queue. It exposes eight voltage configurations for touchscreen and auxiliary inputs and lets firmware describe positive/negative references per configuration.

## Important APIs, types, and functions
- `struct mx25_gcq_priv` holds the regmap, completion, shared TSADC clock, IRQ, optional reference regulators, per-channel reference millivolts, and conversion mutex.
- `mx25_gcq_channels` defines channels `xp`, `yp`, `xn`, `yn`, `wiper`, and `inaux0..2`.
- `mx25_gcq_setup_cfgs()` initializes queue configuration registers and parses child-node `reg`, `fsl,adc-refp`, and `fsl,adc-refn` properties.
- `mx25_gcq_get_raw_value()` writes queue item 0, enables EOQ IRQ, starts one forced queue run, waits for completion, and reads FIFO data.
- `mx25_gcq_irq()` handles EOQ, disables the queue run, acknowledges status bits, and completes readers.

## Control flow
Probe maps MMIO, wraps it in a 32-bit regmap, initializes defaults, parses per-channel reference configuration, enables any referenced external regulators, enables the parent TSADC clock, requests the IRQ, and registers a direct-mode IIO device. `read_raw` uses the mutex for raw conversions and returns a scale of `channel_vref_mv / 2^12`.

## State and persistence
The driver programs the queue configuration registers at probe and stores per-channel reference voltage in memory. User reads do not persist state except for temporary queue item selection and queue-control bits. External regulators are enabled for the lifetime of the device through devm cleanup actions.

## Dependencies and integration points
It depends on the parent `mx25_tsadc` MFD data for the shared clock, `dt-bindings/iio/adc/fsl-imx25-gcq.h` for reference constants, regmap MMIO, regulators named `vref-yp`, `vref-xp`, or `vref-ext`, and a platform IRQ.

## Risks
- The shared clock is not owned by this child driver, so enable/disable sequencing must stay compatible with sibling TSADC users.
- Optional external references are required if firmware selects them; missing regulators correctly fail probe.
- Queue status is acknowledged broadly, so IRQ semantics must remain aligned with the MFD register definitions.
- `regulator_get_voltage()` errors are assigned into unsigned millivolt storage after setup; bad regulator implementations can lead to misleading scales.

## Test signals
Validate DT child-node parsing, invalid `reg` and reference values, internal and external reference scales, EOQ interrupt completion, timeout path, and shared-clock behavior with other TSADC functions enabled.
