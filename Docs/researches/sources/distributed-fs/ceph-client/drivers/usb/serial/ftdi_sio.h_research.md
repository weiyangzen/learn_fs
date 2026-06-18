# sources/distributed-fs/ceph-client/drivers/usb/serial/ftdi_sio.h

## Purpose

This header documents and defines the FTDI vendor protocol used by `ftdi_sio.c`. It contains request numbers, request types, channel identifiers, baud divisor constants, data-format bit fields, modem-control masks, flow-control modes, latency/event/bitmode/EEPROM requests, CBUS GPIO mux constants, and status-byte masks for bulk input.

## Important APIs, Types, And Functions

The header has no functions. Important definitions include `FTDI_SIO_RESET`, `FTDI_SIO_MODEM_CTRL`, `FTDI_SIO_SET_FLOW_CTRL`, `FTDI_SIO_SET_BAUD_RATE`, `FTDI_SIO_SET_DATA`, `FTDI_SIO_GET_MODEM_STATUS`, `FTDI_SIO_SET_LATENCY_TIMER`, `FTDI_SIO_SET_BITMODE`, `FTDI_SIO_READ_PINS`, `FTDI_SIO_READ_EEPROM`, `CHANNEL_A` through `CHANNEL_D`, and `enum ftdi_sio_baudrate`.

For data format it defines `FTDI_SIO_SET_DATA_PARITY_*`, `FTDI_SIO_SET_DATA_STOP_BITS_*`, and `FTDI_SIO_SET_BREAK`. For modem and flow control it defines `FTDI_SIO_SET_DTR_*`, `FTDI_SIO_SET_RTS_*`, `FTDI_SIO_DISABLE_FLOW_CTRL`, `FTDI_SIO_RTS_CTS_HS`, `FTDI_SIO_DTR_DSR_HS`, and `FTDI_SIO_XON_XOFF_HS`. Status masks include `FTDI_RS0_CTS`, `FTDI_RS0_DSR`, `FTDI_RS0_RI`, `FTDI_RS0_RLSD`, `FTDI_RS_OE`, `FTDI_RS_PE`, `FTDI_RS_FE`, `FTDI_RS_BI`, and `FTDI_RS_TEMT`.

## Control Flow

There is no executable control flow, but the constants define the protocol flow used by the C driver: reset or purge through request 0, set baud by encoding divisors into `wValue`/`wIndex`, set data characteristics through request 4, control DTR/RTS through mask/value bits, select flow-control protocol through high `wIndex` bits, read modem status through an IN control request, tune latency/event behavior through control requests, and parse the first two bytes of every bulk-in packet as modem and line status.

## State And Persistence

The header owns no state. It describes hardware state that the driver can set or observe: UART format, break state, DTR/RTS, flow control, latency timer, event character, bitbang mode, CBUS pin level, EEPROM words, modem inputs, line errors, and transmitter-empty status.

## Dependencies And Integration Points

`ftdi_sio.c` includes this header directly. The definitions align Linux tty/serial concepts with FTDI USB vendor commands and with EEPROM/CBUS behavior used by optional gpiolib integration. The file also documents legacy descriptor and endpoint data formats used by maintainers when validating packet parsing.

## Risks

Because this header is protocol authority, incorrect bit definitions propagate into every FTDI operation. The comments include historical notes and old-device caveats; implementation changes must preserve differences between SIO, AM/BM, and newer chips. The modem-control comment notes DTR and RTS cannot be set with one command, while the implementation composes both bits in one value, so behavior should be checked against real devices. Documentation-only descriptor examples can become stale relative to modern variants.

## Test Signals

Validation is indirect: build `ftdi_sio.c`, exercise every request family on hardware or USB emulation, compare baud divisor encodings against FTDI application notes, verify status-byte masks by injecting CTS/DSR/RI/DCD and line errors, test latency/event/EEPROM control messages, and confirm CBUS bitmode constants match EEPROM-configured GPIO pins.
