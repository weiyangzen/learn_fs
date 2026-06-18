# sources/distributed-fs/ceph/src/mds/SnapClient.h

Purpose: Declares the snapshot `MDSTableClient` specialization used by non-table-server MDS ranks to prepare snapshot table mutations and maintain a local cache.

Important APIs/types: Public methods cover table protocol hooks (`resend_queries`, `handle_query_result`, `handle_notify_prep`, `notify_commit`), mutation prepares (`prepare_create`, `prepare_create_realm`, `prepare_destroy`, `prepare_update`), synchronization (`refresh`, `sync`, `wait_for_sync`, `is_synced`), sequence accessors, snapshot set filtering, info lookup, and cache dumping.

Control flow: Callers prepare a table transaction, receive a table tid and optional reply buffer, and later observe commit notifications. Cache refresh waits are keyed by target version. `sync()` forces a query and marks the client unsynced until the reply for that request id or newer arrives.

State and persistence behavior: The class stores `cached_version`, last-created/destroyed sequences, `cached_snaps`, pending update/destroy maps, committing tids, version waiters, and sync status. No direct persistent I/O happens here; persistence is table-server journal state.

Dependencies and integration points: Inherits from `MDSTableClient` with `TABLE_SNAP`, depends on `snap.h`/`SnapInfo`, and is consumed by `Server` snapshot handlers and `SnapRealm` cache construction.

Risks: Header-level invariants require callers not to use cached snap data before sync. Pending destroy stores both removed snap and resulting sequence, which must remain aligned with server semantics. `wait_for_sync()` asserts unsynced state.

Test signals: Mock table-server replies should validate cache version, wait-for-version completion, mutation buffer encoding, and last sequence accessors.
