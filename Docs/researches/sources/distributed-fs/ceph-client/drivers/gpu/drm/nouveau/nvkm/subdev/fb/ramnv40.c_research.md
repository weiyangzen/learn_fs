<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramnv40.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramnv40.c

## Purpose
NV40 RAM implementation for legacy memory clock calculation and programming plus RAM type/size detection. It provides a shared constructor used by several NV4x RAM wrappers.

## Important APIs, Types, And Functions
Defines `nv40_ram_calc()`, `nv40_ram_prog()`, `nv40_ram_tidy()`, `nv40_ram_new_()`, and `nv40_ram_new()`. Uses `struct nv40_ram` from `ramnv40.h` to cache PLL control and coefficient values.

## Control Flow
Calc parses the memory PLL BIOS record and computes PLL coefficients with `nv04_pll_calc()`. Prog detects active CRTCs, waits for vblank, disables VGA memory access, precharges/refreshes RAM, enters self-refresh, programs memory PLL registers per chipset, exits self-refresh, runs the BIOS memory reset script, then restores CRTC access. `nv40_ram_new()` reads type/size from registers and sets partition count.

## State And Persistence
Calculated PLL control/coefficient values persist in `struct nv40_ram` between calc and prog. Hardware state includes VGA sequencer access bits, RAM refresh/self-refresh, PLL registers, BIOS init side effects, and partition count.

## Dependencies And Integration Points
Depends on BIOS BIT/M/init/pll parsing, NV04 PLL calculation, timer delays, legacy display vblank registers, and wrappers such as NV40/NV41/NV49.

## Risks
Display memory access disable/restore timing is fragile. Vblank polling timeouts, wrong chipset PLL register set, or missing BIOS memory reset script can blank displays or hang memory. Type detection is register-based and board-specific.

## Test Signals
Signals include successful memory clock change on NV4x boards, no stuck VGA sequencer state, BIOS M script execution, stable display after reclock, and correct RAM type/partition logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramnv40.c -->
