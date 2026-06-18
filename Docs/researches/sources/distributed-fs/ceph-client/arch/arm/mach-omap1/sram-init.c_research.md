<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/sram-init.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/sram-init.c

## Purpose
Detects, maps, protects, and allocates internal OMAP1 SRAM, then installs the SRAM-resident clock reprogramming routine used by low-level clock changes.

## Important APIs, Types, and Functions
Defines `omap_sram_push()`, `omap_sram_reprogram_clock()`, and `omap1_sram_init()`. Internal helpers include `omap_sram_push_address()` and `omap_detect_and_map_sram()`.

## Control Flow
Init determines SRAM size from CPU type, maps physical SRAM executable with `__arm_ioremap_exec`, preserves the bootloader area, clears the rest, marks it read-only/executable, copies `omap1_sram_reprogram_clock` into the top of SRAM using `fncpy`, and stores the function pointer. `omap_sram_push()` allocates downward, temporarily makes target pages writable, copies code, then restores ROX permissions.

## State and Persistence Behavior
Static SRAM allocator state tracks base, physical start, skip, size, and ceiling. `_omap_sram_reprogram_clock` is the installed callable SRAM function pointer.

## Dependencies and Integration Points
Depends on CPU revision detection, ARM `fncpy`, executable mappings, `set_memory_rw/rox`, cache/TLB helpers, and assembly symbols from `sram.S`.

## Risks
SRAM size probing is avoided because secure SRAM writes can hang; wrong CPU classification can overrun SRAM. The allocator is simple and not reclaiming. Function copy alignment and page permissions are boot-critical.

## Test Signals
Boot OMAP15xx and OMAP16xx, verify SRAM mapping succeeds, clock reprogramming through `omap_sram_reprogram_clock()` works, and suspend code can also be pushed without `Not enough space in SRAM`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/sram-init.c -->
