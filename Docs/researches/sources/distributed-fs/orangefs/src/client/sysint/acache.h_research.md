# sources/distributed-fs/orangefs/src/client/sysint/acache.h
## sources/distributed-fs/orangefs/src/client/sysint/acache.h

**Purpose:** Public sysint header for the attribute cache component, documenting cache policy and exposing initialization, configuration, lookup, update, invalidation, and perf-counter APIs.

**APIs and control flow:** It aliases `PINT_acache_options` to `PINT_tcache_options`, maps option constants to tcache constants, defines perf counter IDs, and declares `PINT_acache_initialize/finalize`, `get_info/set_info`, `get_cached_entry`, `update`, whole-entry invalidation, size-only invalidation, and `PINT_acache_get_pc()`.

**State and dependencies:** The header depends on PVFS object types, attrs, locks, quicklist/quickhash, tcache, and perf counters. It documents which sysint operations retrieve, insert, or invalidate cached attrs.

**Risks and tests:** Callers must pass valid output pointers to `get_cached_entry`; the implementation rejects nulls. The header's operation list is important for invalidation correctness and can drift as state machines change. Tests should include compile-time users of every API and operation-level integration checks that remove/rename/io/truncate invalidate expected cache state.
