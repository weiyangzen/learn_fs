# sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-attr-cache.c

## Purpose
`dbpf-attr-cache.c` implements a bounded in-memory cache from `TROVE_object_ref` to `TROVE_ds_attributes`, with optional small keyval payload caching for configured key names. It reduces dspace database lookups and keeps bstream size metadata available to hot paths.

## Important APIs, types, and functions
The global `dbpf_attr_cache_mutex` is intentionally public; callers must hold it around cache operations. Configuration entry points are `dbpf_attr_cache_set_keywords()`, `dbpf_attr_cache_set_size()`, `dbpf_attr_cache_set_max_num_elems()`, and `dbpf_attr_cache_do_initialize()`. Lifecycle functions are `dbpf_attr_cache_initialize()` and `dbpf_attr_cache_finalize()`. Lookup/update functions include `dbpf_attr_cache_elem_lookup()`, `dbpf_attr_cache_ds_attr_fetch_cached_data()`, `dbpf_attr_cache_ds_attr_update_cached_data()`, `dbpf_attr_cache_ds_attr_update_cached_data_bsize()`, `dbpf_attr_cache_insert()`, and `dbpf_attr_cache_remove()`. Keyval helpers include `dbpf_attr_cache_elem_get_data_based_on_key()`, `dbpf_attr_cache_elem_set_data_based_on_key()`, and `dbpf_attr_cache_keyval_pair_fetch_cached_data()`.

## Control flow and state
Initialization validates the configured keyword count, initializes `s_key_to_attr_table`, seeds `rand()`, and resets `s_current_num_cache_elems`. Insertions replace existing entries or evict an arbitrary entry when the max element count is exceeded. Eviction starts at a random hash bucket and scans forward. Finalization drains every hash bucket, frees cached keyval payloads, finalizes the qhash, and frees the keyword string list.

## Persistence and integration
The cache is not persistent; it shadows the dspace DB. `dbpf-dspace.c` populates the cache on `dbpf_dspace_attr_get()` and updates it after `dbpf_dspace_attr_set()`. Bstream write paths remove or update entries when datafile sizes may change.

## Dependencies
It depends on `quickhash`, `quicklist`, `gen-locks`, `PINT_split_string_list()`, `PINT_free_string_list()`, `TROVE_ds_attributes`, and gossip debug categories.

## Risks and test signals
The implementation assumes external locking and does not lock internally, so misuse can race table mutation and free. `dbpf_attr_cache_elem_set_data_based_on_key()` asserts malloc success instead of returning `-TROVE_ENOMEM`. The header declares `dbpf_attr_cache_keyval_pair_update_cached_data()`, but this source does not define it; builds only pass if no code references that symbol or another file provides it. Tests should cover max-entry eviction, keyword count rejection, keyval payload overwrite/free, cache invalidation on dspace removal and bstream writes, and concurrent caller lock discipline.
