# sources/distributed-fs/ceph-client/drivers/auxdisplay/panel.c

## Purpose
Implements a legacy parallel-port front-panel driver combining an HD44780-compatible `/dev/lcd` and a matrix-keypad `/dev/keypad`. It supports several hard-coded panel profiles, configurable pin mappings, parallel/serial/TI LCD protocols, keypad scanning/debounce/repeat, and backlight poke-on-keypress behavior.

## Important APIs, Types, And Functions
- Global `lcd` and `keypad` state select enabled devices, protocol, geometry, pins, char conversion, and charlcd pointer.
- LCD write paths: `lcd_write_cmd_p8()`, `lcd_write_data_p8()`, `lcd_write_cmd_s()`, `lcd_write_data_s()`, and TI variants feed `hd44780_common`.
- `lcd_init()` builds an `hd44780_common` charlcd, applies profile/module parameters, maps logical LCD signals to parport bits, and selects callbacks.
- Keypad paths: `phys_scan_contacts()`, `panel_process_inputs()`, `input_state_high()`, `input_state_falling()`, `panel_bind_key()`, and `keypad_read()`.
- `panel_attach()` and `panel_detach()` are parport driver lifecycle callbacks.

## Control Flow
Attach resolves profile defaults, module-parameter overrides, enabled LCD/keypad choices, and keypad profile table. It filters for the configured parport number, registers/claims a parport device, initializes and registers LCD first, then initializes keypad and registers `/dev/keypad`. A timer scans contacts at `HZ/50`, debounces logical inputs, fills a circular keypad buffer for readers, and pokes LCD backlight on keypress. Detach deletes the timer, deregisters keypad and LCD, releases charlcd/common storage, and unregisters the parport device.

## State And Persistence
Substantial global state persists across module life: parport device pointer, signal bitmaps, LCD bit masks, keypad logical input list, physical contact history, circular keypad buffer, timer, spinlock, atomic single-open gate, profile parameters, and charlcd state. Hardware state is maintained on the parport data/control lines and LCD controller.

## Dependencies And Integration Points
Depends on parport, misc devices (`/dev/keypad` plus charlcd `/dev/lcd`), `charlcd`, `hd44780_common`, timers, waitqueues, spinlocks, and module parameters. It reuses HD44780 common logic while providing its own physical transport.

## Risks And Edge Cases
The file documents dirty init/deinit and has a TODO noting logical inputs are not freed on detach, so repeated attach/detach can leak key bindings. Profile/pin overrides are complex and collision checks between keypad and LCD pins are absent. Keypad buffer operations are not strongly synchronized with timer producers. `keypad_profile` can be NULL for disabled/unknown types, so initialization must only run when valid. Parport locking uses spinlocks around slow udelays.

## Test Signals
Each profile and override combination, parport mismatch/claim failure, LCD parallel/serial/TI writes, KS0074 character conversion, keypad single-open/read blocking/nonblocking behavior, key press/repeat/release strings, debounce transitions, backlight poke on keypress, and detach/reload leak/error behavior are important signals.
