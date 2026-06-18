# sources/distributed-fs/ceph-client/drivers/usb/serial/whiteheat.c

## Purpose

`whiteheat.c` is the Linux usb-serial driver for Connect Tech WhiteHEAT four-port USB serial adapters. It handles both the pre-renumeration firmware-loader device and the post-firmware serial device, then translates tty operations into WhiteHEAT firmware commands sent over a dedicated command endpoint.

## Important APIs, Types, and Functions

The file registers two `struct usb_serial_driver` instances: `whiteheat_fake_device` for firmware download and `whiteheat_device` for the real four-port adapter. `whiteheat_firmware_download()` loads `whiteheat_loader.fw` and `whiteheat.fw` through EZ-USB helpers. `whiteheat_attach()` probes firmware state by issuing `WHITEHEAT_GET_HW_INFO`, creates `struct whiteheat_command_private` for the command port, and installs custom command URB callbacks. Per-data-port `struct whiteheat_private` stores cached modem control bits. Runtime entry points include `whiteheat_open()`, `whiteheat_close()`, `whiteheat_set_termios()`, `whiteheat_tiocmget()`, `whiteheat_tiocmset()`, and `whiteheat_break_ctl()`. Firmware command helpers include `firm_send_command()`, `firm_open()`, `firm_close()`, `firm_setup_port()`, `firm_set_rts()`, `firm_set_dtr()`, `firm_set_break()`, `firm_purge()`, `firm_get_dtr_rts()`, and `firm_report_tx_done()`.

## Control Flow

Before firmware is loaded, the fake device probe downloads both firmware images and intentionally returns an attach failure so the pre-renumeration device does not remain bound. After the adapter reappears with the real product ID, attach sends a synchronous hardware-info command over command port 4 and initializes command-port state. Opening a tty starts the shared command read URB, sends firmware open and purge commands, pushes termios settings, clears data endpoint halts, and then delegates data streaming to `usb_serial_generic_open()`. Command submission serializes on `command_info->mutex`, writes a command byte plus payload through the command-port write URB, waits on `wait_command`, and interprets command-complete/failure replies from `command_port_read_callback()`. Closing reports TX completion, sends close, closes the generic data path, and decrements the command-port user count so the command read URB is killed when no ports are open.

## State and Persistence Behavior

All persistent state is runtime-only. The command port keeps a mutex, a shared open count, a command-completion flag, a wait queue, and a 64-byte result buffer. Each user port keeps only an unlocked cached MCR byte for DTR/RTS. Firmware remains resident on the device after upload until unplug or reset, which is why attach clears endpoint halts before probing firmware version. No on-disk or nonvolatile host state is maintained by the driver.

## Dependencies and Integration Points

The driver depends on usb-serial core registration, tty termios/modem-control callbacks, generic usb-serial bulk data handling, EZ-USB firmware download support, and the firmware protocol definitions in `whiteheat.h`. It integrates with userspace as normal ttyUSB ports and with firmware through a fifth bulk-in/out command endpoint separate from the four data ports.

## Risks and Test Signals

Risks include `whiteheat_private.mcr` being explicitly noted as unlocked, command-port lifetime coupling across multiple open data ports, command timeouts leaving firmware or host state ambiguous, fixed assumptions about command port index 4 and five bulk endpoints, and failures if firmware files are missing. Test signals include pre-renumeration firmware download, real-device attach reporting firmware version, concurrent opens on multiple ports, termios parity/baud/flow-control changes producing `WHITEHEAT_SETUP_PORT`, DTR/RTS get/set round trips, command timeout/error handling, and disconnect while command URBs are active.
