# sources/distributed-fs/ceph-client/scripts/gendwarfksyms/types.c

## Purpose
`types.c` expands cached DIE fragments into symtypes strings, resolves nested type references, calculates CRC32 symbol versions, and optionally writes a symtypes file.

## Important APIs, Types, and Functions
It defines `type_list_entry`, `type_expansion`, `type_map`, and `version`. Key routines include `type_map_add()`, `type_map_get()`, `get_type_name()`, `__type_expand()`, `type_parse()`, `expand_type()`, `expand_symbol()`, `calculate_version()`, and `generate_symtypes_and_versions()`.

## Control Flow
Generation has three phases: iterate `die_map` to keep the longest expansion for each named type, iterate symbols to expand their type strings and calculate CRCs by recursively expanding type references, then write sorted type-map entries if a symtypes file was requested. Expansion-cycle caches prevent infinite recursion.

## State and Persistence Behavior
`type_map` and expansion caches are process-global during generation and freed at the end. Symbol CRCs are written back into `symbols.c` state. Type-string kABI overrides can synthesize types absent from DWARF.

## Dependencies and Integration Points
It consumes DIE fragments from `die.c`, symbols from `symbols.c`, kABI overrides from `kabi.c`, and zlib `crc32()`.

## Risks and Test Signals
The "longest expansion wins" heuristic is central and can mask shorter incomplete expansions. Type reference parsing is strict, especially quoted names with spaces. Test recursive types, anonymous types, type-string overrides, missing type references, symtypes sorting, and `--dump-versions`.
