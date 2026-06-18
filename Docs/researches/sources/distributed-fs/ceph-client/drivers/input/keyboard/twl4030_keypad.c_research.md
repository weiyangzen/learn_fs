# sources/distributed-fs/ceph-client/drivers/input/keyboard/twl4030_keypad.c

## Purpose

This platform child driver supports the keypad controller in TWL4030-family MFD chips. It programs the controller's 8x8 hardware decoder, reads full matrix state over the TWL I2C module, filters ghost states, and reports matrix key changes.

## Important APIs, Types, and Functions

`struct twl4030_keypad` stores the keymap, cached row state, dimensions, IRQ, debug device, and input. `twl4030_kpread()` and `twl4030_kpwrite_u8()` wrap TWL module I2C access. `twl4030_col_xlate()` maps all-ground rows to an extra column. `twl4030_read_kp_matrix_state()` reads row status bytes. `twl4030_is_in_ghost_state()` detects ambiguous multi-key states. `twl4030_kp_scan()` reports changed keys. `twl4030_kp_program()` configures debounce, timeout, edge detection, and clear-on-read behavior.

## Control Flow

Probe allocates state/input, parses matrix dimensions, validates limits, gets IRQ, builds a keymap large enough for an extra column, registers input, programs hardware, requests a threaded IRQ, and unmasks key/timeout interrupts. The IRQ handler reads and clears `KEYP_ISR1`; if a key interrupt is present it scans the current matrix, otherwise it releases all keys. Scanning compares each row with cached state, skips ghost states, reports `MSC_SCAN` and key events, updates row cache, and syncs.

## State and Persistence Behavior

`kp_state[]` persists currently reported row bits. Hardware keeps debounce/timeout/edge/SIH settings and keypad enable state after probe. There is no explicit suspend/resume hook in this file, relying on the TWL core and always-on keypad hardware semantics.

## Dependencies and Integration Points

It depends on TWL4030 MFD APIs, matrix-keypad properties, platform IRQ child devices, input events, and optional OF compatible `ti,twl4030-keypad`. The keypad is an I2C-backed MFD child, so all event reads happen in threaded context.

## Risks and Edge Cases

Input is registered before hardware programming and IRQ request; failures after registration leave devm-managed input but may expose a partially initialized device briefly. Ghost states are ignored without releasing prior keys, which can leave stale reports until a non-ghost scan. The extra ground-row column requires keymap size and userspace expectations to match. I2C read failure releases all keys only in IRQ path, not in direct scan read failure.

## Test Signals

Test row/column bounds, extra-column ground rows, ghost combinations, I2C read/write failures, timeout interrupt release-all behavior, keymap build size, unmasking interrupts, and MFD suspend/resume interactions.
