# sources/distributed-fs/ceph-client/fs/nfs/nfs42.h

## Purpose
`nfs42.h` declares NFSv4.2 client procedure entry points and small helpers for newer protocol features: server-side allocation/deallocation, copy/clone, seek, layout stats/errors, copy notify, and extended attributes.

## Important APIs, Types, And Functions
When `CONFIG_NFS_V4_2` is enabled, declarations include `nfs42_proc_allocate()`, `nfs42_proc_copy()`, `nfs42_proc_deallocate()`, `nfs42_proc_zero_range()`, `nfs42_proc_llseek()`, `nfs42_proc_layoutstats_generic()`, `nfs42_proc_clone()`, `nfs42_proc_layouterror()`, `nfs42_proc_copy_notify()`, `nfs42_proc_getxattr()`, `nfs42_proc_setxattr()`, `nfs42_proc_listxattrs()`, and `nfs42_proc_removexattr()`. `nfs42_files_from_same_server()` compares NFSv4 server owner major IDs for copy/clone eligibility. `nfs42_listxattr_xdrsize()` estimates the maximum XDR buffer needed for a user xattr list buffer.

## Control Flow And Integration Points
This header is consumed by NFSv4 file, xattr, pNFS, and copy offload code. The file-same-server helper derives `nfs_client` objects from input and output file inodes and calls `nfs4_check_serverowner_major_id()`. The listxattr sizing helper assumes worst-case one-character user xattr names, includes null terminators and EOF word, and rounds to four-byte alignment.

## State And Persistence Behavior
The header defines no state. Its functions operate on files, inodes, pNFS layout segments, stateids, and NFS servers owned elsewhere. Constants `PNFS_LAYOUTSTATS_MAXDEV` and `READ_PLUS_SCRATCH_SIZE` guide bounded compound and scratch-buffer sizing.

## Dependencies
Dependencies include Linux xattr definitions, NFSv4 server owner identity, pNFS layout structures, NFSv4.2 operation implementations, and conditional compilation under `CONFIG_NFS_V4_2`.

## Risks And Edge Cases
The layoutstats maximum is explicitly marked as a FIXME, so scaling to more devices per compound is a known limitation. `nfs42_files_from_same_server()` checks owner identity, not path or export identity, and must be used in contexts where that is the right criterion. `nfs42_listxattr_xdrsize()` is a sizing upper bound; incorrect assumptions could under-allocate listxattr XDR buffers.

## Test Signals
Build with and without NFSv4.2, test fallocate/punch-zero/copy/clone/llseek xfstests, pNFS layoutstats and layouterror paths, xattr get/set/list/remove, same-server and cross-server copy decisions, and listxattr buffers with many short names.
