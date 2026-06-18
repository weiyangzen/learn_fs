# sources/distributed-fs/ceph-client/kernel/module/internal.h

## Purpose
Defines private shared declarations for the module subsystem. It centralizes `struct load_info`, symbol lookup structures, module use tracking, memory layout encoding helpers, feature-gated prototypes, and inline stubs used by the split implementation files.

## Important APIs, Types, And Functions
Key types are `struct kernel_symbol`, `struct load_info`, `enum mod_license`, `struct find_symbol_arg`, `struct module_use`, `enum fail_dup_mod_reason`, `struct mod_fail_load`, `struct mod_unload_taint`, `struct mod_tree_root`, and `struct modversion_info_ext`. Important declarations cover signature checks, symbol resolution, kallsyms layout, sysfs setup, version checks, decompression, tree lookup, strict RWX, stats, duplicate autoload suppression, taint tracking, and kmemleak hooks.

## Control Flow
The header has no runtime control flow, but it defines the contracts that `main.c` calls during load and unload. Most optional subsystems expose real functions under their Kconfig guard and no-op or permissive inline stubs otherwise.

## State And Persistence
`struct load_info` is the central transient load transaction state: ELF header, section headers, section strings, string table, module pointer, indices for special sections, decompression pages, signature result, and kallsyms offsets. Global state declarations include `module_mutex`, `modules`, linker-provided symbol tables, and `mod_tree`.

## Dependencies And Integration Points
Depends on ELF, modules, mutex/RCU, memory management, Kconfig feature symbols, and linker-defined ksymtab/kcrctab ranges. It links all module subfiles to the loader core without exporting these interfaces publicly.

## Risks And Edge Cases
The `sh_entsize` encoding reserves high bits for memory type and lower bits for offsets; overflow or mismatched masks corrupt layout. Stub behavior must match feature-off expectations. Changes to `load_info.index` or `struct kernel_symbol` must stay synchronized with modpost, linker output, and versioning code.

## Test Signals
Compile coverage across feature permutations is essential. Runtime signals include successful module load paths using signatures, compression, kallsyms, sysfs, modversions, and unload tracking, plus absence of unresolved references when options are disabled.
