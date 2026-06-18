# sources/distributed-fs/ceph-client/drivers/input/keyboard/tca8418_keypad.c

## Purpose

This I2C driver supports the TI TCA8418 keyboard scanner. It configures selected rows/columns as keypad pins, enables key event interrupts, drains the hardware FIFO, and reports matrix key events.

## Important APIs, Types, and Functions

`struct tca8418_keypad` stores the I2C client, input device, and row shift. `tca8418_write_byte()` and `tca8418_read_byte()` wrap SMBus byte access. `tca8418_configure()` writes keypad GPIO masks, debounce registers, and interrupt configuration. `tca8418_read_keypad()` drains `REG_KEY_EVENT_A` until an empty code. `tca8418_irq_handler()` checks interrupt status, warns on overflow, reads key events, and clears all interrupt bits.

## Control Flow

Probe verifies SMBus support, parses matrix dimensions, validates against 8x10 hardware limits, allocates state, probes presence by reading `REG_KEY_LCK_EC`, allocates input, builds keymap, requests a shared threaded IRQ, configures the chip, and registers input. IRQ flow reads `REG_INT_STAT`, ignores empty interrupts, logs overflow, drains key events when key interrupt is set, and writes `0xff` to clear all pending sources.

## State and Persistence Behavior

The driver does not keep key state; it trusts FIFO make/break event values. The row shift is persisted for scan-code calculation. Hardware keypad/GPIO/debounce/interrupt configuration persists after probe; there are no open/close or PM hooks.

## Dependencies and Integration Points

It depends on I2C SMBus byte operations, matrix-keypad properties, optional `keypad,autorepeat`, client IRQ, and OF compatible `ti,tca8418`. It uses the input keycode array created by `matrix_keypad_build_keymap()`.

## Risks and Edge Cases

The row/column conversion adjusts the chip's one-based event code with a wraparound path when `col == 0`; malformed event code zero is already treated as empty, but unexpected codes can calculate invalid rows. The IRQ is requested before chip configuration, so a live interrupt line may run against partially configured hardware. Overflow is only logged, with no recovery beyond FIFO drain/clear. No PM means system sleep depends on external chip state.

## Test Signals

Test all row/column bounds, event-code conversion, FIFO empty and multi-entry cases, overflow interrupt, shared IRQ returning `IRQ_NONE`, missing IRQ behavior, SMBus read/write failures, autorepeat property, and module autoload via I2C/OF tables.
