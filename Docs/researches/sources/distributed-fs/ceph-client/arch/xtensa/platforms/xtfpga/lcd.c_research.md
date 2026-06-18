# sources/distributed-fs/ceph-client/arch/xtensa/platforms/xtfpga/lcd.c

## Purpose
`lcd.c` is the XTFPGA board-family character LCD driver used during early Xtensa platform bring-up. It writes controller commands and character data directly to board MMIO addresses and displays a boot banner.

## Important APIs, types, and functions
- `LCD_INSTR_ADDR` and `LCD_DATA_ADDR` derive instruction and data MMIO byte addresses from `CONFIG_XTFPGA_LCD_BASE_ADDR`.
- `lcd_put_byte()` emits either one 8-bit write or two 4-bit-nibble writes depending on `CONFIG_XTFPGA_LCD_8BIT_ACCESS`.
- `lcd_init()` programs display mode, display-on, clear-display, and the initial `XTENSA LINUX` string.
- `lcd_disp_at_pos()`, `lcd_shiftleft()`, and `lcd_shiftright()` are the platform-facing LCD operations declared by `<platform/lcd.h>`.

## Control flow
`arch_initcall(lcd_init)` runs after core arch setup. Initialization writes the 8-bit mode command three times with HD44780-style delays, optionally switches into 4-bit mode, enables display output, clears the panel, and writes the banner at position zero. Later callers set DDRAM position with `LCD_DISPLAY_POS | pos` and stream bytes through `LCD_DATA_ADDR`.

## State and persistence behavior
There is no software state. The persistent state is the external LCD controller's display buffer, cursor position, and command mode. Writes use `WRITE_ONCE()` to avoid compiler coalescing or reordering of repeated MMIO-looking byte accesses.

## Dependencies and integration points
The file depends on Xtensa XTFPGA hardware address macros, Linux delay helpers, and the platform LCD header. `setup.c` uses `lcd_disp_at_pos()` during power-off; other platform code may use the shift helpers for board status output.

## Risks and edge cases
The driver assumes the LCD MMIO mapping is valid before `arch_initcall`. Timing is fixed-delay and may be marginal on changed LCD hardware or clocking. The non-8-bit mode writes high nibbles only, so wiring must match the board's expected 4-bit interface. No bounds are enforced for `pos` or string length.

## Test signals
Booting an XTFPGA kernel should show `XTENSA LINUX`; shutdown should show `POWEROFF` through `setup.c`. Useful checks are logic-analyzer/MMIO traces for command ordering, both 4-bit and 8-bit Kconfig builds, and compile coverage that `<platform/lcd.h>` prototypes match these exported functions.
