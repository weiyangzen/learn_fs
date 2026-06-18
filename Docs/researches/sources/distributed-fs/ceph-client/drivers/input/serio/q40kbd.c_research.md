<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/q40kbd.c -->
# sources/distributed-fs/ceph-client/drivers/input/serio/q40kbd.c

## Purpose
`q40kbd.c` is the Q40 m68k PS/2 keyboard controller driver. It exposes the Q40 keyboard registers as a single `SERIO_8042` port and handles the Q40 keyboard IRQ.

## Important APIs, types, and functions
- `struct q40kbd` stores the serio port and a spinlock protecting register access.
- `q40kbd_interrupt()` checks the keyboard interrupt bit, reads `KEYCODE_REG`, delivers the byte, and unlocks the keyboard interrupt latch.
- `q40kbd_flush()` drains up to 100 pending keycodes while the interrupt bit is set.
- `q40kbd_stop()` disables keyboard IRQ generation and unlocks the keyboard.
- `q40kbd_open()` flushes stale data, unlocks the keyboard, and enables keyboard IRQs.
- `q40kbd_close()` stops IRQ generation and flushes stale data.
- `q40kbd_probe()` allocates state and serio, requests `Q40_IRQ_KEYBOARD`, registers the port, and stores driver data.

## Control flow
The platform probe allocates driver objects, initializes the spinlock and serio fields, stops the keyboard hardware, requests the fixed Q40 keyboard IRQ, registers the serio port, and records driver data. Open enables hardware IRQs; interrupts deliver bytes; close disables hardware IRQs. Remove unregisters the port first so close disables hardware, then frees the IRQ and state.

## State and persistence
Only the port pointer and spinlock are stored. Hardware IRQ enable/latch state changes on open, close, interrupt, and probe. No persistent settings are saved.

## Dependencies and integration points
It depends on Q40 architecture register helpers/constants, platform driver infrastructure, IRQ handling, spinlocks, and serio.

## Risks
- The driver requests the IRQ at probe, not open, so the interrupt handler exists even while the serio port is closed; hardware IRQs are disabled by `q40kbd_stop()`.
- Remove frees only `q40kbd`; the serio object is freed by serio unregister semantics.
- Flush has a fixed 100-byte cap.

## Test signals
- Build on Q40/m68k configurations.
- Hardware tests should cover probe IRQ failure, open/close IRQ enable, interrupt byte delivery, flush of stale data, and remove while open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/q40kbd.c -->
