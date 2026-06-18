# Group Research: group_1676_reactos_sources_windows_reactos_drivers_filesystems_ext2_inc_linux__72f9973db411

Scope checked against `Docs/research_subset_a.md`: `sources/windows/reactos` is included in subset A. Every listed file was read completely; files reported as empty are zero-byte files.

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/module.h -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/module.h

This is the central Linux-kernel compatibility header for the ReactOS/Ext2Fsd ext2 driver. Despite the name, it is not just module metadata: it supplies byte-order helpers, Linux-style error-pointer macros, module/init/export no-ops, spinlocks, wait queues, timers, page and buffer-head structures, NLS declarations, jiffies, pool allocation wrappers, slab-cache declarations, block I/O constants, and time/division helpers.

Key definitions and behavior:
- Includes `linux/types.h`, `linux/errno.h`, `linux/rbtree.h`, `linux/fs.h`, and `linux/log2.h`.
- Provides `offsetof`, `container_of`, endian conversion macros, `ntohl`/`ntohs`/`htonl`/`htons`, and `cpu_to_*`/`*_to_cpu` families assuming little-endian CPU.
- Maps `printk` to `DbgPrint`; defines Linux `KERN_*` log prefixes as string constants.
- Implements Linux `ERR_PTR`, `PTR_ERR`, `IS_ERR`, and `BUG_ON`/`WARN_ON` using NT-style casts and `assert`.
- Turns Linux module primitives into no-ops or local wrappers: `THIS_MODULE`, `MODULE_LICENSE`, `EXPORT_SYMBOL`, `try_module_get`, `module_put`, `module_init`, `module_exit`, `LOAD_MODULE`, and `UNLOAD_MODULE`.
- Defines `spinlock_t` around `KSPIN_LOCK` plus saved `KIRQL`; `spin_lock_irqsave` stores the acquired IRQL in the caller flag.
- Implements `set_bit`, `clear_bit`, `test_bit`, `test_and_set_bit`, and `test_and_clear_bit` using interlocked operations for mutations.
- Defines a minimal `task_struct`, `current`, scheduler stubs (`cond_resched`, `need_resched`, `yield`, `might_sleep`), and `mutex_t` over `FAST_MUTEX`.
- Declares wait-queue structures and functions implemented elsewhere (`init_waitqueue_head`, `wake_up`, `prepare_to_wait`, `finish_wait`, etc.).
- Defines `struct block_device` with NT device/file object fields plus buffer-head cache/tree fields.
- Defines `struct page`, page flag constants, and Linux page flag macros over bit operations.
- Defines `struct buffer_head`, buffer state bits, state helper macros, buffer cache APIs (`__getblk`, `__bread`, `brelse`, `submit_bh`, `sync_dirty_buffer`, extents-specific buffer helpers, etc.), and inline wrappers such as `sb_getblk`, `sb_bread`, `map_bh`, `wait_on_buffer`, and `lock_buffer`.
- Declares NLS table structure and registration/loading/UTF-8 conversion routines.
- Defines `jiffies` by querying `KeQueryTickCount` and scaling by `KeQueryTimeIncrement` to `HZ == 100`.
- Maps `kmalloc`/`kfree` to `Ext2AllocatePool`/`Ext2FreePool` using tag `'JBDM'`; declares slab-like `kmem_cache` APIs backed by NT lookaside lists.
- Provides Linux block operation constants (`READ`, `WRITE`, `READ_SYNC`, `WRITE_BARRIER`, etc.), timer comparison macros, `smp_rmb` no-op, and `do_div`.

Dependencies:
- Requires NT kernel headers and types indirectly via `linux/types.h`.
- Depends on driver-side implementations for buffer heads, wait queues, pool allocation, slab cache, NLS, block I/O, and page allocation.

Research notes:
- This header concentrates many compatibility APIs that would normally be split across Linux headers such as `module.h`, `spinlock.h`, `sched.h`, `slab.h`, `buffer_head.h`, `pagemap.h`, `nls.h`, and `timer.h`; the zero-byte sibling headers in this group likely exist only to satisfy include paths.
- `BITS_PER_LONG` is fixed at 32 in `types.h`, so bit helpers here operate in 32-bit chunks even on `_WIN64`; separate `CFS_BITS_PER_LONG` exists but is not used by these macros.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/module.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/mutex.h -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/mutex.h

This file is empty: 0 lines, 0 bytes.

Research notes:
- It contributes no symbols, macros, or includes.
- Mutex compatibility for this tree is provided in `linux/module.h` through `typedef struct mutex { FAST_MUTEX lock; } mutex_t` and `mutex_init`/`mutex_lock`/`mutex_unlock`.
- The file appears to be an include-path placeholder for Linux-source compatibility.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/mutex.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/nls.h -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/nls.h

This file is empty: 0 lines, 0 bytes.

Research notes:
- It contributes no declarations directly.
- NLS structures and routines are declared in `linux/module.h`, including `struct nls_table`, `register_nls`, `unregister_nls`, `load_nls`, `unload_nls`, `load_nls_default`, and UTF-8 conversion helpers.
- This file exists as a compatibility include placeholder.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/nls.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/pagemap.h -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/pagemap.h

This file is empty: 0 lines, 0 bytes.

Research notes:
- It defines no page-cache APIs itself.
- Page structures, page flags, allocation declarations, and buffer-page helpers are centralized in `linux/module.h`.
- It is a compatibility placeholder for code that includes Linux `pagemap.h`.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/pagemap.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/poison.h -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/poison.h

This file is empty: 0 lines, 0 bytes.

Research notes:
- It does not define Linux poison constants.
- No runtime behavior or compile-time declarations are provided here.
- It is likely retained only to satisfy imports from ported Linux/JBD/ext code.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/poison.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/proc_fs.h -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/proc_fs.h

This file is empty: 0 lines, 0 bytes.

Research notes:
- It provides no `/proc` filesystem API.
- Any ported code including `linux/proc_fs.h` compiles only because this placeholder exists and the relevant procfs behavior is unused or compiled out.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/proc_fs.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/rbtree.h -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/rbtree.h

This header ports the Linux red-black tree interface. It contains the original Linux rbtree usage comment, defines node/root structures, color and parent accessors, insertion-link helpers, and declares balancing/traversal routines implemented elsewhere.

Key definitions:
- `struct rb_node` stores `rb_parent_color`, `rb_right`, and `rb_left`, with parent pointer and color packed together.
- `struct rb_root` holds the tree root node.
- Defines `RB_RED`, `RB_BLACK`, `rb_parent`, `rb_color`, `rb_is_red`, `rb_is_black`, `rb_set_red`, `rb_set_black`, `rb_set_parent`, and `rb_set_color`.
- Defines `RB_ROOT`, `rb_entry`, `RB_EMPTY_ROOT`, `RB_EMPTY_NODE`, and `RB_CLEAR_NODE`.
- Declares `rb_insert_color`, `rb_erase`, `rb_next`, `rb_prev`, `rb_first`, `rb_last`, `rb_replace_node`, and a generic `rb_insert`.
- Inline `rb_link_node` initializes a newly linked node and stores it into the parent’s child pointer.

Dependencies:
- Uses `ULONG_PTR`, `container_of`, and `__attribute__`, which are provided by the local compatibility headers.
- Runtime behavior depends on `src/rbtree.c`, not part of this group.

Research notes:
- The tree is used by the ext2 compatibility/block layer for structures such as buffer-head lookup trees.
- `RB_CLEAR_NODE(node)` sets the parent pointer to the node itself. In this header, `RB_EMPTY_NODE(node)` is defined as `rb_parent(node) != node`; this is inverted from the common Linux idiom and means cleared nodes test false under this macro. Callers need to match this local semantic or avoid relying on it.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/rbtree.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/sched.h -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/sched.h

This file is empty: 0 lines, 0 bytes.

Research notes:
- Scheduler compatibility is centralized in `linux/module.h`, which defines `task_struct`, `current`, task state constants, `cond_resched`, `need_resched`, `yield`, and `might_sleep`.
- This file is an include placeholder.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/sched.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/slab.h -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/slab.h

This file is empty: 0 lines, 0 bytes.

Research notes:
- Slab compatibility is declared in `linux/module.h` through `kmem_cache_t`, `struct kmem_cache`, `kmem_cache_create`, `kmem_cache_alloc`, `kmem_cache_free`, and `kmem_cache_destroy`.
- `kmalloc`, `kfree`, and `kzalloc` are also provided from `module.h`.
- This is a compatibility placeholder.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/slab.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/spinlock.h -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/spinlock.h

This file is empty: 0 lines, 0 bytes.

Research notes:
- Spinlock compatibility is implemented in `linux/module.h` using `KSPIN_LOCK`, `KIRQL`, and `KeAcquireSpinLock`/`KeReleaseSpinLock`.
- This file exists to satisfy Linux include paths.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/spinlock.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/stddef.h -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/stddef.h

This small compatibility header defines boolean enum constants and `offsetof` when not already available.

Key definitions:
- Include guard `_LINUX_STDDEF_H`.
- Anonymous enum sets `false = 0` and `true = 1`.
- Defines `offsetof(TYPE, MEMBER)` as `((size_t) &((TYPE *)0)->MEMBER)` if absent.

Research notes:
- This is a minimal Linux-style `stddef.h` shim, not a full standard-library replacement.
- The driver also defines an `offsetof` variant in `linux/module.h`, guarded by `#ifndef offsetof`.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/stddef.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/string.h -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/string.h

This file is empty: 0 lines, 0 bytes.

Research notes:
- It does not wrap or declare string functions.
- Standard C string functions used by the driver arrive through other headers such as `linux/types.h` including C/NT headers.
- This file is an include-path placeholder.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/string.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/time.h -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/time.h

This file is empty: 0 lines, 0 bytes.

Research notes:
- Time compatibility for this group is in `linux/module.h`, including `HZ`, `jiffies`, `JIFFIES()`, and `time_after`/`time_before` macros.
- This file is a placeholder for Linux source compatibility.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/time.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/timer.h -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/timer.h

This file is empty: 0 lines, 0 bytes.

Research notes:
- `struct timer_list` and timer comparison helpers are declared in `linux/module.h`.
- No timer registration or callback runtime is provided by this file.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/timer.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/types.h -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/types.h

This header maps Linux scalar types and annotations onto NT/ReactOS build types.

Key definitions:
- Includes `linux/config.h`, NT kernel/disk headers, Win32 definitions, and C runtime headers.
- Defines fixed-width Linux-style types: `__u8`, `__s8`, `__u16`, `__s16`, `__u32`, `__s32`, `__u64`, `__s64`.
- Defines short aliases `s8`/`u8` for ReactOS and `s16`/`u16`/`s32`/`u32`/`s64`/`u64` for MSVC or ReactOS.
- Maps `__le16`, `__le32`, and `__le64` to unsigned integer aliases; defines `__be16` and `__be32` as bitwise-marked types.
- Defines `bool` as `BOOLEAN`.
- Neutralizes compiler annotations/macros: `__attribute__`, `__bitwise`, `__releases`, `noinline`, `__acquire`, `__release`, `preempt_enable`, and `preempt_disable`.
- Defines Linux identity/FS types: `uid_t`, `gid_t`, `pid_t`, `gfp_t`, `umode_t`, `sector_t`, `blkcnt_t`, and `loff_t`.
- Defines `BITS_PER_LONG` as 32 and `ORDER_PER_LONG` as octal `05`; separately defines pointer-sized `long_ptr_t`/`ulong_ptr_t` and `CFS_BITS_PER_LONG`/`CFS_ORDER_PER_LONG`.
- Provides old-MSVC fallback `__FUNCTION__` and a `BUG()` macro that calls `DbgBreakPoint()`.

Research notes:
- This is foundational for compiling ported Linux ext/JBD code in the NT kernel environment.
- Endianness type annotations are mostly documentation here; the bitwise checking attributes are compiled away.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/types.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/version.h -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/version.h

This file is empty: 0 lines, 0 bytes.

Research notes:
- It defines no `LINUX_VERSION_CODE` or `KERNEL_VERSION` macros.
- It is only an include compatibility placeholder in this tree.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/version.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/resource.h -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/resource.h

This is a Microsoft Developer Studio generated resource header for the ext2 driver resource script.

Contents:
- Contains only comments and `APSTUDIO_INVOKED` guarded defaults.
- Defines `_APS_NEXT_RESOURCE_VALUE`, `_APS_NEXT_COMMAND_VALUE`, `_APS_NEXT_CONTROL_VALUE`, and `_APS_NEXT_SYMED_VALUE` for resource editor use.

Research notes:
- It has no runtime filesystem logic.
- It is relevant only to `.rc`/resource build metadata.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/resource.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/access.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/access.c

This file implements simple Unix-mode access checks for the ext2 driver.

Functions:
- `Ext2CheckInodeAccess(PEXT2_VCB Vcb, struct inode *in, int attempt)`: chooses UID/GID from `Vcb->uid/gid` or effective IDs when `VCB_USER_EIDS` is set, grants all access to root or owner, checks group mode bits for matching group, otherwise checks “other” mode bits. Returns whether the requested `attempt` mask is present.
- `Ext2CheckFileAccess(PEXT2_VCB Vcb, PEXT2_MCB Mcb, int attempt)`: wrapper that checks `Mcb->Inode`.

Dependencies:
- Uses mode helper macros such as `Ext2IsGroupReadOnly`, `Ext2IsGroupWritable`, `Ext2IsOtherReadOnly`, and `Ext2IsOtherWritable`.
- Uses access flags `Ext2FileCanRead`, `Ext2FileCanWrite`, and `Ext2FileCanExecute`.

Research notes:
- Owner/root are granted read, write, and execute regardless of individual mode bits.
- Group/other handling differentiates “read-only” and “writable” helper states and includes execute whenever read is granted.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/access.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/block.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/block.c

This file is the driver’s low-level NT block I/O helper layer. It handles MDLs, user-buffer locking, splitting a logical read/write into extents and associated IRPs, synchronous reads, sector-aligned disk reads, device I/O controls, media-removal control, and shutdown forwarding.

Key functions:
- `Ext2CreateMdl`: allocates an MDL for a buffer and either builds it for nonpaged pool or probes/locks pages.
- `Ext2DestroyMdl`: walks and frees an MDL chain, unlocking locked pages first.
- `Ext2LockUserBuffer`: attaches an MDL to an IRP user buffer and probes/locks it.
- `Ext2GetUserBuffer`: returns a system address for the IRP MDL or the raw user buffer.
- `Ext2ReadWriteBlockSyncCompletionRoutine`: completion for synchronous multi-block I/O; frees associated IRP resources, propagates failure to the master IRP, decrements outstanding block count, sets final information, and signals the wait event.
- `Ext2ReadWriteBlockAsyncCompletionRoutine`: completion for asynchronous I/O; propagates failure, updates final byte count and file object flags/current offset, releases any held resource, frees the read/write context, and leaves master completion to the I/O manager.
- `Ext2ReadWriteBlocks`: builds either a direct single-extent IRP path or multiple associated IRPs over an extent chain, sets partial MDLs, completion routines, verify/write-through flags, waits when allowed, and returns `STATUS_PENDING` for async completion.
- `Ext2ReadSync`: builds and sends a synchronous `IRP_MJ_READ` to the target device with optional verify override.
- `Ext2ReadDisk`: aligns arbitrary offset/size reads to sector boundaries, reads into a temporary buffer, and copies out the requested slice.
- `Ext2DiskIoControl`: builds and sends a synchronous device-control IRP.
- `Ext2MediaEjectControlCompletion` and `Ext2MediaEjectControl`: update `VCB_REMOVAL_PREVENTED` and send `IOCTL_DISK_MEDIA_REMOVAL`.
- `Ext2DiskShutDown`: forwards `IRP_MJ_SHUTDOWN` to the target device.

Research notes:
- `Ext2ReadWriteBlocks` is central to file data I/O because it bridges filesystem extents to NT storage IRPs.
- Error cleanup is SEH-based and tries to free any unsubmitted associated IRPs/MDLs.
- Async completion stores `ThreadId`/resource information so a resource acquired by the caller can be released after lower-device completion.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/block.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/cleanup.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/cleanup.c

This file implements `IRP_MJ_CLEANUP` handling. Cleanup is the Windows file-object transition where handle state, locks, cache maps, delete-on-close, notifications, and share access are torn down before final close releases object references.

Primary function:
- `Ext2Cleanup(PEXT2_IRP_CONTEXT IrpContext)`

Behavior:
- Ignores cleanup on the filesystem control device and uninitialized VCBs.
- For volume opens, releases volume lock state if this file object owns it, decrements open counts, and removes share access.
- For file opens, acquires the FCB main resource, handles repeated cleanup, validates CCB, decrements VCB/FCB open counts, marks archive attribute after modification, and releases directories through `ext3_release_dir`.
- Updates timestamps and saves inode metadata for modified files when needed.
- Checks oplocks, recomputes fast-I/O state, tracks noncached open counts, and drops byte-range locks via `FsRtlFastUnlockAll`.
- Handles deferred allocation/truncation state from create/setinfo paths (`FCB_ALLOC_IN_CREATE`, `FCB_ALLOC_IN_SETINFO`, `FCB_ALLOC_IN_WRITE`), including cache size updates.
- Removes share access and uninitializes cache maps; flushes/purges cache when the remaining opens are noncached or deletion is pending.
- Handles delete-on-close for regular files, directories, and symlink opens, calling `Ext2DeleteFile` and reporting directory/file removal notifications.
- Completes the IRP or queues it if pending.

Research notes:
- The function carefully tracks `VcbResourceAcquired`, `FcbResourceAcquired`, and `FcbPagingIoResourceAcquired` for SEH cleanup.
- Symlink delete-on-close can redirect deletion from the target FCB/Mcb to `Ccb->SymLink`.
- Cache purge may recursively generate close requests, which explains some lock-order caution also seen in `close.c`.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/cleanup.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/close.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/close.c

This file implements final `IRP_MJ_CLOSE` handling and delayed close work-queue dispatch.

Functions:
- `Ext2Close(PEXT2_IRP_CONTEXT IrpContext)`: releases CCBs and decrements VCB/FCB references after cleanup has already run. Handles filesystem device closes, volume-close CCB release, file-close CCB release, fast-I/O disabling, FCB drop timestamp updates, and deferred FCB dereference.
- `Ext2QueueCloseRequest(PEXT2_IRP_CONTEXT IrpContext)`: converts a normal close context into a delayed-close context, optionally sleeps if already delayed/file busy, initializes a work item, and queues it to `DelayedWorkQueue`.
- `Ext2DeQueueCloseRequest(PVOID Context)`: work item entry that enters the filesystem, invokes `Ext2Close`, and routes exceptions through the ext2 exception filter/handler.

Research notes:
- Comments explicitly warn against taking the VCB resource in the normal file close path because cache purging from cleanup can cause recursive close IRPs and reverse lock order.
- If resource acquisition fails, close is queued rather than blocking in the dispatch path.
- `FcbDerefDeferred` avoids calling `Ext2ReleaseFcb` while holding the FCB main resource.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/close.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/cmcb.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/cmcb.c

This file implements Cache Manager callback routines used by the driver’s `CACHE_MANAGER_CALLBACKS`.

Functions:
- `Ext2AcquireForLazyWrite`: validates the FCB, acquires the file resource exclusive, records the lazy-writer thread, and sets top-level IRP to `FSRTL_CACHE_TOP_LEVEL_IRP`.
- `Ext2ReleaseFromLazyWrite`: verifies/reverses lazy-writer state, releases the file resource, and clears top-level IRP.
- `Ext2AcquireForReadAhead`: acquires the file resource shared for read-ahead and sets top-level IRP.
- `Ext2ReleaseFromReadAhead`: clears top-level IRP and releases the resource.
- `Ext2NoOpAcquire`: for no-op cache callbacks, only sets top-level IRP.
- `Ext2NoOpRelease`: clears top-level IRP.

Research notes:
- These callbacks mediate Cache Manager lazy writer/read-ahead synchronization with the driver’s FCB resources.
- The no-op variants still maintain `IoSetTopLevelIrp` state, which prevents recursive filesystem entry from being misclassified.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/cmcb.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/create.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/create.c

This is the main create/open path for files, directories, symlinks, and volume opens. It performs Windows create-disposition policy, ext namespace lookup, symlink following, inode creation, EA replacement, share/oplock checks, cache setup, delete-on-close setup, and supersede/overwrite handling.

Key functions:
- `Ext2IsNameValid`: rejects invalid Windows filename characters such as `|`, `:`, `/`, `*`, `?`, `"`, `<`, and `>`.
- `Ext2FollowLink`: reads inline or block-backed symlink contents, converts `/` to `\`, converts OEM to Unicode, recursively looks up the target with depth/stack guards, and updates Mcb symlink/special state and target references.
- `Ext2IsSpecialSystemFile`: identifies root-level Windows special files/directories such as `pagefile.sys`, `swapfile.sys`, `hiberfil.sys`, `Recycled`, `RECYCLER`, and `$RECYCLE.BIN`.
- `Ext2LookupFile`: resolves a Unicode path relative to a parent or root MCB, uses the MCB cache first, scans directories on cache miss, allocates/loads new MCBs, sets file attributes from inode mode/access, follows symlinks unless disabled, and returns a referenced MCB.
- `Ext2ScanDir`: builds a dentry for a child name and calls `ext3_find_entry` to find the on-disk directory entry and inode number.
- `Ext2AddDotEntries`: after creating a directory, appends and initializes `.` and `..` entries, sets link count, dirties the buffer, and marks the inode dirty.
- `Ext2OverwriteEa`: validates a Windows EA buffer, obtains an ext4 xattr ref, purges existing user xattrs, validates EA names, and writes EA values through `ext4_fs_set_xattr`.
- `Ext2CreateFile`: the main file create/open state machine. It parses create options/disposition, resolves parent and target names, creates missing files/directories when allowed, opens target directories for rename semantics, handles symlink reparse-point options, checks ext access, allocates/reuses FCBs and CCBs, checks oplocks/share access, sets cache and section pointers, handles delete-on-close, creates directory dot entries, overwrites EAs, emits notifications, and handles supersede/overwrite.
- `Ext2CreateVolume`: handles direct volume opens, share access, volume locking when opened exclusively, cache flushing for raw/noncached access, and VCB open/reference counts.
- `Ext2Create`: dispatch entry for `IRP_MJ_CREATE`; handles the filesystem device object, verifies mount/VCB state, rejects locked/dismounting volumes, and routes to volume or file create.
- `Ext2CreateInode`: allocates an inode near the parent group, initializes owner/group/mode/timestamps/generation/extra inode size, initializes extents when supported, saves the inode, and adds the directory entry.
- `Ext2SupersedeOrOverWriteFile`: purges cache, truncates/expands allocation, resets sizes, updates timestamps/inode size, saves the inode, and overwrites EAs.

Research notes:
- The function has careful reference choreography around MCBs, FCBs, CCBs, and symlink targets; most failures unwind in the `finally` block.
- The path resolver uses `Vcb->McbLock`, while create/open FCB allocation uses `Vcb->FcbLock` and then per-FCB main resources.
- Ext4 extent support is forced for new inodes when the superblock has `EXT4_FEATURE_INCOMPAT_EXTENTS`.
- `FILE_OPEN_BY_FILE_ID` is explicitly not implemented.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/create.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/debug.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/debug.c

This file contains debug-only tracing plus allocation wrappers used in both debug and non-debug builds. Under `EXT2_DEBUG`, it provides formatted debug printing, IRP call/complete tracing, NTSTATUS stringification, MCB reference tracing, and guarded pool allocation. Without `EXT2_DEBUG`, only direct pool wrappers remain.

Debug-only globals and tables:
- `DebugFilter = DL_DEFAULT`
- `ProcessNameOffset`
- IRP major-function string table.
- File information class string table.
- FS information class string table.

Key functions:
- `Ext2Printf`: timestamped debug print with CPU and thread ID.
- `Ext2NiPrintf`: similar non-indented print helper.
- `Ext2GetProcessNameOffset`: scans the current process object for `"System"` to find process-name offset.
- `Ext2DbgPrintCall`: decodes and logs IRP major/minor functions, file names, read/write offsets and flags, file/fs information classes, directory query options, filesystem control codes, device controls, lock operations, cleanup, shutdown, and PNP.
- `Ext2DbgPrintComplete`: logs failed IRP completions with symbolic NTSTATUS names.
- `Ext2NtStatusToString`: large switch mapping many NTSTATUS/RPC/ACPI/CTX/PNP values to string names, defaulting to `STATUS_UNKNOWN`.
- `Ext2TraceMcb`: debug helper to log and mutate MCB reference counts with callsite formatting.
- `Ext2AllocatePool` under `EXT2_DEBUG`: allocates 0x20 bytes extra, stores size metadata, writes start/end guard bytes, and updates global allocation counters under `Ext2MemoryLock`.
- `Ext2FreePool` under `EXT2_DEBUG`: checks metadata and guard bytes, poisons guard regions, updates allocation counters, and frees with tag.
- `Ext2AllocatePool`/`Ext2FreePool` without `EXT2_DEBUG`: thin wrappers over `ExAllocatePoolWithTag` and `ExFreePoolWithTag`.

Research notes:
- Most of the file is diagnostic mapping, especially the NTSTATUS string table.
- Debug pool wrappers can catch buffer underruns/overruns around allocations made through `Ext2AllocatePool`.
- Because `Ext2TraceMcb` changes reference counts while logging, it is not passive tracing; callers must use it only where that side effect is intended.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/debug.c -->