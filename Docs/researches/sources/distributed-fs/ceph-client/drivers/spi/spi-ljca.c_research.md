# sources/distributed-fs/ceph-client/drivers/spi/spi-ljca.c

## Purpose

`spi-ljca.c` exposes the Intel La Jolla Cove Adapter USB-SPI function as a Linux SPI controller on the auxiliary bus. It translates SPI transfers into LJCA USB protocol commands.

## Important APIs, Types, And Functions

`struct ljca_spi_dev` holds the LJCA client, SPI controller, LJCA SPI descriptor, cached speed/mode, and fixed 60-byte input/output protocol buffers. Protocol structures are `ljca_spi_init_packet` and `ljca_spi_xfer_packet`; commands include init, read, write, write-read, and deinit.

Important functions are `ljca_spi_read_write()`, `ljca_spi_init()`, `ljca_spi_deinit()`, `ljca_spi_transfer()`, `ljca_spi_transfer_one()`, `ljca_spi_probe()`, remove, and system suspend/resume wrappers.

## Control Flow, State, And Persistence

Probe allocates an SPI host, stores LJCA platform data, sets mode support to CPOL/CPHA, chooses a 48 MHz max clock, and registers the controller. For each transfer, the driver computes a LJCA divider from requested speed, initializes the bridge if speed or mode changed, then splits the transfer into chunks no larger than `LJCA_SPI_MAX_XFER_SIZE`. Each chunk carries an indicator containing sequence id, completion flag, and adapter SPI index.

State is limited to cached mode/speed and the stack of chunked transfers through fixed buffers. There is no persistent storage; remove unregisters the controller and sends LJCA deinit.

## Dependencies And Integration Points

The driver depends on `linux/auxiliary_bus.h`, SPI core, and `linux/usb/ljca.h`. It imports the `LJCA` namespace and binds to `usb_ljca.ljca-spi`. Runtime PM is not used for transfers; system sleep calls suspend/resume the SPI controller.

## Risks And Test Signals

Risks include protocol-size limits, unvalidated returned packet lengths beyond the minimum packet header, mode/speed caching errors across devices, and divider clamping to the bridge's minimum speed enum. Test with long transfers crossing the 60-byte packet boundary, read-only/write-only/full-duplex transfers, all four SPI modes, suspend/resume, and disconnect during transfer.
