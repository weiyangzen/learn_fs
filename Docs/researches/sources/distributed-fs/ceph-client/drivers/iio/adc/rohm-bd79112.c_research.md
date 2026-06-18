# sources/distributed-fs/ceph-client/drivers/iio/adc/rohm-bd79112.c

ROHM BD79112 SPI ADC/GPIO driver for a 32-pin signal monitoring hub. It exposes selected pins as 12-bit voltage ADC channels through IIO and the remaining pins as GPIOs, using a custom regmap over SPI for ADC and IO register access.

`struct bd79112_data` holds SPI/regmap/device state, GPIO chip, valid GPIO mask, VREF, optimized SPI messages, and DMA-aligned buffers. SPI/regmap callbacks are `bd79112_reg_read` and `bd79112_reg_write`. IIO path is `bd79112_read_raw`. GPIO path includes direction get/set, value get/set, `set_multiple`, `bd79112_gpio_dir_set`, and valid-mask initialization. Probe uses `devm_iio_adc_device_alloc_chaninfo_se` to derive ADC channels from firmware.

Probe initializes regmap with custom SPI operations, enables `vdd` and `iovdd`, prepares optimized two-transfer reads and one-transfer writes, allocates IIO channel info from firmware, optionally registers all pins as GPIOs if no ADC channels are described, clears GPIO enable registers so described ADC pins are ADCs, registers IIO, computes the complement GPIO mask, defaults GPIO pins to input, and registers a GPIO chip. Raw reads call `regmap_read` on the channel number; scale returns VDD in mV over 12 bits.

Regmap uses a Maple cache with volatile ADC and GPI value ranges. The ADC/GPIO mux is configured only at probe, and GPIO valid mask prevents operations on ADC pins. Dependencies include SPI, regmap custom callbacks, regulators, IIO ADC helper channel allocation, GPIO framework, firmware channel descriptions, and `IIO_DRIVER` namespace import.

Risks include unsupported runtime mux changes, stale valid-mask assumptions if registers are modified externally, ADC status flag bits returned with raw ADC data because `bd79112_read_raw` does not mask/check them, and invalid offset protection relying on valid masks. Test SPI framing, firmware channel allocation, no-ADC all-GPIO mode, mixed valid masks, GPIO bank operations, raw ADC status behavior, regulator scale, and regmap cache/volatile behavior.
