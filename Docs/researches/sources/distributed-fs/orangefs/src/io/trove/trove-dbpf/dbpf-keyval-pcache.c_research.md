# sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-keyval-pcache.c

## Purpose
`dbpf-keyval-pcache.c` implements a small position-to-keyname cache for DBPF keyval iteration. It maps `(handle, TROVE_ds_position)` to the key name and length, reducing repeated database cursor work for keyval position lookups.

## Important APIs, types, and functions
`PINT_dbpf_keyval_pcache_initialize()` allocates the cache wrapper, initializes its mutex, creates a `PINT_tcache`, disables expiration, and sets a hard limit of 51200 entries. `PINT_dbpf_keyval_pcache_finalize()` destroys the tcache and mutex. `PINT_dbpf_keyval_pcache_lookup()` returns a cached key pointer and length. `PINT_dbpf_keyval_pcache_insert()` replaces any existing entry for the same handle/position and inserts a copied key name. Static helpers implement compare, hash, and payload free.

## Control flow and state
State is `PINT_dbpf_keyval_pcache`, containing a `PINT_tcache *` and mutex. Lookup and insert both lock around tcache access. The hash mixes high and low handle bits with the position and masks into a 1024-entry table. Entries store `keyname[PVFS_NAME_MAX]` and an integer length.

## Persistence and integration
The cache is volatile and mirrors keyval iteration state. It is initialized for collections in DBPF management code and passed into keyval iteration helpers, including dspace removal cleanup.

## Dependencies
It depends on `tcache`, `quickhash`, `gen-locks`, `TROVE_handle`, `TROVE_ds_position`, `PVFS_NAME_MAX`, and gossip debug logging.

## Risks and test signals
`PINT_dbpf_keyval_pcache_initialize()` leaks the wrapper if tcache initialization fails. `PINT_dbpf_keyval_pcache_insert()` does not validate `length <= PVFS_NAME_MAX`, so overlong key names can overflow `keyname`. `dbpf_keyval_pcache_hash()` casts the lookup key to `dbpf_keyval_pcache_entry` even though callers pass `dbpf_keyval_pcache_key`; current first fields match, but it is fragile. Tests should cover replacement, lookup miss/hit, hard-limit eviction, overlong key rejection expectation, finalize after partial init failure, and thread contention.
