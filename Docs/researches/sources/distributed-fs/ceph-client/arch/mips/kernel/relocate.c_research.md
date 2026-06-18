# sources/distributed-fs/ceph-client/arch/mips/kernel/relocate.c

## Purpose
Implements boot-time kernel relocation and KASLR support for MIPS, including relocation-table application, exception-table relocation, optional FDT movement, command-line handling, and panic-time relocation reporting.

## Important APIs, Types, and Functions
- `plat_post_relocation()` and `plat_get_fdt()` are weak platform hooks.
- `sync_icache()` uses `synci` over the relocated image.
- `reloc_handler()` and relocation-specific helpers apply `R_MIPS_64`, `R_MIPS_32`, `R_MIPS_26`, and `R_MIPS_HI16`.
- `do_relocations()` walks `_relocation_start` to `_relocation_end`.
- `relocate_exception_table()` adjusts exception table entries.
- KASLR helpers `get_random_boot()`, `kaslr_disabled()`, and `determine_relocation_address()` choose relocation offset when `CONFIG_RANDOMIZE_BASE` is enabled.
- `relocate_kernel()` is the main entry returning the actual `start_kernel` address.
- `register_kernel_offset_dumper()` adds a panic notifier that prints relocated section addresses.

## Control Flow
`relocate_kernel()` initializes firmware command-line state and early DT, computes kernel and BSS lengths, chooses a relocation address, validates alignment/non-overlap, clears `arcs_cmdline` to avoid duplicates, optionally relocates an overlapping external FDT, copies text/data to the new location, applies relocations, syncs I-cache, relocates exception tables, copies BSS, notifies platform of FDT relocation and post-relocation fixups, updates `__current_thread_info`/`$gp` for the relocated image, computes relocated `start_kernel`, and records `__kaslr_offset`. If anything fails, it returns the original `start_kernel`.

## State and Persistence
Relocation mutates the in-memory kernel image copy, relocated BSS, exception table, FDT pointer/platform state, command-line buffers, `__current_thread_info`, and `__kaslr_offset`. No disk persistence.

## Dependencies and Integration Points
Depends on linker-provided relocation and section symbols, firmware command-line helpers, OF/FDT scanning, mem layout, cache synchronization instructions, panic notifier list, and platform hooks. `setup.c` later exports and reports `__kaslr_offset`.

## Risks
Relocation address must be 64 KiB aligned and not overlap the original image. `R_MIPS_26` can overflow if target high bits differ after relocation. `R_MIPS_HI16` handling is simplified and must match generated relocation records. External FDT movement must avoid overwriting the target image. Clang `$gp` workaround is delicate. A failed relocation path must leave original command-line and FDT state usable.

## Test Signals
Boots with and without `nokaslr` should reach `start_kernel`; `/proc/kallsyms`/panic notifier should reflect relocation when enabled. FDT bootargs should not duplicate. KASLR offset should vary with entropy and respect max offset. Relocation failures should fall back rather than crash before `start_kernel`.
