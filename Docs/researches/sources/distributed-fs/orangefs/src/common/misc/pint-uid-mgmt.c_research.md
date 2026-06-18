# sources/distributed-fs/orangefs/src/common/misc/pint-uid-mgmt.c

Purpose: Implements a small in-memory UID activity history for OrangeFS. It records recent user ids, access counts, first/last timestamps, and exposes a dump function for statistics.

Important APIs and functions: `PINT_uid_mgmt_initialize()` allocates the fixed-size LRU list and hash table. `PINT_uid_mgmt_finalize()` frees both. `PINT_add_user_to_uid_mgmt()` records an occurrence for a UID, incrementing existing entries or evicting the least-recently-used slot. `PINT_dump_all_uid_stats()` copies all slots into a caller-provided `PVFS_uid_info_s` array. `uid_hash_compare_keys()` supports quickhash lookup.

Control flow: Initialization first frees any existing list/hash state, allocates a list head and hash table, then allocates `UID_MGMT_MAX_HISTORY` empty entries linked into LRU order. Add looks up the UID in the hash table, updates count/time if found, or evicts the tail entry, removes its old hash mapping when occupied, fills new UID/count/timestamps, adds it to the hash, and moves it to the LRU head. Dump locks the mutex, walks exactly `UID_MGMT_MAX_HISTORY` entries, and copies their info.

State and persistence behavior: Global state is `uid_lru_list`, `uid_hash_table`, and `uid_mgmt_mutex`. Entries are volatile and reset on initialize/finalize. Timestamps use current timeval helpers and counts persist only in process memory.

Dependencies and integration points: Uses quicklist, quickhash, PVFS uid types, `PINT_util_get_current_timeval()`, and gen mutexes. The encoded `PVFS_uid_info_s` type in the header allows stats to cross protocol boundaries.

Risks and test signals: `PINT_add_user_to_uid_mgmt()` mutates list/hash state without taking `uid_mgmt_mutex`, while dump does lock, so concurrent add/dump/finalize is unsafe. Initialization failure paths leak prior allocations and newly allocated partial entries/hash table. `PINT_dump_all_uid_stats()` assumes initialization and a non-null output array. Tests should cover repeated initialize/finalize, LRU eviction after 25 unique UIDs, counter increments, timestamp ordering, null/uninitialized calls, and multi-threaded add/dump races.
