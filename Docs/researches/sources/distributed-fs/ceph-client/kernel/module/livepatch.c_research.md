# sources/distributed-fs/ceph-client/kernel/module/livepatch.c

## Purpose
Persists enough original ELF metadata for livepatch modules after ordinary module init memory is freed.

## Important APIs, Types, And Functions
Defines `copy_module_elf` and `free_module_elf`. It fills `mod->klp_info` with a copied ELF header, section header table, section string table, and symbol table index.

## Control Flow
When `main.c` recognizes a livepatch module and kallsyms have been populated, `copy_module_elf` allocates `mod->klp_info`, duplicates the section headers and section strings from `load_info`, records `symndx`, and rewrites the symtab section address to point at `mod->core_kallsyms.symtab`. Unload cleanup calls `free_module_elf`.

## State And Persistence
The copied ELF metadata persists for the lifetime of the livepatch module. It is independent of the temporary load buffer and init-memory kallsyms that will be freed.

## Dependencies And Integration Points
Depends on `CONFIG_LIVEPATCH`, `struct klp_modinfo`, module kallsyms layout, and `main.c` livepatch checks. It allows the livepatch subsystem to inspect sections and symbols after load.

## Risks And Edge Cases
Allocation failure must unwind partially copied metadata. The symtab address rewrite assumes livepatch modules keep a complete core kallsyms symtab; if kallsyms filtering changed, livepatch resolution could break.

## Test Signals
Load and unload livepatch modules, verify symbol/section resolution after init memory is freed, and run failure-injection on each allocation path to confirm cleanup.
