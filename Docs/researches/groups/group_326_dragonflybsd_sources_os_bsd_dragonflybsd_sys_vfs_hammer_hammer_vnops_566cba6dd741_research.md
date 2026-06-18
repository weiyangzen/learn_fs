# Group Research: group_326_dragonflybsd_sources_os_bsd_dragonflybsd_sys_vfs_hammer_hammer_vnops_566cba6dd741

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/bsd/dragonflybsd`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_vnops.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_vnops.c

HAMMER1 vnode operation implementation for regular files, directories, symlinks, device nodes, FIFOs, strategy I/O, namespace mutation, and kqueue notification.

Key responsibilities:
- Defines the HAMMER vnode operation vectors for normal vnodes, special-device vnodes, and FIFO vnodes.
- Implements `fsync` with multiple policy modes, including full flush, asynchronous relaxation, REDO/UNDO FIFO flushing for version-four filesystems, and an ignore mode.
- Implements regular-file `read` and `write` through the VM shortcut path and buffer cache, using variable HAMMER block sizes, clustering, sequential heuristics, large-I/O signal checks, atime/mtime updates, and write-size/rlimit checks.
- Generates REDO records for fast-fsync write/truncate paths and disables REDO tracking when heuristic limits are exceeded.
- Implements POSIX metadata and namespace VOPs: access, advisory locks, open/close, create, mkdir, mknod, link, symlink, remove, rmdir, rename, whiteout, getattr, setattr, readlink, readdir, lookup, and lookup-dotdot.
- Supports historical/as-of lookups and PFS access through `@@` name extensions, including special `@@PFS` symlink expansion.
- Implements strategy read/write and bmap support for file data, with direct I/O shortcuts for aligned zone-large data, indirect/double-buffered reads, sparse-hole zero-fill, truncation interlocks, and bulk in-memory record installation for writes.
- Provides `mountctl`, ioctl dispatch, and kqueue filter operations for read/write/vnode events.

Important implementation details:
- Most metadata-changing paths acquire `hmp->fs_token`, start a HAMMER transaction, modify inode or directory records, then release the token after transaction completion.
- Directory lookup and unlink use HAMMER directory name keys as chained hash ranges and merge in-memory records with on-disk records via cursor iteration.
- `hammer_dounlink()` centralizes remove/rmdir/whiteout target resolution, type validation, directory emptiness checks, directory-entry deletion, cache unlinking, and vnode delete notification.
- `rename` first removes or ignores the target, links the source inode into the target directory, updates the moved inode parent/ctime, then removes the old directory entry.
- `getattr` synthesizes snapshot-stable atime/mtime for read-only/historical inodes and reports fsids that vary by as-of TID while remaining tied to the PFS shared UUID.
- Strategy read handles gaps, frontend/backend truncation state, on-disk direct read eligibility, and post-read cache-node hints for file and parent directory traversal.
- Strategy write installs new bulk records and queues direct writes; HAMMER does not overwrite existing data blocks in-place.

Dependencies:
- Includes DragonFly VFS, namecache, buffer-cache, FIFO, kqueue, mountctl, VM, transaction, cursor, inode, blockmap, flusher, REDO, and HAMMER object APIs through `hammer.h`.
- Uses vnode helpers such as `vop_helper_read_shortcut`, `vop_helper_access`, `vop_helper_chown`, `vop_helper_chmod`, `vfsync`, `cluster_readx`, `cluster_write`, `nvextendbuf`, and `nvtruncbuf`.
- Depends on HAMMER transaction, cursor, inode, record, buffer, direct-I/O, and flusher primitives defined elsewhere in the HAMMER1 implementation.

Notable risks:
- The file has many cross-locking paths between vnode locks, `fs_token`, cursor locks, inode locks, buffer locks, and flusher activity; the explicit `EDEADLK` retry paths are critical.
- Several comments acknowledge broken or weakened atomicity around rename/unlink deadlock avoidance and truncate/backend flushing.
- REDO correctness depends on subtle interaction between write-generated records, truncate records, `HAMMER_INODE_REDO`, `HAMMER_INODE_RDIRTY`, and flusher termination records.
- Variable block sizes around the `HAMMER_XDEMARC` boundary require careful bmap, clustering, truncation, and buffer-cache sizing.
- Snapshot/as-of and PFS path syntax is embedded in normal name lookup and symlink handling, so changes to lookup parsing can affect user-visible snapshot access.
- Dynamic vnode references around inactive/reclaim and notification paths are race-prone and handled with repeated `hammer_get_vnode()` checks.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_volume.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_volume.c

HAMMER1 volume management implementation for adding, deleting, listing, formatting, freeing, and accounting non-root filesystem volumes.

Key responsibilities:
- Implements `hammer_ioc_volume_add()` for adding a new block device as a HAMMER volume.
- Implements `hammer_ioc_volume_del()` for removing a non-root volume, optionally reblocking live data off the volume first.
- Implements `hammer_ioc_volume_list()` for returning mounted volume numbers and device names to userspace.
- Formats new volume headers by copying filesystem identity, version, label, signature, root volume number, and layout parameters from the root volume.
- Initializes freemap layer1/layer2 entries for newly added volumes and frees freemap metadata for removed volumes.
- Counts total and empty big-blocks in a volume and updates root-volume filesystem statistics after volume add/remove.
- Drives full-filesystem reblock work when deleting a non-empty volume with `HAMMER_IOC_VOLUME_REBLOCK`.

Important implementation details:
- Volume add/delete operations are serialized by `hmp->volume_lock`.
- Structural freemap mutations run under `hammer_sync_lock_sh(trans)` and `hmp->blkmap_lock`.
- Added volumes are assigned the first unused volume number below `HAMMER_MAX_VOLUMES`.
- Root volume removal is forbidden, and deletion is refused if the target volume is non-empty unless reblock is requested.
- `hammer_format_freemap()` allocates layer1 blocks for the new volume, marks freemap-reserved big-blocks, marks usable big-blocks free, and marks tail-aligned space unavailable.
- `hammer_free_freemap()` first verifies that all non-freemap/non-unavailable big-blocks are empty, then clears layer2 entries and marks layer1 unavailable.
- Volume removal unloads cached buffers associated with the volume, unloads the volume, decrements volume count, and adjusts root statistics.

Dependencies:
- Uses HAMMER1 transaction, blockmap, volume, buffer, CRC, flusher, reblock, sync, and mount-stat APIs through `hammer.h`.
- Interacts with userspace ioctl payloads `hammer_ioc_volume` and `hammer_ioc_volume_list`.
- Depends on HAMMER freemap geometry macros such as `HAMMER_BLOCKMAP_LAYER1_OFFSET`, `HAMMER_BLOCKMAP_LAYER2_OFFSET`, `HAMMER_BIGBLOCK_SIZE`, and encoded raw volume offsets.

Notable risks:
- Comments note that freemap formatting/freeing uses `hammer_modify_buffer()` and can theoretically pressure or overwrite the UNDO FIFO for large devices.
- Deletion contains an explicit three-pass `hammer_flusher_sync()` workaround before unloading buffers, indicating historically fragile synchronization.
- Freemap accounting assumes non-root volumes and asserts heavily on layer state; corrupted freemap state may panic rather than degrade gracefully.
- User-visible deletion depends on exact volume device-name matching.
- Volume statistics and mount stat block counts must remain synchronized with root-volume on-disk header updates.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_volume.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/Makefile -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/Makefile

Kernel module makefile for the HAMMER2 VFS implementation.

Key responsibilities:
- Builds the `hammer2` kernel module.
- Adds the main HAMMER2 source directory plus bundled `zlib` and `xxhash` directories to `.PATH`.
- Enables `-DINVARIANTS` for the module build.
- Lists HAMMER2 VFS, vnode, inode, chain, flush, freemap, cluster, ioctl, messaging, compression, I/O, synchronization, admin, bulkfree, and strategy implementation files.
- Builds prefixed or locally namespaced compression/hash support from HAMMER2's bundled zlib and xxhash sources.
- Includes DragonFly's `bsd.kmod.mk` kernel-module rules.

Dependencies:
- Depends on the DragonFly kernel module build system.
- Depends on HAMMER2 sources in the same directory and bundled `zlib`/`xxhash` implementation files.
- Comments explain that `Z_PREFIX` and `XXH_NAMESPACE` are defined in the vendored headers directly so HAMMER2 can also be specified via `conf/files`.

Notable risks:
- Compression/hash symbol prefixing is intentionally managed in headers rather than this makefile; changing one side without the other can create kernel symbol conflicts.
- `KCFLAGS+= -DINVARIANTS` makes this module build with extra assertions enabled, which can alter behavior compared with a non-invariant production build.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2.h

Central internal HAMMER2 kernel header defining in-memory topology, cluster state, transaction state, helper-thread state, XOP request structures, device/PFS structures, flags, inline helpers, global variables, and subsystem prototypes.

Key responsibilities:
- Defines lock and spinlock shims used by HAMMER2.
- Defines core in-memory chain topology structures for representing on-media objects, including chain cores, red-black child trees, blockref state, parent pointers, data buffers, and chain flags.
- Defines the HAMMER2 I/O cache wrapper around DragonFly buffers, including hash tables, reference/dirty/in-progress flags, dedup bitmaps, and debug tracking.
- Defines HAMMER2 error-code flags and conversion helpers between HAMMER2 internal errors and kernel `errno` values.
- Defines lookup, modify, resolve, delete, insert, flush, transaction, dirty-chain, logical-write, cluster, and thread flag sets.
- Defines cluster state for multi-node PFS operation, including quorum/synchronization flags and per-cluster chain items.
- Defines in-memory inode state, including locks, vnode association, embedded cluster, ccache, advisory-lock state, dirty/delete/create/sync flags, metadata copy, and size tracking.
- Defines PFS transaction counters and flags.
- Defines helper-thread structures used for synchronization, bulkfree, and XOP workers.
- Defines all XOP request payload structures and the `union hammer2_xop` used to fan out VOP work across cluster nodes.
- Defines device-vnode, volume, device, and PFS management structures.
- Declares global vop tables, tunables/stat counters, object caches, subsystem entry points, XOP descriptors, dmsg/rmsg handlers, I/O wrappers, chain/inode/cluster APIs, freemap APIs, vnode/VFS APIs, and admin-thread APIs.
- Provides inline helpers for dedup masks, error conversion, mount-to-PFS conversion, XOP focus-data access/release, and kqueue notification.

Important implementation details:
- HAMMER2's core object model is chain-based: volumes, inodes, indirect blocks, data blocks, and freemap nodes are represented by `hammer2_chain`.
- Chain block table updates are delayed for inserts/updates but performed immediately for deletions; flush code propagates modified chains bottom-up.
- Cluster operations use temporary working clusters, quorum checks, and XOP workers to avoid dead or stalled nodes blocking the frontend.
- XOP structures can reference up to four inodes and carry per-cluster FIFOs for pipelined backend responses.
- `hammer2_dev` represents a hard block device and can be shared by multiple mounted PFSs; `hammer2_pfs` represents a per-cluster filesystem view or the super-root.

Dependencies:
- Includes DragonFly kernel headers for vnode, mount, buffer cache, locks, threads, object cache, queues, red-black trees, namecache-adjacent structures, credentials, and dmsg.
- Includes HAMMER2 public/on-disk headers `hammer2_xxhash.h`, `hammer2_disk.h`, `hammer2_mount.h`, and `hammer2_ioctl.h`.
- Prototype declarations span nearly every HAMMER2 implementation file: subr, inode, chain, flush, ioctl, I/O, admin, XOP, synchronization, message, VFS, freemap, cluster, iocom, strategy, and ondisk.

Notable risks:
- This is a high-blast-radius internal ABI header; structural or flag changes affect most HAMMER2 compilation units.
- Concurrency semantics are encoded in comments, flags, and helper macros across chains, inodes, clusters, XOPs, and threads; changing them requires whole-filesystem reasoning.
- The cluster/quorum model permits partial availability and asynchronous backend completion, so error flag interpretation must remain consistent.
- `HAMMER2_INUMHASH_MASK` is defined from `HAMMER2_IOHASH_SIZE - 1`, which currently matches `HAMMER2_INUMHASH_SIZE` but is a latent coupling hazard if sizes diverge.
- Inline data access for XOP focus chains must be paired correctly with `hammer2_xop_pdata()` when `focus_dio` is referenced.
- Many subsystem interfaces accept locked structures or return locked/held references by convention, so misuse can cause leaks, deadlocks, or stale media-data access.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_admin.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_admin.c

HAMMER2 helper-thread and XOP administration implementation, including worker thread signaling, lifecycle management, XOP allocation, dispatch, collection, retirement, and the primary XOP worker loop.

Key responsibilities:
- Defines storage XOP descriptors for HAMMER2 frontend/backend operations, including inode cluster, readdir, resolve, unlink, rename, scans, lookup, delete, inode create/destroy/connect/flush/sync, strategy read/write, and bmap.
- Implements atomic helper-thread signaling, signal-with-clear, wait-for-flags, wait-for-any-with-timeout, and wait-for-clear operations.
- Creates, freezes, unfreezes, remasters, and deletes HAMMER2 helper threads.
- Allocates and initializes XOP requests from `cache_xops`, including modify transaction IDs and inode references.
- Attaches operation names and up to three additional inode references to XOPs.
- Creates and cleans up per-PFS XOP worker groups.
- Starts XOPs across cluster elements, selecting worker groups differently for strategy I/O and non-strategy operations.
- Retires XOPs from frontend and backend participants, caches returned chains in the inode ccache, drains FIFOs, drops inode/name references, and returns XOPs to the object cache.
- Feeds backend chain results through per-cluster FIFOs to the frontend collector.
- Collects frontend responses, advances cluster elements by key, applies cluster/quorum validation, waits for incomplete results, and reports normal end-of-scan or errors.
- Runs the primary XOP worker thread loop, handling stop/freeze/unfreeze/remaster states and executing queued XOP storage functions.

Important implementation details:
- Thread flags are manipulated with compare-and-set loops and `HAMMER2_THREAD_WAITING` interlocks around `tsleep`.
- XOP worker creation allocates `hammer2_xop_nthreads` groups, each with threads for every chain in the mounted PFS root cluster.
- Strategy XOPs are routed to a worker partition separate from normal XOPs to prevent buffer-cache strategy work from deadlocking behind metadata operations.
- Non-strategy XOPs are routed by inode hash, or spread over CPU-local groups depending on cluster size and `hammer2_spread_workers`.
- `hammer2_xop_next()` uses a small per-thread dependency hash of up to four inodes per XOP to avoid running dependent XOPs concurrently on the same cluster index.
- Backend feed uses bounded per-node FIFOs and stalls when full until the frontend drains entries or detaches.
- Frontend collect skips keys that cannot satisfy quorum and advances `collect_key`, returning `HAMMER2_ERROR_ENOENT` for normal scan exhaustion.
- The worker loop can drop stale queued XOPs if the frontend is no longer active.

Dependencies:
- Includes `hammer2.h`, using HAMMER2 thread, PFS, inode, chain, XOP, cluster, FIFO, object-cache, transaction, and spinlock definitions.
- Calls storage XOP functions declared in `hammer2.h` and implemented primarily in `hammer2_xops.c` and strategy/inode/flush modules.
- Uses DragonFly kernel primitives including `lwkt_create`, `tsleep`, `wakeup`, atomics, CPU fences, TAILQ operations, object caches, and per-CPU identifiers.

Notable risks:
- Comments explicitly warn that thread structures and XOPs can disappear immediately after successful atomic state transitions; post-signal dereferences must remain tightly controlled.
- XOP retirement is shared by frontend and backend paths and can free the object; any caller assumptions after queueing or retire are dangerous.
- Worker selection and dependency hashing are correctness-sensitive for modifying clustered operations; the file notes rename as a problematic multi-inode case.
- FIFO flow control relies on atomic run-mask flags and wakeups; missed wakeups or incorrect mask accounting can stall frontend/backend communication.
- `hammer2_xop_helper_cleanup()` iterates `pfs_nmasters`, while creation uses `iroot->cluster.nchains`; correctness depends on those bounds matching active worker slots.
- Timeout waits map `ETIMEDOUT` to HAMMER2 internal timeout errors, but many waits poll for long intervals, so teardown latency depends on signaling discipline.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_admin.c -->