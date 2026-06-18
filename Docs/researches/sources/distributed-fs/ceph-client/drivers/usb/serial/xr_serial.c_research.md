# sources/distributed-fs/ceph-client/drivers/usb/serial/xr_serial.c

## Purpose

`xr_serial.c` supports MaxLinear/Exar USB-to-serial devices in the XR21V141x, XR21B14xx, and XR2280x families. It binds CDC-style control/data interfaces, configures vendor UART registers, exposes modem-control and break handling, and implements RS-485 mode through tty ioctls.

## Important APIs, Types, and Functions

`struct xr_type` describes per-chip register width, request recipient, vendor request IDs, register addresses, and optional chip-specific operations. `struct xr_data` stores the selected type, channel number, and `struct serial_rs485` state per port. Low-level helpers `xr_set_reg()`, `xr_get_reg()`, `xr_set_reg_uart()`, and `xr_get_reg_uart()` issue vendor control transfers. UART lifecycle helpers include `xr_uart_enable()`, `xr_uart_disable()`, `xr_fifo_reset()`, and XR21V141x-specific FIFO/UART sequencing. TTY operations include `xr_open()`, `xr_close()`, `xr_set_termios()`, `xr_tiocmget()`, `xr_tiocmset()`, `xr_dtr_rts()`, `xr_break_ctl()`, and `xr_ioctl()` for `TIOCGRS485` and `TIOCSRS485`. Line configuration is split between `xr21v141x_set_line_settings()` for direct register programming and `xr_cdc_set_line_coding()` for CDC requests.

## Control Flow

`xr_probe()` parses CDC descriptors, finds the union slave data interface, claims it, and records the chip type from `id->driver_info`. `xr_port_probe()` allocates `struct xr_data`, derives the channel from interface number, optionally enables a custom-driver mode, and initializes GPIO mode/direction with DTR/RTS deasserted. Opening a tty resets FIFOs, enables the UART, applies termios, then starts generic usb-serial I/O. Termios changes program baud/format or CDC line coding, update flow-control GPIO mode, and toggle DTR/RTS around B0. RS-485 ioctl updates the sanitized RS-485 state under `termios_rwsem` and reapplies flow mode. Close shuts down generic I/O and disables the UART.

## State and Persistence Behavior

Per-port state is allocated during port probe and freed on port remove. RS-485 flags persist for the port until changed or the device is removed. Hardware registers hold the active UART, GPIO, flow-control, custom-driver, baud, and break state; the driver rewrites them on open/termios/ioctl rather than keeping a complete software mirror. No filesystem-backed persistence exists.

## Dependencies and Integration Points

The driver depends on usb-serial core, USB CDC descriptor parsing, tty termios and ioctl APIs, generic usb-serial bulk I/O, and MaxLinear/Exar vendor control registers. It integrates with userspace through ttyUSB ports plus standard modem-control and RS-485 ioctls, and with firmware/hardware through vendor register access and CDC `SET_LINE_CODING` for some variants.

## Risks and Test Signals

Risks include chip-family register-table mistakes, channel derivation from interface numbers, partial error handling inside `xr_set_flow_mode()` where some register-write failures are ignored, active-low modem-signal inversion, RS-485 support limited to flags without delays, and custom-driver-mode setup failures preventing probe. Test signals include CDC union parsing on every supported PID, open/close UART enable sequencing, baud-rate clamping and XR21V141x fractional divisor programming, CS5/CS6 fallback behavior on unsupported chips, hardware/software flow control, DTR/RTS and break control, RS-485 ioctl round trips, and suspend/disconnect cleanup through usb-serial remove paths.
