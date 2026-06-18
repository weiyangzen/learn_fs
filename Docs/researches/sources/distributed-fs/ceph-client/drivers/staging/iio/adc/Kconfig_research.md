# sources/distributed-fs/ceph-client/drivers/staging/iio/adc/Kconfig

## Purpose
Defines the staging ADC menu and the `AD7816` temperature sensor/ADC option.

## Important Entries and Integration
`config AD7816` is tristate, depends on `SPI` and on `GPIOLIB || COMPILE_TEST`, and builds support for AD7816/AD7817/AD7818. The module name is `ad7816`.

## Risks and Test Signals
The GPIO dependency is important because the driver requires rdwr, convert, and sometimes busy GPIOs. Kconfig and compile tests should cover all three supported IDs.
