# File Research: sources/cow-pools/openzfs/module/zfs/sa.c

## Summary
Implements ZFS System Attributes, a compact per-object attribute storage format using dnode bonus buffers and optional spill blocks. SA stores registered attributes according to persistent layout tables so common attribute sets can be represented compactly.

## Main Responsibilities
- Maintains per-objset SA state, attribute registries, and layout tables.
- Supports legacy ZPL znode layouts and modern `DMU_OT_SA` layouts.
- Builds and caches index tables mapping attribute IDs to offsets.
- Handles bonus/spill sizing, spill allocation/removal, and whole-layout rewrites.
- Performs SA byteswapping using registered per-attribute byteswap functions.
- Provides handle lifecycle and lookup/update/remove APIs.
- Converts older ZPL objects when adding project ID support in kernel builds.

## Key APIs
- `sa_cache_init()`, `sa_cache_fini()`.
- `sa_setup()`, `sa_tear_down()`, `sa_set_sa_object()`.
- `sa_handle_get()`, `sa_handle_get_from_db()`, `sa_handle_destroy()`, `sa_spill_rele()`.
- `sa_lookup()`, `sa_bulk_lookup()`, `sa_lookup_uio()`, `sa_size()`.
- `sa_update()`, `sa_bulk_update()`, `sa_remove()`.
- `sa_replace_all_by_template()`, `sa_replace_all_by_template_locked()`.
- `sa_object_info()`, `sa_object_size()`, `sa_get_db()`, `sa_get_userdata()`, `sa_set_userp()`.
- `sa_register_update_callback()`, `sa_handle_lock()`, `sa_handle_unlock()`.

## Important Behavior
SA layouts are arrays of attribute IDs persisted in ZAP objects. Each unique layout receives a layout number and can have cached `sa_idx_tab_t` offset tables keyed by layout and variable-length sizes. Adding/removing an attribute, or changing a variable-length attribute size, rebuilds the complete attribute set and may create a new layout.

`sa_find_sizes()` computes header size, aligned attribute payload size, and whether attributes must spill from the bonus buffer. Spill blocks are resized up to `SPA_OLD_MAXBLOCKSIZE`; unneeded spills are removed. Normal fixed-size same-length updates write in place.

## Risks
Correctness depends on registry/layout ZAP consistency, per-objset locks, handle locks, and dbuf lifetime management. Byteswapping requires SA metadata to be available, unlike simpler self-describing ZFS blocks. Whole-layout rewrites are sensitive to preserving old data, variable-length header slots, spill transitions, and legacy znode compatibility.
