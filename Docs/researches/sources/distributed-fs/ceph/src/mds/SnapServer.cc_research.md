# sources/distributed-fs/ceph/src/mds/SnapServer.cc

Purpose: Implements the authoritative MDS snapshot table server, including mutation prepare/commit/rollback, client query/notify, OSD snapshot purge tracking, state reset, encode/decode, and forced repair.

Important APIs/functions: `reset_state`, `encode_server_state`, `decode_server_state`, `_prepare`, `_get_reply_buffer`, `_commit`, `_rollback`, `_server_update`, `_notify_prep`, `handle_query`, `check_osd_map`, `can_allow_multimds_snaps`, `handle_remove_snaps`, `dump`, `generate_test_instances`, and `force_update`.

Control flow: `_prepare()` decodes table ops: create allocates a new snap id or records a realm-create noop, destroy bumps `last_snap` as a sequence and records `(removed_snap, seq)`, and update records new metadata. `_commit()` moves pending creates/updates into `snaps`, removes destroyed snaps, updates last-created/destroyed, and adds snap ids/sequences to per-pool `need_to_purge`. `_rollback()` drops pending state. Queries return up-to-date or full table snapshots.

State and persistence behavior: The table-server encoded state includes `last_snap`, `snaps`, `need_to_purge`, pending update/destroy/noop maps, `last_created`, `last_destroyed`, and `snaprealm_v2_since`. `MDSTableServer` journals table operations; `_server_update()` persists removal from `need_to_purge` after OSD/monitor acknowledgement.

Dependencies and integration points: Uses `MDSTableServer`, `MMDSTableRequest`, `MRemoveSnaps`, `OSDMap`, `Objecter`, `MonClient`, `MDSMap`, and `SnapInfo`. `SnapClient` consumes query/notify payloads; monitors receive `MRemoveSnaps` for OSD data pool purge.

Risks: `last_snap` doubles as allocation counter and realm sequence, so destroy must bump it even though no new snapshot is created. Purge state includes both removed snap and destroy sequence per data pool. Multi-MDS snapshots are allowed only when no old-format realms remain. Legacy decode has older pending-destroy format conversion.

Test signals: Cover create/update/destroy prepare/commit/rollback, noop realm create, full/up-to-date queries, notify prep payloads, OSD map purge detection, monitor remove-snaps acknowledgements, upgrade format, forced update reset, and legacy decode versions.
