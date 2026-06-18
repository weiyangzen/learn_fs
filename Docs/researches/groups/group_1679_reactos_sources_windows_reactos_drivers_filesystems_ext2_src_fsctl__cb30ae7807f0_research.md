# Group Research: group_1679_reactos_sources_windows_reactos_drivers_filesystems_ext2_src_fsctl__cb30ae7807f0

Scope: `Docs/research_subset_a.md`, covering ReactOS Ext2 filesystem-control, driver initialization, byte-range locking, Linux compatibility shims, and JBD journal recovery/replay/revoke support.

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/fsctl.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/fsctl.c

## Scope
Implements Ext2 filesystem-control dispatch for volume mount, verify, lock/unlock, dismount, invalidate, retrieval-pointer queries, oplocks, volume dirty state, extended DASD access, Windows reparse-point operations backed by ext2 symlinks, and cache purge/teardown paths.

## Key Elements
- `Ext2FileSystemControl()` dispatches `IRP_MN_USER_FS_REQUEST`, `IRP_MN_MOUNT_VOLUME`, and `IRP_MN_VERIFY_VOLUME`.
- `Ext2UserFsRequest()` maps user FSCTLs to handlers for reparse points, volume lock/unlock/dismount/mounted checks, invalidate volumes, oplocks, dirty-state query, and retrieval-pointer APIs.
- `Ext2LockVcb()`, `Ext2LockVolume()`, `Ext2UnlockVcb()`, and `Ext2UnlockVolume()` enforce open-handle checks, set/clear `VCB_VOLUME_LOCKED`, and update `VPB_LOCKED`.
- `Ext2MountVolume()` creates the per-volume device object, reads and validates the ext2 superblock magic, initializes the VCB, handles old VPB/VCB matching, marks the VPB mounted, inserts the VCB globally, and dereferences the target device on success.
- `Ext2VerifyVcb()` and `Ext2VerifyVolume()` perform removable-media verification, change-count checks, superblock UUID/name comparison, write-protection refresh, and purge/dismount-pending handling on wrong media.
- `Ext2DismountVolume()` flushes files/volume, purges cache, and calls `Ext2CheckDismount()` to detach or replace VPBs.
- `Ext2CheckDismount()` coordinates global and VCB resources plus the VPB spin lock to remove the VCB from global lists, mark dismount pending, allocate a replacement VPB for forced dismount, tear streams down, and destroy VCBs when references are gone.
- `Ext2PurgeVolume()` and `Ext2PurgeFile()` flush or purge cache-manager sections, image sections, group descriptor buffer heads, and per-FCB section objects.
- Retrieval-pointer support uses `Ext2BuildExtents()` to fill `RETRIEVAL_POINTERS_BUFFER` or internal paging-file mapping arrays.
- Reparse-point support treats ext2 symlinks as Windows `IO_REPARSE_TAG_SYMLINK`, translating slash direction and OEM/Unicode names.

## Dependencies
Depends on Ext2 VCB/FCB/CCB/MCB structures, `Ext2BuildExtents()`, inode read/write/truncate helpers, VCB initialization/destruction, cache-manager APIs, FsRtl oplock/file-lock APIs, VPB spin-lock operations, lower disk IOCTL helpers, NLS conversion helpers, and global VCB list state.

## Behavior/Risks
- The mount path assumes successful `Ext2LoadSuper()` plus `EXT2_SUPER_MAGIC` is enough to claim the volume before `Ext2InitializeVcb()` performs deeper setup.
- Reparse handling only supports relative symlink reparse buffers and explicitly rejects other tags or absolute symlink flags.
- `Ext2QueryRetrievalPointers()` contains `DbgBreak()` calls, so this path appears diagnostic or unfinished.
- `Ext2GetRetrievalPointers()` uses `BLOCK_BITS` conversions and must keep VCN/LCN units consistent with Windows callers.
- Dismount and forced VPB replacement are highly stateful; correctness depends on VPB reference counts, `VCB_NEW_VPB`, `VCB_DISMOUNT_PENDING`, and global VCB resource ordering.
- Purge paths deliberately acquire paging resources before cache flush/purge to synchronize with mapped and cached IO.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/fsctl.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/init.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/init.c

## Scope
Implements Ext2 driver startup, optional unload, registry configuration loading, global object allocation, device object registration, dispatch-table setup, fast I/O/cache callbacks, lookaside-list initialization, Linux/JBD compatibility initialization, and NLS setup.

## Key Elements
- Defines global `Ext2Global`, build version/date/time strings, `DriverEntry()`, optional `DriverUnload()`, registry query helpers, and ERESOURCE alignment checks.
- `Ext2RegistryQueryCallback()` parses registry values for writing support, bitmap checking, ext3 force writing, auto mount, codepage, hiding prefix, and hiding suffix.
- `Ext2QueryRegistrySettings()` builds the `Parameters` registry path, enables automount by default, applies registry settings, converts configured wide strings to ANSI/OEM fields, and stores the volumes registry path.
- `DriverEntry()` initializes Linux compatibility support, JBD caches, `Ext2Global`, disk and CD-ROM filesystem device objects, reaper threads, major dispatch functions, fast I/O callbacks, cache-manager callbacks, filter callbacks, performance-stat allocation sizes, lookaside lists, symbolic link, NLS tables, and filesystem registration.
- `DriverUnload()` unregisters global resources, deletes the symbolic link, unloads NLS tables, destroys lookaside lists, dereferences registered devices, unloads JBD caches, destroys Linux compatibility state, and frees `Ext2Global`.

## Dependencies
Depends on Windows driver initialization APIs, ReactOS/NT conditional signatures, Ext2 request builder and fast I/O routines, reaper threads, NLS loader, global pool/lookaside helpers, journal module init/exit macros, and Linux compatibility init/teardown.

## Behavior/Risks
- Error cleanup in `DriverEntry()` frees some global/device/JBD/Linux resources but does not mirror all later startup steps because failures can occur at many points.
- Writing support can be enabled directly or implicitly through ext3 force-writing registry configuration.
- The code sets fast I/O mod-write callbacks twice, which is harmless but redundant.
- `Ext2QueryRegistrySettings()` writes `sHidingPrefix[HIDINGPAT_LEN - 1]` after suffix conversion too, likely intending `sHidingSuffix`.
- Resource alignment is asserted at compile time for global, VCB, FCB, block-device, and group-descriptor locks.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/init.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/jbd/recovery.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/jbd/recovery.c

## Scope
Provides Linux JBD journal recovery logic used by the ReactOS Ext2 driver. It scans the journal, records revoke entries, replays committed descriptor data, and supports skip-recovery startup.

## Key Elements
- `journal_recover()` performs the classic three recovery passes: `PASS_SCAN`, `PASS_REVOKE`, and `PASS_REPLAY`.
- `journal_skip_recovery()` scans enough journal state to advance transaction sequence numbers while ignoring existing log contents.
- `do_one_pass()` walks the circular journal, validates magic, block type, and transaction sequence, handles descriptor, commit, and revoke blocks, wraps at journal bounds, and records end transaction state.
- `jread()` maps journal offsets with `journal_bmap()`, gets a buffer head, performs readahead where enabled, waits for data, and returns IO errors on failed reads.
- `count_tags()` counts descriptor tags, accounting for optional UUID fields and `JFS_FLAG_LAST_TAG`.
- `scan_revoke_records()` parses revoke blocks and calls `journal_set_revoke()` for each revoked block.

## Dependencies
Depends on JBD journal structures, `journal_bmap()`, buffer-head IO helpers supplied by the Linux shim, revoke APIs from `revoke.c`, transaction ID comparison helpers, endian conversion macros, and block-device sync.

## Behavior/Risks
- Replay copies logged data blocks back to filesystem-device blocks unless `journal_test_revoke()` suppresses them.
- IO errors during replay attempt to recover what they can but return failure after the pass.
- Recovery trusts descriptor tag bounds and revoke block `r_count`; malformed journal metadata is handled mostly by stopping scan or returning IO-style errors.
- At the end of successful recovery, the transaction sequence advances past the recovered range and revoke state is cleared.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/jbd/recovery.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/jbd/replay.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/jbd/replay.c

## Scope
Ports substantial Linux JBD journal core support into the ReactOS Ext2 tree: abort/error handling, journal-head cache management, log block allocation, journal initialization/loading/wiping, superblock feature negotiation/update, transaction buffer-list management, buffer forget/release, and JBD module cache startup/shutdown.

## Key Elements
- Commit request helpers `__log_start_commit()` and `log_start_commit()` set `j_commit_request` and wake the commit waitqueue.
- Abort helpers record `JFS_ABORT`, preserve `j_errno`, optionally update the journal superblock, and expose `journal_abort()`, `journal_errno()`, `journal_clear_err()`, and `journal_ack_err()`.
- Journal-head helpers allocate, attach, grab, put, and remove `struct journal_head` objects from buffer heads while managing `BH_JBD`, `b_private`, `b_jcount`, and buffer references.
- `journal_next_log_block()`, `journal_bmap()`, and `journal_get_descriptor_buffer()` allocate logical journal blocks and map inode-backed or external journal blocks to physical block numbers.
- `journal_init_common()` initializes waitqueues, mutexes, locks, commit interval, abort-by-default state, and revoke tables.
- `journal_init_inode()` creates an inode-backed journal, allocates write buffers, maps the journal superblock, and stores `j_superblock`.
- `journal_load()` loads the superblock, validates feature bits, invokes recovery, resets dynamic journal state, clears abort, and marks the journal loaded.
- `journal_wipe()`, `journal_update_format()`, `journal_update_superblock()`, and `journal_reset()` manage on-disk superblock format and dynamic log head/tail fields.
- Transaction-list helpers file/unfile buffers across `BJ_Metadata`, `BJ_Forget`, `BJ_LogCtl`, `BJ_Reserved`, and related lists.
- `journal_forget()` removes a buffer from current journaling state, preserves checkpoint dependencies through `BJ_Forget`, and drops buffer references.
- Module init/exit creates and destroys revoke, journal-head, and handle caches.

## Dependencies
Depends on Linux JBD headers/types, revoke initialization from `revoke.c`, recovery from `recovery.c`, buffer-head operations from `linux.c`, endian and transaction helper macros, journal superblock definitions, and Ext2 inode block mapping through `bmap()`.

## Behavior/Risks
- This file is named `replay.c` but functions as a broad JBD journal core subset, not only replay.
- Many full Linux JBD runtime paths are compiled out or stubbed compared with a complete kernel JBD implementation, especially commit-thread/checkpoint destruction sections.
- `journal_load()` always calls recovery before `journal_reset()`, then writes the superblock as clean/current.
- `journal_bmap()` aborts the journal on failed inode mapping, making inode-backed journal block mapping a critical dependency.
- Journal-head lifetime depends on paired buffer references; misuse can leak or prematurely release cached buffer heads.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/jbd/replay.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/jbd/revoke.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/jbd/revoke.c

## Scope
Implements JBD revoke support: hash-table allocation, runtime revoke/cancel logic, commit-time revoke descriptor writing, recovery-time revoke insertion/testing, and revoke cleanup.

## Key Elements
- Defines `jbd_revoke_record_s` for block-number plus transaction sequence records and `jbd_revoke_table_s` for power-of-two hash tables.
- `journal_init_revoke_caches()` and `journal_destroy_revoke_caches()` manage slab caches for revoke records and tables.
- `journal_init_revoke()` allocates two revoke tables so runtime and committing/recovery state can be switched.
- `journal_revoke()` marks a block revoked, optionally finds a cached buffer head, sets revoke bits, calls `journal_forget()` for supplied buffers, and inserts the revoke record.
- `journal_cancel_revoke()` removes a pending revoke when the block is journaled again and clears revoke state on buffer aliases.
- `journal_switch_revoke_table()` flips the active revoke table for a new transaction.
- `journal_write_revoke_records()` serializes revoke records into JBD revoke descriptor blocks and frees records after writing.
- `journal_set_revoke()`, `journal_test_revoke()`, and `journal_clear_revoke()` provide recovery-time revoke table operations.

## Dependencies
Depends on JBD transaction handles, journal locks, buffer-head revoke state bits, journal descriptor allocation from `replay.c`, `journal_forget()`, list helpers, kmem cache shims, endian conversion, and transaction ID comparison helpers.

## Behavior/Risks
- Revokes prevent stale journal metadata from overwriting newer data after block deletion/reuse.
- A later journaled write in the same transaction cancels an earlier revoke, while a later revoke must dominate earlier logged data.
- Runtime commit code is inside `#ifdef __KERNEL__`; the ReactOS build depends on how its compatibility headers define this path.
- `insert_revoke_hash()` retries allocation when `journal_oom_retry` is enabled, yielding until memory becomes available.
- Recovery stores only the latest revoke sequence per block and skips replay when the logged transaction is not newer than that revoke.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/jbd/revoke.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/linux.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/linux.c

## Scope
Provides a Windows/ReactOS compatibility layer for Linux-style JBD and ext2 helper code, including slab-like caches, waitqueues, buffer heads, block-device buffer lookup, cache-manager-backed block reads/writes, block mapping, inode references, and compatibility initialization.

## Key Elements
- Defines a global `current_task` and `current` pointer for Linux-style current-task access.
- Implements `kzalloc()`, `kmem_cache_create()`, `kmem_cache_destroy()`, `kmem_cache_alloc()`, and `kmem_cache_free()` using nonpaged lookaside lists.
- Implements waitqueue initialization, add/remove, prepare/finish wait, and a stubbed `wake_up()`.
- Creates a buffer-head cache with `ext2_init_bh()` and `ext2_destroy_bh()`.
- `new_buffer_head()` and `free_buffer_head()` allocate/free buffer heads, MDLs, pinned BCBs, and memory accounting.
- Maintains buffer heads in a per-block-device red-black tree keyed by block number.
- `get_block_bh_pin()` and `submit_bh_pin()` use `CcPinRead()`, `CcPreparePinWrite()`, `CcSetDirtyPinnedData()`, and BCB ownership to back Linux buffer heads with Windows cache-manager pinned data.
- MDL-backed alternatives exist in `get_block_bh_mdl()` and `submit_bh_mdl()`, but the active build selects the pinned path.
- `__getblk()`, `__brelse()`, `__bforget()`, `ll_rw_block()`, `bh_submit_read()`, `sync_dirty_buffer()`, `mark_buffer_dirty()`, and `sync_blockdev()` supply JBD buffer IO semantics.
- `bmap()` maps inode logical blocks through `Ext2BuildExtents()`.
- `iget()` and `iput()` provide simple inode reference counting.
- `ext2_init_linux()` and `ext2_destroy_linux()` initialize/destroy buffer-head support.

## Dependencies
Depends on Ext2 VCB/block-device structures, Windows cache-manager APIs, MDL helpers, red-black tree helpers, buffer state macros, global BH reaper signaling, Ext2 extent mapping, and Ext2 flush/block-extent accounting.

## Behavior/Risks
- `wake_up()` is effectively a no-op, which limits fidelity for Linux waitqueue users unless higher-level code avoids relying on real wakeups.
- Buffer locks and waits are mostly stubbed, so correctness relies on surrounding Windows resources and cache-manager synchronization.
- `__find_get_block()` calls `__getblk()`, so it may instantiate a buffer rather than only finding an existing cached one.
- `__brelse()` writes dirty buffers before dropping references and queues zero-reference buffers to the VCB free list for the BH reaper.
- The active pinned-buffer path keeps cache-manager BCBs owned by the buffer head and marks pinned data dirty on write submission.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/linux.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/lock.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/lock.c

## Scope
Implements byte-range lock control dispatch for regular Ext2 files.

## Key Elements
- `Ext2LockControl()` validates that the request targets a mounted volume file object rather than the filesystem device.
- Rejects volume FCBs and directory files for lock control.
- Acquires the FCB main resource shared while processing the lock request.
- Calls `FsRtlCheckOplock()` before file-lock processing and leaves completion pending when oplock processing takes ownership.
- Calls `FsRtlProcessFileLock()` on `Fcb->FileLockAnchor`, letting FsRtl complete the IRP.
- Updates `Fcb->Header.IsFastIoPossible` after file-lock state changes.

## Dependencies
Depends on Ext2 IRP context/FCB structures, FsRtl oplock and file-lock packages, `Ext2OplockComplete()`, `Ext2IsFastIoPossible()`, and normal Ext2 IRP-context completion.

## Behavior/Risks
- The function sets `IrpContext->Irp = NULL` when FsRtl owns IRP completion, preventing double completion by Ext2.
- Directory locking is rejected with `STATUS_INVALID_PARAMETER`.
- If oplock handling returns anything other than success, Ext2 does not complete the context immediately because the oplock package may finish asynchronously.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/lock.c -->