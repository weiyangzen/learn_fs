# sources/distributed-fs/ceph-client/drivers/media/i2c/s5c73m3/s5c73m3-spi.c

## Purpose
`s5c73m3-spi.c` provides the SPI transport used by the S5C73M3 core to upload firmware and perform raw SPI reads. It also registers a small SPI driver whose probe captures the matching SPI device into the shared camera state.

## Important APIs, Types, and Functions
The internal transfer primitive is `spi_xmit(struct spi_device *spi_dev, void *addr, int len, enum spi_direction dir)`, which builds a one-transfer `spi_message` for TX or RX and calls `spi_sync()`. Exported internal helpers are `s5c73m3_spi_write()`, `s5c73m3_spi_read()`, `s5c73m3_register_spi_driver()`, and `s5c73m3_unregister_spi_driver()`. `s5c73m3_spi_probe()` sets `bits_per_word = 32`, calls `spi_setup()`, and stores the probed `spi_device` under `state->lock`.

## Control Flow
The core driver calls `s5c73m3_register_spi_driver()` during I2C probe, filling `state->spidrv` with a probe callback, driver name `S5C73M3-SPI`, and OF match table `samsung,s5c73m3`. When a matching SPI device probes, the SPI callback recovers the enclosing `struct s5c73m3`, configures SPI word size, and records `state->spi_dev`. Firmware upload splits the buffer into chunks, sends any remainder, and finally sends 32 zero padding bytes.

## State and Persistence
The file persists only the current `state->spi_dev` pointer in shared memory. There is no firmware cache, persistent SPI configuration beyond `bits_per_word`, or file state.

## Dependencies and Integration Points
It depends on the Linux SPI core, device-tree matching, V4L2 logging through the shared sensor subdev, and `struct s5c73m3` from `s5c73m3.h`. It integrates tightly with `s5c73m3-core.c`, which registers/unregisters the SPI driver and calls the SPI read/write helpers during boot.

## Risks and Edge Cases
`spi_xmit()` returns `-ENODEV` if firmware upload happens before a SPI device has probed. Pointer arithmetic is performed on `void *`/`const void *`, relying on GNU C behavior used by the kernel. `s5c73m3_spi_write()` always emits 32 bytes of padding after the payload. The SPI driver is embedded per camera state, so multiple instances depend on the SPI core accepting dynamically registered driver objects safely.

## Test Signals
Signals include a successful SPI probe log, `spi_setup()` accepting 32-bit words, firmware upload split into expected chunks plus padding, clean `-ENODEV` before SPI binding, proper unregister on I2C remove or probe failure, and no `spi_sync failed` errors during ROM/SPI boot.
