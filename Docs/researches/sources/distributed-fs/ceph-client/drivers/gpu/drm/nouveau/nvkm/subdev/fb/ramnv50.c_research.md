<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramnv50.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramnv50.c

## Purpose
Implements NV50-family framebuffer RAM discovery and memory reclocking support. It builds a hardware sequencer program that safely changes memory timings, mode registers, GPIO-controlled voltage/ODT signals, and the memory PLL while FIFO and framebuffer access are quiesced.

## Important APIs, Types, And Functions
Defines `struct nv50_ramseq` as a register-backed `hwsq` script with timing, mode-register, GPIO, PLL, FIFO, and FB-control registers. `struct nv50_ram` embeds `struct nvkm_ram`. Key functions are `nv50_ram_timing_calc`, `nv50_ram_timing_read`, `nv50_ram_calc`, `nv50_ram_prog`, `nv50_ram_tidy`, `nv50_fb_vram_rblock`, `nv50_ram_ctor`, and `nv50_ram_new`.

## Control Flow
`nv50_ram_new` allocates RAM state, calls `nv50_ram_ctor`, and initializes all sequencer register descriptors. `nv50_ram_ctor` reads memory type, size, partitions, ranks, and initializes the VRAM allocator with a row-block size derived from memory-controller registers. For reclocking, `nv50_ram_calc` selects a BIOS performance entry, resolves RAM map and timing data, computes mode registers, emits a sequencer program that waits for vblank, blocks FIFO, disables FB, enters self-refresh, programs MPLL and memory timings, toggles GPIO voltage/ODT lines, resets DLL when required, and re-enables FB/FIFO. `nv50_ram_prog` executes the script when `NvMemExec` allows it; `nv50_ram_tidy` discards it.

## State And Persistence
Persistent driver state includes `ram->base.target`, `ram->base.next`, mode registers, VRAM allocator geometry, partition mask, rank count, and the prepared `hwsq` script. Hardware state is volatile MMIO state in memory controller, PLL, GPIO, and FIFO/FB registers. BIOS tables are read-only inputs.

## Dependencies And Integration Points
Depends on Nouveau BIOS parsers for performance, PLL, RAM map, RAM config, and timing records; on GPIO DCB lookup for memory-control pins; on PLL calculation; on `hwsq` sequencing helpers; and on shared RAM helpers such as `nvkm_gddr3_calc`. It integrates with the framebuffer subdev through `nvkm_ram_func`.

## Risks And Edge Cases
The code has chipset-specific and poorly documented bit handling, with several `XXX` comments. Missing or malformed VBIOS tables fail reclocking. Timing support is narrow, mode register calculation is implemented for GDDR3 in this path, and an incorrect sequencer can hang display or memory access. VRAM geometry mismatches are warned about but not fatal.

## Test Signals
Useful signals are successful boot-time VRAM sizing, no VBIOS parsing errors, debug logs for timing registers and row-block size, successful memory reclock without FIFO/FB hangs, and suspend/resume or mode-setting stability under memory pressure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramnv50.c -->
