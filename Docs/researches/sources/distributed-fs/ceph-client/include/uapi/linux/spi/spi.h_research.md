# sources/distributed-fs/ceph-client/include/uapi/linux/spi/spi.h

## Purpose
Defines userspace-visible SPI mode bit flags and mode combinations shared by spidev and userspace SPI tools.

## Important APIs, Types, and Constants
There are no structs or functions. Constants include `SPI_CPHA`, `SPI_CPOL`, `SPI_MODE_0` through `SPI_MODE_3`, `SPI_CS_HIGH`, `SPI_LSB_FIRST`, `SPI_3WIRE`, `SPI_LOOP`, `SPI_NO_CS`, `SPI_READY`, dual/quad/octal transfer flags, `SPI_CS_WORD`, `SPI_3WIRE_HIZ`, `SPI_RX_CPHA_FLIP`, `SPI_MOSI_IDLE_LOW`, `SPI_MOSI_IDLE_HIGH`, and `SPI_MODE_USER_MASK`.

## Control Flow, State, and Persistence
The header is declarative. SPI device state is set by ioctl users such as `spidev.h`. `SPI_MODE_USER_MASK` bounds userspace-accepted bits and must not overlap kernel-private mode bits.

## Dependencies and Integration Points
Depends on `<linux/const.h>` for `_BITUL`. Used by `spidev.h`, SPI test tools, and libraries that construct mode words for `SPI_IOC_WR_MODE` and `SPI_IOC_WR_MODE32`.

## Risks and Test Signals
Risks include adding a bit without extending `SPI_MODE_USER_MASK`, overlap with kernel-only mode bits, and old 8-bit mode ioctls truncating newer flags. Test via compile-time mask assertions, spidev mode32 round trips, and hardware or loopback transfers for each line-width flag supported by a controller.
