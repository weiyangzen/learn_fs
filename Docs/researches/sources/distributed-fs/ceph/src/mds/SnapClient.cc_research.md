# sources/distributed-fs/ceph/src/mds/SnapClient.cc

Purpose: Implements the MDS table client cache for the global snapshot table, including query refresh, sync, prepare requests, commit notifications, and snapshot lookup/filtering.

Important APIs/functions: `resend_queries`, `handle_query_result`, `handle_notify_prep`, `notify_commit`, `prepare_create`, `prepare_create_realm`, `prepare_destroy`, `prepare_update`, `refresh`, `sync`, `get_snaps`, `filter`, `get_snap_info`, `get_snap_infos`, and `dump_cache`.

Control flow: `refresh()` sends a full-table query with the cached version and optionally records waiters by desired version. `handle_query_result()` decodes either an up-to-date marker or a full table payload, updates cached live and pending maps, advances last-created/destroyed sequences, clears committed tids, and releases waiters once synced and sufficiently fresh. Notify-prep messages reuse query decoding and send a notify ack.

State and persistence behavior: `SnapClient` itself is a cache; authoritative persistence is in `SnapServer`/`MDSTableServer` journaled state. The cache tracks live snaps, pending update/destroy records, committing tids, version waiters, sync request id, and last create/destroy sequence overlays so readers see local committing transactions.

Dependencies and integration points: Uses `MMDSTableRequest`, `MDSTableClient`, `MDSRank`, `MDSMap`, `SnapInfo`, and `SnapRealm`. `SnapRealm` calls `get_snaps`, `filter`, and `get_snap_infos` to compute inherited realm snapshots.

Risks: Snapshot visibility relies on overlaying `committing_tids` in sorted order. If sync request ids are mishandled after resend or server-ready transitions, waiters may complete too early or stall. Cache APIs assert `cached_version > 0`, so callers must sync before use.

Test signals: Cover full and up-to-date query replies, notify prep/ack, resend after reconnect, create/destroy/update prepares, pending transaction overlay, sync waiters, dump refusal before sync, and filtering around simultaneously pending create and destroy tids.
