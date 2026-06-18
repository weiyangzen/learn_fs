# sources/control-plane/longhorn-engine/pkg/replica/hash.go

Purpose: implements asynchronous snapshot hashing, checksum-file persistence, and silent corruption detection for replica snapshots.

Important APIs/types/functions: `SnapshotHashStatus` records state, checksum, error, and silent-corruption flag behind a status lock. `SnapshotHashJob` carries context, cancel function, snapshot name, rehash flag, and status. `LockFile`/`UnlockFile` serialize hashing across the node using `/host/var/lib/longhorn/.lock/hash`. `Execute` drives change-time checks, cached checksum reuse, CRC64 hashing, checksum-file update, and corruption detection. Helpers read/write/delete checksum JSON files, get ctime, copy data with cancellation/existence checks, and create the `crc64` hash.

Control flow: `Execute` takes the node-wide lock, gets current ctime, returns early if silent corruption is already recorded, skips hashing when a valid checksum exists and rehash is false, otherwise hashes the snapshot. After hashing it detects same-ctime/different-checksum silent corruption and preserves the old checksum metadata while setting the flag. A deferred block updates job state and writes checksum metadata only when hashing actually occurred.

State and persistence: checksum metadata is persisted as JSON beside the snapshot disk using the disk checksum name. The node-wide lock file persists as a coordination artifact. Hashing reads the snapshot via direct sparse IO.

Dependencies and integration points: used by sync-agent snapshot hash RPCs and `SnapshotHashList`. Depends on `gofrs/flock`, sparse-tools direct IO and xattr-style hash info type, disk name helpers, and the process cwd for snapshot file paths.

Risks: cwd dependence means callers must run in the replica directory. `GetSnapshotChangeTime` assumes Linux `syscall.Stat_t.Ctim`. Error handling in `isSilentCorruptionAlreadyDetected` dereferences `err` in the `err != nil || info == nil` branch; if `info == nil` with nil error ever occurs, it would panic. A blocked file lock can stall a hash job indefinitely unless context cancellation is handled outside the lock call. CRC64 is fast but not cryptographically strong.

Test signals: no direct tests in this subset for hashing execution. `sync/rpc/list_test.go` covers hash job list retention, not file hashing correctness.
