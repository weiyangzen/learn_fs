# sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/matroxfb_misc.h

## Purpose
Declares shared Matrox helper APIs for PLL calculation, VGA hardware initialization/restoration, and BIOS/PInS reading.

## Important APIs, Types, and Functions
- `matroxfb_PLL_calcclock()` is the exported generic PLL divider search.
- `PLL_calcclock()` is a convenience inline using `minfo->features.pll`.
- `matroxfb_vgaHWinit()` and `matroxfb_vgaHWrestore()` create and apply VGA register state.
- `matroxfb_read_pins()` extracts BIOS power-up information and applies hardware limits.

## Control Flow
The header enables other Matrox modules to call common routines without duplicating PLL or VGA register logic. The inline simply forwards to the exported function with per-device PLL features.

## State and Persistence
No header-local state. Called functions mutate `struct matrox_fb_info` and hardware registers.

## Dependencies and Integration Points
Includes `matroxfb_base.h` for core Matrox structures and is included by DAC, Maven, G450, and base driver code.

## Risks
All declarations expose low-level hardware mutation; call sites must already hold the appropriate higher-level mode-setting discipline. The inline depends on `features.pll` having been initialized, usually by `matroxfb_read_pins()`.

## Test Signals
Compile all Matrox submodules against this header and verify mode setup calls resolve. Runtime test signal is successful PLL calculation after BIOS/PInS initialization.
