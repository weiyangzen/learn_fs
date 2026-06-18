# sources/distributed-fs/ceph/src/mds/events/EMetaBlob.h

Purpose: Defines the main metadata payload container embedded in MDS journal events to describe inode, dentry, dirfrag, table, inode-allocation, truncate, destroy, and idempotency updates.

Important APIs/types: `fullbit` records a primary dentry and inode snapshot with dirty flags, xattrs, dirfrag tree, symlink, snap realm buffer, and old inodes. `remotebit` records a remote dentry link. `nullbit` records a null dentry. `dirlump` groups all dentry records and fnode state for one dirfrag with complete/dirty/new/importing/dirty-dft flags. Top-level `EMetaBlob` tracks roots, ordered lumps, table tids, opened inode, renamed dir fragments, inode/session allocation versions, truncate starts/finishes, destroyed inodes, client request/flush idempotency records, and touched inodes.

Control flow: Mutation code calls helpers like `add_dir_context`, `add_dir`, `add_primary_dentry`, `add_remote_dentry`, `add_null_dentry`, `add_root`, `set_ino_alloc`, `add_table_transaction`, and truncate/destroy/idempotency helpers while building a journal event. Replay decodes the blob and applies root/lump/table/allocation/truncate/destroy/client-request side effects to `MDSRank` and cache state.

State and persistence behavior: `EMetaBlob` is a compact persistent representation of projected metadata. `dirlump` lazily encodes/decodes dentry vectors in `dnbl`. `fullbit` stores a complete inode image rather than a delta, while flags indicate how replay should mark dirty parent/pool/snapflush/ephemeral-random state. Inode allocation fields coordinate inotable and sessionmap versions.

Dependencies and integration points: Uses `CInode`, `CDir`, `CDentry`, `LogSegment`, `LogSegmentRef`, `interval_set`, snap realm encoding, and `MDPeerUpdate`. It is embedded by `EUpdate`, `EOpen`, `EExport`, `EImportStart`, `EFragment`, `ESubtreeMap`, and `EPeerUpdate`.

Risks: This is replay-critical. The header warns that modified inode versions must be updated manually. Encoding version changes require updating constructors and encode paths. Incomplete dir context, missing dirty-parent flags, or wrong inotable/sessionmap versions can cause replay divergence or prevent log trimming.

Test signals: Dencoder coverage for every nested type, replay of primary/remote/null dentries, roots, imports, table tids, inode allocation/preallocation, truncate start/finish rewrite, destroyed inodes, client idempotency, and old/new feature encodings.
