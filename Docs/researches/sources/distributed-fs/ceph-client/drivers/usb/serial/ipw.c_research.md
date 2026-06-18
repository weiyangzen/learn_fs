<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/ipw.c -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/ipw.c

## Purpose
Implements a USB serial driver for the IPWireless 3G UMTS TDD modem. It exposes a single tty used for AT commands and PPP-like data while delegating most data-plane mechanics to the shared `usb-wwan` helper layer.

## Important APIs, Types, And Functions
The file defines one USB ID pair, `IPW_VID`/`IPW_PID`, and many device-specific control request constants for initialization, RX bulk gating, baud, line settings, pin control, purge, handflow, and status polling. `ipw_open()` sends initialization control messages, clears bulk halts, calls `usb_wwan_open()`, enables RX bulk, and sends initial flow-control bytes. `ipw_close()` purges, disables RX bulk, and calls `usb_wwan_close()`. `ipw_dtr_rts()` maps carrier-control requests to two vendor commands. `ipw_attach()` allocates `struct usb_wwan_intf_private`, initializes its suspend lock, and stores it as serial private data; `ipw_release()` frees it.

## Control Flow
Probe binds a one-port `usb_serial_driver` and installs `usb_wwan_port_probe()`/`usb_wwan_port_remove()`. On open, the driver allocates a 16-byte flow-control buffer, sends `IPW_SIO_INIT`, clears both bulk endpoint halts, starts the `usb_wwan` read/write machinery, enables modem-to-host bulk transmission with `IPW_SIO_RXCTL`, and sends `IPW_SIO_HANDFLOW`. Close reverses device flow by issuing purge and RX-off commands before shutting down the helper layer. DTR/RTS operations are synchronous vendor control messages and do not maintain a local modem shadow.

## State And Persistence
Persistent device state is not modified. Runtime state lives mostly in `usb_wwan_intf_private` and per-port data allocated by usb-wwan helpers. The module does not expose parameters. Modem-control state is effectively device-side and partly faked, as comments note unresolved DCD/DTR/RTS/CTS semantics.

## Dependencies And Integration Points
The driver depends on the USB core, usb-serial core, tty layer, and `usb-wwan.h` helper implementation for buffered writes, read URB handling, suspend locking, and port lifecycle. Userspace modem managers or PPP stacks interact through the tty.

## Risks And Edge Cases
Several vendor requests are reverse-engineered and comments admit modem-control interpretation is incomplete. `ipw_open()` logs failures for initialization, RX enable, and handflow but still returns success after `usb_wwan_open()`, so userspace may see an open tty even when setup partially failed. `IPW_SIO_SET_LINE` and `IPW_SIO_SET_PIN` share request number `0x03`; correct behavior relies on value payload interpretation. Long synchronous control-message timeouts can delay open/close.

## Test Signals
Signals include successful open on real hardware, expected control-message sequence under usbmon, working AT command exchange, PPP session stability, close disabling RX traffic, DTR/RTS command observation, suspend/resume behavior inherited from usb-wwan, and fault injection proving partial setup failures are visible enough for diagnosis.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/ipw.c -->
