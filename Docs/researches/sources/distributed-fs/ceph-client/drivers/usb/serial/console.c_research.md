<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/console.c -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/console.c

Purpose: optional built-in USB serial console support for `console=ttyUSB<n>`. The complete 304-line source was read.

Important APIs/types/functions: `struct usbcons_info`, global `usbcons_info`, `usbcons`, `usb_console_setup()`, `usb_console_write()`, `usb_console_device()`, `usb_serial_console_init()`, `usb_serial_console_exit()`, and `usb_serial_console_disconnect()`.

Control flow and state: console registration is deferred until minor 0 exists. Setup parses baud/parity/bits/flow, gets the port, obtains autopm, creates a fake tty if `set_termios` is needed, calls driver `open`, applies termios, marks the port initialized and console-owned, and stores the port globally. Writes call the converter `write` callback and append CR after LF. State is the global console port pointer and `port->port.console`.

Dependencies and integration points: console subsystem, tty core, USB serial lookup/reference handling, runtime PM, converter `open`, `write`, and optional `set_termios`; only built with `USB_SERIAL_CONSOLE`.

Risks and test signals: risks include fake tty lifetime, special locking with `disc_mutex`, writes during disconnect, drivers not accepting `tty == NULL`, and minor-0 registration behavior. Test boot console options, printk output, disconnect, fake termios setup, and console-enabled/disabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/console.c -->
