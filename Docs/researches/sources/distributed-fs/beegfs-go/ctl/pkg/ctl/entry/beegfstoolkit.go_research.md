# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/entry/beegfstoolkit.go

Purpose: ports BeeGFS toolkit path/hash helpers used to display verbose entry metadata such as chunk, dentry, and inode paths.

Important APIs/types/functions: `getFileChunkPath`; `timestampFromEntryID`; `timestampToPath`; `getMetaDirEntryPath`; `getMetaInodePath`; `getHashPath`; `getBaseHashPath`; `getHashes`.

Control flow: file chunk paths are built from original parent UID, timestamp parsed from parent entry ID, path components derived from timestamp reverse positions, original parent entry ID, and entry ID. Metadata dentry/inode paths are hash-based using fixed BeeGFS directory fanout constants and `hash32`.

State and persistence: pure computation; no filesystem access.

Dependencies and integration points: used by `entry.newVerbose` in `entry.go`. Relies on `hash32.go` to match BeeGFS storage toolkit behavior.

Risks: only supports the 2014.01 style chunk path with user/timestamp directories. Special entry IDs and malformed timestamps produce best-effort `?` plus errors. Hash constants must match server layout.

Test signals: no direct tests in this work item. Useful tests would compare outputs with known C++ BeeGFS toolkit fixtures for normal, root/lost+found, malformed, and short timestamp entry IDs.
