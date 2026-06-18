# sources/distributed-fs/ceph-client/drivers/usb/serial/kl5kusb105.h

## Purpose
This header defines the constants used by the KL5KUSB105 USB serial driver. It identifies the PalmConnect USB serial device, the KLSI vendor requests, supported baud/data-bit encodings, read-on/read-off configuration values, and provisional modem-line masks.

## Important APIs, Types, and Constants
`PALMCONNECT_VID` and `PALMCONNECT_PID` populate the driver's USB ID table. The anonymous enum maps supported baud rates to device-specific values. `kl5kusb105a_dtb_7` and `kl5kusb105a_dtb_8` encode data-bit choices. Request constants `KL5KUSB105A_SIO_SET_DATA`, `KL5KUSB105A_SIO_POLL`, and `KL5KUSB105A_SIO_CONFIGURE` are used for settings, line polling, and read configuration. `KL5KUSB105A_SIO_CONFIGURE_READ_ON` and `_READ_OFF` drive open/close read state. `KL5KUSB105A_DSR` and `KL5KUSB105A_CTS` map status bits to TTY modem lines.

## Control Flow
`kl5kusb105.c` includes this header and uses the baud/data constants in `klsi_105_set_termios`, request constants in `klsi_105_chg_port_settings`, `klsi_105_get_line_state`, `klsi_105_open`, and `klsi_105_close`, and line masks when translating polled status to `TIOCM_DSR` and `TIOCM_CTS`.

## State and Persistence
This header has no runtime state. Its constants define values stored at runtime in `struct klsi_105_private.cfg` and sent to the device.

## Dependencies and Integration Points
The header is private to the KLSI driver and assumes Linux USB/TTY types are supplied by the C file. The values are reverse-engineered hardware protocol constants, so the primary integration point is the device firmware rather than another source module.

## Risks
The modem-line masks are explicitly uncertain and currently make DSR and CTS identical. Several possible modem-line names are left in a disabled block, showing incomplete hardware understanding. Incorrect constants can affect open/read enablement or termios behavior globally for the only supported product.

## Test Signals
Tests should confirm USB ID matching, each baud constant accepted by the device, READ_ON/READ_OFF behavior, 7-bit versus 8-bit settings, and real hardware modem-line polling for CTS/DSR to validate or correct the duplicated masks.
