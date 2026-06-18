# sources/distributed-fs/ceph-client/drivers/net/can/m_can/tcan4x5x.h

## Purpose
`tcan4x5x.h` defines private TCAN4x5x SPI/regmap data structures and the regmap initialization prototype shared by the TCAN core and regmap files.

## Important APIs, Types, And Functions
- `TCAN4X5X_SANITIZE_SPI` enables clearing unused TX bytes for full-duplex reads.
- `struct tcan4x5x_buf_cmd` is the packed SPI command header: opcode, 16-bit address, and word count.
- `struct tcan4x5x_map_buf` combines a command header and a 256-word data buffer, cacheline aligned for transfer use.
- `struct tcan4x5x_priv` embeds `m_can_classdev` and stores regmap, SPI device, GPIOs, regulator, TX/RX buffers, and DT option state.
- `tcan4x5x_spi_cmd_set_len()` converts byte length to the TCAN command word count.
- `tcan4x5x_regmap_init()` is implemented by `tcan4x5x-regmap.c`.

## Control Flow
The TCAN SPI probe allocates an M_CAN class device with enough private space for `struct tcan4x5x_priv`; the core and regmap files recover this structure from `m_can_classdev` or SPI driver data and share the same transfer buffers.

## State And Persistence
The header defines volatile runtime state only. GPIO descriptors, regulator handles, regmap, SPI device, and aligned buffers are owned for the lifetime of the SPI device.

## Dependencies And Integration Points
It includes GPIO consumer, regmap, regulator, SPI, and `m_can.h`. It is the bridge between the bus transport implementation and the M_CAN class wrapper.

## Risks And Edge Cases
- Buffer length and SPI command length assume transfers are multiples of four bytes.
- Because the class device is embedded first, container conversions depend on stable struct layout.
- The static transfer buffer size must stay consistent with regmap `.max_raw_read` and `.max_raw_write`.

## Test Signals
Build TCAN core/regmap together, validate struct layout through normal probe, and test SPI transfers at the maximum configured raw size.
