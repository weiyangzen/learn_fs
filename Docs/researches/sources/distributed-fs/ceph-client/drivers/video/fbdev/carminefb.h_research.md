# sources/distributed-fs/ceph-client/drivers/video/fbdev/carminefb.h

## Purpose
`carminefb.h` defines Carmine PCI BAR numbers, display-memory sizing, display-selection flags, and board-specific DRAM initialization constants consumed by `carminefb.c`.

## Important APIs, Types, and Functions
The file has no functions. Important constants are `CARMINE_MEMORY_BAR`, `CARMINE_CONFIG_BAR`, `MAX_DISPLAY`, `CARMINE_DISPLAY_MEM`, `CARMINE_TOTAL_DISPLAY_MEM`, `CARMINE_USE_DISPLAY0`, and `CARMINE_USE_DISPLAY1`. DRAM defaults are selected by `CONFIG_FB_CARMINE_DRAM_EVAL` or `CONFIG_CARMINE_DRAM_CUSTOM`.

## Control Flow
Compile-time configuration controls which DRAM timing macro set is visible. Runtime initialization in `init_hardware()` writes these constants to Carmine DCTL and CTL registers.

## State and Persistence
The header defines constants only. Runtime persistence is in hardware registers and display memory after the driver writes these values.

## Dependencies and Integration Points
It is included by the Carmine PCI fbdev driver and must be consistent with `carminefb_regs.h`. The memory sizing assumes two 800x600x32-bit framebuffers.

## Risks and Edge Cases
If neither DRAM configuration block is enabled, required `CARMINE_DFLT_*` macros are absent and the driver will not compile. The custom config symbol name differs from the eval symbol prefix, so Kconfig consistency is important. The fixed display-memory size constrains supported modes.

## Test Signals
Compile tests should cover each DRAM configuration. Hardware tests should verify DRAM init completes, framebuffer memory is stable, and both display-memory offsets are valid.
