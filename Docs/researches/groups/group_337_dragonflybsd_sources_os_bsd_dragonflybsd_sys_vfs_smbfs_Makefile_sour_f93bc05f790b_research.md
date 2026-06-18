# Group Research: group_337_dragonflybsd_sources_os_bsd_dragonflybsd_sys_vfs_smbfs_Makefile_sour_f93bc05f790b

Scope checked against `Docs/research_subset_a.md`: all files are under the included `sources/os/bsd/dragonflybsd` source tree. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/smbfs/Makefile -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/smbfs/Makefile

This Makefile builds the DragonFlyBSD `smbfs` kernel module. It pulls in SMB network protocol support from `netproto/smb`, crypto DES code, kernel helpers, and libkern MD4 support.

The module sources include the net SMB connection/device/request/crypto/iod files plus the SMBFS VFS layer: `smbfs_vfsops.c`, `smbfs_node.c`, `smbfs_io.c`, `smbfs_vnops.c`, `smbfs_subr.c`, and `smbfs_smb.c`. DES source files are added explicitly for authentication support.

It defines generated option headers when not building inside a kernel build directory: `opt_inet.h` is generated according to `SMB_INET`, and `opt_netsmb.h` always defines `NETSMB`. The module is then included through `bsd.kmod.mk`.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/smbfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/smbfs/smbfs.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/smbfs/smbfs.h

This is the primary SMBFS mount-interface header. It defines the SMBFS VFS type/version constants, mount flags, max path component count, and the userspace/kernel mount argument structure `struct smbfs_args`.

`struct smbfs_args` carries the mount protocol version, netsmb device handle, mount flags, mount/root paths, uid/gid ownership mapping, file and directory modes, and case-conversion option. These fields drive both VFS presentation and SMB name conversion behavior.

Under `_KERNEL`, the file defines `struct smbmount`, the per-mount control block. It links the DragonFly mount to the SMB share, root smbnode, owner/mount credentials, case options, vnode-name lookup stack, and smbnode hash table protected by `sm_hashlock`. It also exposes conversion macros such as `VFSTOSMBFS`, `VTOSMBFS`, and `VTOVFS`.

The exported prototypes connect this header to I/O and vnode code: `smbfs_ioctl`, `smbfs_doio`, and `smbfs_vinvalbuf`.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/smbfs/smbfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/smbfs/smbfs_io.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/smbfs/smbfs_io.c

This file implements SMBFS data and directory I/O, including regular read/write paths, buffer-cache strategy I/O, VM pager getpages/putpages, and vnode buffer invalidation.

Directory reads are handled by `smbfs_readvdir`. It synthesizes `.` and `..`, maintains a per-node SMB find context in `n_dirseq`, reopens searches when the requested offset changes, advances through server search results with `smbfs_findnext`, and optionally does fast vnode prepopulation via `smbfs_nget`.

Regular reads in `smbfs_readvnode` validate vnode type and offset, invalidate cached buffers when remote mtime changes, then call `smb_read`. Writes in `smbfs_writevnode` handle append and sync cases, enforce `RLIMIT_FSIZE`, call `smb_write`, and update the vnode pager size when the file grows.

`smbfs_doio` translates buffer-cache reads/writes into single-segment `uio` SMB reads or writes. Read shortfalls are zero-filled. Writes clip dirty ranges to the known file size and preserve dirty/interrupted buffers for retry in some error paths.

The VM pager paths `smbfs_getpages` and `smbfs_putpages` map pages through a temporary pbuf KVA, build a `uio`, and issue SMB reads/writes. Because SMBFS closes FIDs on vnode close, these paths reopen the remote file when `n_opencount` is zero, then close it afterward. The comments call out race risks around concurrent opens.

`smbfs_vinvalbuf` serializes buffer invalidation with `NFLUSHINPROG`/`NFLUSHWANT`, retries `vinvalbuf`, supports interruptible waits, and clears `NMODIFIED` after successful invalidation.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/smbfs/smbfs_io.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/smbfs/smbfs_node.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/smbfs/smbfs_node.c

This file manages SMBFS vnode-private nodes, name storage, vnode lookup hashing, reclaim/inactive handling, and attribute caching.

It defines the FNV-style `smbfs_hash` used for name hashing and the per-mount vnode hash table lookup. `smbfs_node_alloc` is the central allocator/lookup routine: it handles special `..` lookup, rejects `.`, searches the hash table for an existing `(parent, name)` node, safely retries after `vget`, and creates a new vnode/smbnode pair when attributes are supplied.

New nodes receive type from SMB DOS attributes, a copied name, pseudo inode, parent linkage, optional parent vnode reference, and are inserted into the per-mount hash table under `sm_hashlock`. `smbfs_nget` wraps this with attribute-cache insertion.

Reclaim removes nodes from the hash, clears the root pointer when needed, frees names and node memory, and releases parent references. It also sets `sm_didrele` so unmount can retry `vflush` when parent references were dropped.

Inactive closes any still-open SMB file handle, invalidates buffers, uses cached credentials, and releases them. Attribute-cache helpers store size, mtime, DOS attributes, and attr age; cached attributes expire after roughly two seconds. `smbfs_attr_cacherename` rehashes a node under a new name after successful remote rename.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/smbfs/smbfs_node.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/smbfs/smbfs_node.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/smbfs/smbfs_node.h

This header defines the SMBFS vnode-private `struct smbnode` and node-level flags. Each node stores parent/vnode/mount pointers, attribute cache data, size, inode, DOS attributes, open count, cached open credential, SMB FID, granted access mode, name, directory search context, last directory offset, record-lock state, and hash linkage.

Important flags include flush serialization bits, `NMODIFIED`, and `NREFPARENT`, which records that the node holds a parent vnode reference. `SMBFS_ROOT_INO` is set to 2.

The header provides conversion macros `VTOSMB` and `SMBTOV` and prototypes for node lifecycle, VM pager hooks, regular read/write helpers, attribute cache helpers, and the name hash function.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/smbfs/smbfs_node.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/smbfs/smbfs_smb.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/smbfs/smbfs_smb.c

This file implements SMB protocol operations used by the SMBFS vnode and VFS layers. It constructs SMB_COM and TRANS2 requests, parses replies, maps SMB metadata into `smbfattr`, and provides directory enumeration across dialect variants.

It generates pseudo inode numbers with parent inode plus `smbfs_hash`, with optional MD5 support compiled out unless `USE_MD5_HASH` is enabled. Locking is implemented via `SMB_COM_LOCKING_ANDX` for LANMAN1+ dialects.

Filesystem statistics are fetched through either TRANS2 `QUERY_FS_INFORMATION` (`smbfs_smb_statfs2`) or legacy `QUERY_INFORMATION_DISK` (`smbfs_smb_statfs`). File size, path attributes, handle timestamps, NT basic info, opens, closes, creates, deletes, renames, moves, mkdir, and rmdir are each represented by dedicated helpers.

Directory search has two implementations. Older dialects use `SMB_COM_SEARCH` with fixed 8.3-style entries and search keys. LANMAN2/NT dialects use TRANS2 `FIND_FIRST2`/`FIND_NEXT2`, support long names, resume names, server search IDs, and NT time/attribute formats. `smbfs_findopen`, `smbfs_findnext`, and `smbfs_findclose` abstract those dialect differences.

`smbfs_smb_lookup` is built on the directory search machinery. It has explicit handling for root and dot lookups, weak handling for `..`, and returns attributes plus pseudo inode values. Name conversion to local encoding is performed after directory entries are read.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/smbfs/smbfs_smb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/smbfs/smbfs_subr.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/smbfs/smbfs_subr.c

This file contains SMBFS support routines for time conversion, full-path construction, and filename conversion.

The time code converts among Unix `timespec`, SMB server seconds, NT 100ns-since-1601 timestamps, and DOS date/time fields. DOS conversion logic is inherited from msdosfs-style routines and caches the last computed date/time to avoid repeated full calendar conversion.

`smbfs_fullpath` serializes an SMB path into an mbchain by walking parent links through `smb_fphelp`, adding backslash separators, applying uppercase conversion for old dialects, and appending an optional final component. The helper uses the mount’s `sm_npstack` as a temporary parent stack and enforces `SMBFS_MAXPATHCOMP`.

`smbfs_fname_tolocal` applies the VC’s local iconv conversion when available. Case conversion hooks are present but commented out.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/smbfs/smbfs_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/smbfs/smbfs_subr.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/smbfs/smbfs_subr.h

This header declares SMBFS utility types, directory-search state, debug macros, lock command constants, and the SMB wire helper API.

`struct smbfattr` is the filesystem-neutral attribute structure populated from SMB replies: DOS attributes, size, access/change/modify times, and pseudo inode. `struct smbfs_fctx` tracks findfirst/findnext/findclose operations, including flags, current result attributes/name, wildcard, directory node, SMB credential, request state, remaining entries, search key, SMB search ID, info level, and resume-name data.

The function declarations cover byte-range locks, statfs variants, file-size changes, path/handle attribute updates, opens/closes, create/delete/rename/move/mkdir/rmdir, directory enumeration, full path construction, filename conversion, and all time conversion helpers.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/smbfs/smbfs_subr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/smbfs/smbfs_vfsops.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/smbfs/smbfs_vfsops.c

This file registers the SMBFS VFS operations and implements mount, unmount, root, statfs, sync, init, and uninit.

Mount validates `NETSMB`, copies `smbfs_args`, checks the mount ABI version, resolves the userspace SMB device handle into an SMB share, allocates `struct smbmount`, initializes the per-mount vnode hash, stores credentials and mode/case settings, formats `f_mntfromname` as an SMB UNC-like source, installs vnode ops, and obtains the root vnode.

Unmount repeatedly calls `vflush` because SMBFS vnodes can hold parent references and may need more than one pass. It then releases the SMB share, credential, hash table, lock, and mount structure.

`root` creates or references the root smbnode by synthesizing root attributes through `smbfs_smb_lookup(NULL, NULL, ...)` and naming the root node `"TheRooT"`. `statfs` chooses TRANS2 or legacy SMB statfs based on dialect and fills VFS stat fields. `sync` walks dirty vnodes and invokes `VOP_FSYNC` except for locked, clean, or lazy-sync cases.

The file also declares sysctls for SMBFS version/debug level, module dependencies on `netsmb`, `libiconv`, and `libmchain`, and initializes the pbuf free count.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/smbfs/smbfs_vfsops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/smbfs/smbfs_vnops.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/smbfs/smbfs_vnops.c

This file defines the SMBFS vnode operation vector and implements user-visible file operations on top of SMB protocol helpers.

Open validates type, handles directory open counts locally, validates cached mtimes, invalidates buffers on remote changes, opens remote files with read/write or read-only SMB access, stores cached credentials, and increments `n_opencount`. Close decrements open counts, closes directory search contexts, flushes buffers, closes remote FIDs, releases cached credentials, and invalidates attributes.

Attribute handling uses the short-lived cache from `smbfs_node.c`; cache misses call `smbfs_smb_lookup`. `setattr` supports file truncation through SMB writes, timestamp updates through the best available dialect-specific command, and rejects unsupported flags or read-only changes. Ownership and mode are mostly mount-option projections rather than remote SMB metadata.

Read, write, and readdir delegate to `smbfs_readvnode` and `smbfs_writevnode`. Create, remove, rename, mkdir, and rmdir use SMB wire helpers and update local vnode/name caches where possible. Hard links, symlinks, and mknod are unsupported.

Lookup performs path-component validation, read-only checks for mutating operations, access checks, remote lookup, and vnode allocation via `smbfs_nget`. It contains explicit logic for create/delete/rename lookup semantics and lock-parent behavior.

Other operations include a no-op fsync, logical bmap, synchronous-only strategy pass-through to `smbfs_doio`, unsupported ioctl, a `dosattr` extended attribute view, pathconf, vnode print, and advisory locking through local `lf_advlock` plus SMB byte-range locks.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/smbfs/smbfs_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/tmpfs/Makefile -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/tmpfs/Makefile

This Makefile builds the DragonFlyBSD `tmpfs` kernel module. It includes the four implementation files: `tmpfs_vnops.c`, `tmpfs_subr.c`, `tmpfs_fifoops.c`, and `tmpfs_vfsops.c`.

It declares no manual page with `NOMAN=` and delegates the actual module build rules to `bsd.kmod.mk`.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/tmpfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/tmpfs/tmpfs.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/tmpfs/tmpfs.h

This is the main TMPFS internal header. It defines directory entries, directory RB trees, node structures, mount structures, file handles, locking macros, conversion helpers, and support-function prototypes.

Directories are represented by `struct tmpfs_dirent` entries stored in two RB trees: one ordered by name and one ordered by cookie. TMPFS does not store physical `.` or `..` entries; readdir synthesizes them. Cookies are derived from dirent addresses and masked to positive 64-bit offsets.

`struct tmpfs_node` holds common vnode attributes, timestamps, flags, link count, vnode association, interlock, vnode state, and type-specific data. Type-specific storage includes device IDs, directory parent/tree state, symlink target, regular-file backing VM object/accounting, and FIFO hooks.

`struct tmpfs_mount` stores mount limits and counters: max pages, used pages, root node, max/in-use nodes, max file size, used-node list, per-mount malloc zones, inode counter, export data, and mount references. The mount token macros use the DragonFly mount token.

The header exposes allocation, directory, vnode, resize, attribute, timestamp, truncate, and rename-lock ordering helpers implemented by `tmpfs_subr.c` and used by vnode/VFS ops.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/tmpfs/tmpfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/tmpfs/tmpfs_fifoops.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/tmpfs/tmpfs_fifoops.c

This file customizes vnode operations for FIFOs stored in TMPFS while delegating core FIFO behavior to `fifo_vnode_vops`.

`tmpfs_fifo_kqfilter` marks the TMPFS node as accessed for read filters or modified for write filters, then forwards to the FIFO kqfilter operation. `tmpfs_fifo_close` marks access, updates timestamps through `tmpfs_update`, then forwards to FIFO close.

The exported `tmpfs_fifo_vops` uses `fifo_vnoperate` as default and overrides close, reclaim, access, getattr, setattr, and kqfilter with TMPFS-aware operations.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/tmpfs/tmpfs_fifoops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/tmpfs/tmpfs_mount.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/tmpfs/tmpfs_mount.h

This header defines the userspace-to-kernel mount argument ABI for TMPFS.

`TMPFS_ARGS_VERSION` is version 2. `struct tmpfs_mount_info` carries requested node limit, filesystem size limit, maximum file size, and root uid/gid/mode. The `MNT_*` flag constants identify which mount parameters were supplied: gid, uid, mode, inodes, size, and max file size.

The kernel VFS mount implementation consumes this structure in `tmpfs_vfsops.c`.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/tmpfs/tmpfs_mount.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/tmpfs/tmpfs_subr.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/tmpfs/tmpfs_subr.c

This file implements TMPFS support routines for node allocation/free, directory entries, vnode allocation, file creation, directory indexing, resizing, attribute changes, timestamps, truncation, inode assignment, RB-tree comparison, and rename lock ordering.

`tmpfs_alloc_node` enforces node limits, allocates a per-mount tmpfs node, initializes common attributes and timestamps, assigns an inode, and initializes type-specific storage. Regular files receive a swap-pager VM object with `OBJ_NOPAGEIN`; symlinks copy their target; directories initialize name and cookie RB trees.

`tmpfs_free_node` removes the node from the used list, releases type-specific resources, deallocates VM objects or symlink targets, clears root references, updates page accounting, destroys locks, and frees the node object. Directory entries are separately allocated/freed by `tmpfs_alloc_dirent` and `tmpfs_free_dirent`, which update target link counts.

`tmpfs_alloc_vp` ensures one active vnode per node. It handles races against existing vnodes, avoids deadlocks when called while holding a directory node lock, initializes vnode type and VMIO/KVABIO state for regular files, assigns FIFO ops for FIFOs, and links node/vnode bidirectionally.

`tmpfs_alloc_file` combines node allocation, dirent allocation, vnode allocation, and directory attachment for create/mkdir/mknod/symlink paths. Directory attachment/detachment maintains both RB trees, parent pointers, link counts, directory sizes, and timestamp status flags.

Directory helpers synthesize `.`/`..`, look up entries by name or cookie, and emit dirents with DragonFly `vop_write_dirent`. `tmpfs_reg_resize` manages file growth/truncation, per-mount page accounting, vnode buffer extension/truncation, backing aobj size, swap free-space cleanup, and small-file block-size growth up to `TMPFS_BLKSIZE`.

Attribute helpers implement chflags, chmod, chown, chsize, chtimes, timestamp flushing, and truncate semantics. `tmpfs_lock4`/`tmpfs_unlock4` impose a deterministic lock order for rename across source directory, target directory, source node, and optional target node.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/tmpfs/tmpfs_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/tmpfs/tmpfs_vfsops.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/tmpfs/tmpfs_vfsops.c

This file implements TMPFS VFS operations: mount, unmount, root lookup, file-handle conversion, export checks, and statfs.

Mount parses optional `tmpfs_mount_info`, applies root defaults and non-root restrictions, computes page/node/file-size limits from requested size, swap size, and physical memory, allocates the mount structure and per-mount malloc zones, creates the root directory node, marks root `SF_NOCACHE`, initializes mount flags, installs normal and FIFO vnode ops, fills mount stat names, and populates initial statfs data.

Unmount takes the mount token, optionally enables forced close, truncates regular-file nodes before vnode flushing so data can be discarded, calls `vflush`, removes all directory entries, drops the root link, frees every remaining node, destroys per-mount allocation zones, checks page/node counters, and frees the mount structure.

`tmpfs_root` returns a vnode for the root node through `tmpfs_alloc_vp`. `tmpfs_fhtovp` scans used nodes for a matching inode/generation file handle and returns a vnode. `tmpfs_vptofh` writes the tmpfs file handle. `tmpfs_checkexp` integrates with DragonFly export lookup.

`tmpfs_statfs` reports page-sized blocks, free/used page counts, free node counts, and root owner. The file registers TMPFS as `VFCF_MPSAFE`.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/tmpfs/tmpfs_vfsops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/tmpfs/tmpfs_vnops.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/tmpfs/tmpfs_vnops.c

This file implements the normal TMPFS vnode operation vector. It covers namecache-aware lookup/create/remove/rename operations, regular I/O, VM/swap backing behavior, attributes, kqueue filters, reclaim/inactive handling, pathconf, and advisory locking.

Lookup uses DragonFly namecache operations: `tmpfs_nresolve` searches the directory RB tree and allocates a vnode for hits, while `tmpfs_nlookupdotdot` returns the parent vnode. Create, mknod, mkdir, and symlink all call `tmpfs_alloc_file`, then update the namecache and emit kqueue notifications.

Open restores any pages previously moved into the node’s backing aobj. Close updates timestamps. Access enforces read-only mount and immutable rules before calling helper permission logic. Getattr/getattr_lite project tmpfs node fields into VFS attribute structures. Setattr sequences flag, size, ownership, mode, and time updates, restores saved pages before resize, updates timestamps, and emits knotes.

Read first tries `vop_helper_read_shortcut`, then restores saved pages if needed and reads through KVABIO buffer-cache blocks, optionally using clustered reads. Write enforces file-size limits and `RLIMIT_FSIZE`, supports append, resizes as needed, fills gaps safely through `bread_kvabio`, writes through buffer-cache paths chosen by memory pressure and `tmpfs_bufcache_mode`, handles UIO_NOCOPY/pageout cases specially, updates SUID/SGID, timestamps, size, and knotes.

`tmpfs_strategy` sends regular-file pageout I/O to the swap pager through the node’s aobj. If there is no swap, write pages are simply marked as needing commit. Completion clears or restores commit state without propagating swap errors to the buffer. `tmpfs_bmap` presents logical contiguity for clustering.

Remove, link, rename, rmdir, and symlink maintain directory RB trees, link counts, parent pointers, deleted-directory behavior, namecache state, and vnode notifications. Rename uses `tmpfs_lock4` to avoid directory lock-order reversals and handles target replacement rules for files and directories.

Readdir synthesizes `.` and `..`, uses cookie-ordered RB traversal for real entries, returns optional NFS cookies, and marks access. Readlink copies the stored target string. Inactive recycles deleted nodes and moves live regular-file pages from vnode object into the node backing aobj so vnode reclamation does not discard cached tmpfs data. Reclaim clears vnode/node associations and frees nodes whose link count is zero.

The file also supports mountctl export updates, debug printing, POSIX pathconf values, advisory locks through `lf_advlock`, and kqueue filters for read/write/vnode events. The exported `tmpfs_vnode_vops` wires these operations into DragonFly’s VFS.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/tmpfs/tmpfs_vnops.c -->