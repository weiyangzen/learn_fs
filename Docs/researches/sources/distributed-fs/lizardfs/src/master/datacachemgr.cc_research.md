# sources/distributed-fs/lizardfs/src/master/datacachemgr.cc

Purpose: fixed-size in-memory cache-validity tracker keyed by inode and client session.

Important APIs/functions: `dcm_open`, `dcm_access`, `dcm_modify`, `dcm_init`, and `dcm_clear`; internal `datacache_entry` table with inode hash chains and LRU links.

Control flow: `dcm_open` returns whether a session's cached inode data is valid, moving existing entries to LRU tail or recycling the LRU head for a new `(inode,sessionid)` with `cacheok=0`. `dcm_access` marks an existing entry valid and moves it to the tail. `dcm_modify` invalidates/removes entries for the same inode owned by other sessions and marks the modifying session valid if present. `dcm_init` resets hash buckets and LRU chain.

State and persistence: static arrays of 500,000 entries and 250,000 hash buckets; volatile only.

Dependencies and integration: called by master client/session file operation paths to decide whether client-side cached data remains usable.

Risks: fixed memory footprint and single global table; no locking visible here, so it assumes event-loop serialization or external synchronization. Session ID is stored in 31 bits of a bitfield.

Test signals: no direct tests in this subset.
