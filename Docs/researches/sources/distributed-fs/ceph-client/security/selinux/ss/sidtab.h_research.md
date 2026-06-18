# sources/distributed-fs/ceph-client/security/selinux/ss/sidtab.h

## Purpose
`sidtab.h` defines the SID table data structures and public APIs for SELinux runtime SID management. It captures the allocation geometry, initial SID handling, reverse hash, conversion metadata, locking, and optional string cache contract used by `sidtab.c` and `services.c`.

## Important APIs, Types, and Functions
`struct sidtab_entry` stores SID, context hash, `struct context`, optional cached string, and reverse-hash node. `union sidtab_entry_inner`, `sidtab_node_leaf`, and `sidtab_node_inner` define page-sized tree nodes. `struct sidtab_isid_entry` stores fixed initial SIDs. `struct sidtab_convert_params` connects old-to-new conversion args with a target sidtab. `struct sidtab` owns roots, count, conversion pointer, frozen flag, lock, optional cache state, initial SID entries, and `context_to_sid` hash. Inline `sidtab_search()` and `sidtab_search_force()` expose context pointers from entries.

## Control Flow
The constants derive node capacities from page size and structure size, allowing a multi-level tree up to `U32_MAX` dynamic SIDs. Callers search by SID, insert by context, and coordinate policy reload through conversion/freeze helpers.

## State and Persistence
The header separates fixed initial SID state from dynamically allocated SIDs. `count` is explicitly documented as atomically read/written, while `convert` and `frozen` are lock-protected writer state.

## Dependencies and Integration Points
It includes Linux spinlock/log2/hashtable APIs and `context.h`. It is consumed by `policydb.h`, `services.h`, and all code that needs SID-to-context resolution.

## Risks
The allocation geometry is sensitive to structure-size changes. Any new fields in `sidtab_entry` can reduce leaf capacity and should be evaluated against `SIDTAB_MAX_LEVEL`. Callers must respect that returned context pointers are protected by the surrounding RCU/policy lifetime.

## Test Signals
Build tests with different page sizes and `CONFIG_SECURITY_SELINUX_SID2STR_CACHE_SIZE` values are useful. Runtime tests should validate initial SID setup, dynamic SID overflow behavior, conversion freeze semantics, and cache enable/disable compilation.
