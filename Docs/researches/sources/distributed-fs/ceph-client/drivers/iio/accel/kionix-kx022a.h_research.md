# sources/distributed-fs/ceph-client/drivers/iio/accel/kionix-kx022a.h

Purpose: shared register and chip-info contract for the KX022A-family core and I2C/SPI wrappers. It defines KX022A/KX132 register addresses, bit masks, device IDs, FIFO sizes, and the `struct kx022a_chip_info` abstraction used to handle multiple related chips with one core.

Important types and constants: the header defines IDs for KX022A, KX132ACR-LBZ, KX134ACR-LBZ, KX132-1211, and KX134-1211; control bits such as software reset, PC1, data-ready, range select, ODR, FIFO enable, watermark, and interrupt config; and `struct kx022a_chip_info` fields for chip name, regmap config, scale table, channels, FIFO length, register addresses, interrupt registers, output register, and FIFO byte-count callback.

Integration, risks, and tests: wrappers use exported chip-info objects for match data and pass them to `kx022a_probe_internal()`. Any register definition error propagates into core behavior across both I2C and SPI. One visible risk is macro alias fragility around interrupt polarity definitions, so compile coverage is important. Test signals include successful compilation for all chip-info users, correct match-data pointer resolution, WHO_AM_I comparison against header IDs, FIFO length/watermark limits, and scale table sizing.
