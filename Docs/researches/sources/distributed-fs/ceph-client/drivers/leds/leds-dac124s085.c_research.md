# sources/distributed-fs/ceph-client/drivers/leds/leds-dac124s085.c

Purpose: simple SPI LED-class driver for the four-channel DAC124S085 DAC, treating each DAC output as a 12-bit brightness LED.

Important APIs/types/functions: `struct dac124s085_led` contains classdev, SPI device, channel id, generated name, and mutex. `dac124s085_set_brightness()` packs channel id, `REG_WRITE_UPDATE`, and 12-bit brightness into a little-endian 16-bit word and writes it over SPI. Probe allocates one `struct dac124s085` with four LEDs, sets `spi->bits_per_word = 16`, and registers four classdevs.

Control flow: probe initializes each channel name `dac124s085-N`, sets max brightness to `0xfff`, and registers classdevs, unwinding any earlier registrations on failure. Brightness callbacks serialize per channel and do a single `spi_write()`. Remove unregisters all four LEDs.

State and persistence: no cached brightness except LED core fields. DAC output state remains in hardware until rewritten, powered down externally, or device reset. Mutex scope is per LED, not global across all channels.

Dependencies/integration: SPI core, LED class, DAC124S085 command format. Device matching is by SPI modalias `"dac124s085"`.

Risks: per-channel mutexes do not serialize concurrent SPI writes across channels; SPI core serializes transfers, but shared-device timing assumptions should be verified. Endianness is explicitly little-endian in the command word. No devm classdev registration, so unregister paths matter.

Test signals: check four LEDs appear, write boundary brightness values 0/4095, verify command word channel bits, simulate register failure unwind, and remove cleanup.
