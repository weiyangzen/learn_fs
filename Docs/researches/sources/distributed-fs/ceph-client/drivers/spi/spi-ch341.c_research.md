# sources/distributed-fs/ceph-client/drivers/spi/spi-ch341.c

## Purpose

`spi-ch341.c` is a USB-to-SPI controller driver for the QinHeng/WCH CH341A adapter. It registers a USB driver, exposes a SPI host backed by USB bulk transfers, configures CH341 stream/pin modes, and creates a default SPI device with modalias `spi-ch341a`.

## Important APIs, Types, and Functions

`struct ch341_spi_dev` stores the SPI controller, USB device, bulk pipe addresses, RX URB/buffer, TX buffer, and created child SPI device. `ch341_probe()` and `ch341_disconnect()` handle USB lifecycle. `ch341_transfer_one()` sends a `CH341A_CMD_SPI_STREAM` packet and reads the response through bulk endpoints. `ch341_set_cs()` drives CS through UIO stream commands. `ch341_config_stream()` and `ch341_enable_pins()` initialize the adapter.

## Control Flow

Probe finds bulk IN/OUT endpoints, allocates a devm SPI host, allocates buffers and a RX URB, submits the URB, configures controller callbacks and mode bits, stores USB interface data, sends stream configuration, enables pins, registers the controller, and creates a child SPI device. Each transfer builds a packet of at most 32 bytes including command byte, copies TX data after it, sends it on the bulk OUT pipe, then reads response bytes from the bulk IN pipe. Disconnect unregisters the child device and controller, disables pins, kills the URB, and frees it.

## State and Persistence Behavior

State is volatile USB/controller state. The TX buffer is reused for CS and transfer commands. The driver creates one child SPI device automatically after controller registration. Adapter pin state is enabled on probe and disabled on disconnect. There is no runtime PM or persistent storage.

## Dependencies and Integration Points

The file integrates with the USB core, SPI controller core, bulk endpoints, URBs, and a board-info-created child SPI device. It matches USB device ID `1a86:5512`.

## Risks and Edge Cases

`ch341_transfer_one()` caps the packet length at 32 bytes and silently truncates longer SPI transfers to 31 payload bytes while returning only the USB read status, not the number transferred. It unconditionally copies from `trans->tx_buf`, so RX-only transfers with NULL TX buffer can crash. It unconditionally reads into `trans->rx_buf`, so TX-only transfers with NULL RX buffer can also crash. The submitted RX URB appears unused for transfer data because transfers use synchronous `usb_bulk_msg()` reads. The driver advertises only `SPI_CPHA` and has fixed speed behavior.

## Test Signals

Tests should cover probe with missing endpoints, allocation failures, stream/pin command failures, transfer lengths 0, 1, 31, 32, and greater than 31 payload bytes, TX-only/RX-only validation, disconnect during pending operations, CS-high/low command bytes, and USB stall/disconnect errors from bulk messages.
