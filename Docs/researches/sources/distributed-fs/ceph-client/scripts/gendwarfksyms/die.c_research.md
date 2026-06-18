# sources/distributed-fs/ceph-client/scripts/gendwarfksyms/die.c

## Purpose
`die.c` owns the DWARF DIE cache for `gendwarfksyms`, storing partially and fully rendered type fragments keyed by DIE address and processing state.

## Important APIs, Types, and Functions
The central map is `{die->addr, enum die_state} -> struct die`. `die_map_get()` creates or returns a cache entry. `die_map_add_string()`, `die_map_add_linebreak()`, and `die_map_add_die()` append render fragments. `die_map_for_each()` and `die_map_free()` support later type expansion and cleanup.

## Control Flow
DWARF walkers request cache entries for desired states, append fragments while rendering, and mark states in `dwarf.c`. Later `types.c` iterates the map to build type strings. Cleanup frees fragment strings, FQNs, and cache entries while reporting debug statistics.

## State and Persistence Behavior
The die map is global process state for one `gendwarfksyms` run across processed CUs/objects until freed. It persists rendered fragments and FQNs to avoid repeated DWARF walks.

## Dependencies and Integration Points
It is used heavily by `dwarf.c` and `types.c`, and depends on kernel list/hashtable helpers and allocation wrappers.

## Risks and Test Signals
State identity relies on DIE addresses being stable and meaningful within libdw objects. Incorrect state transitions can reuse incomplete strings. Test duplicate DIE reuse, complete vs unexpanded entries, FQN ownership, and cleanup under `--dump-die-map`.
