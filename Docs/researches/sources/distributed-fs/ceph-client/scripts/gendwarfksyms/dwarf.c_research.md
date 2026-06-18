# sources/distributed-fs/ceph-client/scripts/gendwarfksyms/dwarf.c

## Purpose
`dwarf.c` walks DWARF compile units, finds exported symbols, renders their type signatures into canonical fragments, resolves fully qualified names, and applies stable kABI interpretation rules while populating the DIE map.

## Important APIs, Types, and Functions
Attribute helpers read DWARF strings, flags, udata, and references. Type processors cover base, typedef, modifiers, pointers, arrays, subroutines, structures/classes/unions, variants, enumerations, members, parameters, and unspecified assembly types. `process_cu()` is the entry point. kABI support includes reserved, ignored, renamed, declaration-only, byte-size, enumerator, and type-string behavior.

## Control Flow
`process_cu()` first resolves FQNs by recursively visiting scopes. It then scans namespaces/classes/structures for exported `DW_TAG_subprogram` and `DW_TAG_variable` DIEs matching the symbol table, initializes per-symbol expansion state, and renders a symbol cache. Missing external symbols can be represented by `__gendwarfksyms_ptr_` pointer DIEs and processed after the CU scan.

## State and Persistence Behavior
It writes global DIE-map entries, symbol DIE addresses, pointer fallback DIE addresses, and per-symbol expansion caches. Private `.c` definitions can be treated as declarations to avoid versioning private implementation details.

## Dependencies and Integration Points
It depends on libdw, `symbols.c`, `die.c`, `cache.c`, `kabi.c`, and `types.c`. Its output fragments are later expanded and CRC'd by `generate_symtypes_and_versions()`.

## Risks and Test Signals
DWARF layout differences across compilers are high risk. Recursion and expansion suppression must avoid cycles while still detecting ABI-relevant nested changes. kABI union conventions are policy-sensitive. Test with GCC/Clang/Rust-like linkage names, examples in `examples/kabi_ex.h`, symbol pointer fixtures, private `.c` definitions, anonymous scopes, and `--stable`.
