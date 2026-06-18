## sources/distributed-fs/coda/coda-src/volutil/vol-dump.cc

Purpose: `vol-dump.cc` implements server-side Coda volume dump and dump-size estimation. It serializes readonly/backup volumes to the dump format over RPC2 SMARTFTP and maintains version-vector list files for incremental dumps.

Important APIs/types/functions: RPCs are `S_VolNewDump` and `S_VolDumpEstimate`. Serialization helpers include `DumpDumpHeader`, `DumpVolumeDiskData`, `DumpVnodeDiskObject`, `DumpVnodeIndex`, `DumpVnodeDiskObject_estimate`, and `DumpVnodeIndex_estimate`. It uses `vvtable`, `ListVV`, `DumpListVVHeader`, `ValidListVVHeader`, and `getlistfilename`.

Control flow: `S_VolNewDump` initializes volutil, attaches the requested volume, rejects RW/non-replicated sources for dumping, allocates a dump buffer, determines a replicated or non-replicated uniquifier baseline, opens a `newlist`, optionally opens/validates `ancient` for incremental mode, binds back to the client dump subsystem, then writes header, volume disk data, large index, small index, and dump end. `DumpVnodeIndex` writes count/list metadata, then either emits all vnodes for full dumps or compares against the ancient VV table to emit modified/new vnodes and `D_RMVNODE` records for deletions. `S_VolDumpEstimate` walks similar state to populate level estimates.

State and persistence behavior: writes dump bytes to the client, writes a new VV list file, reads an ancient VV list file, and updates only transient volume attachment state. On dump failure it unlinks the new list. It does not mutate the dumped volume except normal attach/put behavior.

Dependencies/integration points: relies on `dumpstuff.cc`, volume/vnode/index iterators, inode open/read, directory page access, ACL externalization, RPC2 binding/side effects, VRDB reverse translation, and VV-list incremental logic. `vol-ancient.cc` promotes successful new lists.

Risks: only readonly/backup volumes can be dumped; callers must clone/backup first. Incremental correctness depends on valid ancient list files and version-vector/store-id comparisons. `DumpVnodeDiskObject_estimate` uses `VAclDiskSize` while actual dump externalizes ACL strings, so estimates can drift. `DumpVnodeIndex` decrements `nVnodes` while iterating and relies on list consistency. `D_BADINODE` records are emitted for missing file inodes, producing lossy dumps.

Test signals: full and incremental dump/restore flows, invalid ancient list fallback to full, deletion records, large and small vnodes, directory ACLs, missing/barren inode handling, RPC failures, dump estimate monotonicity across levels, and cleanup of `newlist` on failure.
