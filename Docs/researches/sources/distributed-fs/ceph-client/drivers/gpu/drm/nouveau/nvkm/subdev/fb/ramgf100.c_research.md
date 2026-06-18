<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramgf100.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramgf100.c

## Purpose
Fermi GF100 RAM implementation, including FBP-based VRAM sizing/allocation layout, GDDR5 training-pattern initialization, BIOS-driven reclocking script generation, and shared helpers for later generations.

## Important APIs, Types, And Functions
Defines `struct gf100_ramfuc`, `struct gf100_ram`, `gf100_ram_new_()`, `gf100_ram_new()`, `gf100_ram_ctor()`, FBP probe helpers, `gf100_ram_init()`, `gf100_ram_calc()`, `gf100_ram_prog()`, `gf100_ram_tidy()`, and `gf100_ram_train()`.

## Control Flow
Construction probes enabled FBPs/LTCs, computes lower and upper VRAM regions for mixed-memory layouts, initializes the MM allocator, parses reference and memory PLL BIOS records, and registers ramfuc MMIO targets. Init loads GDDR5 training patterns. Calc parses RAMMAP/RAMCFG/timing BIOS entries, determines current and target clock modes, builds a memx script for PLL changes, self-refresh, timing/MR programming, training, and reenable. Prog executes or discards the script according to `NvMemExec`; tidy discards any pending script.

## State And Persistence
Persistent state includes RAM type/size, MM allocator regions, PLL descriptors, ramfuc register cache, and generated scripts between calc/prog. Hardware persistence includes memory controller timing registers, PLL registers, MR values, training state, and VRAM address split.

## Dependencies And Integration Points
Depends on BIOS RAMMAP/timing/PLL parsers, clock source reads, ramfuc/memx, common RAM allocator, and GF100 framebuffer wrappers. Later RAM files reuse FBP probing and constructor helpers.

## Risks
This is high-risk hardware sequencing. Mixed-memory allocator math must not expose reserved VGA/VBIOS areas incorrectly. BIOS version assumptions (`0x10`) and magic register scripts can fail on boards outside known coverage. Reclocking with wrong PLL/timing values can hang memory.

## Test Signals
Signals include probe logs for FBP/LTC sizes and lower/upper VRAM split, GDDR5 training load, successful `NvMemExec` reclock cycles, stable VRAM allocation in mixed configurations, and no FB/FIFO faults after clock changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramgf100.c -->
