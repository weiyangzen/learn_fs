# sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/hashtable.h

## Purpose

This NetIDMgr utility header declares a simple caller-synchronized hashtable abstraction with caller-supplied hash, compare, add-reference, and delete-reference callbacks. It stores key/data associations by reference, not by copying.

## Important APIs, Types, and Functions

- `hash_function_t` computes a `khm_int32` hash from a key.
- `comp_function_t` compares two keys with strcmp-style ordering.
- `add_ref_function_t` and `del_ref_function_t` are lifecycle hooks invoked when entries are added, replaced, removed, or table-deleted.
- `hash_bin` stores `void *data`, `void *key`, and linked-list fields through `LDCL`.
- `hashtable` stores bin count, callback pointers, and an array of bin heads.
- `hash_new_hashtable`, `hash_del_hashtable`, `hash_add`, `hash_del`, `hash_lookup`, and `hash_exist` are the core table operations.
- `hash_string` and `hash_string_comp` are helpers for NULL-terminated wide-string keys.

## Control Flow

Creation fixes the bin count and callback functions. `hash_add()` hashes the key, removes an existing equal-key association if present, stores the new key/data pair by reference, and invokes the add-ref hook. `hash_del()` removes the matching association and invokes the delete-ref hook. Lookup and existence checks hash and compare keys in a bin chain. Deleting the table walks remaining entries and invokes delete-ref hooks.

## State and Persistence Behavior

The hashtable owns its internal bin nodes and bin array, but it does not own key or data memory unless callbacks implement ownership. Keys should either be constants or embedded in the data object so key lifetime follows data lifetime. No persistence is performed.

## Dependencies and Integration Points

Depends on NetIDMgr base definitions in `<khdefs.h>` and linked-list macros in `<khlist.h>`. It is a generic in-memory utility for NetIDMgr components that need keyed lookup and optional reference accounting.

## Risks

- The API is explicitly not thread-safe; callers must serialize operations on a table.
- Because keys and data are stored by reference, dangling pointers are easy if callers free objects before removal.
- Replacement calls the delete-ref hook for the old object before add-ref for the new one; hooks must tolerate that ordering.
- `hash_lookup()` returning NULL is defined as equivalent to nonexistence, so storing NULL data is not supported.
- Hash function quality and bin count directly affect performance.

## Test Signals

Unit tests should cover create/delete, add/lookup/exist/delete, replacement with equal keys, hook invocation counts, wide-string hash/compare behavior, and caller-side locking assumptions. Tests should also cover NULL keys if the chosen comparator supports them.
