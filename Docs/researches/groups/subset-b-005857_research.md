# Research: subset-b-005857

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fs/super.h -->
# sources/distributed-fs/ceph-client/include/linux/fs/super.h

Purpose: declares the inline VFS superblock helpers that higher-level filesystem code uses for freeze exclusion, read-only checks, encoding checks, and block-size/freeze operations. It is the small operational companion to `fs/super_types.h`, keeping common `struct super_block` state manipulation out of open-coded call sites.

Important APIs and types: `sb_start_write()`, `sb_end_write()`, `sb_start_pagefault()`, `sb_end_pagefault()`, `sb_start_intwrite()`, and `sb_end_intwrite()` wrap the three freeze levels in `sb->s_writers.rw_sem`. `sb_start_write_trylock()` and `sb_start_intwrite_trylock()` expose nonblocking acquisition. `sb_write_started()`/`sb_write_not_started()` are lockdep-oriented assertions. `DEFINE_GUARD(super_write, ...)` enables scoped write protection. `sb_rdonly()`, `sb_is_blkdev_sb()`, `sb_encoding()`, `sb_same_encoding()`, `sb_has_encoding()`, `sb_set_blocksize()`, `sb_min_blocksize()`, `freeze_super()`, and `thaw_super()` are the public utility surface.

Control flow: write paths call a start helper before dirtying pages/inodes or running metadata updates and call the matching end helper when complete. Freezing takes the inverse side of the percpu rwsems in increasing freeze levels, so callers must preserve documented lock ordering: normal writes are outermost to inode locks, pagefault protection sits near `mmap_lock`, and internal filesystem writes rank below pagefault protection.

State and persistence: this header does not persist data directly, but it protects persistent filesystem mutations against freeze/thaw transitions. The unicode helpers read `s_encoding` and `s_encoding_flags`, returning no-op compatibility in non-unicode builds. Dependencies include percpu rwsems, lockdep, unicode maps, block device superblock state, and the `super_block` layout.

Risks and test signals: the main risks are unbalanced start/end pairs, using the wrong freeze level, lock-order regressions with `s_umount`, and assuming lockdep helpers are definitive in non-lockdep builds. Tests should cover freeze while concurrent write/pagefault/internal writers run, trylock failure behavior on frozen filesystems, read-only remount checks, unicode casefold compatibility, and block-size setup error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fs/super.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fs/super_types.h -->
# sources/distributed-fs/ceph-client/include/linux/fs/super_types.h

Purpose: defines the VFS superblock object model, superblock operation table, freeze state, freeze holder flags, and public/internal superblock flags. This is the central type contract shared by filesystem implementations, mount code, writeback, quota, exportfs, fsnotify, fscrypt, fsverity, and sync/shutdown paths.

Important APIs and types: `struct sb_writers` tracks freeze state, kernel/userspace freeze nesting counts, freeze owner, and per-level percpu rwsems. `enum freeze_holder` distinguishes kernel and userspace freezes and whether nesting or exclusive owner thawing is allowed. `struct super_operations` defines filesystem callbacks for inode lifecycle, writeback, freeze/thaw, statfs, mount option display, quota I/O, shrinker callbacks, device removal, shutdown, and filesystem error reporting. `struct super_block` stores identity, operation pointers, mount/root links, block device and backing info, quota state, freeze writers, filesystem-private `s_fs_info`, timestamp bounds, fsnotify state, UUID/sysfs identity, dentries/inodes LRUs, writeback lists, sync lock, stack depth, namespace ownership, and pending filesystem error accounting.

Control flow: filesystem mount/fill-super code initializes `struct super_block`, populates operation vectors and filesystem-private state, and VFS subsystems subsequently drive callbacks. Freeze/thaw callbacks coordinate with `super.h` writer helpers. Writeback uses `s_inodes_wb` and `s_wb_err`; memory pressure uses per-superblock shrinkers and LRUs; unmount/shutdown paths consult flags such as `SB_ACTIVE`, `SB_BORN`, `SB_DYING`, and `SB_DEAD`.

State and persistence: superblocks are in-memory anchors for persistent filesystem instances. They carry durable identity (`s_dev`, `s_uuid`, `s_magic`, `s_id`) and runtime policy (`s_flags`, `s_iflags`, timestamp limits, encoding flags, quota masks). Persistent changes are delegated to filesystem callbacks, but this structure governs visibility, locking, writeback, and lifecycle.

Dependencies and integration points: depends on `fs_dirent.h`, errseq, list LRUs, uid/gid namespaces, quota, fscrypt/fsverity optional fields, fsnotify optional fields, xattr handlers, export operations, backing devices, MTD/block devices, and workqueues. Stackable filesystems depend on `s_stack_depth`; user namespace and idmapped mount policy depend on `s_user_ns` and `SB_I_NOIDMAP`.

Risks and test signals: changes are high blast radius because field lifetime, lock ordering, and flag semantics are assumed across VFS. Risks include callback signature drift, stale flag interpretation, incorrect freeze nesting, use-after-free through mounts/dentries, and mismatched optional config fields. Test with broad filesystem compile matrices, mount/remount/unmount, freeze/thaw nesting, quota-on/off, writeback error reporting through `syncfs`, fsnotify marks, fscrypt keyring teardown, and stacked filesystem depth checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fs/super_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fs_api.h -->
# sources/distributed-fs/ceph-client/include/linux/fs_api.h

Purpose: this compatibility header currently includes `<linux/fs.h>` and defines no additional API of its own. It likely exists as a source-level include shim for code that wants a stable `fs_api.h` name while consuming the normal Linux VFS declarations.

Important APIs and functions: all usable declarations come from `linux/fs.h`; this file contributes no types, macros, functions, state, or control flow.

State and persistence: none. Dependencies are entirely transitive through `linux/fs.h`.

Integration points, risks, and test signals: the risk is accidental expectation that this header provides a narrower or independent API contract. Include-order tests and build coverage are the only meaningful signals; deleting or expanding it should be checked against out-of-tree or generated code that includes `linux/fs_api.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fs_api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fs_context.h -->
# sources/distributed-fs/ceph-client/include/linux/fs_context.h

Purpose: defines the modern VFS mount API context used to collect mount/reconfigure parameters, parse them, create or find a superblock, and report structured mount diagnostics. It is the interface behind `fsopen`, `fsconfig`, `fsmount`, new-mount helpers, submounts, and remount/reconfigure.

Important APIs and types: `enum fs_context_purpose` separates explicit mounts, submounts, and reconfiguration. `enum fs_context_phase` records UAPI state transitions from parameter collection through creation/reconfiguration or failure. `enum fs_value_type` and `struct fs_parameter` describe parsed parameter values. `struct fs_context` stores operation vectors, mutex, filesystem type, private context, root, namespaces, credentials, source string, security state, proposed superblock flags, internal flags, phase, and behavior booleans. `struct fs_context_operations` supplies `free`, `dup`, `parse_param`, `parse_monolithic`, `get_tree`, and `reconfigure`. Public helpers include `fs_context_for_mount()`, `fs_context_for_reconfigure()`, `fs_context_for_submount()`, `vfs_parse_fs_param()`, `vfs_get_tree()`, `get_tree_nodev()`, `get_tree_single()`, `get_tree_keyed()`, `get_tree_bdev()`, `setup_bdev_super()`, `put_fs_context()`, and logging macros `infof`, `warnf`, `errorf`, and `invalf`.

Control flow: a caller allocates a context for a purpose, feeds it parameters via `vfs_parse_fs_param()` or monolithic parsing, then calls `vfs_get_tree()` so the filesystem's `get_tree` callback can instantiate or reuse a superblock. Reconfigure begins with an existing root and uses `reconfigure` after parameter collection. The phase field protects UAPI ordering. Logging stores bounded messages in a refcounted `fc_log` that can be shared with subordinate mounts.

State and persistence: `fs_context` is transient mount/reconfigure state, but it controls persistent superblock creation and remount policy by carrying `sb_flags`, `sb_flags_mask`, `s_iflags`, security options, proposed `s_fs_info`, and filesystem-private parsing state. It owns references to namespaces, credentials, source strings, parameter files/names, and log storage until `put_fs_context()`.

Dependencies and integration points: integrates with `fs_parser.h`, LSM mount option handling, block-device setup, mount namespaces, pid/net/user namespaces, old `mount(2)` compatibility, filesystem-specific parameter structs, and the fscontext file operations for the UAPI fd.

Risks and test signals: risks include phase transition bugs, leaked parameter references, double-free between `ops->free` and common teardown, wrong `sb_flags_mask` on remount, inconsistent old/new mount API parsing, and missing log diagnostics. Tests should exercise `fsopen/fsconfig/fsmount`, legacy mount strings, submount duplication, failed `get_tree`, reconfigure flag masks, invalid source parameters, security option propagation, and concurrent UAPI access under `uapi_mutex`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fs_context.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fs_dirent.h -->
# sources/distributed-fs/ceph-client/include/linux/fs_dirent.h

Purpose: defines stable conversions between VFS/userspace directory entry file types and common filesystem on-disk file type values. It centralizes the low three-bit file type convention shared by many Linux filesystems.

Important APIs and types: `S_DT_SHIFT`, `S_DT()`, and `S_DT_MASK` derive dirent type bits from `umode_t`. `DT_*` constants describe userspace `getdents(2)`/`readdir(3)` values, while `FT_*` constants describe common on-disk file types. `fs_ftype_to_dtype()`, `fs_umode_to_ftype()`, and `fs_umode_to_dtype()` are implemented in `fs/fs_dirent.c`.

Control flow: filesystems convert inode modes to on-disk or userspace directory types when constructing directory entries, and convert stored `FT_*` values to `DT_*` when returning entries. Whiteouts are not stored as a separate on-disk type here and are exposed as character-device style directory entries by filesystems that use whiteouts.

State and persistence: the `FT_*` constants are persistent on-disk ABI for filesystems using this common layout, and the `DT_*` values are userspace ABI. The file deliberately warns that values must not change.

Dependencies and integration points: depends only on Linux stat and type definitions, but is included by superblock type definitions and filesystem directory code. Integration points include ext-like directory formats, VFS `filldir` paths, and compatibility with libc `dirent.h`.

Risks and test signals: risks are ABI/layout changes, confusing `DT_WHT` with persistent `FT_*`, and handling unknown/reserved bits incorrectly. Tests should cover all mode-to-type conversions, invalid on-disk values, whiteout exposure, and cross-filesystem directory listings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fs_dirent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fs_parser.h -->
# sources/distributed-fs/ceph-client/include/linux/fs_parser.h

Purpose: declares the generic filesystem parameter parser used by `fs_context`-based mount implementations. It lets filesystems describe accepted parameter names, expected value types, flags, and enum tables in a compact table-driven format.

Important APIs and types: `struct constant_table` maps strings to integer values. `fs_param_type` is the validation/conversion function type used by built-in validators such as `fs_param_is_bool`, integer parsers, enum parser, string parser, block-device lookup, fd parser, uid/gid parser, and file-or-string parser. `struct fs_parameter_spec` describes one option name, parser, returned option id, flags such as `fs_param_neg_with_no`, `fs_param_can_be_empty`, and `fs_param_deprecated`, plus type-specific data. `struct fs_parse_result` returns negation and parsed scalar/id values. `fs_parse()`, `__fs_parse()`, `fs_lookup_param()`, `lookup_constant()`, and optional `fs_validate_description()` are the public functions. Constructor macros `fsparam_flag()`, `fsparam_bool()`, `fsparam_u32()`, `fsparam_enum()`, `fsparam_string_empty()`, and related helpers populate spec tables.

Control flow: filesystem `parse_param` callbacks pass their spec table and incoming `struct fs_parameter` to `fs_parse()`. The parser matches by name, handles `no` negation where allowed, invokes the expected type converter, and returns the option id for a switch statement. Block-device/file/path parameters may be looked up with `fs_lookup_param()`.

State and persistence: no persistent state is owned here. Parsed values affect transient mount contexts and ultimately superblock state if accepted. Deprecated flags and validation support are build-time/runtime diagnostics for parser table quality.

Dependencies and integration points: tightly integrated with `fs_context.h`, mount API UAPI value types, id mapping for uid/gid parsing, path lookup, block device opening, and filesystem-specific option enums.

Risks and test signals: risks include accepting malformed values, incorrect negation semantics, enum table drift, leaking filename/file references, and parser tables that forget terminators or duplicate names. Tests should cover every parameter type, `nofoo` handling, empty strings, deprecated options, monolithic mount strings, validation-enabled builds, and filesystem-specific option switch coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fs_parser.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fs_pin.h -->
# sources/distributed-fs/ceph-client/include/linux/fs_pin.h

Purpose: defines the small VFS pin object used to attach killable references to superblocks and mounts. Pins let teardown paths find and kill outstanding objects that are tied to a filesystem or mount lifecycle.

Important APIs and types: `struct fs_pin` contains a waitqueue, completion flag, hlist nodes for superblock and mount lists, and a `kill` callback. `init_fs_pin()` initializes the waitqueue and list nodes and installs the callback. `pin_insert()`, `pin_remove()`, and `pin_kill()` are implemented out of line.

Control flow: users initialize a pin with a subsystem-specific kill callback, insert it against a `vfsmount`, and remove or kill it during teardown. `pin_kill()` invokes the callback and coordinates with waiters through the embedded waitqueue and `done` flag.

State and persistence: pins are in-memory lifetime state only. They protect resources that may indirectly refer to persistent filesystem data by ensuring teardown sees and drains them.

Dependencies and integration points: depends on wait queues, hlist nodes, and `vfsmount`. It integrates with superblock `s_pins` and mount pin lists.

Risks and test signals: risks are list corruption, missed wakeups, double kill/remove, and callbacks that sleep or recurse in invalid contexts. Tests should stress unmount with active pins, concurrent remove/kill, callback failure behavior, and leak detection after namespace teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fs_pin.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fs_stack.h -->
# sources/distributed-fs/ceph-client/include/linux/fs_stack.h

Purpose: declares helper functions for stackable filesystems to copy inode attributes from lower filesystems to upper inodes without requiring the caller to hold `i_rwsem`.

Important APIs and functions: `fsstack_copy_attr_all()` and `fsstack_copy_inode_size()` are implemented in `fs/stack.c`. Inline helpers `fsstack_copy_attr_atime()` and `fsstack_copy_attr_times()` copy atime, mtime, and ctime through the modern inode timestamp accessors.

Control flow: overlay/stacking filesystems call these helpers after lower-inode changes or during lookup/revalidation to synchronize visible upper inode metadata. The file intentionally avoids locking requirements because stackable filesystems frequently operate while holding their own ordering constraints.

State and persistence: helpers update in-memory inode attributes; persistence of upper metadata is filesystem-specific. Size copying can affect writeback and stat results, while timestamp copying affects cache coherency and userspace-visible metadata.

Dependencies and integration points: depends on `linux/fs.h` inode timestamp helpers and stackable filesystem code such as overlay-like layers.

Risks and test signals: risks include stale upper attributes, racing lower changes, copying too much metadata, and timestamp granularity mismatches. Tests should cover stat consistency after lower writes, truncation/size updates, timestamp updates, and stacked filesystem behavior under concurrent operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fs_stack.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fs_struct.h -->
# sources/distributed-fs/ceph-client/include/linux/fs_struct.h

Purpose: defines `struct fs_struct`, the per-task/shared filesystem view containing root, current working directory, umask, and exec state. It is the kernel-side state behind `chroot`, `chdir`, `umask`, clone sharing of filesystem context, and task exit cleanup.

Important APIs and types: `struct fs_struct` stores a user count, seqlock, umask, `in_exec`, and `struct path` values for root and pwd. Public functions include `exit_fs()`, `set_fs_root()`, `set_fs_pwd()`, `copy_fs_struct()`, `free_fs_struct()`, `unshare_fs_struct()`, and `current_chrooted()`. `get_fs_root()` and `get_fs_pwd()` take the seqlock in exclusive-read style, copy the path, and take a path reference. `current_umask()` reads `current->fs->umask`.

Control flow: fork/clone either shares or copies `fs_struct`; path-changing syscalls update root/pwd with seqlock protection; users retrieve stable path references through the inline getters; `exit_fs()` drops the task's reference on exit.

State and persistence: this is process runtime state, not filesystem persistence. It controls pathname resolution and file creation permissions, making it security-sensitive despite being transient.

Dependencies and integration points: depends on scheduler task state, path references, spin/seqlock infrastructure, VFS path lookup, namespace/chroot handling, and exec code that tracks `in_exec`.

Risks and test signals: risks include path reference leaks, use-after-free if copied without `path_get`, races during chroot/chdir, and incorrect sharing after `unshare(CLONE_FS)`. Tests should cover multithreaded chdir/chroot, clone with and without `CLONE_FS`, umask inheritance, exec-time behavior, and namespace teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fs_struct.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fscache-cache.h -->
# sources/distributed-fs/ceph-client/include/linux/fscache-cache.h

Purpose: declares the FS-Cache backend interface used by cache implementations to register caches and service netfs cookies, volumes, operations, invalidations, resizing, withdrawal, and accounting. It is paired with backend documentation and complements the netfs-facing `fscache.h`.

Important APIs and types: `enum fscache_cache_state` tracks cache lifecycle from not-present through preparing, active, I/O error, and withdrawn. `struct fscache_cache` stores operation vectors, list linkage, provider-private state, refcount, active volume/access/object counters, debug id, state, and name. `struct fscache_cache_ops` supplies cache-provider callbacks for volume acquisition/free, cookie lookup/withdraw, cookie resize, invalidation, operation start, and write preparation. Public functions include `fscache_acquire_cache()`, `fscache_add_cache()`, `fscache_withdraw_cache()`, `fscache_withdraw_volume()`, `fscache_withdraw_cookie()`, `fscache_io_error()`, reference helpers for volumes/cookies, and `fscache_wait_for_operation()`. Inline helpers expose cookie state, key storage, cache-resource cookie, object count accounting, and optional stats counters.

Control flow: a backend acquires and adds a cache, implements callbacks, counts objects while live, starts operations on requested cookies, and withdraws volumes/cookies during shutdown or error. Access counters and waitqueues coordinate teardown so cache structures are not freed while objects or operations remain.

State and persistence: backend-private persistent cache contents are outside this header, but `fscache_cache` owns in-memory lifecycle and accounting state for those contents. `fscache_cookie_state()` uses acquire semantics to order cookie state reads against cookie contents.

Dependencies and integration points: integrates with `fscache.h`, netfs cache resources, workqueues, waitqueues, trace enums, cachefiles-like providers, `/proc/fs/fscache`, and optional stats.

Risks and test signals: risks include object-count leaks that block withdrawal, cache state races after I/O error, callback implementations that ignore access counts, and memory ordering bugs around cookie state. Tests should cover cache add/remove, backend I/O error, concurrent cookie lookup/invalidate/withdraw, resize during active operations, stats-enabled/disabled builds, and teardown waiting for objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fscache-cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fscache.h -->
# sources/distributed-fs/ceph-client/include/linux/fscache.h

Purpose: declares the netfs-facing FS-Cache API used by filesystems such as NFS and SMB to cache remote file contents through a generic cache backend. It provides volume/cookie lifecycle, coherency updates, invalidation, cache read/write operations, and no-op stubs when FS-Cache is disabled.

Important APIs and types: `struct fscache_volume` represents a cached filesystem/server volume with refcounts, active cookie/access counts, key, cache pointer, coherency bytes, flags, and work item. `struct fscache_cookie` represents one cached object/file with refcounts, active/access counters, volume, backend-private state, hash/proc/commit/work links, object size, LRU timestamp, flags, state, advice, key, and auxiliary coherency data. `enum fscache_cookie_state`, `enum fscache_want_state`, advice flags, and invalidation flags define lifecycle and operation intent. Public wrappers include `fscache_acquire_volume()`, `fscache_relinquish_volume()`, `fscache_acquire_cookie()`, `fscache_use_cookie()`, `fscache_unuse_cookie()`, `fscache_relinquish_cookie()`, `fscache_update_cookie()`, `fscache_resize_cookie()`, `fscache_invalidate()`, `fscache_begin_read_operation()`, `fscache_read()`, `fscache_begin_write_operation()`, `fscache_write()`, `fscache_end_operation()`, `fscache_write_to_cache()`, `fscache_clear_page_bits()`, and `fscache_note_page_release()`.

Control flow: a netfs acquires a volume during mount, acquires per-inode cookies with index keys and aux data, marks cookies in use while files are open or I/O is active, begins read/write operations to obtain `netfs_cache_resources`, issues cache I/O through backend `netfs_cache_ops`, updates aux data/size on close or metadata changes, invalidates on direct/local writes, and relinquishes cookies/volume on inode/superblock teardown. Wrappers compile to cheap validity checks and disabled-mode no-ops or `-ENOBUFS`.

State and persistence: in-memory volume/cookie state mirrors cache backend objects. Auxiliary data and object size encode coherency; invalidation counters let callers detect operations that completed against stale state. Persistent cached bytes are backend-owned and can be retired or invalidated through relinquish/invalidate paths.

Dependencies and integration points: depends on VFS address spaces, writeback, netfs helper library, `netfs_cache_resources`, backend operations from `fscache-cache.h`, page/folio private bits, and network filesystem mount/inode lifecycle code.

Risks and test signals: risks include using cookies after relinquish, missing invalidations after local writes, stale aux data, page-bit leaks causing hung writeback, operation-resource misuse, and behavior differences between enabled and disabled builds. Tests should cover mount/unmount volume lifecycle, open/close with writes, cache read hits/misses/holes, DIO invalidation, resize/truncate, backend withdrawal during I/O, and builds with `CONFIG_FSCACHE` off/module/built-in.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fscache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fscrypt.h -->
# sources/distributed-fs/ceph-client/include/linux/fscrypt.h

Purpose: declares the filesystem encryption interface for per-file contents, filenames, symlinks, policy/key management, inline crypto, and VFS operation hooks. Filesystems include this header to integrate with `fs/crypto` while still compiling cleanly when encryption support is disabled.

Important APIs and types: `FSCRYPT_CONTENTS_ALIGNMENT` defines the 16-byte encryption alignment requirement. `struct fscrypt_str` and `struct fscrypt_name` carry plaintext/on-disk encrypted filenames, hashes, crypto buffers, and no-key state. `struct fscrypt_operations` is the filesystem callback table for inode-info offset, bounce-page needs, subblock support, legacy key prefixes, context get/set, dummy policy lookup, empty-dir checks, stable inode validation, and encrypted-data block device discovery. Public APIs cover dentry revalidation and movement, bounce page/folio handling, pagecache and in-place block encryption/decryption, policy ioctls, dummy encryption mount parsing/display, keyring ioctls, inode key setup/drop/free, filename encryption/matching/display conversion, bio decryption, zeroout, file open, link/rename/lookup/readdir/setattr/setflags preparation, encrypted symlink handling, symlink getattr, and inline crypto bio helpers.

Control flow: filesystem mount code calls `fscrypt_set_ops()`. New encrypted inode creation calls `fscrypt_prepare_new_inode()` and persists context with `fscrypt_set_context()`. Directory lookup/readdir paths call `fscrypt_prepare_lookup()` or partial variants to decide plaintext versus no-key names and set dentry flags. VFS operations use `fscrypt_prepare_link()`, `fscrypt_prepare_rename()`, `fscrypt_prepare_setattr()`, and `fscrypt_file_open()` to enforce key and policy constraints. I/O paths choose fs-layer encryption, inline crypto, or disabled behavior through `fscrypt_inode_uses_*` helpers.

State and persistence: persistent state is the fscrypt context stored by the filesystem and policy/key material managed by `fs/crypto`; this header defines the callback contract for retrieving and setting it. In-memory state includes per-inode `fscrypt_inode_info` stored at a filesystem-specific offset, superblock master keyrings, no-key dentry flags, bounce pages, and inline-crypto bio contexts.

Dependencies and integration points: integrates with VFS inode/dentry/file operations, UAPI fscrypt ioctls, block crypto, bio and folio/pagecache paths, symlink handling, filesystem mount options, keyrings, directory hashing, and dentry revalidation. Disabled stubs deliberately return `-EOPNOTSUPP` when encrypted state is encountered while allowing unencrypted filesystems to compile without ifdefs.

Risks and test signals: risks include policy/context mismatch, creating names from no-key dentries, missing truncate restrictions without keys, unstable inode-number IV modes, incorrect inline crypto merge limits, bounce-page leaks, and divergence between enabled and disabled builds. Tests should cover encrypted and unencrypted directories, key add/remove and no-key lookup invalidation, link/rename policy constraints, symlink encryption, pagecache and direct I/O, inline crypto fallback, dummy encryption mount options, context size limits, and fscrypt-disabled behavior on encrypted metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fscrypt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fserror.h -->
# sources/distributed-fs/ceph-client/include/linux/fserror.h

Purpose: declares the filesystem error reporting interface used to route I/O, media-loss, metadata, and shutdown errors to superblock-level reporting and fsnotify/filesystem callbacks.

Important APIs and types: `enum fserror_type` distinguishes buffered read/write, direct I/O read/write, data lost, and metadata errors. `struct fserror_event` packages async work, superblock, optional inode, byte range, error type, and negative errno. `fserror_mount()` and `fserror_unmount()` manage superblock error-reporting lifecycle. `fserror_report()` is the generic reporter, while inline helpers specialize common cases: `fserror_report_io()`, `fserror_report_data_lost()`, `fserror_report_file_metadata()`, `fserror_report_metadata()`, and `fserror_report_shutdown()`.

Control flow: code detecting an error calls a helper with the affected inode/superblock, range, type, error, and allocation mask. The event can be queued via its work item and later delivered to superblock error reporting, including `super_operations.report_error` when a filesystem supplies it.

State and persistence: events are transient in-memory records, but they report failures that may imply persistent corruption or data loss. `super_block.s_pending_errors` accounts in-flight reporting. Filesystems may persist additional health state in their callback.

Dependencies and integration points: depends on VFS superblock/inode types, workqueues, GFP allocation context, and the `report_error` callback in `struct super_operations`.

Risks and test signals: risks include reporting from reclaim/IO contexts with unsuitable GFP flags, losing range/type fidelity, flooding reports, and unmount races with queued events. Tests should inject buffered/direct I/O errors, metadata corruption reports, data-loss notifications, shutdown reporting, allocation failures, and unmount while events are pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fserror.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fsi-occ.h -->
# sources/distributed-fs/ceph-client/include/linux/fsi-occ.h

Purpose: declares the FSI OCC client interface for submitting requests to IBM On-Chip Controller devices and defines the known OCC response/status codes.

Important APIs and types: response constants include in-progress, success, invalid command/length/data, checksum error, internal error, bad state, and several critical exception classes. `OCC_MAX_RESP_WORDS` caps responses at 2048 words. `fsi_occ_submit()` sends an opaque request buffer to a device and returns an opaque response with an in/out response length.

Control flow: OCC client drivers prepare a request, call `fsi_occ_submit()`, and interpret the response status codes and payload. The function abstracts the lower FSI/SBEFIFO transport and device binding.

State and persistence: no persistent state is defined here. OCC state is device/firmware runtime state, while request/response buffers are caller-owned transient data.

Dependencies and integration points: depends only on `struct device` and integrates with FSI OCC driver code, hwmon/power-management clients, and SBEFIFO transport where present.

Risks and test signals: risks include response length overflow, endian/protocol mismatch in callers, command-in-progress polling errors, and misclassification of critical OCC states. Tests should cover all response codes, maximum-sized responses, short responses, transport failures, and concurrent submissions if the provider supports them.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fsi-occ.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fsi-sbefifo.h -->
# sources/distributed-fs/ceph-client/include/linux/fsi-sbefifo.h

Purpose: declares the FSI SBEFIFO client interface for sending big-endian command streams to IBM Self-Boot Engine FIFO devices and parsing command status.

Important APIs and types: command constants cover OCC SRAM put/get and SBE FFDC retrieval; `SBEFIFO_MAX_FFDC_SIZE` caps failure data capture size. `sbefifo_submit()` sends a `__be32` command buffer and returns a `__be32` response buffer with in/out length. `sbefifo_parse_status()` validates response status for a command and returns payload length.

Control flow: a client builds a command stream, submits it to the target device, then calls the status parser to separate protocol status from payload bytes. OCC transport code can use this lower layer for OCC SRAM commands.

State and persistence: no persistent kernel state is declared. The device/firmware FIFO state is external and transient across command execution.

Dependencies and integration points: depends on `struct device` and big-endian integer types; integrates with FSI SBEFIFO drivers and OCC/diagnostic clients.

Risks and test signals: risks include incorrect response length units, endian mistakes, not bounding FFDC retrieval, and command/status mismatch. Tests should cover successful commands, status error responses, malformed short responses, max FFDC reads, and concurrent or timeout behavior in provider code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fsi-sbefifo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fsi.h -->
# sources/distributed-fs/ceph-client/include/linux/fsi.h

Purpose: defines the public device/driver interface for IBM FSI devices, including FSI device identity, driver registration, device I/O helpers, direct slave range access, and minor allocation for FSI character devices.

Important APIs and types: `struct fsi_device` embeds `struct device` and records engine type, version, unit, slave pointer, address, and size. `struct fsi_device_id` plus `FSI_DEVICE()` and `FSI_DEVICE_VERSIONED()` support driver matching. `struct fsi_driver` contains probe/remove callbacks, a generic `device_driver`, and an id table. Helpers include `fsi_get_drvdata()`, `fsi_set_drvdata()`, `fsi_device_read()`, `fsi_device_write()`, `fsi_device_peek()`, `fsi_driver_register()`, `fsi_driver_unregister()`, `module_fsi_driver()`, `fsi_slave_claim_range()`, `fsi_slave_release_range()`, `fsi_slave_read()`, `fsi_slave_write()`, `fsi_get_new_minor()`, and `fsi_free_minor()`.

Control flow: bus discovery creates `fsi_device` instances; FSI drivers register an id table and probe matching devices; drivers issue address-relative reads/writes or claim direct slave ranges for broader access. Character device users obtain minors by FSI device type.

State and persistence: state is runtime bus/device binding, driver data, claimed slave address ranges, and allocated device minors. Hardware register contents persist in external FSI-attached devices but are not modeled here.

Dependencies and integration points: depends on Linux driver core and integrates with FSI bus core, OCC/SBEFIFO/SCOM/cfam character devices, module aliasing, and platform firmware discovery.

Risks and test signals: risks include overlapping slave range claims, size/address validation gaps, minor leaks, version matching mistakes, and unsafe direct access. Tests should cover driver bind/unbind, read/write sizes and alignment, peek behavior, range claim conflicts, minor allocation/free, and module auto-loading from FSI ids.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fsi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fsl-diu-fb.h -->
# sources/distributed-fs/ceph-client/include/linux/fsl-diu-fb.h

Purpose: defines the userspace ioctl ABI and kernel register/descriptor layouts for the Freescale Display Interface Unit framebuffer driver.

Important APIs and types: userspace structs `mfb_chroma_key` and `aoi_display_offset` support chroma-key and area-of-interest offset ioctls. `MFB_SET_*` and `MFB_GET_*` ioctl constants control alpha, brightness, chroma key, AOI display position, pixel format, and legacy MPC5121 gamma. Backward-compatible old pixel-format ioctl numbers are retained. Kernel-only `struct diu_ad` describes packed DDR area descriptors for display planes, and `struct diu` maps DIU registers. `MFB_MODE0` and `MFB_MODE1` define supported display modes.

Control flow: framebuffer ioctl handlers copy userspace structs, update software state, and program DIU descriptors/registers. Display enable uses descriptor addresses and register fields to configure planes, palette/gamma/cursor/background, display size, sync parameters, interrupts, and color bars.

State and persistence: ioctl settings and descriptors are runtime display state, not persistent storage. Descriptor layout is hardware ABI in DMA-visible memory and must match endian/packing requirements.

Dependencies and integration points: depends on Linux ioctl/type definitions and integrates with the DIU framebuffer driver, platform device setup, user framebuffer utilities, and hardware display timing code.

Risks and test signals: risks include ioctl ABI collisions (`MFB_SET_CHROMA_KEY` and legacy gamma share numbers with different payloads), packed descriptor endian mistakes, old pixel-format compatibility, and programming unsupported modes. Tests should cover all ioctls, legacy ioctl numbers, descriptor DMA layout, endian platforms, suspend/resume display restore, and invalid AOI/pixfmt inputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fsl-diu-fb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fsl/bestcomm/ata.h -->
# sources/distributed-fs/ceph-client/include/linux/fsl/bestcomm/ata.h

Purpose: declares the MPC52xx BestComm ATA DMA task wrapper used by the PATA driver to configure and run ATA receive/transmit DMA buffer descriptors.

Important APIs and types: `struct bcom_ata_bd` contains status, source physical address, and destination physical address. Public functions are `bcom_ata_init()`, `bcom_ata_rx_prepare()`, `bcom_ata_tx_prepare()`, `bcom_ata_reset_bd()`, and `bcom_ata_release()`.

Control flow: the ATA driver allocates a task with queue length and max buffer size, prepares it for RX or TX per command, queues descriptors through generic BestComm helpers, resets descriptor state between commands, and releases the task on teardown.

State and persistence: state is runtime DMA task and descriptor ring content. Physical addresses refer to DMA buffers and FIFO/register endpoints; no persistent storage is owned here.

Dependencies and integration points: depends on `struct bcom_task` from `bestcomm.h`, BestComm engine/private task images, and the MPC52xx ATA/PATA driver.

Risks and test signals: risks include wrong RX/TX preparation, descriptor address direction mistakes, stale status bits after reset, and queue length/max buffer mismatches. Tests should cover PIO fallback, DMA read/write, error reset, task IRQ handling, unaligned/scattered transfers, and release during probe failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fsl/bestcomm/ata.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fsl/bestcomm/bestcomm.h -->
# sources/distributed-fs/ceph-client/include/linux/fsl/bestcomm/bestcomm.h

Purpose: provides the public MPC52xx BestComm DMA task API and generic buffer-descriptor ring helpers used by ATA, FEC Ethernet, PSC/audio, and other task-specific wrappers.

Important APIs and types: `struct bcom_bd` is a variable-sized generic descriptor with status and task-specific data words. `struct bcom_task` records task number, flags, IRQ, descriptor ring virtual/physical addresses, per-descriptor cookies, producer/consumer indices, ring length, descriptor size, and task-private data. `bcom_enable()`, `bcom_disable()`, and `bcom_get_task_irq()` control tasks. Ring helpers include `bcom_queue_empty()`, `bcom_queue_full()`, `bcom_get_bd()`, `bcom_buffer_done()`, `bcom_prepare_next_buffer()`, `bcom_submit_next_buffer()`, and `bcom_retrieve_buffer()`.

Control flow: client drivers allocate task-specific wrappers, prepare the next descriptor, fill DMA-specific fields, submit it with an optional cookie, and handle IRQs by checking `bcom_buffer_done()` and retrieving completed descriptors. `bcom_submit_next_buffer()` writes the cookie, issues a memory barrier, sets `BCOM_BD_READY`, advances the producer index, and optionally enables the hardware task.

State and persistence: runtime state is descriptor-ring ownership, producer/consumer indices, cookies, status bits, and hardware task enable state. The ring is DMA-visible; `BCOM_BD_READY` mediates ownership between CPU and BestComm.

Dependencies and integration points: integrates with BestComm engine allocation/loading code, task-specific ATA/FEC/GEN_BD wrappers, device IRQ handling, DMA-mapped buffers, and drivers under ATA/network/audio.

Risks and test signals: risks include descriptor-size pointer arithmetic mistakes, missing barriers before hardware sees descriptors, ring full/empty ambiguity, cookie/index desynchronization, and enabling tasks too early. Tests should cover ring wraparound, full/empty behavior, concurrent IRQ completion, task enable/disable, descriptor status propagation, and DMA transfer stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fsl/bestcomm/bestcomm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fsl/bestcomm/bestcomm_priv.h -->
# sources/distributed-fs/ceph-client/include/linux/fsl/bestcomm/bestcomm_priv.h

Purpose: defines the private BestComm engine/task internals used by the engine driver and intermediate task wrappers: SRAM zones, task descriptor tables, task image format, descriptor bitfields, pragmas, initiator IDs/priorities, low-level task allocation/loading, and register helpers.

Important APIs and types: constants size SRAM regions for task contexts, variables, increments, FDTs, and task descriptors. `struct bcom_tdt` mirrors a hardware task descriptor table entry. `struct bcom_engine` stores OF node, SDMA registers, register base, TDT/context/variable/FDT pointers, and lock. `struct bcom_task_header` describes task images with `BCOM_TASK_MAGIC`. Many `BCOM_PRAGMA_*`, `BCOM_INITIATOR_*`, and `BCOM_IPR_*` constants encode hardware scheduling and bus behavior. Private functions include `bcom_task_alloc()`, `bcom_task_free()`, `bcom_load_image()`, and `bcom_set_initiator()`. Inline helpers control prefetch, task enable/disable, descriptor/variable access, descriptor classification, initiator rewriting, task pragmas, auto-start, and TCR initiator fields.

Control flow: engine setup maps registers and allocates SRAM-backed tables. Task wrappers allocate a task, load a task image into SRAM, adjust initiators/pragmas, and program task control registers. Runtime helpers directly read/write big-endian SDMA registers and convert SRAM physical addresses back to virtual pointers.

State and persistence: state is hardware task programming and SRAM-resident descriptor/context tables. It is volatile and platform-specific, but mistakes can corrupt DMA execution across devices.

Dependencies and integration points: depends on PowerPC I/O helpers, MPC52xx SDMA register definitions, OF nodes, BestComm SRAM allocator, and public `bestcomm.h`. It is intentionally not for ordinary device drivers.

Risks and test signals: risks include SRAM layout misalignment, wrong task image sizes, incorrect initiator/priorities, one-way prefetch disable side effects, endian register access errors, and invalid descriptor rewriting. Tests should cover engine probe/remove, task load validation, every task wrapper, hardware IRQ/error handling, original MPC5200 ATA prefetch erratum, and suspend/resume if supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fsl/bestcomm/bestcomm_priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fsl/bestcomm/fec.h -->
# sources/distributed-fs/ceph-client/include/linux/fsl/bestcomm/fec.h

Purpose: declares BestComm task wrappers and descriptor bits for MPC52xx FEC Ethernet transmit and receive DMA.

Important APIs and types: `struct bcom_fec_bd` contains status and skb physical address. TX status bits include transmit frame done, transmit CRC, and append bad CRC. RX status bits report last buffer, broadcast/multicast, length violation, non-octet alignment, CRC error, overrun, truncation, length mask, and aggregate error mask. Functions include `bcom_fec_rx_init()`, `bcom_fec_rx_reset()`, `bcom_fec_rx_release()`, `bcom_fec_tx_init()`, `bcom_fec_tx_reset()`, and `bcom_fec_tx_release()`.

Control flow: the FEC driver creates RX/TX tasks with FIFO address and queue lengths, queues skb buffers, checks descriptor status in IRQ/NAPI paths, resets tasks on link/device reset, and releases them during teardown.

State and persistence: runtime DMA ring state tracks skb ownership and hardware error/status bits. No persistent state is stored.

Dependencies and integration points: depends on `struct bcom_task`, BestComm engine, FEC Ethernet driver, DMA mapping, and network stack skb lifecycle.

Risks and test signals: risks include mishandling RX error bits, length-mask interpretation, skb DMA address lifetime, reset while descriptors are owned by hardware, and TX CRC flags. Tests should cover RX/TX traffic, malformed frames, ring wraparound, reset under load, DMA mapping failures, and link down/up.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fsl/bestcomm/fec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fsl/bestcomm/gen_bd.h -->
# sources/distributed-fs/ceph-client/include/linux/fsl/bestcomm/gen_bd.h

Purpose: declares generic BestComm buffer-descriptor task wrappers, including PSC convenience wrappers, for devices that can use simple FIFO-to-buffer or buffer-to-FIFO DMA tasks.

Important APIs and types: `struct bcom_gen_bd` contains descriptor status and buffer physical address. RX/TX initialization functions take queue length, FIFO physical address, initiator, priority, and RX max buffer size. Reset and release functions are provided for both directions. `bcom_psc_gen_bd_rx_init()` and `bcom_psc_gen_bd_tx_init()` pick PSC-specific initiators/FIFOs from a PSC number.

Control flow: client drivers initialize generic RX/TX tasks, queue buffers with the public BestComm ring helpers, process completed descriptors in IRQ paths, reset tasks on stream stop, and release on driver teardown.

State and persistence: state is volatile DMA descriptor ring state and task configuration.

Dependencies and integration points: depends on BestComm core, `phys_addr_t`, PSC/audio/serial style drivers, and task initiator definitions from private BestComm code.

Risks and test signals: risks include wrong initiator/IPR selection, max buffer mismatch, queue cleanup during stop, and PSC wrapper mapping errors. Tests should cover audio/PSC playback and capture, ring reset, transfer underflow/overflow, probe-failure unwind, and concurrent stream start/stop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fsl/bestcomm/gen_bd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fsl/bestcomm/sram.h -->
# sources/distributed-fs/ceph-client/include/linux/fsl/bestcomm/sram.h

Purpose: declares the SRAM allocator used by the BestComm engine for task descriptors, contexts, variables, and descriptor rings that must reside in a dedicated on-chip SRAM region.

Important APIs and types: `struct bcom_sram` records base physical address, base virtual address, size, region-heap allocator pointer, and spinlock. Global `bcom_sram` points to the active allocator. Public functions are `bcom_sram_init()`, `bcom_sram_cleanup()`, `bcom_sram_alloc()`, and `bcom_sram_free()`. Inline helpers `bcom_sram_va2pa()` and `bcom_sram_pa2va()` translate within the SRAM window.

Control flow: engine probe initializes the SRAM allocator from a device tree node and owner name, BestComm setup allocates aligned regions, and cleanup frees allocator state. Runtime code translates task table physical addresses to virtual pointers when inspecting or editing task images.

State and persistence: volatile SRAM allocations are tracked by an in-memory region heap. Contents are hardware DMA/task programming state only.

Dependencies and integration points: depends on PowerPC region heap and MMU types, spinlocks, OF device nodes, and BestComm private engine code.

Risks and test signals: risks include alignment mistakes, out-of-range translations, allocator leaks, freeing invalid pointers, and global `bcom_sram` use before init. Tests should cover allocator init/failure, aligned allocations, exhaustion, free/reallocate cycles, address translation boundaries, and engine teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fsl/bestcomm/sram.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fsl/edac.h -->
# sources/distributed-fs/ceph-client/include/linux/fsl/edac.h

Purpose: provides a minimal platform-data structure for Freescale/NXP EDAC memory-controller integration.

Important APIs and types: `struct mpc85xx_edac_pci_plat_data` contains an OF node pointer identifying the PCI/controller node associated with EDAC setup.

Control flow and state: platform glue supplies this struct to EDAC probe code, which uses the node to locate registers and report errors. The header itself has no control flow and owns no persistent state.

Dependencies and integration points: integrates with Freescale EDAC drivers and Open Firmware device discovery.

Risks and test signals: risks are limited to stale or missing node pointers and platform-data ABI drift. Tests should cover EDAC probe on MPC85xx/Layerscape platforms, missing OF node handling, and controller remove/unbind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fsl/edac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fsl/enetc_mdio.h -->
# sources/distributed-fs/ceph-client/include/linux/fsl/enetc_mdio.h

Purpose: declares NXP ENETC MDIO/PCS helpers and register definitions for Clause 22/45 PHY access and SGMII PCS interface-mode programming.

Important APIs and types: PCS register constants define link timers and interface mode bits, including SGMII enable, autonegotiation, speed encoding, and half duplex. `enum enetc_pcs_speed` encodes 10/100/1000/2500 settings, with 2500 intentionally sharing the gigabit PCS encoding. `struct enetc_mdio_priv` stores ENETC hardware pointer and MDIO base. When `CONFIG_FSL_ENETC_MDIO` is reachable, read/write helpers for C22 and C45 and `enetc_hw_alloc()` are declared; otherwise stubs return `-EINVAL` or `ERR_PTR(-EINVAL)`.

Control flow: ENETC drivers allocate an `enetc_hw`, register an MDIO bus with the helper read/write callbacks, and configure PCS registers for the negotiated PHY/SerDes mode.

State and persistence: state is runtime MDIO bus and PCS register programming. No persistent storage is owned, but PHY/PCS configuration affects link behavior until reset.

Dependencies and integration points: depends on phylib `mii_bus`, ENETC hardware abstraction, device MMIO, and network driver link setup.

Risks and test signals: risks include Clause 22/45 address encoding bugs, 2.5G SGMII speed confusion, missing module dependency causing stub use, and PCS timer misprogramming. Tests should cover C22/C45 PHY reads/writes, autoneg on/off, 10/100/1000/2500 links, disabled-config stubs, and error injection for bus timeouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fsl/enetc_mdio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fsl/ftm.h -->
# sources/distributed-fs/ceph-client/include/linux/fsl/ftm.h

Purpose: defines register offsets and bit masks for the NXP/Freescale FlexTimer Module used by timer, PWM, capture/compare, and quadrature decoder drivers.

Important APIs and types: register offsets cover status/control, counter, modulo, initial count, status, mode, sync, output init/mask, combine, deadtime, external trigger, polarity, fault status/control, filters, quadrature decoder, configuration, software output, PWM load, and channel control/value registers. Bit masks define clock source/prescaler, overflow flags/interrupts, mode enable/write-protect, quadrature decoder bits, fault status, channel mode bits, and maximum prescaler.

Control flow: drivers compute offsets with `FTM_CSC(channel)` and `FTM_CV(channel)`, program mode/control registers, set clock/prescaler/modulo, enable interrupts or PWM/capture features, and handle errata such as unusable quadrature filter bits.

State and persistence: this is runtime hardware register state. No persistent kernel data is defined.

Dependencies and integration points: consumed by FTM clocksource, PWM, counter, or platform drivers that map the FTM MMIO block.

Risks and test signals: risks include register offset drift between SoCs, prescaler miscalculation, write-protect handling, and errata bits that read as tied zero. Tests should cover timer overflow interrupts, PWM generation, capture/compare, quadrature mode without filters, suspend/resume, and invalid channel bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fsl/ftm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fsl/guts.h -->
# sources/distributed-fs/ceph-client/include/linux/fsl/guts.h

Purpose: maps Freescale/NXP Global Utilities (GUTS) and Run Control/Power Management (RCPM) register layouts and bit definitions for PowerPC/QorIQ SoCs.

Important APIs and types: `struct ccsr_guts` maps POR status, GPIO, mux control, device disable, power management, reset, version, RCW, I/O delay, PAMU bypass, clock, DMA, local bus, DDR clock, SerDes, and transaction control registers. PPC86xx-specific helpers `guts_set_dmacr()` and `guts_set_pmuxcr_dma()` update DMA source/mux bits, with many PMUX/clock divider constants. `struct ccsr_rcpm_v1` and `struct ccsr_rcpm_v2` map low-power, interrupt mask, timebase, power-gating, and deep-sleep registers for different RCPM generations.

Control flow: platform and driver code maps GUTS/RCPM registers, reads boot/configuration state, selects pinmux/DMA routing, gates devices/clocks, controls sleep states, and configures timebase behavior. Inline helpers use big-endian clear/set operations for register fields.

State and persistence: state is SoC-global runtime register programming and boot status. Values may survive until reset and affect many devices, but the header owns no in-memory state.

Dependencies and integration points: depends on I/O accessors and Linux types; integrates with PowerPC platform setup, DMA, audio/SSI, display clocking, low-power suspend, reset, and device-disable code.

Risks and test signals: risks include accessing registers absent on a given chip, endian mistakes, global side effects from mux/clock changes, and incorrect RCPM generation layout. Tests should cover SoC-specific register presence, DMA mux setup, low-power entry/exit, reset-status decoding, clock divider programming, and compile coverage for PPC86xx and non-PPC86xx configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fsl/guts.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fsl/mc.h -->
# sources/distributed-fs/ceph-client/include/linux/fsl/mc.h

Purpose: declares the Freescale/NXP Management Complex bus public interface for DPAA2 objects, drivers, resources, MSI interrupts, MC command portals, DPRC container management, and basic DPBP/DPCON object APIs.

Important APIs and types: `struct fsl_mc_driver` wraps driver-core registration with MC match ids, probe/remove/shutdown/suspend/resume callbacks, and `driver_managed_dma`. Resource types include DPMCP, DPBP, DPCON, and IRQ pools. `struct fsl_mc_resource`, `struct fsl_mc_device_irq`, `struct fsl_mc_obj_desc`, and `struct fsl_mc_device` model allocatable resources, IRQs, firmware object descriptors, and Linux devices. Command helpers define `struct mc_cmd_header`, `enum mc_cmd_status`, command flags, `mc_encode_cmd_header()`, token/object/version readers, and `struct fsl_mc_io` portal state with mutex or raw spinlock serialization. Registration/resource APIs include `fsl_mc_driver_register()`, `module_fsl_mc_driver()`, portal allocate/free, object allocate/free, IRQ allocate/free, endpoint lookup, MSI domain creation, DPRC scan/remove/setup/cleanup/reset, IRQ pool population/cleanup, and DPBP/DPCON open/close/enable/disable/reset/attribute/notification operations.

Control flow: MC bus discovery creates DPRC/container devices, scans child firmware objects, creates `fsl_mc_device` instances, allocates portals/resources/IRQs, and binds matching `fsl_mc_driver`s. Drivers send commands through an `fsl_mc_io` portal, using tokens from open commands, then close/free resources on remove. DPRC code rescans containers and removes devices that no longer exist in firmware.

State and persistence: Linux-visible state mirrors MC firmware object state: object ids, handles/tokens, resource pools, ICIDs, regions, IRQs, portals, and device links. Hardware/firmware object configuration persists according to MC firmware semantics; this header defines command ABI packing and runtime ownership.

Dependencies and integration points: depends on driver core, module device tables, interrupts/MSI domains, UAPI `fsl_mc.h`, IOMMU grouping, VFIO-style managed DMA, DPAA2 Ethernet/crypto/switch drivers, and irqchip ITS support.

Risks and test signals: risks include command header endian/packing errors, portal serialization misuse in atomic context, resource pool leaks, IRQ pool exhaustion, stale object descriptors after rescan, wrong IOMMU container grouping, and driver-managed DMA bypass mistakes. Tests should cover module alias matching, DPRC scan hotplug/remove, portal command status handling, IRQ allocation/free, DPBP/DPCON operations, endpoint lookup, suspend/resume/shutdown callbacks, and concurrent command submission through shared portals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fsl/mc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fsl/netc_global.h -->
# sources/distributed-fs/ceph-client/include/linux/fsl/netc_global.h

Purpose: provides tiny common MMIO read/write wrappers for NXP NETC code.

Important APIs and functions: `netc_read()` calls `ioread32()` and `netc_write()` calls `iowrite32()` on a supplied `void __iomem *` register address.

Control flow and state: drivers call these helpers when accessing NETC registers. The header owns no state and imposes little-endian/native 32-bit MMIO semantics through the selected accessors.

Dependencies and integration points: depends on Linux I/O accessors and is shared by NETC networking support.

Risks and test signals: risks are mostly endian/register-width assumptions and lack of barriers beyond normal MMIO accessor semantics. Tests should cover register access on supported NETC platforms and compile coverage for consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fsl/netc_global.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fsl/ntmp.h -->
# sources/distributed-fs/ceph-client/include/linux/fsl/ntmp.h

Purpose: declares NXP NETC Table Management Protocol data structures and APIs for managing control buffer descriptor rings and selected NETC tables such as MAC filtering and RSS indirection.

Important APIs and types: `struct maft_keye_data`, `maft_cfge_data`, and `maft_entry_data` describe MAC address filter table key/config entries. `struct netc_cbdr_regs` maps control BD ring registers, `struct netc_swcbd` tracks software buffers and DMA addresses, `struct netc_cbdr` stores ring device, registers, indices, DMA allocation, software descriptors, and a mutex, and `struct ntmp_user` groups rings, device, and table version info. With `CONFIG_NXP_NETC_LIB`, APIs include `ntmp_init_cbdr()`, `ntmp_free_cbdr()`, MAFT add/query/delete, and RSST update/query; otherwise stubs return success/no-op.

Control flow: NETC drivers initialize a command BD ring from MMIO registers, serialize command submission with `ring_lock`, allocate per-command DMA buffers, issue table operations, and free the ring on teardown. Table users update MAC filter entries and RSS tables through the NTMP abstraction.

State and persistence: state includes DMA ring memory, producer/consumer indices, command buffers, and hardware table contents. MAFT/RSST entries persist in device tables until changed or reset.

Dependencies and integration points: depends on DMA APIs, devices, Ethernet address layout, NETC library config, and NETC switch/NIC drivers.

Risks and test signals: risks include stubs returning success when the library is disabled, ring index wrap bugs, DMA alignment/size errors, command serialization issues, table version mismatches, and unvalidated RSS table counts. Tests should cover CDBR init/free, MAFT add/query/delete, RSST update/query, disabled-library builds, ring wraparound, DMA mapping failures, and concurrent table updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fsl/ntmp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fsl/ptp_qoriq.h -->
# sources/distributed-fs/ceph-client/include/linux/fsl/ptp_qoriq.h

Purpose: declares register layouts, bit definitions, state, endian accessors, and public operations for the QorIQ/eTSEC PTP hardware clock driver.

Important APIs and types: register structs map control, alarm, fixed-period interval, and external timestamp groups. `struct ptp_qoriq_registers` stores mapped register group pointers. Offset and bit macros define timer control, event/mask/status, alarm, FIPER, external trigger, Tx/Rx timestamp, clock selection, prescaler, and default periods. `struct ptp_qoriq` stores base, register pointers, spinlock, PTP clock/caps, resource/device, feature flags, IRQ, PHC index, timing parameters, and endian-specific read/write callbacks. Public operations include `ptp_qoriq_isr()`, `ptp_qoriq_init()`, `ptp_qoriq_free()`, `ptp_qoriq_adjfine()`, `ptp_qoriq_adjtime()`, `ptp_qoriq_gettime()`, `ptp_qoriq_settime()`, `ptp_qoriq_enable()`, and `extts_clean_up()`.

Control flow: platform driver maps registers, picks eTSEC or standard offsets and endian accessors, initializes the PHC, handles timer IRQs for alarms/FIPER/external timestamps, and implements PTP clock callbacks for time adjustment, set/get, and feature enable.

State and persistence: state is runtime PHC register programming, PTP clock registration, feature flags, IRQ state, and frequency/timer compensation fields. Hardware time persists while powered but is not filesystem storage.

Dependencies and integration points: depends on I/O accessors, interrupts, PTP clock kernel API, resources, and network drivers that consume hardware timestamping.

Risks and test signals: risks include endian mismatch, incorrect clock period/addend calculations, missing spinlock protection around multi-register time reads/writes, IRQ event cleanup races, and feature bit differences between eTSEC and QorIQ variants. Tests should cover PHC register/unregister, get/set/adjfine/adjtime accuracy, external timestamp events, periodic outputs, IRQ storms, suspend/resume, and big/little-endian platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fsl/ptp_qoriq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fsl_devices.h -->
# sources/distributed-fs/ceph-client/include/linux/fsl_devices.h

Purpose: defines shared Freescale platform-data conventions and structures for USB, SPI, PCMCIA, and deep-sleep handling on older Freescale SoCs.

Important APIs and types: USB enums describe controller versions, operating modes, and PHY modes. `struct fsl_usb2_platform_data` carries controller/PHY mode, port enables, workarounds, board init/exit hooks, MMIO registers, clock, power budget, endian/setup flags, suspend state, erratum flags, PHY clock validation, and saved EHCI/USB register state. `struct fsl_spi_platform_data` stores initial SPMODE, bus number, CPM/QE mode flags, chipselect count/control hook, and sysclk. `struct mpc8xx_pcmcia_ops` supplies hardware control and voltage callbacks. `fsl_deep_sleep()` reports whether suspend removes core power on supported PPC83xx suspend builds, otherwise returns 0.

Control flow: board/platform code fills platform data before registering devices; drivers consume flags and callbacks during probe, runtime operation, suspend/resume, and errata handling. USB suspend stores registers into the save area and restores them later.

State and persistence: platform data is runtime configuration and suspend/resume state, not persistent storage. It reflects board wiring and SoC errata that must remain stable for a device instance.

Dependencies and integration points: integrates with Freescale USB host/device/OTG drivers, SPI drivers, PCMCIA platform code, clocks, platform devices, and PPC suspend support.

Risks and test signals: risks include wrong endian flags, stale erratum flags, callback lifetime issues, incorrect register restore, and mismatch between board wiring and platform data. Tests should cover USB modes/PHY variants, suspend/resume including deep sleep, SPI chipselect callbacks, CPM/QE mode selection, PHY clock timeout handling, and erratum-specific paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fsl_devices.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fsl_hypervisor.h -->
# sources/distributed-fs/ceph-client/include/linux/fsl_hypervisor.h

Purpose: exposes the Freescale hypervisor management driver interface and includes the corresponding UAPI ioctl definitions. Kernel users can register for failover notifications.

Important APIs and types: `fsl_hv_failover_register()` and `fsl_hv_failover_unregister()` manage notifier blocks for hypervisor failover events. UAPI structures and ioctl numbers come from `<uapi/linux/fsl_hypervisor.h>`.

Control flow: a driver initializes a `notifier_block`, registers it, receives failover callbacks from the hypervisor management driver, and unregisters before teardown. Userspace communicates with the management device through the included UAPI ioctls.

State and persistence: notifier registration is runtime state. Hypervisor partition/device state is external to this header.

Dependencies and integration points: integrates with the Freescale hypervisor management driver, notifier chains, and userspace management tools using the ioctl ABI.

Risks and test signals: risks include failing to unregister notifiers, callback ordering/priority mistakes, and ABI drift with UAPI definitions. Tests should cover notifier registration/unregistration, simulated failover events, module unload with registered callbacks, and ioctl compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fsl_hypervisor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fsl_ifc.h -->
# sources/distributed-fs/ceph-client/include/linux/fsl_ifc.h

Purpose: defines the Freescale Integrated Flash Controller register ABI, bit fields, controller state, and endian-aware MMIO helpers for NAND, NOR, and GPCM local-bus devices.

Important APIs and types: constants define bank count, IFC versions, CSPR/AMASK/CSOR fields, NAND page/ECC/row/page/block/timing fields, NOR and GPCM options, ready/busy status, global control, event/error status, clock control/status, NAND command/address/instruction opcodes, chip select/start bits, event/interrupt enables, ECC status fields, timeout counts, and NOR/GPCM error fields. Register structs map `fsl_ifc_nand`, `fsl_ifc_nor`, `fsl_ifc_gpcm`, `fsl_ifc_global`, and `fsl_ifc_runtime`. `struct fsl_ifc_ctrl` stores device, global/runtime register bases, IRQs, lock, NAND-private pointer, version, bank count, NAND status/waitqueue, and endian mode. Public helpers include `convert_ifc_address()`, `fsl_ifc_find()`, global `fsl_ifc_ctrl_dev`, and inline `ifc_in32/16/8()` and `ifc_out32/16/8()`.

Control flow: IFC controller probe maps global/runtime registers, detects version/bank count/endian mode, services common and NAND IRQs, and child NAND/NOR/GPCM drivers program chip-select properties, timing registers, operation sequences, commands, addresses, and event masks. NAND command sequences use FIR opcodes, CSEL, sequence start, event status, waitqueues, and ECC status registers.

State and persistence: hardware register programming defines flash bus mappings, timing, ECC, events, and operation state until reset. Kernel runtime state in `fsl_ifc_ctrl` serializes access and wakes NAND waiters. Flash contents persist externally; this header defines the controller path used to access them.

Dependencies and integration points: depends on I/O accessors, OF platform, interrupts, waitqueues, and MTD/NAND/NOR platform drivers. It also integrates with SoC address translation and chip-select lookup code.

Risks and test signals: risks are high because bitfield errors can corrupt flash operations. Specific risks include `__ilog2()` macros receiving invalid non-power-of-two values, bank-count differences between IFC versions, endian helper reliance on initialized global state, event/status races, ECC status interpretation, NAND page/spare-size mismatches, and touching absent registers on older controllers. Tests should cover controller probe for v1.0/v1.1/v2.0, NAND read/write/erase with ECC correction/failure, NOR and GPCM timing, interrupt and polling completion, endian variants, address conversion/find, invalid chip-select setup, and suspend/resume register restoration if implemented.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fsl_ifc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fsldma.h -->
# sources/distributed-fs/ceph-client/include/linux/fsldma.h

Purpose: declares a small Freescale DMA helper for externally starting or stopping a DMA channel.

Important APIs and functions: `fsl_dma_external_start(struct dma_chan *dchan, int enable)` toggles external-start behavior for a DMA engine channel.

Control flow and state: DMA clients call the helper with a `dma_chan` and enable flag when hardware handshaking or external trigger control is needed. The header owns no state; provider code updates DMA controller state.

Dependencies and integration points: depends on DMA engine `struct dma_chan` being visible to consumers and integrates with Freescale DMA controller drivers and device drivers requiring external starts.

Risks and test signals: risks include calling it on unsupported DMA channels, ambiguous enable values, and missing provider symbols in configs. Tests should cover enable/disable on supported channels, unsupported channel errors, triggered transfers, and compile/link coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fsldma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fsnotify.h -->
# sources/distributed-fs/ceph-client/include/linux/fsnotify.h

Purpose: provides inline VFS notification hooks for filesystem events, consolidating fanotify/inotify/dnotify/audit call sites across file, dentry, inode, mount, and namespace operations.

Important APIs and functions: `fsnotify_sb_has_priority_watchers()` and `fsnotify_sb_has_watchers()` fast-path event suppression by checking superblock watcher counts. Core wrappers include `fsnotify_name()`, `fsnotify_dirent()`, `fsnotify_inode()`, `fsnotify_parent()`, `fsnotify_dentry()`, `fsnotify_path()`, and `fsnotify_file()`. Permission hooks under `CONFIG_FANOTIFY_ACCESS_PERMISSIONS` include `fsnotify_open_perm_and_set_mode()`, `fsnotify_file_area_perm()`, `fsnotify_mmap_perm()`, `fsnotify_truncate_perm()`, and `fsnotify_file_perm()`. Event-specific helpers cover link count, rename/move, inode/mount/mntns delete, inode removal, create, link, delete, `d_delete_notify()`, unlink, mkdir, rmdir, access, modify, open, close, xattr, attribute changes, and mount attach/detach/move.

Control flow: VFS and filesystem code call event helpers after successful operations or before permission-sensitive reads/writes/mmap/truncate. The helpers skip work when no watchers exist, add `FS_ISDIR` where needed, route events to parent/name or child/inode as appropriate, generate rename cookies for paired move events, and call audit hooks for creates. Permission hooks may invoke pre-content/HSM notifications and must run without superblock write freeze protection held.

State and persistence: fsnotify marks and watcher counts live in fsnotify backend state attached to inodes, mounts, and superblocks. This header emits transient events; it does not persist data. Event masks and cookies become observable userspace notification ABI.

Dependencies and integration points: depends on `fsnotify_backend.h`, audit, slab/bug helpers, VFS files/dentries/paths, fanotify HSM/pre-content support, superblock `SB_I_ALLOW_HSM`, and file mode bits such as `FMODE_NONOTIFY` and `FMODE_PATH`.

Risks and test signals: risks include missing events for VFS operations, duplicate events, unstable dentry names, notifying fanotify-generated fds, permission hook deadlocks with freeze protection, rename cookie mismatches, and HSM pre-content policy bypass. Tests should cover inotify/fanotify for create/delete/link/rename/open/close/modify/access/xattr/attrib, permission denial, pre-content range events, mount namespace events, no-watcher fast paths, negative/disconnected dentries, and audit child records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fsnotify.h -->
