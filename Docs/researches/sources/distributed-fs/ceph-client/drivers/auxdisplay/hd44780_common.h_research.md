# sources/distributed-fs/ceph-client/drivers/auxdisplay/hd44780_common.h

## Purpose
Declares the shared HD44780-compatible controller abstraction used by multiple physical transports. It keeps HD44780 command semantics centralized while allowing GPIO, parallel-port, or serial shims to provide byte/nibble write callbacks.

## Important APIs, Types, And Functions
- `DEFAULT_LCD_BWIDTH` and `DEFAULT_LCD_HWIDTH` define default internal and hardware DDRAM widths.
- `struct hd44780_common` stores interface width, buffer/address widths, mode flags, transport write callbacks, and a transport-private pointer.
- Function declarations expose all charlcd-compatible operations plus allocation/free helpers.

## Control Flow
Transport drivers call `hd44780_common_alloc()`, fill `ifwidth`, geometry, write callbacks, and `lcd->ops`, then call `charlcd_register()`. The charlcd core invokes the declared common functions via the ops table.

## State And Persistence
The header defines the persistent common state embedded in `lcd->drvdata`. Transport ownership of `hd44780` is explicit and not managed by the common free function.

## Dependencies And Integration Points
Requires `struct charlcd` and enum definitions from `charlcd.h` in includers. Used by `hd44780.c`, `hd44780_common.c`, and `panel.c`.

## Risks And Edge Cases
`write_cmd_raw4` is only valid for 4-bit displays but is required by initialization when `ifwidth == 4`; transports must initialize it before registration. Invalid `bwidth`/`hwidth` can lead to bad cursor addressing.

## Test Signals
Compile-time coverage across transports, allocation default values, and 4-bit registration paths that exercise raw-nibble initialization are the main signals.
