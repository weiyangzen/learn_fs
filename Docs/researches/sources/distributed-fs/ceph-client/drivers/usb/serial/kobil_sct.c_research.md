# sources/distributed-fs/ceph-client/drivers/usb/serial/kobil_sct.c

## Purpose
This driver supports KOBIL USB smart-card terminals, including Adapter B, Adapter K, USBTWIN, and KAAN SIM products. It exposes one serial-like port but uses interrupt endpoints and vendor control requests tailored to smart-card APDU transfer and reader control rather than a conventional UART.

## Important APIs, Types, and Functions
`struct kobil_private` contains a 300-byte APDU staging buffer, fill/send indexes, and product-specific device type. `kobil_ctrl_send` and `kobil_ctrl_recv` wrap vendor endpoint control requests. Main hooks include `kobil_open`, `kobil_close`, `kobil_write`, `kobil_write_room`, `kobil_read_int_callback`, `kobil_tiocmget`, `kobil_tiocmset`, `kobil_set_termios`, `kobil_ioctl`, and `kobil_init_termios`.

## Control Flow
Probe initializes private state and records the product ID. Open queries hardware and firmware versions, configures Adapter B/K line settings to 9600 even parity one stop bit, resets queues for those adapters, and starts interrupt-in reads for USBTWIN, Adapter B, and KAAN SIM. Close kills interrupt OUT and IN URBs.

Reads arrive through `kobil_read_int_callback`, which pushes any interrupt payload directly into the TTY flip buffer and resubmits the interrupt-in URB. Writes are APDU-aware: bytes are appended to the private buffer until a complete block is detected. TWIN, KAAN SIM, and Adapter K use `buf[1] + 3` as complete length; Adapter B uses `buf[2] + 4`. Once complete, Adapter B/K temporarily stop reading, send the APDU in chunks no larger than `interrupt_out_size` with sleeps between chunks, reset buffer indexes, and restart reading for Adapter B/K.

Modem and termios controls are product-dependent. USBTWIN and KAAN SIM reject ioctl/modem operations. Adapter B supports DTR and RTS via vendor status-line requests; Adapter K effectively supports RTS. `kobil_set_termios` supports 1200 or 9600 baud plus parity/stop selection through the header's bit masks and clears mark/space parity.

## State and Persistence
All state is per-port and volatile. APDU staging persists across partial writes until the driver detects a complete block, then resets. Device queues can be reset through open and `TCFLSH`. Termios changes are sent to the device but not cached in private state beyond the actual device configuration.

## Dependencies and Integration Points
This file depends on `kobil_sct.h` for vendor request and bitmask definitions, the USB serial interrupt endpoint model, TTY flip buffers, and Linux ioctl/termios APIs. It integrates with smart-card user-space through serial writes that are expected to form APDU-sized protocol messages.

## Risks
Write buffering has no explicit locking around `filled`/`cur_pos`, so concurrent write paths would rely on serial-core serialization. `write_room` always returns 8 and does not reflect the 300-byte staging buffer. APDU completion is inferred from early bytes; malformed user data can fill the staging buffer and return `-ENOMEM`. The sleeps between interrupt chunks are timing-sensitive. Product-specific support is uneven and some devices do not support ioctl calls.

## Test Signals
Test each product ID path, APDU length detection for Adapter B versus others, buffer overflow rejection, interrupt chunking and restart-read behavior, hardware/firmware version requests, queue reset on open/flush, unsupported ioctl behavior for USBTWIN/KAAN SIM, termios encoding, and interrupt read resubmission after normal packets.
