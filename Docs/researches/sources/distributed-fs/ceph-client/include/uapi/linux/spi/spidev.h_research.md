# sources/distributed-fs/ceph-client/include/uapi/linux/spi/spidev.h

## Purpose
Defines the `/dev/spidev*` ioctl ABI used by userspace to configure an SPI device and submit synchronous transfer batches.

## Important APIs, Types, and Constants
`struct spi_ioc_transfer` describes one transfer with userspace `tx_buf` and `rx_buf` pointers, `len`, `speed_hz`, `delay_usecs`, `bits_per_word`, `cs_change`, `tx_nbits`, `rx_nbits`, `word_delay_usecs`, and padding. `SPI_IOC_MESSAGE(N)` submits an array of transfers. Configuration ioctls include `SPI_IOC_RD_MODE`, `SPI_IOC_WR_MODE`, `SPI_IOC_RD_LSB_FIRST`, `SPI_IOC_WR_LSB_FIRST`, `SPI_IOC_RD_BITS_PER_WORD`, `SPI_IOC_WR_BITS_PER_WORD`, `SPI_IOC_RD_MAX_SPEED_HZ`, `SPI_IOC_WR_MAX_SPEED_HZ`, `SPI_IOC_RD_MODE32`, and `SPI_IOC_WR_MODE32`.

## Control Flow, State, and Persistence
Userspace configures defaults, then submits transfer arrays that execute together like `spi_sync()`. Transfer fields can temporarily override device speed and word size. Device defaults persist for the file/device until changed by ioctl.

## Dependencies and Integration Points
Depends on `<linux/types.h>`, `<linux/ioctl.h>`, and `<linux/spi/spi.h>`. Integrates with the spidev character driver and SPI controller drivers.

## Risks and Test Signals
The struct layout is explicitly 32/64-bit stable and must be zero-initialized for future compatibility. Risks include `_IOC_SIZEBITS` overflow via large `N`, invalid user pointers, unsupported `word_delay_usecs` silently ignored, and use of 8-bit mode ioctls for mode bits above bit 7. Test with ABI size checks, loopback transfers, invalid pointer handling, `SPI_IOC_MESSAGE(0/large)`, and mode32 round trips.
