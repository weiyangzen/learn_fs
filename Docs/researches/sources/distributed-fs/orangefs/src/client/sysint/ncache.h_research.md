# sources/distributed-fs/orangefs/src/client/sysint/ncache.h
## sources/distributed-fs/orangefs/src/client/sysint/ncache.h

**Purpose:** Public sysint header for the name cache component, documenting cached fields and exposing cache lifecycle, configuration, lookup, update, invalidation, and perf-counter APIs.

**APIs and control flow:** It aliases tcache options into `NCACHE_*` enum values, defines perf counter IDs, and declares `PINT_ncache_initialize/finalize`, `get_info/set_info`, `get_cached_entry`, `update`, `invalidate`, and `PINT_ncache_get_pc()`.

**State and dependencies:** Depends on PVFS types/attrs, locks, quicklist/quickhash, tcache, and perf counters. The comments document operations expected to retrieve, insert, or delete ncache entries.

**Risks and tests:** The documented operation list must remain synchronized with lookup, create, mkdir, symlink, readdir, remove, and rename state-machine behavior. The API assumes non-null parent refs and entry names. Tests should include API-level compile coverage and end-to-end invalidation after remove/rename and failed lookup operations.
