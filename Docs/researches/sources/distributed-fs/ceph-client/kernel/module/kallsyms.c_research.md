# sources/distributed-fs/ceph-client/kernel/module/kallsyms.c

## Purpose
Implements kallsyms support for modules: symbol table layout, runtime symbol metadata population, build-id extraction, address-to-symbol lookup, symbol-name lookup, and iteration over module symbols.

## Important APIs, Types, And Functions
Important functions are `layout_symtab`, `add_kallsyms`, `init_build_id`, `module_address_lookup`, `lookup_module_symbol_name`, `module_get_kallsym`, `module_kallsyms_lookup_name`, `find_kallsyms_symbol_value`, and `module_kallsyms_on_each_symbol`. Internal helpers include `lookup_exported_symbol`, `is_exported`, `elf_type`, `is_core_symbol`, `find_kallsyms_symbol`, and `__find_kallsyms_symbol_value`.

## Control Flow
During layout, the full ELF symtab and strtab are kept in init memory while a filtered core kallsyms copy is appended to module data. `add_kallsyms` builds typetabs, copies retained core symbols and names, and publishes `mod->kallsyms` to init-time data with RCU. After module init, `main.c` switches to `mod->core_kallsyms`. Lookup paths use RCU to find the containing module and scan its kallsyms for nearest symbols or exact names.

## State And Persistence
Symbol metadata persists in module init memory until init is freed, then in `mod->core_kallsyms` for the module lifetime. Livepatch modules keep all symbols. Optional build IDs are copied into `mod->build_id`.

## Dependencies And Integration Points
Depends on `CONFIG_KALLSYMS`, build-id parsing, exported symbol tables, module address lookup, RCU, and `/proc/kallsyms` style interfaces. It cooperates with `sysfs.c` for section address visibility.

## Risks And Edge Cases
Filtering must preserve enough symbols for diagnostics while dropping init symbols after init memory is freed. Name copying uses bounded `strscpy`; bad size accounting could truncate or desynchronize names. Lookup is linear per module symbol table and intentionally avoids heavy locking in oops paths.

## Test Signals
Signals include correct `/proc/kallsyms` module entries, stack traces resolving module symbols, build-id reporting, livepatch symbol availability, `module_kallsyms_on_each_symbol` iteration, and safe behavior while modules load/unload under RCU.
