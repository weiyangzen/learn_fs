# sources/distributed-fs/ceph-client/drivers/iio/adc/max77541-adc.c

Purpose: this platform IIO child driver exposes ADC readings from the MAX77541 MFD PMIC. It provides VSYS, VOUT1, VOUT2 voltage channels and a temperature channel using the parent device regmap.

Important APIs, types, and functions: channel enums identify VSYS, VOUT1, VOUT2, and temperature. `max77541_adc_raw()` reads the channel's data register. `max77541_adc_scale()` derives voltage scale from fixed VSYS or the parent regulator range field `MAX77541_BITS_MX_CFG1_RNG`; temperature scale is fixed. `max77541_adc_offset()` supplies absolute-zero-derived temperature offset. `max77541_adc_probe()` obtains the parent regmap and registers the IIO device.

Control flow: the MFD core creates a `max77541-adc` platform device. Probe allocates a small private pointer to the parent regmap, configures direct-mode IIO metadata, assigns four static channels, and registers. Reads dispatch by mask: raw regmap reads channel data, scale computes per-channel units, and temp offset returns a fixed integer.

State and persistence: the ADC driver stores only a parent regmap pointer. Conversion data and range selection live in parent MAX77541 registers. There is no local locking, relying on regmap serialization and parent MFD ownership.

Dependencies and integration points: it depends on the MAX77541 MFD header/register definitions, platform bus, regmap, and IIO direct mode. Scale for VOUT channels is coupled to the M2 configuration register in the parent device.

Risks and test signals: test parent regmap availability, all range selections for VOUT scale, raw reads for each channel, and temperature offset/scale unit interpretation. Main risks are implicit parent configuration coupling and lack of explicit NULL check after `dev_get_regmap()`.
