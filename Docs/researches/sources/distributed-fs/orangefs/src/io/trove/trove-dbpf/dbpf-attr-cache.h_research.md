# sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-attr-cache.h

## Purpose
`dbpf-attr-cache.h` defines the DBPF attribute cache contract, cache element layouts, defaults, and setinfo-style configuration hooks.

## Important APIs, types, and functions
`DBPF_ATTR_CACHE_MAX_NUM_KEYVALS` caps cached keyval names at 8, `DBPF_ATTR_CACHE_DEFAULT_SIZE` defaults the hash table to 511 buckets, and `DBPF_ATTR_CACHE_DEFAULT_MAX_NUM_CACHE_ELEMS` defaults the hard element cap to 1024. `dbpf_keyval_pair_cache_elem_t` stores a key string, copied payload pointer, and payload length. `dbpf_attr_cache_elem_t` stores the qhash link, `TROVE_object_ref`, cached `TROVE_ds_attributes`, the fixed keyval pair array, and active keyval count. Public methods cover lifecycle, lookup, dspace attr updates/fetches, keyval pair lookup/fetch/update, insert/remove, and configuration.

## Control flow and state
The header describes state held by the implementation but owns no runtime state. Its comments establish return conventions: generally `0` on success and `-1` on failure, with some Trove-specific errors from buffer-size checks.

## Persistence and integration
The structures mirror persistent dspace records stored in DBPF's database and optional keyval entries but are volatile. Callers in dspace, bstream, and keyval code include this header to coordinate cache population and invalidation.

## Dependencies
It includes `pvfs2-internal.h`, `dbpf.h`, `trove-types.h`, and `quickhash.h`.

## Risks and test signals
The declaration for `dbpf_attr_cache_keyval_pair_update_cached_data()` has no definition in the paired source file, which is a link-time risk if callers use it. The fixed-size keyval array makes configuration validation important. Tests should compile all users, verify ABI assumptions for `TROVE_object_ref`, and check that configured keyword lists above eight are rejected without corrupting existing cache state.
