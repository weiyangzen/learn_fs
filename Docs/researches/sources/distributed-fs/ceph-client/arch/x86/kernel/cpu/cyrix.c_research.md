# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/cyrix.c

## Purpose
`cyrix.c` implements vendor identification and initialization for Cyrix and National Semiconductor Geode-era x86 CPUs. It handles CPUs with disabled or absent CPUID, reads Cyrix DIR/CCR registers, builds model strings, enables Cyrix/NSC memory/cache modes, applies old errata workarounds, marks Cyrix-specific MTRR emulation features, and registers Cyrix and NSC vendor descriptors.

## Important APIs, Types, and Functions
Low-level register helpers are `__do_cyrix_devid()` and `do_cyrix_devid()`, which probe CCR/DIR registers under IRQ protection. Main hooks are `early_init_cyrix()`, `init_cyrix()`, `init_nsc()`, and `cyrix_identify()`. Supporting routines include `check_cx686_slop()`, `set_cx86_reorder()`, `set_cx86_memwb()`, `geode_configure()`, and `test_cyrix_52div()`.

Registered descriptors are `cyrix_cpu_dev` (`CyrixInstead`, early init, full init, pre-CPUID identify) and `nsc_cpu_dev` (`Geode by NSC`, NSC init).

## Control Flow
On CPUs without CPUID, `common.c` can call vendor `c_identify()`. `cyrix_identify()` uses the 5/2 division flags test to detect Cyrix 486-class CPUs, sets the vendor string, and enables CPUID on affected 6x86/6x86MX models by writing CCR registers.

Early init reads DIR0/DIR1 and marks `X86_FEATURE_CYRIX_ARR` for 6x86 and 6x86MX/M II families. Full init converts Cyrix's extended MMX bit into `X86_FEATURE_CXMMX`, clears the original generic bit, recalibrates delay if the SLOP bit was set, derives family/model/stepping and printable model name from DIR values, applies MediaGX/Geode PCI/DMA/TSC workarounds, enables MMX extensions and memory write-back/reorder modes where needed, and marks `X86_BUG_COMA` on affected cores.

`init_nsc()` handles NSC-branded GX processors directly or delegates back to Cyrix initialization for other rebranded parts.

## State and Persistence
State is mostly in `struct cpuinfo_x86`: vendor, model ID, feature flags, bug flags, stepping, cache size, and loops-per-jiffy. The global `Cx86_dir0_msb` records the Cyrix family nibble for older bug logic. CCR/CR0 changes in memory write-back/reorder/power setup persist for the running CPU. `isa_dma_bridge_buggy` and TSC stability state are global platform effects for MediaGX systems.

## Dependencies and Integration Points
The file depends on Cyrix processor register helpers, PCI direct config access, ISA DMA, TSC stability, scheduler delay calibration, CR0 flags, and generic vendor registration in `cpu.h`. It integrates with `common.c` identification and with legacy MTRR emulation through `X86_FEATURE_CYRIX_ARR`.

## Risks
This file manipulates undocumented or lightly documented legacy CPU registers and chipset behavior. IRQ protection around CCR/DIR access is important. Incorrect model decoding can enable wrong memory modes, mark the wrong bug flags, or produce bad model strings. MediaGX workarounds affect ISA DMA and TSC stability globally. Hardware availability for regression tests is limited.

## Test Signals
Boot on Cyrix/NSC/Geode hardware or emulators with CPUID disabled/enabled and verify vendor detection, model string, `CXMMX`, `CYRIX_ARR`, `COMA`, cache size, delay-loop calibration, TSC stability messages, and MediaGX DMA workaround. Exercise 32-bit builds where most of this code is relevant.
