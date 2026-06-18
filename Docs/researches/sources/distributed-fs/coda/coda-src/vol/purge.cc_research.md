# sources/distributed-fs/coda/coda-src/vol/purge.cc

Purpose: provides `VPurgeVolume`, the high-level path to remove a volume from file-server memory and recoverable storage.

Important API: `VPurgeVolume(Volume *vp)` asserts that `DeleteVolume(vp)` succeeds, deletes the volume from the in-memory hash table, marks the volume shutting down, and calls `VPutVolume` so last-reference cleanup frees it.

Control flow/state: this intentionally bypasses `VDetachVolume` because the historical comment says FSYNC behavior was not understood. It first removes persistent state via recovery deletion, then removes VM traces and lets reference-counted volume cleanup complete.

Dependencies/integration: integrates `volume.h`, `recov.h`, `vutil.h`, vnode indexes, partition/inode code, and the recoverable volume deletion path. Risks include the comment "NEED TO REVIEW THIS CODE", hard assertion on delete failure, potential double deletion from hash because `DeleteVolume` itself hashes/frees in current code, and lack of FSYNC notification. Test signals: purge a volume while offline, purge failure injection, hash table state after purge, absence of leaked vnodes/inodes, and utility/file-server coordination regressions.
