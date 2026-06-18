# sources/distributed-fs/ceph-client/drivers/iio/adc/rn5t618-adc.c

Ricoh RN5T618 PMIC ADC IIO driver exposing eight current/voltage channels with raw, averaged raw, and scale attributes. It uses the parent MFD regmap and ADC-end interrupt to perform single conversions.

`struct rn5t618_adc_data` stores device, parent `struct rn5t618`, conversion completion, and IRQ. `rn5t618_ratios[]` provides channel scale ratios. Core functions are `rn5t618_read_adc_reg`, `rn5t618_adc_irq`, `rn5t618_adc_read`, and `rn5t618_adc_probe`. `rn5t618_maps[]` maps VADP/VUSB channels to the RN5T618 power driver.

Probe gets parent MFD data, resolves the ADC virtual IRQ from regmap-irq data, initializes IIO channels, stops any auto-conversion by clearing `ADCCNT3`, requests the threaded ADC IRQ, registers IIO maps, and registers the IIO device. Scale reads return reference voltage times ratio over 4095. Raw and averaged reads select a channel, enable ADC-end IRQ, set/clear average mode, initialize completion, set `GODONE`, wait up to 500 ms for IRQ, read the two-register 12-bit result, and return it.

Only completion and IRQ identity are kept. The driver disables automatic conversion at probe and uses single-conversion mode for every read. Hardware IRQ status registers are cleared in the IRQ handler. Dependencies include RN5T618 MFD definitions, parent regmap, regmap IRQ domain, IIO direct mode, and IIO machine maps.

Risks include no mutex around conversion setup, no polling fallback, IRQ handler clearing threshold IRQ status as well as ADC-end status, and the unusual `.indexed = 1.` initializer spelling. Test concurrent reads, IRQ timeout, all scale ratios, auto-conversion disabled state, VADP/VUSB maps, missing IRQ, and 12-bit assembly.
