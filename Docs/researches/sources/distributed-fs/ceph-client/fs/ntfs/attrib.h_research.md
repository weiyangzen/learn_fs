# sources/distributed-fs/ceph-client/fs/ntfs/attrib.h

## Purpose

`attrib.h` exposes the NTFS attribute subsystem interface. It defines the attribute search context, hole-handling constants, the unnamed-attribute sentinel, inline helpers, and public functions for mapping runlists, searching attributes, resizing, adding/removing attributes, reading whole metadata attributes, and range allocation operations.

## Important APIs, Types, And Functions

- `extern __le16 AT_UNNAMED[]` is the canonical unnamed attribute name.
- `struct ntfs_attr_search_ctx` tracks the currently mapped MFT record, current attribute record, enumeration state, owning inode, attribute-list entry, and base-record state when lookups cross into extent records.
- `enum { HOLES_NO, HOLES_OK }` controls whether resize/growth operations may represent new space as holes.
- Runlist APIs include `ntfs_map_runlist_nolock()`, `ntfs_map_runlist()`, `ntfs_attr_vcn_to_lcn_nolock()`, `ntfs_attr_find_vcn_nolock()`, `__ntfs_attr_find_vcn_nolock()`, `ntfs_attr_map_whole_runlist()`, and `ntfs_attr_vcn_to_rl()`.
- Search and attribute-list APIs include `ntfs_attr_lookup()`, `load_attribute_list()`, `ntfs_attr_get_search_ctx()`, `ntfs_attr_reinit_search_ctx()`, and `ntfs_attr_put_search_ctx()`.
- Mutation APIs include `ntfs_attr_record_resize()`, `ntfs_resident_attr_value_resize()`, `ntfs_attr_make_non_resident()`, `ntfs_attr_set()`, `ntfs_attr_set_initialized_size()`, `ntfs_attr_add()`, `ntfs_attr_record_rm()`, `ntfs_attr_record_move_to()`, `ntfs_attr_record_move_away()`, `ntfs_attr_update_mapping_pairs()`, `ntfs_attr_rm()`, `ntfs_attr_remove()`, and `ntfs_attr_fallocate()`.
- Size and capability helpers include `ntfs_attr_size()`, `ntfs_attr_size_bounds_check()`, and `ntfs_attr_can_be_resident()`.
- `ntfs_attrs_walk()` is inline syntactic sugar for enumerating all attributes using `ntfs_attr_lookup(AT_UNUSED, ...)`.

## Control Flow And Usage

Callers typically obtain a `struct ntfs_attr_search_ctx` with `ntfs_attr_get_search_ctx()`, call `ntfs_attr_lookup()` repeatedly or through `ntfs_attrs_walk()`, use `ctx->attr` and `ctx->mrec`, then release the context with `ntfs_attr_put_search_ctx()`. When an operation changes the lookup target, `ntfs_attr_reinit_search_ctx()` resets enumeration to the beginning.

Runlist callers either use the unlocked wrapper `ntfs_map_runlist()` or call `_nolock` variants while holding the correct runlist lock. Mutating APIs assume the caller understands whether the target `ntfs_inode` is a base inode or an attribute inode.

## State And Persistence Behavior

The header itself has no persistence, but its API contract exposes persistent state changes in MFT records, mapping pairs, attribute lists, runlists, cluster allocation, and inode size/flag fields. `struct ntfs_attr_search_ctx` may hold mapped MFT records and extent inode references, so lifecycle correctness directly affects mapped-record persistence and memory safety.

## Dependencies And Integration Points

The header includes `ntfs.h` and `dir.h`, so it integrates with core NTFS types, constants, VFS inode wrapping, and name collation support. It is consumed by attribute-list handling, compression, inode operations, bitmap management, and any code that needs to locate or mutate NTFS attributes.

## Risks And Edge Cases

- Search contexts carry mapped-record ownership. Forgetting `ntfs_attr_put_search_ctx()` leaks mappings; reusing a context after a documented mapping failure can dereference invalid pointers.
- `ntfs_attr_size()` returns resident value length or non-resident data size only; it does not return allocated size or initialized size.
- `ntfs_attrs_walk()` reports `-1` on error with errno in comments inherited from older code, while the underlying kernel code returns negative errno values; users should verify actual call-site expectations.
- Many APIs require specific lock state that is documented in implementation comments rather than encoded in types.

## Test Signals

Compile-time coverage should verify all declarations match implementations. Runtime tests should cover search-context enumeration, reinitialization after extent lookups, runlist lookup wrappers under read/write lock modes, and all public mutation APIs through higher-level inode operations.
