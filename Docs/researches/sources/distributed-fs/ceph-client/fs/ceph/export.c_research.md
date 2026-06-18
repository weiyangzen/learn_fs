# Research: sources/distributed-fs/ceph-client/fs/ceph/export.c

## Purpose

`export.c` implements CephFS `export_operations` so CephFS can be exported through Linux exportfs/NFS. It encodes inodes into stable file handles, reconstructs dentries and parents from those handles, and resolves child names for exportfs. It handles ordinary head inodes, connected handles with parent inode numbers, snapshot inodes, snapdir dentries, disconnected aliases, encrypted directory names, and stale/unlinked inode cases.

## Important APIs, Types, and Functions

- `struct ceph_nfs_fh` is the basic handle containing only `ino`.
- `struct ceph_nfs_confh` contains `ino` and `parent_ino` for connected handles.
- `struct ceph_nfs_snapfh` contains `ino`, `snapid`, `parent_ino`, and name `hash` for snapped inodes.
- `ceph_encode_fh()` is the exportfs encode hook. It emits ordinary basic/connected handles or delegates snapped inodes to `ceph_encode_snapfh()`.
- `ceph_encode_snapfh()` encodes snapshot file handles, deriving parent inode and dentry hash from an alias when possible and falling back to self-parent for directory/snapdir handles.
- `__lookup_inode()` finds a head inode in the local inode cache or sends `CEPH_MDS_OP_LOOKUPINO`; it rejects reserved vinos and shutdown inodes.
- `ceph_lookup_inode()` wraps `__lookup_inode()` and returns `-ESTALE` for unlinked head inodes.
- `__fh_to_dentry()` reconstructs an ordinary dentry by inode number, refreshes LINK caps with `ceph_do_getattr()`, and rejects stale unlinked unopened files.
- `__snapfh_to_dentry()` reconstructs snapped or snapdir dentries from `ceph_nfs_snapfh`, optionally reconstructing the parent side of the handle.
- `ceph_fh_to_dentry()` dispatches ordinary and snapped file-handle decoding.
- `__get_parent()` sends `CEPH_MDS_OP_LOOKUPPARENT` for ordinary parent lookup.
- `ceph_get_parent()` is the exportfs parent hook and includes special handling for snapped directories and snapdir parents.
- `ceph_fh_to_parent()` decodes connected handles to parents, including snapshot handles.
- `__get_snap_name()` resolves names in snapdir contexts by returning the configured snapdir name or enumerating snapshots with `CEPH_MDS_OP_LSSNAP`.
- `ceph_get_name()` sends `CEPH_MDS_OP_LOOKUPNAME` for ordinary names and decrypts/decodes encrypted names when needed.
- `ceph_export_ops` registers encode/decode/parent/name hooks with exportfs.

## Control Flow

Encoding starts in `ceph_encode_fh()`. For ordinary inodes, it verifies the caller-provided raw handle has enough `u32` slots, stores the inode number, optionally stores the parent inode number, and returns `FILEID_INO32_GEN` or `FILEID_INO32_GEN_PARENT`. For snapped inodes, `ceph_encode_snapfh()` requires the larger snapshot handle and stores the snap id, parent inode, and directory hash. For non-snapdir snapped entries it tries to find an alias and parent outside the snapdir; if no parent can be derived, only directories can be encoded using self-parent semantics.

Decoding ordinary handles goes through `ceph_fh_to_dentry()` and `__fh_to_dentry()`. The latter performs inode lookup, forces a LINK-cap getattr to make `i_nlink` reliable, returns `-ESTALE` for unlinked unopened files, and returns `d_obtain_alias(inode)` so exportfs can work with connected or disconnected aliases.

Snapshot decoding goes through `__snapfh_to_dentry()`. It builds the target `ceph_vino` differently depending on whether exportfs wants the object or parent. If the inode is not cached, it sends LOOKUPINO with snap id, and for non-parent snapped child lookup it also supplies the saved parent inode and name hash. Snapdir replies are converted with `ceph_get_snapdir()`. If a snapped directory's head has been unlinked, it uses `d_obtain_root()` to avoid marking the snapdir dentry disconnected and causing exportfs to continue walking parents that cannot be resolved.

Parent reconstruction for ordinary entries uses `CEPH_MDS_OP_LOOKUPPARENT`; `ceph_fh_to_parent()` can fall back to the encoded `parent_ino` if LOOKUPPARENT returns `-ENOENT`. `ceph_get_parent()` has separate logic for snapped directories: non-directory snapped children are unsupported, non-snapdir snapped directories use the snapdir of the head inode as the simplified parent, and deleted heads again use `d_obtain_root()` to terminate exportfs traversal cleanly.

Name lookup uses `ceph_get_name()`. For head inodes, it sends `CEPH_MDS_OP_LOOKUPNAME` with child inode and parent vino, then copies the returned name. If the parent is encrypted, it converts the Ceph returned dname/alternate ciphertext through `ceph_fname_to_usr()`. Snapshot names use `__get_snap_name()`: the snapdir itself is named with the mount's snapdir name, while entries inside snapdir are found by repeated LSSNAP requests until the child snapid matches a returned snapshot entry.

## State and Persistence Behavior

File handles are packed binary snapshots of Ceph inode identity and, when needed, parent/snapshot context. They are not persisted by this file; NFS/exportfs consumers store and return them. The authoritative state remains in the Ceph MDS cluster.

The reconstruction paths use local inode cache when possible, but they refresh through MDS requests when cache misses or parent/name resolution require authoritative metadata. Stale handling depends on current inode/link state:

- Reserved vinos are immediately stale.
- Shutdown inodes are stale.
- Unlinked unopened ordinary files are stale after LINK-cap refresh.
- Deleted snapped directory heads use root-style dentries to prevent impossible parent walks.

## Dependencies and Integration Points

- Linux exportfs calls `ceph_export_ops`.
- MDS request operations used here are LOOKUPINO, LOOKUPPARENT, LOOKUPNAME, and LSSNAP.
- `super.h` supplies Ceph inode/vino helpers, snapshot constants, mount snapdir name, and inode cache helpers.
- `mds_client.h` supplies request creation/submission and reply parsing.
- `crypto.h` supplies encrypted name conversion through `ceph_fname_to_usr()`.
- `ceph_dentry_hash()` is implemented in `dir.c` and is required to encode snapshot handles that the MDS can later resolve.
- VFS helpers `d_obtain_alias()` and `d_obtain_root()` are central to disconnected exportfs reconstruction.

## Risks and Edge Cases

- Snapshot handles depend on parent inode and hash context for non-directory snapped entries. If the alias is unavailable at encode time, non-directory snapshot handle encoding fails.
- `FILEID_BTRFS_WITH_PARENT` is reused for snapshot handles because it fits the packed data shape; consumers must dispatch by fileid type exactly as this file does.
- Local inode cache hits may avoid an MDS round trip, but shutdown inode detection is required to avoid returning stale objects.
- Ordinary file handle decode must refresh LINK caps before trusting `i_nlink`; otherwise a concurrently unlinked file could be exported incorrectly.
- Encrypted parent names require alternate-name data from the MDS. Missing or inconsistent fscrypt context can make `get_name` fail.
- Snapshot name lookup may require paging through all snapshots with LSSNAP; large snapshot directories can make exportfs name resolution expensive.
- Parent fallback in `ceph_fh_to_parent()` handles older or racey MDS behavior but can return stale if both LOOKUPPARENT and encoded parent lookup fail.

## Test Signals

Useful tests include:

- Export ordinary CephFS files and directories over NFS, then reopen by file handle after dropping local dentries/inodes.
- Decode connected file handles after parent rename/unlink races and verify stale behavior.
- Export snapped directories and snapdir entries, including deleted head directories, and verify parent traversal terminates correctly.
- Resolve names for encrypted directories and no-encryption directories through exportfs `get_name`.
- Confirm unlinked unopened files return `-ESTALE` while still-open unlinked files can be represented as aliases when intended.
- Exercise `fh_to_parent` fallback by forcing LOOKUPPARENT misses.
