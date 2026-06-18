# sources/distributed-fs/ceph-client/drivers/video/fbdev/riva/riva_hw.c

## Purpose
`riva_hw.c` is the low-level hardware abstraction for NV3/NV4/NV10-family RIVA chips. It hides architecture-specific register programming behind `RIVA_HW_INST` callbacks, computes PLL and FIFO arbitration values for a requested mode, loads fixed-function PRAMIN/PFIFO/PGRAPH state, saves/restores extended mode state, and initializes chip configuration.

## Important APIs, types, and functions
- Exported APIs: `CalcStateExt()` calculates `RIVA_HW_STATE` from bpp, virtual width, display size, height, and dot clock; `RivaGetConfig()` fills chip configuration and callback pointers.
- State callbacks installed into `RIVA_HW_INST`: `LoadStateExt`, `UnloadStateExt`, `SetStartAddress`, `SetSurfaces2D`, `SetSurfaces3D`, `ShowHideCursor`, `LockUnlock`, and `Busy`.
- Arbitration families: `nv3CalcArbitration`, `nv4CalcArbitration`, `nv10CalcArbitration`, update wrappers, and `nForceUpdateArbitrationSettings()`.
- Configuration functions: `nv3GetConfig()`, `nv4GetConfig()`, `nv10GetConfig()`.

## Control flow
On setup, `RivaGetConfig()` selects an architecture-specific config function, derives RAM/crystal/vblank/cursor details, assigns callbacks, then maps FIFO method object pointers. On mode set, `CalcStateExt()` computes PLL M/N/P, arbitration watermarks, cursor location/config, pixel format, pitch, repaint, offset, flat-panel/two-head fields, and returns a filled state. `LoadStateExt()` writes common fixed tables, architecture tables from `riva_tbl.h`, bpp-specific tables, offsets/pitches, two-head/flat-panel state, PRAMDAC PLL/scale/general registers, interrupt/vblank registers, and resets FIFO counters. `UnloadStateExt()` reads the inverse subset into `RIVA_HW_STATE`.

## State and persistence behavior
State is persisted only in memory and hardware registers. `RIVA_HW_INST` records chip capabilities, MMIO pointers, FIFO free/empty counts, current state pointer, cursor start, and function pointers. `RIVA_HW_STATE` snapshots mode registers and render surface pitch/offsets. Hardware writes are immediate and global to the device; no locking is provided inside this file beyond caller discipline.

## Dependencies and integration points
It depends on `riva_hw.h` for register access and object layouts, `riva_tbl.h` for fixed register tables, `nv_type.h` for chipset tests, and Linux PCI helpers for integrated chipset memory/arbitration details. `fbdev.c` calls `CalcStateExt()` and uses the installed callbacks for mode loading, panning, cursor, acceleration waits, and state save/restore.

## Risks and test signals
Risks include opaque magic register tables, arithmetic overflow/divide-by-zero if clocks or PCI bridge reads are invalid, busy-wait loops, architecture-specific register drift, writing read-only/unknown registers during load, and fragile big-endian handling. Test signals include mode setting across NV3/NV4/NV10/NV20/NV30, stable accelerated blits after mode load, cursor placement, panning start address, flat-panel and two-head behavior, correct VRAM size/cursor offset, and no FIFO underrun/snow at high pixel clocks.
