<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramgt215.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramgt215.c

## Purpose
GT215/NVA3 RAM implementation for NV50-era DDR2/DDR3/GDDR3 reclocking, including optional one-time DDR link training, timing calculation, GPIO voltage/ODT control, PLL switching, and memx script generation.

## Important APIs, Types, And Functions
Defines `struct gt215_ramfuc`, `struct gt215_ltrain`, `struct gt215_ram`, `gt215_ram_new()`, `gt215_ram_init()`, `gt215_ram_calc()`, `gt215_ram_prog()`, `gt215_ram_tidy()`, `gt215_ram_dtor()`, link-training helpers, timing calculator, PLL lock helper, and GPIO helper.

## Control Flow
Init checks BIOS M0205 training support, allocates training VRAM, programs pattern buffers, and snapshots training registers. On first calc, optional link training reclocks to the training frequency, executes a training script, reads results, computes median settings, and reclocks back. Normal calc parses RAMMAP/RAMCFG/timing data, computes GT215 MCLK settings, calculates mode registers for DDR2/DDR3/GDDR3, and emits a script that disables display/FB access, enters self-refresh, switches PLL or bypass clocks, programs timing/MR registers, toggles GPIO voltage/ODT, resets DLLs, and re-enables FB.

## State And Persistence
State includes target BIOS timing/config, MR cache, training memory, training state machine and computed registers, ramfuc cache, and RAM allocator data from `nv50_ram_ctor()`. Hardware persistence includes PLL, timing, mode registers, GPIO voltage/ODT, and training registers.

## Dependencies And Integration Points
Depends on NV50 RAM construction, GT215 clock helpers, GPIO, BIOS RAMMAP/timing/M0205 tables, ramfuc/memx, and type-specific calculators. Used by `gt215.c` framebuffer wrapper.

## Risks
Training and reclocking are timing-sensitive and depend on PMU memx execution. Error paths must post clocks correctly. Multiple partition training is marked incomplete. GPIO inversion/log interpretation and DLL disable/reset ordering can break board-specific memory.

## Test Signals
Signals include training result debug dumps, computed `r_100720/r_1111e0/r_111400`, successful `NvMemExec` reclocks across supported memory types, no display flicker beyond expected masks, and clean cleanup of training memory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramgt215.c -->
