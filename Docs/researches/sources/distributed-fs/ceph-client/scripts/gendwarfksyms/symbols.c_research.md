# sources/distributed-fs/ceph-client/scripts/gendwarfksyms/symbols.c

## Purpose
`symbols.c` manages the exported-symbol table, ELF symbol address resolution, pointer fallback matching, and final `#SYMVER` output.

## Important APIs, Types, and Functions
It maintains hash maps by symbol name and by `{section,address}`. Public APIs include `symbol_read_exports()`, `symbol_read_symtab()`, `symbol_get()`, `symbol_set_ptr()`, `symbol_set_die()`, `symbol_set_crc()`, `symbol_for_each()`, `symbol_print_versions()`, `symbol_free()`, and `is_symbol_ptr()`.

## Control Flow
Exports are read from stdin into unprocessed symbols. ELF global symbols set section/address data. DWARF processing marks DIE or pointer DIE addresses. Type expansion sets CRCs, propagating the same CRC to address aliases. Version printing warns for symbols that never reached processed state.

## State and Persistence Behavior
The symbol maps are global heap state for the process. `state`, `crc`, `addr`, `die_addr`, and `ptr_die_addr` persist across object/CU processing until freed.

## Dependencies and Integration Points
It depends on libelf/gelf, kernel hash helpers, and `gendwarfksyms.h`. `dwarf.c` queries and mutates symbol state; `types.c` finalizes CRCs.

## Risks and Test Signals
Alias propagation by address can override versions and emits warnings. Symbols without debug info depend on `__gendwarfksyms_ptr_` naming. Test duplicate exports, aliases, undefined symbols, `SHT_SYMTAB_SHNDX`, pointer fallbacks, and missing debug info warnings.
