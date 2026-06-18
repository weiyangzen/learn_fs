# Group Research: group_1893_xnu_sources_os_darwin_xnu_bsd_vfs_vfs_cprotect_c_sources_os_darwin__0137d051ae0d

Scope: subset A from `Docs/research_subset_a.md`, covering the listed `sources/os/darwin/xnu/bsd/vfs` files. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/darwin/xnu/bsd/vfs/vfs_cprotect.c -->
# File Research: sources/os/darwin/xnu/bsd/vfs/vfs_cprotect.c

## Scope

This file implements VFS-side content-protection key container helpers and key-store notification plumbing. It manages `cpx_t` allocation, key material storage, AES-IV context generation, copy/flush/free behavior, filesystem notification of device lock/EP/CX state changes, protection-class validation, and cached parsing of the kernel `osversion`.

## Public And Internal APIs Covered

- CPX sizing/lifetime: `cpx_size()`, `cpx_sizex()`, `cpx_alloc()`, `cpx_alloc_ctx()`, `cpx_free_ctx()`, `cpx_writeprotect()`, `cpx_free()`, `cpx_init()`.
- CPX flags/accessors: SEP-wrapped key, composite key, offset IV, synthetic-offset IV, key length, key presence, and key pointer APIs.
- IV context APIs: `cpx_set_aes_iv_key()` and `cpx_iv_aes_ctx()`.
- Key state mutation: `cpx_flush()`, `cpx_can_copy()`, `cpx_copy()`.
- Key-store actions: `cp_key_store_action()` and `cp_key_store_action_for_volume()`.
- Validation/version helpers: `cp_is_valid_class()` and `cp_os_version()`.

## Control Flow And Behavior

`cpx_alloc()` uses either page allocation with optional write protection under `CONFIG_KEYPAGE_WP` or zone allocation from `cpx_zone` otherwise. Non-write-protected builds allocate an optional AES context from `aes_ctz_zone` when requested. `cpx_init()` clears flags, sets key length to zero, and records the maximum key length.

`cpx_iv_aes_ctx()` lazily derives a 128-bit AES IV context by SHA1 hashing cached key material, using the digest as AES key input, and tagging the context as VFS-generated. Changing key length clears VFS IV context bits so a later IV request regenerates state.

`cp_key_store_action*()` builds a callback argument and walks mounts with `vfs_iterate()`. The callback optionally filters by filesystem UUID and dispatches `FIODEVICELOCKED`, `FIODEVICEEPSTATE`, or `FIODEVICECXSTATE` through `VFS_IOCTL()`.

## State And Data Structures

- `struct cpx` is variable length and stores flags, max/current key length, optional AES context pointer, and key bytes.
- Debug builds add leading/trailing magic checks.
- Zones: `cpx_zone` clears freed fixed CPX storage; `aes_ctz_zone` clears AES contexts.
- Callback state is carried by `cp_vfs_callback_arg`, including optional UUID filtering.

## Dependencies

Depends on content-protection headers, mount iteration and VFS ioctl dispatch, SHA1 and AES helpers, kernel zones, and optional VM page protection APIs under `CONFIG_KEYPAGE_WP`.

## Risks And Invariants

- Key material and AES contexts are explicitly zeroed on flush/free paths; this is a confidentiality invariant.
- `cpx_copy()` assumes destination AES context exists if initialized flags are copied.
- In `CONFIG_KEYPAGE_WP` builds, `cpx_alloc()` sets `CPX_WRITE_PROTECTABLE` before calling `cpx_init()`, while `cpx_init()` clears flags. The write-protection/free paths depend on that flag, so this ordering is a sensitive invariant.
- `cp_vfs_callback()` silently ignores mounts without UUID support or mismatched UUIDs.
- `parse_os_version()` accepts only versions shaped like digits, one letter, digits; parse failure caches sentinel value `1`.
<!-- END FILE RESEARCH: sources/os/darwin/xnu/bsd/vfs/vfs_cprotect.c -->

<!-- BEGIN FILE RESEARCH: sources/os/darwin/xnu/bsd/vfs/vfs_disk_conditioner.c -->
# File Research: sources/os/darwin/xnu/bsd/vfs/vfs_disk_conditioner.c

## Scope

This file implements the kernel disk conditioner used to simulate slower storage behavior on a per-mount basis. It delays I/O, constrains mount I/O limits, tracks simulated HDD seek/spin-up behavior, and restores original mount fields on disable or unmount.

## Public And Internal APIs Covered

- `disk_conditioner_delay()` computes and applies synthetic delay for buffer I/O.
- `disk_conditioner_get_info()` returns current conditioner settings.
- `disk_conditioner_set_info()` enables, disables, or updates settings after root and entitlement checks.
- `disk_conditioner_unmount()` restores and frees conditioner state.
- `disk_conditioner_mount_is_ssd()` reports effective SSD/HDD behavior.
- Internal helpers save and restore mount I/O fields.

## Control Flow And Behavior

`disk_conditioner_set_info()` requires root plus `com.apple.private.dmc.set`. It lazily allocates per-mount conditioner state, snapshots original read/write/segment/queue fields, clamps requested limits to hardware-advertised mount limits, updates mount throttling fields while enabled, and resets throttle periods.

`disk_conditioner_delay()` exits unless the vnode, mount, and enabled conditioner state are available. HDD mode estimates seek cost from block distance since the last I/O and adds spin-up latency after long idle periods. SSD mode uses the full block range as the access-time scale. Throughput caps add read or write transfer delay. Existing elapsed time is subtracted before calling `delay()`.

## State And Data Structures

- `struct _disk_conditioner_info_t` embeds public `disk_conditioner_info`, saved mount fields, last block number, and last I/O timestamp.
- State is attached to `mp->mnt_disk_conditioner_info`.
- Mount fields affected include max read/write byte counts, segment counts, I/O queue depth, and I/O scale.

## Dependencies

Depends on buffer/vnode/mount internals, `fsctl` conditioner structures, IOKit entitlement checking, kauth credentials, time helpers, and mount throttling reset via `throttle_info_mount_reset_period()`.

## Risks And Invariants

- Saved mount fields must be restored exactly when disabling and during unmount.
- Delay math depends on `BLK_MAX(mp)` and device block sizing; invalid or zero sizing would be hazardous.
- The delay loop asserts the remaining delay fits in `INT_MAX`.
- `disk_conditioner_get_info()` returns success even when no conditioner state exists, leaving caller-provided output unchanged.
- Mount mutation is protected with `mount_lock()`, while delay reads conditioner state locklessly on the I/O path.
<!-- END FILE RESEARCH: sources/os/darwin/xnu/bsd/vfs/vfs_disk_conditioner.c -->

<!-- BEGIN FILE RESEARCH: sources/os/darwin/xnu/bsd/vfs/vfs_disk_conditioner.h -->
# File Research: sources/os/darwin/xnu/bsd/vfs/vfs_disk_conditioner.h

## Scope

This private VFS header declares the disk conditioner kernel-private API.

## APIs And Constants

- Declares `disk_conditioner_get_info(mount_t, disk_conditioner_info *)`.
- Declares `disk_conditioner_set_info(mount_t, disk_conditioner_info *)`.
- Declares `disk_conditioner_mount_is_ssd(mount_t)`.

## Dependencies And Role

The declarations are exposed only under `KERNEL_PRIVATE` and depend on `sys/fsctl.h` for `disk_conditioner_info`.

## Risks And Invariants

- The header intentionally does not expose `disk_conditioner_delay()` or unmount cleanup; those are internal call-site contracts.
- Consumers must compile with kernel-private mount and fsctl definitions available.
<!-- END FILE RESEARCH: sources/os/darwin/xnu/bsd/vfs/vfs_disk_conditioner.h -->

<!-- BEGIN FILE RESEARCH: sources/os/darwin/xnu/bsd/vfs/vfs_exclave_fs.c -->
# File Research: sources/os/darwin/xnu/bsd/vfs/vfs_exclave_fs.c

## Scope

This file implements the VFS-backed exclave filesystem bridge. It registers APFS base directories by filesystem tag, tracks open vnodes by file id, supports graft inode translation, exposes open/create/read/write/remove/sync/readdir/getsize/sealstate operations, and includes development-only ENOSPC injection.

## Public And Internal APIs Covered

- Lifecycle: `vfs_exclave_fs_start()` and `vfs_exclave_fs_stop()`.
- Registration: `vfs_exclave_fs_register()`, `vfs_exclave_fs_register_path()`, `vfs_exclave_fs_unregister()`, `vfs_exclave_fs_get_base_dirs()`.
- Exclave root/file operations: `vfs_exclave_fs_root()`, `vfs_exclave_fs_root_ex()`, `vfs_exclave_fs_open()`, `vfs_exclave_fs_create()`, `vfs_exclave_fs_close()`.
- I/O and metadata: `vfs_exclave_fs_read()`, `vfs_exclave_fs_write()`, `vfs_exclave_fs_remove()`, `vfs_exclave_fs_sync()`, `vfs_exclave_fs_readdir()`, `vfs_exclave_fs_getsize()`, `vfs_exclave_fs_sealstate()`.
- Internal helpers manage registered tags, open-vnode counts, APFS graft info, inode mapping, base-directory creation, and vnode attributes.

## Control Flow And Behavior

Startup initializes two mutexes, an open-vnode hash sized from `desiredvnodes`, and a registered-tag hash. Registration accepts only APFS directories, queries graft metadata, rejects writable tags on grafts, refs the base vnode, probes root-auth for sealed state on read-only tags, and installs a `registered_fs_tag_t`.

Writable filesystem tags are `EFT_EXCLAVE` and `EFT_EXCLAVE_MAIN`. Root lookup for writable tags rejects path-like exclave IDs, opens the per-exclave root directory, and creates it if missing. `exclave_fs_open_internal()` resolves paths under either the registered base directory or an already-open root vnode, optionally deletes before create to avoid inode reuse, calls `vn_open_auth()`, translates graft inode numbers when needed, and increments the open-vnode table.

Read/write build a single-segment kernel `uio` and call `VNOP_READ()` or `VNOP_WRITE()`. Writes are rejected for non-writable tags, and development/debug builds can force `ENOSPC` for configured exclaves. Close decrements the open table and calls `vn_close()`. Remove delegates to `unlink1()`. Sync maps exclave sync operations to `F_BARRIERFSYNC`, `F_FULLFSYNC`, or `VNOP_FSYNC()`.

`vfs_exclave_fs_readdir()` uses `VNOP_GETATTRLISTBULK()` to produce packed `exclave_fs_dirent_t` records. For `EFT_SYSTEM`, release builds reject VFS directory enumeration, while development/debug builds allow it only if integrity checks are disabled or the base is not sealed.

## State And Data Structures

- `registered_fs_tag_t` stores fs tag, flags, base vnode, device id, and optional APFS graft info.
- `open_vnode` records vnode, device, host file id, fs tag, open count, and debug flags.
- Global hashes are protected by `regtag_mtx` and `open_vnodes_mtx`.
- Graft mapping translates between root inode `2`, APFS graft directory id, and the graft inode range.

## Dependencies

Depends on XNU VFS namei/open/vnode APIs, APFS graft ioctls (`FSIOC_GET_GRAFT_INFO`, `FSIOC_EVAL_ROOTAUTH`), `unlink1()` from VFS syscalls, attrlist bulk directory enumeration, devfs/fsevents headers, PE boot arguments, and kernel allocation/locking primitives.

## Risks And Invariants

- Base-directory registration forbids nested registered ancestors; this prevents ambiguous roots.
- Open-vnode refcounts must balance `vnode_ref()`/`vnode_rele()` and `vnode_getwithref()`/`vnode_put()` across register, open, close, unregister, and stop paths.
- Graft inode translation must be applied in the correct direction: API-facing file ids are graft ids, while open-table keys are host ids.
- `release_open_vnodes()` drops all vnode refs for a tag during unregister, regardless of external clients that may still think file ids are open.
- Create deletes an existing file before opening with `O_EXCL` to avoid inode reuse; the attack window is explicitly handled by adding `O_EXCL`.
- `vfs_exclave_fs_readdir()` has a direct `return ENOBUFS` before common cleanup when `eofflag` is false, which is a notable resource-lifetime edge.
<!-- END FILE RESEARCH: sources/os/darwin/xnu/bsd/vfs/vfs_exclave_fs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/darwin/xnu/bsd/vfs/vfs_exclave_fs.h -->
# File Research: sources/os/darwin/xnu/bsd/vfs/vfs_exclave_fs.h

## Scope

This header defines the public kernel interface for the VFS-backed exclave filesystem bridge.

## APIs And Constants

- Defines packed `exclave_fs_dirent_t` with attrlist return fields, object type, file id, name location/length, and data length.
- Defines `EXCLAVE_FS_BASEDIR_ROOT_ID`.
- Defines sync operations: barrier, full fsync, and UBC fsync.
- Defines register/list entitlement strings.
- Declares lifecycle, registration, root/open/create/close/read/write/remove/sync/readdir/getsize/sealstate APIs.
- Declares `vfs_exclave_fs_query_volume_group()`.

## Dependencies And Role

The header includes kernel type definitions and assumes vnode, UUID string, and bool types are available from included kernel context.

## Risks And Invariants

- `exclave_fs_dirent_t` is packed and must match the byte layout produced by `VNOP_GETATTRLISTBULK()` consumers.
- API callers must treat file ids as opaque, especially for graft-backed base directories.
- The header exposes entitlement names but enforcement is performed by call sites outside this header.
<!-- END FILE RESEARCH: sources/os/darwin/xnu/bsd/vfs/vfs_exclave_fs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/darwin/xnu/bsd/vfs/vfs_exclave_fs_helper.cpp -->
# File Research: sources/os/darwin/xnu/bsd/vfs/vfs_exclave_fs_helper.cpp

## Scope

This C++ helper implements APFS volume-group lookup for the exclave filesystem bridge using IOKit service matching.

## Public And Internal APIs Covered

- Defines `vfs_exclave_fs_query_volume_group(const uuid_string_t, bool *)`.

## Control Flow And Behavior

On macOS targets, the function validates the input UUID string, creates an `AppleAPFSVolume` service matching dictionary, filters by `VolGroupUUID`, and sets `*exists` if a matching service is found. It releases all IOKit objects on exit.

On non-macOS targets, it returns `ENOTSUP`.

## State And Data Structures

No persistent state is kept. Temporary `OSDictionary`, `OSString`, and `IOService` references are allocated and released in one call.

## Dependencies

Depends on IOKit `IOService` matching, `IOPlatformExpert`, UUID parsing, and the C exclave FS header.

## Risks And Invariants

- The caller-visible result is initialized to false only on macOS builds; non-macOS returns `ENOTSUP`.
- All IOKit references must be released on every error path.
- `OSString::withCStringNoCopy()` relies on the input string remaining valid for the match setup.
<!-- END FILE RESEARCH: sources/os/darwin/xnu/bsd/vfs/vfs_exclave_fs_helper.cpp -->

<!-- BEGIN FILE RESEARCH: sources/os/darwin/xnu/bsd/vfs/vfs_fsevents.c -->
# File Research: sources/os/darwin/xnu/bsd/vfs/vfs_fsevents.c

## Scope

This file implements the kernel side of `/dev/fsevents` when `CONFIG_FSE` is enabled, plus fallback stubs when disabled. It creates and coalesces filesystem events, manages watcher queues, serializes event copyout, supports kqueue/select/read/ioctl interfaces, handles unmount-pending notifications, and exposes helper functions used by other VFS code.

## Public And Internal APIs Covered

- Event creation/filtering: `need_fsevent()`, `add_fsevent()`, `test_fse_access_granted()`, `create_fsevent_from_kevent()`.
- Event metadata helpers: `get_pathbuff()`, `release_pathbuff()`, `get_fse_info()`, `vnode_get_fse_info_from_vap()`.
- Watcher management: `add_watcher()`, `remove_watcher()`, `watcher_add_event()`, `fmod_watch()`.
- Device/file operations: `fseventsopen()`, `fseventsclose()`, `fseventsread()`, `fseventswrite()`, `fseventsioctl()`, `fseventsf_read()`, `fseventsf_ioctl()`, `fseventsf_select()`, `fseventsf_close()`, `fseventsf_kqfilter()`, `fseventsf_drain()`.
- Initialization: `fsevents_init()` and `fsevents_internal_init()`.
- Unmount coordination: `fsevent_unmount()`.

## Control Flow And Behavior

Initialization creates an exhaustible `kfs_event` zone, fills it to `kern.maxkfsevents`, clears watcher state, installs the character device, and creates `/dev/fsevents`.

`add_fsevent()` validates event type and watcher interest, coalesces repeated same-process events within about one second, allocates one or two `kfs_event` objects for normal or two-path operations, parses variadic event arguments, captures vnode attributes/path strings, marks dropped-data flags when needed, and queues the event to interested watchers. Special cases handle document-id events, activity events, access-granted events, and unmount-pending events. Hardlink-sensitive events may be replicated for sibling links using APFS next-link lookup and `fsgetpath_internal()`.

Watchers are created through the clone ioctl, which copies an event-interest array, allocates an `fsevent_handle`, registers a watcher, allocates a file descriptor, and attaches `fsevents_fops`. Watcher queueing increments event references, uses a ring buffer, wakes readers immediately past thresholds, or schedules a delayed thread-call wakeup. Non-entitled/non-system watchers that fall too far behind have queued events dropped and receive `FSE_EVENTS_DROPPED`.

`fmod_watch()` serializes readers, sleeps when no events are queued, emits dropped-event markers first, copies events into the caller `uio`, and releases event references as queue entries are consumed. `copy_out_kfse()` emits typed argument records for regular, compact, document-id, activity, access-granted, and two-path events.

`fseventswrite()` accepts externally written serialized events, parses them in a permanent 4 KiB staging buffer, preserves incomplete records across chunk boundaries, and reinjects parsed events through `add_fsevent()`.

## State And Data Structures

- `kfs_event` stores event type, flags, refcount, timestamp, pid, and union payloads for regular, document-id, activity, and access-granted events.
- `fs_event_watcher` stores interest array, excluded devices, ring queue, read/write indexes, flags, max event id, process identity, and handle pointer.
- Global state includes watcher table, per-event watcher counts, outstanding-event list, pending rename count, event zone, unmount ack state, coalescing cache, and delayed delivery timer.
- Locks: `event_handling_lock`, `watch_table_lock`, `event_buf_lock`, and `event_writer_lock`.

## Dependencies

Depends on VFS vnode attributes/path lookup, name cache string table, kqueue/select/fileproc APIs, devfs char devices, kauth credentials, IOKit entitlements, audit tokens, APFS hardlink ioctl support, sysctl/PE boot defaults, thread calls, zones, and user `uio` copy helpers.

## Risks And Invariants

- Event objects are refcounted across global lists and watcher queues; `release_event_ref()` must remove list entries and string-table names exactly once.
- The event zone is exhaustible; allocation failure marks all watchers as having dropped events and throttles diagnostics.
- `KFSE_BEING_CREATED` prevents copyout of partially built events.
- Reader serialization uses `num_readers`; close/drain paths wait and wake sleepers before teardown.
- Watcher entitlement filtering silently removes restricted event interests for activity and access-granted events.
- Non-Apple watchers are intentionally filtered for certain system directories and are penalized if they fall behind.
- Fallback `CONFIG_FSE` stubs still provide path buffer allocation and no-op `add_fsevent()`/`need_fsevent()` so other VFS code can compile without feature conditionals.
<!-- END FILE RESEARCH: sources/os/darwin/xnu/bsd/vfs/vfs_fsevents.c -->

<!-- BEGIN FILE RESEARCH: sources/os/darwin/xnu/bsd/vfs/vfs_fslog.c -->
# File Research: sources/os/darwin/xnu/bsd/vfs/vfs_fslog.c

## Scope

This file contains the VFS filesystem logging hook for external process modification message tracing.

## Public And Internal APIs Covered

- Defines `fslog_extmod_msgtracer(proc_t caller, proc_t target)`.

## Control Flow And Behavior

The implementation is currently compiled out with `#if 0` due to the referenced radar. The disabled body would format caller and target process names plus executable UUIDs, escape them, optionally print debug output, and emit a MessageTracer ASL kernel log message for external modification.

## State And Data Structures

No active runtime state is maintained. The disabled code uses stack buffers sized for process names plus UUID strings.

## Dependencies

Includes process, vnode, mount, syslog, UUID, allocation, and historical ASL/KASL headers, though the active function is effectively a no-op.

## Risks And Invariants

- Because the functional body is disabled, callers receive no logging side effect.
- If re-enabled, process locking assumptions in the comment matter: caller and target are expected to be appropriately locked.
- Escaping failures intentionally abort logging in the disabled implementation.
<!-- END FILE RESEARCH: sources/os/darwin/xnu/bsd/vfs/vfs_fslog.c -->

<!-- BEGIN FILE RESEARCH: sources/os/darwin/xnu/bsd/vfs/vfs_init.c -->
# File Research: sources/os/darwin/xnu/bsd/vfs/vfs_init.c

## Scope

This file initializes core VFS infrastructure: vnode operation vectors, vnode tables, filesystem event and name-cache subsystems, static filesystem registrations, dead mount state, VFS locks, dynamic filesystem table insertion/removal, and special-device hash locking.

## Public And Internal APIs Covered

- Operation setup: `vn_default_error()`, `vfs_op_init()`, `vfs_opv_init()`.
- VFS initialization: `vfsinit()`.
- Lock helpers: `vnode_list_lock()`, `vnode_list_unlock()`, `mount_list_lock()`, `mount_list_unlock()`, `mount_lock_init()`, `mount_lock_destroy()`.
- Filesystem registration: `vfstable_add()` and `vfstable_del()`.
- Special hash lock helpers: `SPECHASH_LOCK_ADDR()`, `SPECHASH_LOCK()`, `SPECHASH_UNLOCK()`.

## Control Flow And Behavior

`vfs_op_init()` clears vnode operation vector pointers, assigns operation offsets, and skips disabled operations. `vfs_opv_init()` allocates each operation vector, installs filesystem/layer implementations, validates operation descriptors, and fills missing entries with the vector default operation.

`vfsinit()` initializes vnode tables, VFS events, name cache, operation vectors, all statically configured filesystems, authorization scope, and the dead mount. It also initializes compression support, namespace resolver support, and exclave filesystem support when configured.

`vfstable_add()` registers a filesystem in the first empty static slot or dynamically allocates a `vfstable` when slots are exhausted, links it into `vfsconf`, and registers a sysctl node when needed. `vfstable_del()` unlinks a registered filesystem, unregisters sysctl state, clears static slots, or frees dynamic entries.

## State And Data Structures

- Defines `mount_zone`, VFS SMR domain `vfs_smr`, and static `dead_mount_store`.
- Maintains vnode list, mount, mount list, special hash, and package-extension locks.
- Initializes `dead_mountp` with conservative local/dead mount flags and default I/O constraints.
- Updates global filesystem counters: `numused_vfsslots`, `numregistered_fses`, and `maxvfstypenum`.

## Dependencies

Depends on global vnode operation descriptor arrays, VFS configuration table `vfsconf`, sysctl registration, name cache, vnode authorization, MAC labels, quota/compression/exclave feature gates, lock primitives, and mount/vnode internals.

## Risks And Invariants

- Every operation vector must define `vnop_default`; missing defaults panic.
- Operation descriptors must be present in the global descriptor list unless disabled.
- `vfstable_del()` expects the mount-list mutex to be held by its caller.
- Dynamic `vfstable` deletion temporarily drops and reacquires the mount-list lock around freeing memory.
- `dead_mountp` is a constant pointer to static storage and is initialized late in `vfsinit()`.
<!-- END FILE RESEARCH: sources/os/darwin/xnu/bsd/vfs/vfs_init.c -->

<!-- BEGIN FILE RESEARCH: sources/os/darwin/xnu/bsd/vfs/vfs_io_compression_stats.c -->
# File Research: sources/os/darwin/xnu/bsd/vfs/vfs_io_compression_stats.c

## Scope

This file implements optional VFS I/O compression statistics collection. It samples write buffers, LZ4-compresses them in configurable blocks, updates per-vnode compression histograms, records reclaimed vnode stats into a circular store buffer, notifies userspace, and exposes sysctl controls/dumps.

## Public And Internal APIs Covered

- Main sampling entry: `io_compression_stats(buf_t bp)`.
- Reclaim recording: `vnode_iocs_record_and_free(struct vnode *)`.
- Stats updates: `vnode_updateiocompressionblockstats()` and `vnode_updateiocompressionbufferstats()`.
- Sysctls: `vfs.io_compression_stats_enable`, `vfs.io_compression_stats_block_size`, and `vfs.io_compression_dump_stats`.
- Internal helpers allocate/free per-CPU buffers, compress blocks/buffers, bucket sizes/compressibility, construct store-buffer entries, notify userspace, and iterate live vnodes.

## Control Flow And Behavior

Enabling via sysctl allocates per-CPU LZ4 scratch buffers, per-CPU destination buffers sized by block size, the circular store buffer, and a path scratch buffer. Disabling frees all of them. Changing block size while enabled reallocates buffers; allocation failure disables stats.

`io_compression_stats()` ignores reads and zero-length buffers. For writes, it takes the stats lock opportunistically, maps the buffer, compresses it by blocks using per-CPU scratch/destination buffers with preemption disabled, updates per-vnode block and buffer histograms, emits a KDBG tracepoint, unlocks, and unmaps.

When a vnode with stats is reclaimed, `vnode_iocs_record_and_free()` tries to append a path plus stats snapshot into the store buffer, wraps at buffer end, optionally notifies a host special port, then clears and frees the vnode stats regardless of recording success.

Dump sysctl supports live vnode iteration or store-buffer reads. Store-buffer reads can be read-only or mark the current position as consumed.

## State And Data Structures

- Globals: `io_compression_stats_enable`, `io_compression_stats_block_size`, per-CPU scratch/compression buffers, `per_cpu_buf_size`, `vnpath_scratch_buf`, and `iocs_store_buffer`.
- Locks: `io_compression_stats_lock` protects enable/block-size/buffer lifetime; `iocs_store_buffer_lock` protects archive buffer state.
- Per-vnode stats are allocated from `io_compression_stats_zone` and stored on `vp->io_compression_stats`.

## Dependencies

Depends on buffer mapping, vnode internals, LZ4 raw encoder, Mach host notification port APIs, sysctl, vfs/vnode iteration, KDBG, per-CPU storage, atomic counters, and kernel allocation APIs.

## Risks And Invariants

- Compression runs with preemption disabled while using per-CPU buffers.
- `io_compression_stats()` uses try-locking to avoid blocking I/O paths during sysctl reconfiguration.
- `get_buffer_compressibility_bucket()` uses `log2down(saved_space_pc)`; a zero saved-space percentage is a sensitive input for `__builtin_clz`.
- `vnpath_scratch_buf` is global and protected only by store-buffer/live dump call paths; concurrent path construction relies on higher-level serialization.
- `vnode_updateiocompressionbufferstats()` assumes block stats allocation happened first.
- Store-buffer copyout must handle wraparound and caller-provided buffer size precisely.
<!-- END FILE RESEARCH: sources/os/darwin/xnu/bsd/vfs/vfs_io_compression_stats.c -->

<!-- BEGIN FILE RESEARCH: sources/os/darwin/xnu/bsd/vfs/vfs_io_compression_stats.h -->
# File Research: sources/os/darwin/xnu/bsd/vfs/vfs_io_compression_stats.h

## Scope

This header declares the I/O compression statistics entry points and constants shared by VFS code.

## APIs And Constants

- Declares `io_compression_stats_init(void)` and `io_compression_stats(buf_t bp)`.
- Defines default/min/max compression block sizes.
- Defines optional debug logging macro `io_compression_stats_dbg`.
- Defines `struct iocs_store_buffer`.
- Defines store-buffer sizing and notification thresholds.

## Dependencies And Role

Includes buffer and vnode headers. It is consumed by code that samples buffer writes and by vnode reclamation/stat dump logic.

## Risks And Invariants

- `IO_COMPRESSION_STATS_MAX_BLOCK_SIZE` permits very large per-CPU allocations.
- `IOCS_STORE_BUFFER_SIZE` depends on `struct iocs_store_buffer_entry`, which is defined outside this header.
- The header declares `io_compression_stats_init()`, while the implementation in this group does not define it.
<!-- END FILE RESEARCH: sources/os/darwin/xnu/bsd/vfs/vfs_io_compression_stats.h -->