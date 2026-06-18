# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mc/gp10b.c

## Purpose
Implements the Tegra GP10B MC backend with SoC-specific init to bring units out of ELPG.

## Important APIs, Types, and Functions
`gp10b_mc_init` writes `0xffffffff` to `0x000200` and `0x00020c`. `gp10b_mc_new` registers a GP100-style interrupt table.

## Control Flow, State, and Persistence
The backend uses GP100 interrupt allow/block, GP100 interrupt data, NV04 device control, and GK104 reset map. Init persists all-device enable and ELPG-exit state in MC registers.

## Dependencies and Integration Points
Depends on Tegra power-management expectations, GP100 MC interrupt code, and common MC reset helpers.

## Risks and Test Signals
Risks are ELPG state mismatches, desktop reset maps on Tegra, and interrupt mask differences. Test GP10B boot/resume, ELPG transitions, GPU faults, FIFO interrupts, and reset paths.
