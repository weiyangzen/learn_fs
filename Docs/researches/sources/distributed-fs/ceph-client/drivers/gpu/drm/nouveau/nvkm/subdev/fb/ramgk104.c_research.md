<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramgk104.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramgk104.c

## Purpose
Kepler GK104 RAM implementation. It extends GF100 allocation with RAMMAP table caching, partition-difference handling, GDDR5/DDR3 reclocking scripts, PLL calculation, GPIO voltage switching, and BIOS training-data upload.

## Important APIs, Types, And Functions
Defines `struct gk104_ramfuc`, `struct gk104_ram`, `gk104_ram_new_()`, `gk104_ram_new()`, `gk104_ram_dtor()`, `gk104_ram_init()`, `gk104_ram_calc()`, `gk104_ram_prog()`, `gk104_ram_tidy()`, `gk104_ram_calc_gddr5()`, `gk104_ram_calc_sddr3()`, PLL helpers, and training-table helpers.

## Control Flow
Construction calls `gf100_ram_ctor()`, detects disabled and non-uniform memory partitions (`pmask`/`pnuts`), parses all RAMMAP entries into a list while recording fields that differ, parses ref/mem PLL BIOS entries, finds voltage GPIOs, and registers all ramfuc targets. Init runs RAMMAP init scripts and uploads M0205/M0209 GDDR5 training data. Calc selects former/target/xition configurations, calculates PLLs, snapshots MRs, calls DDR3 or GDDR5 MR calculators, then emits a detailed memx transition script. Prog applies static RAMMAP register changes before and after executing the script; tidy clears pending transition state.

## State And Persistence
State includes cached RAMMAP configs, diff masks, transition state (`former`, `target`, `xition`, `next`), PLL coefficients, voltage GPIO choices, partition masks, MR values, and ramfuc script state. Hardware state persists in PLLs, controller timings, MR registers, training tables, and per-partition adjustments.

## Dependencies And Integration Points
Depends on GF100 allocation/probe logic, NVBIOS RAMMAP/timing/M0205/M0209/PLL parsers, GPIO, clock, ramfuc/memx, and type calculators for DDR3/GDDR5. Used by GK104/GK110 wrappers and descendants that reuse GK104 RAM behavior.

## Risks
Very high risk: BIOS field-diff logic intentionally avoids touching fields that do not vary, and changing that can regress boards. The two-step xition path, partition `nuts` writes, and voltage GPIO timing are hardware-sensitive. Training data remapping must match BIOS table semantics.

## Test Signals
Signals include parsed RAMMAP count, missing training-data warnings, successful low-to-high and high-to-low reclocks, stable GDDR5/DDR3 operation, correct behavior with non-uniform partitions, and debug PLL target/refclock logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramgk104.c -->
