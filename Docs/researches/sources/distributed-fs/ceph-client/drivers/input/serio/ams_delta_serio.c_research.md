# sources/distributed-fs/ceph-client/drivers/input/serio/ams_delta_serio.c

## Purpose

`ams_delta_serio.c` implements the Amstrad Delta/E3 mailboard keyboard serio adapter. The actual PS/2-like bit capture is done by a platform FIQ handler; this driver drains the FIQ circular buffer, validates frame/parity bits, and feeds scancodes to serio.

## Important APIs, Types, and Functions

`struct ams_delta_serio` stores the serio port, keyboard regulator, and FIQ buffer pointer. `check_data()` validates stop bit and odd parity. `ams_delta_serio_interrupt()` drains the FIQ circular buffer and reports scancodes. `ams_delta_serio_open()` and `ams_delta_serio_close()` enable/disable keyboard power. Probe is `ams_delta_serio_init()` and remove is `ams_delta_serio_exit()`.

## Control Flow

Probe allocates state, obtains the FIQ buffer from platform data, gets the `vcc` regulator, requests the platform IRQ, allocates a `SERIO_8042` port, assigns callbacks, registers it, and stores driver data. Opening enables the regulator. The IRQ handler clears the pending flag, drains words from the circular buffer using head/count metadata, validates each word, extracts the data byte, and calls `serio_interrupt()`. Closing disables the regulator, and remove unregisters the serio port.

## State and Persistence Behavior

Persistent state is the regulator, FIQ shared buffer pointer, and serio port. The circular buffer state lives in platform/FIQ memory and is mutated by both the FIQ producer and this IRQ consumer. Keyboard power state follows serio open/close.

## Dependencies and Integration Points

The file depends on Amstrad Delta FIQ platform data definitions, platform IRQs, regulator framework, and serio. It integrates with `atkbd` as a normal AT keyboard port, with userspace expected to load a custom keymap for the mailboard.

## Risks and Edge Cases

The FIQ buffer is shared memory with implicit synchronization through platform conventions. Regulator lookup converts `-ENODEV` to `-EPROBE_DEFER` to allow board constraints to settle. Bad frame/parity data is still reported with serio error flags. A missing platform buffer aborts probe.

## Test Signals

Tests should include valid scancode delivery, invalid stop bit and parity reporting, circular-buffer wraparound, regulator enable/disable, deferred regulator probing, missing platform data failure, and custom keymap operation on E3 mailboard hardware.
