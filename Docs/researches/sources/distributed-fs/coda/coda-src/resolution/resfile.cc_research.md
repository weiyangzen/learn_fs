<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/resfile.cc -->
# sources/distributed-fs/coda/coda-src/resolution/resfile.cc

Purpose: implements replicated regular-file resolution and participant RPCs for fetching and forcing file contents.

Important APIs/control flow: `FileResolve` handles coordinator logic: record stats, mask unavailable hosts, resolve weak equality via `WEResPhase1`, detect inconsistent VVs via `IncVVGroup`, fetch the dominant file into a temp file, multicast `ForceFile` to submissive replicas, and mark all replicas inconsistent on failure. `RS_FetchFile` participant-side opens the file inode or a temporary empty inode and transfers it by SMARTFTP with `ResStatus`. `RS_ForceFile` validates coordinator lock ownership and version-vector dominance, receives replacement data, swaps inode/length/status metadata, updates volume/vnode VVs, and cleans old/new inodes around an RVM transaction. `RS_COP2` delegates to `InternalCOP2`.

State/persistence: changes file data inodes, disk usage, vnode metadata, callbacks, version vectors, and stats. Temporary files/inodes buffer transfers.

Dependencies/integration: uses RPC2 side effects, inodeops, VRDB, volume/vnode locking, `rescoord` weak equality, `resforce` runt statistics, and `resstats`.

Risks/test signals: `RS_FetchFile` tests `fd != 1` instead of `fd != -1` before close, which can leak fd 1 edge cases and close invalid fds. Force transfer length is checked by block count, not exact byte count. Test dominant/submissive VV sets, weak equality, missing inode empty transfer, coordinator lock mismatch, side-effect failure rollback, and inode cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/resfile.cc -->
