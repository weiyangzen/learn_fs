# sources/distributed-fs/ceph-client/drivers/usb/serial/mct_u232.h

## Purpose
This header defines the Magic Control Technology USB-RS232 protocol constants used by `mct_u232.c`: supported vendor/product IDs, vendor request numbers and sizes, LCR/MCR/MSR/LSR bit encodings, and a local forward declaration for baud-rate calculation.

## Important APIs, Types, and Constants
USB IDs cover original MCT, Sitecom, D-Link DU-H3SP, and Belkin F5U109 variants. Request constants define get/set modem status, baud rate, line control, modem control, the unknown post-baud request, and CTS gating. LCR constants map break, parity, data bits, and stop bits. MCR constants map DTR/RTS output encoding. MSR constants map current and delta modem-line bits. LSR constants map transmit and receive error/status bits.

## Control Flow
`mct_u232.c` uses these constants for every vendor control transfer, for termios-to-LCR encoding, for modem control and status translation, for `icount` delta increments, for break handling, and for the data/status indexes in interrupt packets.

## State and Persistence
The header is stateless. Its values are cached in `mct_u232_private.last_lcr`, `last_msr`, `last_lsr`, and `control_state`, and are sent to or read from device firmware/register emulation.

## Dependencies and Integration Points
It is a private header for the MCT driver and assumes Linux USB serial and `speed_t` declarations are present when included. The comments document reverse-engineered protocol behavior and serve as implementation guidance for compatible hardware variants.

## Risks
The header contains a duplicate `MCT_U232_LSR_OE` definition and a static function prototype in a header, which is safe only because it is included by the single C file defining the static function. Some request-size comments differ from observed Belkin/Sitecom behavior, so changing transfer sizes can regress devices that currently tolerate the generic four-byte path.

## Test Signals
Validate request IDs and payload sizes with hardware traces, regular versus code-based baud behavior, MCR bit mapping, MSR delta/current bit translation, LSR error bit availability, and compatibility across MCT, Sitecom, D-Link, and Belkin devices.
