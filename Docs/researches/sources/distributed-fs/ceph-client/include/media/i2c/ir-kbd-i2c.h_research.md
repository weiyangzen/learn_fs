# sources/distributed-fs/ceph-client/include/media/i2c/ir-kbd-i2c.h

## Purpose
Defines the shared state and initialization contract for legacy I2C infrared keyboard/remote receivers and transmitters.

## Important APIs, Types, and Functions
`DEFAULT_POLLING_INTERVAL` is 100 ms. `struct IR_i2c` stores keymap name, RX/TX I2C clients, `rc_dev`, last key byte, polling interval, delayed work, physical path, `get_key` callback, TX lock, carrier, and duty cycle. `enum ir_kbd_get_key_fn` selects built-in decoder variants. `struct IR_i2c_init_data` provides keymap, device name, protocol mask, polling interval, custom/built-in get-key choice, and optional preallocated `rc_dev`.

## Control Flow
The driver periodically polls the I2C receiver with delayed work, calls `get_key()` to decode protocol/scancode/toggle, reports through rc-core, and uses the mutex to avoid polling while transmitting IR.

## State and Persistence Behavior
Runtime state persists for the I2C IR client: polling work, previous byte for repeat suppression, rc-core device, carrier/duty settings, and callback selection.

## Dependencies and Integration Points
Depends on rc-core, I2C clients, mutexes, delayed work, and board-provided init data. Integrates legacy capture cards with the Linux input/RC subsystem.

## Risks
Polling interval and `old` repeat suppression can drop legitimate keys or flood repeats. Custom callbacks must fill protocol/scancode/toggle consistently. TX/RX locking is required to avoid bus conflicts.

## Test Signals
Polling and key repeat behavior, built-in get-key variants, custom callback devices, rc-map selection, IR transmit while receive polling is active, and module unload cancelling delayed work.
