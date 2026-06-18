# sources/distributed-fs/ceph-client/drivers/staging/nvec/nvec-keytable.h

## Purpose
Keyboard scancode translation tables for the NVEC keyboard driver, mapping EC key positions to Linux input key codes.

## Important APIs, Types, And Functions
Defines `code_tab_102us[]` for base 102-key US keyboard scancodes, `extcode_tab_us102[]` for extended scancodes, and `code_tabs[]` selecting the table by NVEC event-size encoding.

## Control Flow
`nvec_kbd.c` copies both tables into its input keycode array during probe and uses `code_tabs[_size][code]` when translating `NVEC_KB_EVT` messages.

## State And Persistence
The arrays are static compile-time data. No mutable or persistent state exists in this header.

## Dependencies And Integration Points
Requires Linux input key-code constants from the including translation unit. It is tightly coupled to `nvec_kbd.c` and the EC keyboard event-size encoding.

## Risks
Zero entries intentionally represent unsupported keys; events landing on zero are suppressed by clearing keybit 0 but still pass through translation. The table is US-layout-specific and contains sparse OEM/media mappings.

## Test Signals
Keyboard event tests should verify base and extended scancodes, Caps Lock, arrow/navigation keys, keypad keys, Fn/search/power entries, and unknown scancodes producing no key event.
