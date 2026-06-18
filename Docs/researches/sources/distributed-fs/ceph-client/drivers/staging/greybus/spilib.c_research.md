# sources/distributed-fs/ceph-client/drivers/staging/greybus/spilib.c

## Purpose
Implements the reusable Greybus SPI controller library. It exposes a Linux `spi_controller`, discovers remote controller and chip-select configuration over Greybus, instantiates child SPI devices, and chunks Linux `spi_message` transfers into Greybus `GB_SPI_TYPE_TRANSFER` operations.

## Important APIs, Types, and Functions
`struct gb_spilib` stores the Greybus connection, parent device, optional hardware ops, transfer cursor state, cached controller caps, and timeout state. `gb_spilib_master_init()` allocates a SPI controller, fetches `GB_SPI_TYPE_MASTER_CONFIG`, assigns controller methods, registers the controller, and creates devices with `gb_spi_setup_device()`. `gb_spilib_master_exit()` unregisters the controller. The transfer path centers on `gb_spi_transfer_one_message()`, `gb_spi_operation_create()`, `gb_spi_decode_response()`, and `setup_next_xfer()`. Sizing helpers `tx_header_fit_operation()`, `calc_tx_xfer_size()`, and `calc_rx_xfer_size()` keep request/response payloads within Greybus limits.

## Control Flow and State
For each SPI message, the library starts at the first transfer and repeatedly builds one Greybus operation that can contain one or more SPI transfers or a partial transfer. TX bytes are copied behind the Greybus transfer descriptors; RX bytes are copied back from the response. `msg->state` uses internal sentinel values for idle, running, operation ready/done, message done, and error. Offsets allow a single large SPI transfer to span multiple Greybus operations, and `last_xfer_size` tracks how much of the current transfer was included in the most recent operation.

## Dependencies and Integration Points
Depends on Greybus operation APIs and Linux SPI core. The Greybus remote side supplies master mode bits, flags, bits-per-word mask, speed range, chip-select count, and per-chip-select device identity. Device config supports generic `spidev`, `spi-nor`, or a remote modalias. Optional `spilib_ops` hooks map to controller prepare/unprepare hardware callbacks.

## Risks and Test Signals
Risks include transfer chunking boundary errors, pointer arithmetic on `void *` buffers, unsupported bufferless transfers, timeout calculations for slow transfers, and maintaining correct `actual_length` across partial operations. `gb_spi_decode_response()` must match the request construction exactly, especially for mixed TX/RX and split transfers. Test signals include controller registration, SPI child enumeration, full-duplex transfer correctness across payload-size boundaries, mode/bits-per-word propagation, invalid remote device type handling, and clean controller unregister.
