# sources/distributed-fs/ceph-client/drivers/leds/leds-spi-byte.c

Purpose: simple SPI LED driver for controllers whose brightness is represented by a single MOSI byte. The included chip definition targets Ubiquiti airCube-compatible `ubnt,acb-spi-led` devices.

Important APIs, types, and functions: `struct spi_byte_chipdef` describes off and maximum byte values. `struct spi_byte_led` owns the LED class device, SPI device, mutex, and chip definition. `spi_byte_brightness_set_blocking()` writes `off_value + brightness` as one byte. `spi_byte_probe()` validates that exactly one LED child exists, sets default state, writes the initial value, and registers an extended LED class device.

Control flow: SPI probe allocates state, initializes the mutex, loads OF match data, calculates `max_brightness`, reads the single child node, applies `LEDS_DEFSTATE_ON` as max brightness, immediately writes hardware, and registers the LED.

State and persistence: no cached hardware value beyond LED core brightness. The device receives each brightness byte directly. Default state keep is not implemented; anything except explicit on starts off.

Dependencies and integration points: depends on SPI core, fwnode child properties, LED class, and OF match data. It declares only brightness control despite the hardware protocol documenting additional modes.

Risks and test signals: test child-count validation, initial brightness write before registration, SPI write failures, and max/off chip definition math. Hardware tests should confirm mode bits are not accidentally set by high brightness and that no MISO response is required.
