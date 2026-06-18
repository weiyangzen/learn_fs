# sources/distributed-fs/ceph-client/arch/arm/kernel/module-plts.c

Purpose: sizes, allocates, and populates ARM module PLT entries used when module branch relocations cannot reach their target directly, with fixed entries for dynamic ftrace when enabled.

Important APIs/types/functions: `module_frob_arch_sections`, `get_module_plt`, and `in_module_plt`. Helpers include `prealloc_fixed`, `cmp_rel`, `is_zero_addend_relocation`, `duplicate_rel`, and `count_plts`.

Control flow: section frobbing locates `.plt`, `.init.plt`, and symtab, marks unwind sections executable when needed for range, sorts executable relocations, counts potential PLTs split between core/init, and converts PLT sections to allocated NOBITS executable sections. At relocation time, `get_module_plt` reuses fixed or last duplicate entries or appends a new literal/ldr pair.

State and persistence: per-module `mod->arch.core/init.plt`, counts, and cached entry pointers track PLT allocation. PLT code/literals persist in module memory until unload/init-free.

Dependencies and integration: used by `module.c` relocation range fallback, ftrace, module loader layout, ARM/Thumb opcode helpers, sort, and RCU module text lookup.

Risks: undercounting PLTs triggers `BUG_ON`; duplicate suppression assumes sorted relocations and zero-addend recognition; PLT distance is itself constrained by module layout. Test signals include loading large/out-of-range modules, ftrace modules, init text release, and `in_module_plt` stack/unwind checks.
