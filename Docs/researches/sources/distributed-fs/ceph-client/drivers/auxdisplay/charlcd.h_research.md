# sources/distributed-fs/ceph-client/drivers/auxdisplay/charlcd.h

## Purpose
Defines the public in-kernel contract for character LCD providers and the common charlcd core. It declares display mode flags, small enums used by callbacks, the public `struct charlcd`, the hardware operation table, and exported lifecycle/helpers.

## Important APIs, Types, And Functions
- Mode flags `LCD_FLAG_B`, `LCD_FLAG_C`, `LCD_FLAG_D`, `LCD_FLAG_F`, `LCD_FLAG_N`, and `LCD_FLAG_L` represent blink, cursor, display, font, line count, and backlight states.
- Enums `charlcd_onoff`, `charlcd_shift_dir`, `charlcd_fontsize`, and `charlcd_lines` normalize callback arguments.
- `struct charlcd` carries ops, optional character conversion table, geometry, buffered cursor address, and `drvdata`.
- `struct charlcd_ops` defines backlight, print, cursor positioning, clear/home/init, shifts, mode changes, and custom-character redefinition callbacks.
- Function declarations expose allocation, registration, unregister, backlight, and poke helpers.

## Control Flow
Hardware drivers allocate with `charlcd_alloc(drvdata_size)`, populate `width`, `height`, `ops`, optional `char_conv`, and callback-specific private data via `lcd->drvdata`, then call `charlcd_register()`. The charlcd core calls ops according to writes and escape commands; drivers call `charlcd_unregister()` and `charlcd_free()` on teardown.

## State And Persistence
The header exposes only public state that providers must maintain coherently: geometry, cursor address, callback table, optional conversion table, and driver private storage. Private core state is hidden in `charlcd.c`.

## Dependencies And Integration Points
Included by hardware drivers such as `hd44780.c`, `hd44780_common.c`, `lcd2s.c`, and `panel.c`. It is the ABI-like internal contract between the generic `/dev/lcd` parser and physical transport implementations.

## Risks And Edge Cases
The comments specify important callback semantics: `print()` must not wrap lines and charlcd advances the buffered cursor itself; `gotoxy()`, `home()`, and `clear_display()` interact with pre-updated `lcd->addr`. Drivers that ignore these semantics can desynchronize cursor state.

## Test Signals
Provider tests should confirm callback ordering around `home`, `clear_display`, and `print`, optional backlight handling when callback is NULL, and private-data layout from `charlcd_alloc()`.
