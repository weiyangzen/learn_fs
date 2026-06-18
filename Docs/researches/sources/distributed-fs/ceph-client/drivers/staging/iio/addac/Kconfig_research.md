# sources/distributed-fs/ceph-client/drivers/staging/iio/addac/Kconfig

## Purpose
Defines staging ADDAC options for the ADT7316/7/8 and ADT7516/7/9 temperature, ADC, and DAC family.

## Important Entries and Integration
`ADT7316` enables the shared core and depends on `GPIOLIB || COMPILE_TEST`. `ADT7316_SPI` depends on `SPI && ADT7316`, defaults to yes, and builds the SPI transport module. `ADT7316_I2C` depends on `I2C && ADT7316` and builds the I2C transport module.

## Risks and Test Signals
The split symbols must keep the shared core available whenever either bus glue is selected. Build matrix tests should cover core-only impossible states, SPI-only, I2C-only, and both transports.
