# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/reader/cursor.go

Purpose: maintains per-action meta-log cursor positions for one lifecycle shard.

Important APIs/type: `Cursor`, `NewCursor`, `MinTsNs`, `Get`, `Advance`, `Freeze`, `Unfreeze`, `IsFrozen`, `Snapshot`, and `Restore`. State maps `ActionKey` to last fully resolved timestamp and separately tracks frozen keys.

Control flow: `Advance` is monotonic, ignores non-positive timestamps, and is a no-op for frozen keys. `Freeze` pins a key and seeds its position if unset. `MinTsNs` returns the minimum state value or zero if empty. `Snapshot` copies positions only; frozen state is persisted elsewhere. `Restore` replaces the map and clears freezes.

State/persistence: in-memory, mutex-protected. `Snapshot`/`Restore` are the persistence boundary used by persisters and startup.

Dependencies/integration: reader uses `MinTsNs` as `SubscribeMetadata.SinceNs`. Dispatcher/blocker flows freeze actions on blocked outcomes.

Risks: long freezes can exceed meta-log retention; comments note operator blocker resolution is needed. Persisted snapshots do not include frozen flags, so callers must reapply them from blocker records.

Test signals: cursor and composition tests cover empty/min, monotonic advance, zero ignore, freeze/unfreeze, freeze-on-unset seeding, snapshot deep copy, restore replacement, and frozen min inclusion.
