<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/fid.h -->
# sources/distributed-fs/ceph-client/fs/9p/fid.h

## Purpose
`fid.h` exposes fid management helpers and cache-mode flag adjustment used by 9p VFS files.

## Important APIs, types, and functions
It declares fid lookup/add functions and defines inline `v9fs_parent_fid`, `clone_fid`, `v9fs_fid_clone`, and `v9fs_fid_add_modes`.

## Control flow
Clone helpers look up and clone protocol fids through a zero-length walk. `v9fs_fid_add_modes` marks fids direct or no-write-cache depending on session cache flags, qid version, direct I/O, sync, and open flags.

## State and persistence
The header mutates fid `mode` bits but stores no independent state.

## Dependencies and integration points
It bridges file/inode/address-space code to fid lookup and cache policy selection.

## Risks and test signals
Risks include incorrect direct-cache decisions for synthetic qid version zero, and clone lifetime mistakes. Test signals include O_DIRECT, directio mount, writeback cache, O_DSYNC, sync mount, and qid.version zero servers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/fid.h -->
