# sources/distributed-fs/openafs/src/volser/vol_split.c

## Purpose
Implements namei-only volume splitting: moving a subtree from an existing volume into a newly created volume, replacing the original subtree with a mountpoint.

## Important APIs And Functions
When `AFS_NAMEI_ENV` and not Windows, public `split_volume` orchestrates the operation. Helpers include `ExtractVnodes` to collect vnode/parent metadata and locate the split root, `FindVnodes` to mark subtree files/directories, `copyDir` to copy directory inode contents, `copyVnodes` to hardlink/copy selected vnode data into the new volume and rewrite parents, `findName` to inverse-lookup the split directory name, `createMountpoint` to create a symlink vnode and update the parent directory, and `deleteVnodes` to remove transferred data from the old volume.

## Control Flow
The split flow extracts large vnodes, finds the split directory and parent name, marks all descendant directories, extracts small vnodes, marks descendant files, marks the new volume as `DESTROY_ME`/out of service, copies file and directory vnodes into the new volume, copies the split directory into the new root vnode, writes new volume metadata, creates a mountpoint in the old parent directory, deletes moved vnodes from the old volume, adjusts disk/file counts, updates both volume headers, and sends progress over RX.

## State And Persistence
This code mutates vnode index files, creates namei hard links or OSD objects, copies directory data, rewrites parent vnode ids for new-root children, creates a symlink mountpoint inode, updates AFS directory entries, decrements old inode references, and persists `V_diskused`, `V_filecount`, quota, uniquifier, service, and destroy flags via `VUpdateVolume`.

## Dependencies And Integration
Depends on namei inode layout masks, vnode classes, inode handles, `afs_dir` operations, `physio.c` directory handles, volserver RPC status output, and optional RXOSD split/remove hooks.

## Risks And Test Signals
This is high-risk destructive code. Failure after copying but before mountpoint/deletion can leave duplicate or inconsistent trees; failure during deletion can leave old data; quota/count updates are manual; many error paths return without freeing lists or fully rolling back. Test signals include split at root child, missing parent/name failures, file-only and deep directory subtrees, hardlink creation failure injection, mountpoint creation verification, post-split salvage/fsck, quota/filecount checks, and RXOSD-enabled builds.
