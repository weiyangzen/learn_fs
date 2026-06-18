<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/sram.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/sram.h

## Purpose
Declares OMAP1 SRAM helpers and assembly symbols used by clock and PM initialization.

## Important APIs, Types, and Functions
Declares `omap_sram_reprogram_clock()`, `omap1_sram_init()`, `omap_sram_push()`, `omap1_sram_reprogram_clock()`, and `omap1_sram_reprogram_clock_sz`.

## Control Flow
No runtime flow. It exposes the C-level callable wrappers and warns consumers not to call raw assembly symbols directly.

## State and Persistence Behavior
No state; state is held in `sram-init.c`.

## Dependencies and Integration Points
Requires `u32` and size types from includers. Bridges C code with `sram.S` symbols.

## Risks
The raw assembly declaration order in the comment area is easy to misuse; callers should use the wrapper so the function has been copied to SRAM first.

## Test Signals
Compile all clock/PM users and verify unresolved assembly symbols are present only when OMAP1 SRAM support is linked.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/sram.h -->
