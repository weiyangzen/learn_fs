# sources/distributed-fs/coda/coda-src/norton/norton-dir.cc

Purpose: implements Norton directory inspection and repair commands. It can list directory entries, delete a name from a directory, and create a name pointing at an existing child vnode.

APIs and flow: `SetDirHandle` resolves a directory vnode through volume index and directory cache. `show_dir` validates large vnode class, warns if `DH_DirOK` fails, and enumerates entries with existence markers from `testVnodeExists`. `delete_name` runs an RVM transaction, calls `DH_Delete`, optionally decrements parent link count, writes back the directory inode, marks the parent version vector inconsistent, and replaces the vnode. `create_name` similarly calls `DH_Create`, updates parent link count for directory children, adjusts child parent fields, and replaces both vnodes.

State/dependencies: mutates RVM vnode and directory-page state through vol/dir/recov APIs. Risks include operator-supplied FIDs, minimal semantic validation, link count drift, and destructive mutations on live metadata; `NortonInit` prevents server co-running. Test signal is manual Norton sessions.
