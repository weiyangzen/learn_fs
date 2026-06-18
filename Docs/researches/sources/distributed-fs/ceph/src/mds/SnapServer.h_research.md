# sources/distributed-fs/ceph/src/mds/SnapServer.h

Purpose: Declares the snapshot `MDSTableServer` specialization that owns global snapshot ids, live `SnapInfo` records, pending table mutations, and snap purge state.

Important APIs/types: Public methods include constructors, `handle_remove_snaps`, `reset_state`, `upgrade_format`, `check_osd_map`, `can_allow_multimds_snaps`, encode/decode/dump, `generate_test_instances`, and `force_update`. Overridden protected methods implement table-server state encoding, prepare/reply/commit/rollback, server update, notify prep, and query handling.

Control flow: Clients submit table mutations through the base table protocol; the server prepares pending changes by tid, notifies clients, commits or rolls back, and serves cache refresh queries. OSD-map checks reconcile `need_to_purge` against removed-snap state and monitor acknowledgements.

State and persistence behavior: Persistent fields are `last_snap`, `last_created`, `last_destroyed`, `snaprealm_v2_since`, `snaps`, `need_to_purge`, and pending maps. `last_checked_osdmap` is transient throttling state. `force_update()` can replace persistent state and reset the base table server if repair detects divergence.

Dependencies and integration points: Depends on `MDSTableServer`, `SnapInfo`, `MRemoveSnaps`, `MonClient`, and Ceph object ids. It is paired with `SnapClient` and feeds `SnapRealm` computations across ranks.

Risks: Header exposes direct table invariants: `upgrade_format()` asserts active state and `last_snap > 0`; callers must not run it before activation. `snaprealm_v2_since` gates multi-MDS snapshot behavior and must be upgraded once.

Test signals: Dencoder tests should include generated populated state, pending maps, purge maps, and force-update conditions.
