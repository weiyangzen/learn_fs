# sources/distributed-fs/ceph-client/arch/alpha/kernel/srmcons.c

## Purpose
`srmcons.c` implements an SRM callback-backed console and TTY driver. It supports early/full console output through firmware callbacks, a one-device system TTY named `srm`, periodic polling for input, CR insertion after newlines, and registration/unregistration hooks used during Alpha setup and time initialization.

## Important APIs, Types, And Functions
- `srmcons_callback_lock` serializes SRM callback get/put operations.
- `srm_is_registered_console` tracks console registration.
- `struct srmcons_private` contains a `tty_port` and polling timer; `srmcons_singleton` is the only device instance.
- `srmcons_result` decodes 61-bit character/count and 3-bit status return values from callbacks.
- `srmcons_do_receive_chars()` polls `callback_getc()`, inserts up to 10 available chars, and pushes tty flip buffer.
- `srmcons_receive_chars()` is the timer callback that tries the callback lock, polls input, and reschedules quickly or slowly based on activity.
- `srmcons_do_write()` writes output in chunks via `callback_puts()`, polls input during writes when a TTY port exists, and emits carriage returns after newlines.
- TTY operations include `srmcons_open()`, `srmcons_close()`, `srmcons_write()`, and `srmcons_write_room()`.
- `srmcons_init()` allocates/registers the TTY driver only if the console was registered earlier.
- Console operations include `srm_console_write()`, `srm_console_device()`, and `srm_console_setup()`.
- `register_srm_console()` opens the firmware console and registers `srmcons`.
- `unregister_srm_console()` closes and unregisters it.

## Control Flow
`setup.c` calls `register_srm_console()` when SRM console output is requested. That opens the firmware console and registers the console driver. Later `srmcons_init()` creates the TTY driver only if the console is registered. Opening `/dev/srm` links the singleton port to the tty and starts the polling timer. The timer periodically polls firmware input and reschedules while the tty is present. Writes lock the callback path, write bounded chunks, interleave receive polling, and add CR after newline for firmware console conventions. Closing the last tty deletes the timer.

## State And Persistence
State includes the singleton tty port, timer, registered tty driver pointer, console registration flag, and firmware console open/closed state. There is no disk persistence. Firmware console state may outlive Linux only in the sense that callbacks target SRM.

## Dependencies And Integration Points
The file depends on SRM callback APIs (`callback_open_console`, `callback_close_console`, `callback_getc`, `callback_puts`), Linux console and TTY subsystems, timers, spinlocks, and setup-time SRM console selection. `setup.c` and `process.c` use registration and shutdown interactions.

## Risks
- Callback operations happen with interrupts disabled/spinlocks held; firmware latency can affect responsiveness.
- Input is polling-based, so responsiveness depends on timer intervals and write-side polling.
- TTY port refcounting is noted as not fully proper (`port->tty` direct assignment).
- TTY driver initialization depends on early console registration ordering.
- CR insertion logic emits a carriage return after chunks containing newline, which is firmware-console-specific.

## Test Signals
- `srmcons` or `console=srm` boot options produce early console output.
- `/dev/srm` opens only when SRM console was registered and supports read/write.
- Input polling receives firmware console input without flooding when idle.
- Unregister during console transition stops callback console use cleanly.
- Panic/SysRq paths with SRM console do not deadlock on callback lock.
