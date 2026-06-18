# sources/distributed-fs/ceph-client/drivers/auxdisplay/hd44780_common.c

## Purpose
Provides controller-generic logic for HD44780-compatible character LCDs. Transport drivers supply `write_cmd`, `write_data`, and optionally `write_cmd_raw4`; this file implements charlcd operations for printing, cursor addressing, initialization, display/cursor/blink/font/line modes, shifting, clearing, and CGRAM custom characters.

## Important APIs, Types, And Functions
- Exported charlcd ops: `hd44780_common_print()`, `gotoxy()`, `home()`, `clear_display()`, `init_display()`, shifts, display/cursor/blink/font/lines, and `redefine_char()`.
- `hd44780_common_set_mode()` and `hd44780_common_set_function()` compose command bytes from stored flags.
- `hd44780_common_alloc()`/`free()` allocate charlcd with `struct hd44780_common` private data and defaults.

## Control Flow
Initialization validates interface width, sets default display flags, waits for power-up, forces the controller into a known 8-bit state three times, optionally switches to 4-bit mode, sends function/display/entry-mode commands, updates backlight, clears the display, and homes the cursor. Later charlcd writes call `print()` and `gotoxy()`; escape sequences call mode and shift helpers.

## State And Persistence
`struct hd44780_common` stores interface width, internal buffer and hardware address widths, current mode flags, transport callbacks, and transport-private `hd44780`. The common flags persist across escape commands and are encoded into HD44780 commands when modes change.

## Dependencies And Integration Points
Used by GPIO HD44780 and legacy parallel-panel transports. Depends on `charlcd_backlight()`, scheduler sleeps, hex parsing, and the callback contract in `hd44780_common.h`.

## Risks And Edge Cases
Address calculation is subtle for multi-line displays: y bit 0 selects the second hardware line and y bit 1 adds visible buffer width. `clear_display()` deliberately homes after clear for clone controllers. `redefine_char()` skips invalid hex nibbles and succeeds once a semicolon exists, so malformed sequences may partly program CGRAM.

## Test Signals
Validate 4-bit and 8-bit init byte sequences, clone clear/home behavior, gotoxy mapping for 1/2/4-line displays, shift boundaries near `bwidth`, all display/cursor/blink/font/line escape commands, and CGRAM redefinition with valid/invalid hex.
