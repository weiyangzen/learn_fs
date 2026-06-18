<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/libps2.c -->
# sources/distributed-fs/ceph-client/drivers/input/serio/libps2.c

## Purpose
`libps2.c` is the shared PS/2 protocol helper library used by keyboard, mouse, and touchpad drivers. It serializes commands, sends bytes with ACK/NAK handling and retries, collects command responses, handles common protocol quirks, and provides a common interrupt helper for PS/2 device drivers.

## Important APIs, types, and functions
- Exported APIs include `ps2_sendbyte()`, `ps2_begin_command()`, `ps2_end_command()`, `ps2_drain()`, `ps2_is_keyboard_id()`, `__ps2_command()`, `ps2_command()`, `ps2_sliced_command()`, `ps2_init()`, and `ps2_interrupt()`.
- Internal flags `PS2_FLAG_ACK`, `PS2_FLAG_CMD`, `PS2_FLAG_CMD1`, `PS2_FLAG_WAITID`, `PS2_FLAG_NAK`, and `PS2_FLAG_PASS_NOACK` track command and ACK state.
- `ps2_do_sendbyte()` writes one byte, waits for ACK/NAK/ERR, and retries NAKs up to a caller-supplied attempt count.
- `__ps2_command()` decodes the command word's send/receive counts, prepares response buffers, sends command and parameters, waits for response bytes, handles reset and GETID timeouts, and copies results back to `param`.
- `ps2_handle_ack()` processes ACK/NAK/ERR and GETID mouse-ID workarounds.
- `ps2_handle_response()` stores response bytes in reverse order and wakes waiters after first and final response bytes.
- `ps2_interrupt()` runs the caller's pre-receive handler and routes bytes to ACK handling, command response collection, or the caller's receive handler.

## Control flow
Drivers initialize a `ps2dev` with `ps2_init()`, providing pre-receive and receive callbacks. Process-context command callers use `ps2_command()` or the begin/end pair for compound commands. The library pauses serio RX while mutating command state, resumes RX while waiting for interrupts, and uses a waitqueue to sleep until ACK or response completion.

Incoming bytes from the serio interrupt path enter `ps2_interrupt()`. If the pre-receive handler reports an error, `ps2_cleanup()` clears command state and wakes waiters. If the byte is processable, the library consumes it as an ACK while waiting for ACK, as a command response while a command is active, or passes it to the driver's normal receive handler.

## State and persistence
State lives in the caller-owned `struct ps2dev`: command mutex, waitqueue, flags, `nak`, response count, response buffer, serio pointer, and callbacks. Nothing is persisted beyond the device lifetime. Command serialization may use the serio port's shared `ps2_cmd_mutex` when the underlying controller requires cross-port serialization.

## Dependencies and integration points
The library depends on the serio core, waitqueues, mutexes, KMSAN unpoisoning for response buffers, PS/2 command conventions, and optional i8042 shared command mutexes. It is consumed by higher-level PS/2 protocol drivers such as keyboard, mouse, and touchpad modules.

## Risks
- RX pause/continue windows are subtle; missed state transitions can lose ACKs or pass command responses to normal input handlers.
- GETID and reset commands have special timeout/response rules; regressions can break device detection.
- `PS2_FLAG_PASS_NOACK` intentionally passes unexpected bytes to receive handlers for some commands, which can interleave normal traffic with command handling.
- `ps2dev->cmdbuf` is size-limited; receive counts are checked, but callers must provide valid `param` buffers for send/receive commands.
- Interrupt handlers and process-context command waiters share flags and waitqueues, so lock ordering with serio locks and controller mutexes is important.

## Test signals
- Build all PS/2 keyboard/mouse/touchpad users with lockdep and KMSAN-enabled configurations.
- Unit-style protocol tests should cover ACK, NAK retry, ERR after NAK, command timeout, reset BAT one-byte/two-byte responses, GETID keyboard and mouse IDs, sliced commands, drain, and pre-receive error cleanup.
- Integration tests should verify shared i8042 command serialization across keyboard and AUX ports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/libps2.c -->
