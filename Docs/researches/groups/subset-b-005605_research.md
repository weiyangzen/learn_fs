# subset-b-005605

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/autofs/inode.c -->
# sources/distributed-fs/ceph-client/fs/autofs/inode.c

Purpose: implements autofs mount-context parsing, superblock construction/destruction, autofs private inode metadata allocation, and generic inode creation for directories and symlinks. It is the entry point that turns fs_context options from the daemon into an initialized autofs superblock.

Important APIs/types/functions: `autofs_new_ino`, `autofs_clean_ino`, `autofs_free_ino`, `autofs_kill_sb`, `autofs_param_specs`, `autofs_parse_fd`, `autofs_parse_param`, `autofs_validate_protocol`, `autofs_fill_super`, `autofs_init_fs_context`, and `autofs_get_inode`. `struct autofs_fs_context` carries mount-time uid/gid/pgrp state while `struct autofs_sb_info` is allocated and attached to `fc->s_fs_info`.

Control flow: fs_context setup allocates option state and a catatonic `sbi`; parameter parsing opens and validates the daemon pipe early, records protocol bounds, mount type, flags, uid/gid, and owner process group; `get_tree_nodev()` calls `autofs_fill_super()`, which initializes simple superblock fields, creates the root inode and dentry, attaches root `autofs_info`, resolves the owner pgrp, marks trigger roots managed, and clears catatonic mode. `autofs_kill_sb()` puts the filesystem back into catatonic mode, drops the daemon pid, kills the anonymous superblock, and frees `sbi` by RCU.

State and persistence: no disk persistence exists; state lives in `sbi`, dentries, inodes, wait queues, and a packet pipe to userspace. `autofs_info` tracks active/expiring list membership, requester uid/gid, expiry timestamps, and child counts. Pipe file references and process-group references are explicitly owned and released.

Dependencies and integration: integrates with the VFS fs_context API, simple/statfs super operations, dentry operations from `root.c`, symlink operations from `symlink.c`, wait queue handling from `waitq.c`, and UAPI autofs protocol versions. It relies on `autofs_check_pipe()` and packet pipe flag helpers declared elsewhere in autofs.

Risks: fd parsing must happen in the syscall context to avoid descriptor reuse races. Error paths around `autofs_fill_super()` can leak or leave partially constructed state if future edits skip dentry/inode ownership rules. Protocol negotiation and pipe validation are security boundaries because they select daemon packet format and kernel/userspace trust.

Test signals: mount autofs with fd/uid/gid/pgrp/minproto/maxproto/type flags; verify `/proc/mounts` option output; exercise missing fd and invalid protocol bounds; unmount while waiters exist to validate catatonic cleanup; run lockdep/KASAN with repeated mount/unmount cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/autofs/inode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/autofs/root.c -->
# sources/distributed-fs/ceph-client/fs/autofs/root.c

Purpose: implements autofs root/directory file operations, dentry automount management, lookup behavior, daemon-controlled creation/removal of mount triggers, and root ioctls for daemon coordination.

Important APIs/types/functions: exports `autofs_root_operations`, `autofs_dir_operations`, `autofs_dir_inode_operations`, and `autofs_dentry_operations`. Key routines are `autofs_d_automount`, `autofs_d_manage`, `autofs_lookup`, `autofs_lookup_active`, `autofs_lookup_expiring`, `autofs_mount_wait`, `do_expire_wait`, `autofs_mountpoint_changed`, directory create/remove helpers, timeout/protocol ioctls, `is_autofs_dentry`, and `autofs_root_ioctl_unlocked`.

Control flow: path walks call `.d_manage` to decide whether to stop at a managed dentry, wait for pending expire/mount work, or return `-EISDIR` to suppress automount. `.d_automount` rejects daemon-triggered mounts, enforces namespace/private propagation checks, waits for expires, marks dentries pending, notifies the daemon via `autofs_wait()`, and rechecks whether userspace replaced the dentry. Lookup reuses active unhashed dentries or creates a negative dentry with attached `autofs_info` and managed flags when it is a root trigger.

State and persistence: maintains in-memory active and expiring lists under `lookup_lock`, per-dentry child counts, pending/expiring flags under `fs_lock`, and mtime/ctime/nlink transitions for synthetic directories and symlinks. Removal uses `d_drop()` and expiring lists rather than normal negative-dentry invalidation so racing path walks can wait on expire completion.

Dependencies and integration: depends on `waitq.c` for mount/expire daemon waits, `expire.c` for expiration helpers, VFS dentry management flags, mount namespace propagation checks, capability checks, and autofs UAPI ioctls (`READY`, `FAIL`, `CATATONIC`, `EXPIRE`, `EXPIRE_MULTI`, timeout, protocol queries).

Risks: dentry lifetime and lock ordering are delicate because active/expiring lists race with RCU path walk, expire, daemon mutations, and dentry release. Incorrect managed-flag handling can cause spurious `ELOOP`, missed automounts, or repeated daemon callbacks. The ioctl path must restrict non-daemon callers unless privileged.

Test signals: concurrent lookup/open/stat during mount and expire; daemon `READY`/`FAIL` ioctl behavior; v4 pseudo-direct leaf automount flag transitions; namespace/private propagation denial; compat timeout ioctl; KCSAN/lockdep around active and expiring list churn.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/autofs/root.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/autofs/symlink.c -->
# sources/distributed-fs/ceph-client/fs/autofs/symlink.c

Purpose: provides autofs symlink inode operations for synthetic symlinks created by the daemon inside autofs directories.

Important APIs/types/functions: `autofs_get_link` and exported `autofs_symlink_inode_operations`. The link target is stored in `inode->i_private` by `autofs_dir_symlink()` in `root.c`.

Control flow: VFS symlink resolution calls `.get_link`; RCU lookup without a dentry returns `-ECHILD`; otherwise the code obtains `sbi` and `autofs_info`, updates `last_used` for non-daemon callers, and returns the in-memory link target.

State and persistence: no disk state exists. The symlink string is heap-allocated and stored in inode private data, later freed by `autofs_evict_inode()` from `inode.c`. Access time is represented only by the autofs expiry `last_used` timestamp.

Dependencies and integration: depends on `autofs_i.h`, `autofs_oz_mode()`, and inode private storage populated by `root.c`.

Risks: callers must respect the `-ECHILD` RCU fallback. Lifetime is safe only if inode eviction frees `i_private` after all link users are gone.

Test signals: resolve daemon-created symlinks as daemon and non-daemon tasks; verify expiry timestamp changes only for non-daemon access; test RCU path walk fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/autofs/symlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/autofs/waitq.c -->
# sources/distributed-fs/ceph-client/fs/autofs/waitq.c

Purpose: implements autofs kernel-to-daemon wait queues, notification packet creation, pipe writes, catatonic teardown, and daemon release of pending mount/expire requests.

Important APIs/types/functions: `autofs_catatonic_mode`, `autofs_wait`, `autofs_wait_release`, `autofs_notify_daemon`, `autofs_write`, `autofs_find_wait`, and `validate_request`. `struct autofs_wait_queue` stores token, name, uid/gid, pid/tgid, dev/ino, status, and waiter count.

Control flow: `autofs_wait()` validates catatonic and pid namespace visibility, builds a request name, locks `wq_mutex`, reuses an existing wait or allocates a new token, selects protocol v4/v5 packet type based on notify kind and mount type, sends a packet to the daemon pipe, then sleeps until release clears `wq->name.name`. The daemon calls `autofs_wait_release()` with `READY` or `FAIL` token status. Pipe errors either fail one waiter or force catatonic mode.

State and persistence: pending waits are in `sbi->queues`, serialized by `wq_mutex`; pipe writes are serialized by `pipe_mutex`; request names are separately allocated with an offset for path strings. Successful mount waits cache requester uid/gid in `autofs_info` for daemon restart and macro substitution.

Dependencies and integration: uses UAPI autofs packet layouts, `__kernel_write()`, wait queues, signal state, pid namespace translation, autofs dentry helpers, and root ioctl release handling.

Risks: error handling must not leak the allocated name or queue object across interruption, catatonic teardown, and daemon release. SIGPIPE suppression is intentional and easy to regress. Namespace pid translation failure returns `-ENOENT`, which affects containers and daemon restarts.

Test signals: parallel callers waiting on the same missing mount; daemon releases with success/failure; pipe close and EPIPE catatonic transition; pid namespace mismatch; interrupted wait; v4 and v5 packet format coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/autofs/waitq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/backing-file.c -->
# sources/distributed-fs/ceph-client/fs/backing-file.c

Purpose: provides common backing-file helpers for stackable filesystems, including open/tmpfile wrappers, credential override, read/write/splice/mmap forwarding, and async I/O completion adaptation.

Important APIs/types/functions: exported `backing_file_open`, `backing_tmpfile_open`, `backing_file_read_iter`, `backing_file_write_iter`, `backing_file_splice_read`, `backing_file_splice_write`, and `backing_file_mmap`. Internal `struct backing_aio` clones caller `kiocb` state for async forwarding.

Control flow: open helpers allocate an FMODE_BACKING file, attach the user-visible path, and call `vfs_open()` or `vfs_tmpfile()` under supplied creds. Read/write helpers reject non-backing files, empty iterators, unsupported direct I/O, and then run the real VFS operation under `ctx->cred`. Async write completion is queued to the superblock DIO workqueue so size/mtime updates are serialized before calling the original completion.

State and persistence: no persistent data; file references, user paths, cloned kiocbs, and slab-allocated `backing_aio` objects carry transient state. Writes remove privileges on the user-facing file and invoke callback hooks for access/end-write accounting.

Dependencies and integration: used by overlay-like filesystems; integrates with Linux security hooks (`security_mmap_backing_file`), VFS iter/splice/mmap APIs, `scoped_with_creds`, superblock DIO workqueues, and `linux/backing-file.h`.

Risks: credential context and user-vs-real file attribution are security-sensitive. Async refcounting and completion ordering must avoid use-after-free and stale `ki_pos`. Direct I/O capability checks must remain aligned with lower file capabilities.

Test signals: overlay/stacked filesystem xfstests for read/write/splice/mmap; async direct I/O completion; privilege stripping on writes; LSM mmap hook denial; WARN coverage for non-FMODE_BACKING misuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/backing-file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/bad_inode.c -->
# sources/distributed-fs/ceph-client/fs/bad_inode.c

Purpose: supplies the VFS sentinel operations used when an inode cannot be read or must be invalidated as permanently unusable.

Important APIs/types/functions: `make_bad_inode`, `is_bad_inode`, `iget_failed`, `bad_inode_ops`, and `bad_file_ops`. Most inode and file callbacks return `-EIO`; symlink and ACL callbacks return error pointers.

Control flow: a filesystem that fails during inode construction calls `iget_failed()`, which converts the inode to bad operations, unlocks it, and drops it. `make_bad_inode()` removes it from the inode hash, sets a regular-file mode and timestamps, disables xattr opflags, and installs the bad op tables. Later VFS operations consistently fail.

State and persistence: the bad state is in-memory only and represented by `inode->i_op == &bad_inode_ops`; it deliberately prevents future normal operation on that inode instance.

Dependencies and integration: exported to filesystems across the kernel; used in iget/read-inode failure paths and invalidated-inode checks.

Risks: callers must use this only for real unreadable/corrupt inodes, because it makes the object uniformly fail with I/O errors. New VFS inode operations need corresponding bad stubs to avoid accidental success.

Test signals: inject inode read I/O failures in filesystems; verify open, lookup, getattr, xattrs, ACLs, fiemap, and write-time updates all fail with `-EIO`; assert `is_bad_inode()` after `iget_failed()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/bad_inode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/befs/Kconfig -->
# sources/distributed-fs/ceph-client/fs/befs/Kconfig

Purpose: defines kernel configuration for BeFS support and optional BeFS debug logging.

Important APIs/types/functions: `config BEFS_FS` is a tristate depending on `BLOCK`, selecting `BUFFER_HEAD` and `NLS`; `config BEFS_DEBUG` is a bool depending on `BEFS_FS`.

Control flow: enabling `BEFS_FS` builds the read-only BeOS filesystem driver as built-in or module. Enabling `BEFS_DEBUG` activates debug support and the `debug` mount option pathway used by `debug.c`/`linuxvfs.c`.

State and persistence: configuration controls build-time availability only; no runtime state is stored here.

Dependencies and integration: integrates with block-device filesystems, native language support, and the `befs` module build in the Makefile.

Risks: help text notes BeFS attributes and indices are not fully exposed. Users may expect write support, but the driver is read-only.

Test signals: Kconfig allmodconfig/build coverage for `BEFS_FS=m/y` and debug on/off; mount option parsing with and without debug compiled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/befs/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/befs/Makefile -->
# sources/distributed-fs/ceph-client/fs/befs/Makefile

Purpose: declares how the BeFS driver object is built from its component files.

Important APIs/types/functions: `obj-$(CONFIG_BEFS_FS) += befs.o`, `ccflags-$(CONFIG_BEFS_DEBUG) += -DDEBUG`, and `befs-objs := datastream.o btree.o super.o inode.o debug.o io.o linuxvfs.o`.

Control flow: when BeFS is enabled, Kbuild links all listed objects into `befs.o`; debug builds add a compile define used by local debug code.

State and persistence: build metadata only.

Dependencies and integration: reflects the subsystem layering: VFS mount/inode code, superblock parsing, inode validation, datastream and B+tree readers, block I/O, and debug helpers.

Risks: omitting a component breaks exported internal symbols; stale debug flags can leave debug paths compiled differently than Kconfig implies.

Test signals: compile BeFS built-in and module, with and without `CONFIG_BEFS_DEBUG`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/befs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/befs/befs.h -->
# sources/distributed-fs/ceph-client/fs/befs/befs.h

Purpose: central BeFS internal header defining in-memory superblock/inode state, error codes, debug prototypes, and address conversion helpers.

Important APIs/types/functions: `struct befs_mount_options`, `struct befs_sb_info`, `struct befs_inode_info`, `enum befs_err`, `BEFS_SB`, `BEFS_I`, `iaddr2blockno`, `blockno2iaddr`, and `befs_iaddrs_per_block`.

Control flow: included by most BeFS implementation files so they can convert between VFS objects and BeFS-private state and between BeFS allocation-group addresses and linear block numbers.

State and persistence: `befs_sb_info` mirrors persistent superblock fields plus mount options and loaded NLS table. `befs_inode_info` mirrors persistent inode addresses, flags, type, and either datastream or short symlink data.

Dependencies and integration: includes on-disk types from `befs_fs_types.h` and endian conversion helpers from `endian.h`; ties VFS inode embedding to BeFS metadata.

Risks: address conversion depends on validated `ag_shift` and block geometry. Any mismatch between on-disk and in-memory fields can produce bad block reads.

Test signals: mount images with different block sizes/ag shifts, stat regular files/directories/symlinks, and verify converted inode/block addresses through debug output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/befs/befs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/befs/befs_fs_types.h -->
# sources/distributed-fs/ceph-client/fs/befs/befs_fs_types.h

Purpose: describes BeFS on-disk structures, constants, bitwise filesystem integer types, superblock/inode flags, datastream layout, and B+tree node/superblock formats.

Important APIs/types/functions: `befs_disk_block_run`, `befs_block_run`, `befs_super_block`, `befs_disk_data_stream`, `befs_data_stream`, `befs_inode`, `befs_disk_btree_super`, `befs_btree_super`, `befs_btree_nodehead`, and `befs_host_btree_nodehead`.

Control flow: parsing code in `super.c`, `inode.c`, `datastream.c`, and `btree.c` reads these packed disk structures and converts fields through `endian.h`.

State and persistence: this file is the persistent contract for BeFS volumes: magic values, byte order, allocation group runs, inode data, inline symlink storage, long symlink datastreams, and directory/index B+trees.

Dependencies and integration: uses Linux fixed-width types and `__bitwise` filesystem-endian wrappers to prevent accidental host-endian use.

Risks: packed structure definitions must match disk layout exactly. B+tree and double-indirect constants influence read bounds and can corrupt lookup if changed incorrectly.

Test signals: sparse/endianness builds, mounting little- and big-endian BeFS images, checking directory B+tree traversal and long symlink reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/befs/befs_fs_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/befs/btree.c -->
# sources/distributed-fs/ceph-client/fs/befs/btree.c

Purpose: implements read-only traversal and lookup for BeFS directory B+trees over datastream storage.

Important APIs/types/functions: public `befs_btree_find` and `befs_btree_read`; internal `befs_bt_read_super`, `befs_bt_read_node`, `befs_find_key`, `befs_btree_seekleaf`, `befs_leafnode`, key/value layout helpers, and string comparison.

Control flow: lookup reads the B+tree superblock, loads the root node, descends interior nodes using binary search and overflow links, then searches the leaf for an exact key. Readdir finds the first leaf, walks right links until `ctx->pos` falls in a node, extracts key/value pairs, and signals end/empty/error with BeFS-specific codes.

State and persistence: transient `struct befs_btree_node` wraps one buffer_head and host-endian node header. Persistent keys, key-length indexes, and value arrays remain in packed on-disk node memory.

Dependencies and integration: layered on `befs_read_datastream()` for block access, endian helpers for fields, and directory operations in `linuxvfs.c` for lookup/readdir.

Risks: node layout pointer arithmetic, key length indexes, and overflow semantics are sensitive to corrupt images. The implementation handles string directory keys only and leaves non-string index comparators disabled.

Test signals: directory lookup/readdir on empty, single-node, multi-node, and overflow B+trees; malformed magic/node fields; small key buffers; big-endian images.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/befs/btree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/befs/btree.h -->
# sources/distributed-fs/ceph-client/fs/befs/btree.h

Purpose: declares the BeFS B+tree lookup and sequential-read interfaces used by the VFS directory layer.

Important APIs/types/functions: `befs_btree_find()` maps a string key to a BeFS value/offset; `befs_btree_read()` returns the key/value at an ordinal position.

Control flow: `linuxvfs.c` calls `befs_btree_find()` during lookup and `befs_btree_read()` during readdir; implementation lives in `btree.c`.

State and persistence: no state in the header; arguments expose datastream-backed persistent B+tree data and caller-owned output buffers.

Dependencies and integration: requires BeFS datastream and offset types from `befs.h`.

Risks: callers must provide adequate key buffers and handle BeFS return codes distinctly from Linux errno values.

Test signals: compile coverage for declarations and directory lookup/readdir behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/befs/btree.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/befs/datastream.c -->
# sources/distributed-fs/ceph-client/fs/befs/datastream.c

Purpose: maps BeFS file-relative blocks and byte positions to disk block runs, reads datastream buffers, reads long symlinks, and counts data plus metadata blocks.

Important APIs/types/functions: `BAD_IADDR`, `befs_read_datastream`, `befs_fblock2brun`, `befs_read_lsymlink`, `befs_count_blocks`, and direct/indirect/double-indirect block-run search helpers.

Control flow: byte positions are converted to file blocks and offsets, then `befs_fblock2brun()` chooses direct, indirect, or double-indirect lookup based on datastream range limits. Direct lookup linearly scans inline runs; indirect lookup reads run arrays; double-indirect lookup computes indexes into fixed-size run groups and reads only the necessary mapping blocks.

State and persistence: consumes persistent `befs_data_stream` fields copied into inode-private state. No mutation occurs. Buffer_heads returned by reads are caller-owned and must be released.

Dependencies and integration: uses `befs_bread_iaddr()`/`sb_bread()`, endian conversion, BeFS block geometry, and feeds `linuxvfs.c` read_folio/bmap and `btree.c` node reads.

Risks: corrupt range limits or run lengths can produce bad reads or arithmetic mistakes. The double-indirect index calculation is especially sensitive, and comments note uncertainty about `BEFS_DBLINDIR_BRUN_LEN` units.

Test signals: read files spanning direct, indirect, and double-indirect extents; long symlinks of boundary lengths; corrupted run arrays; block count comparisons with known images.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/befs/datastream.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/befs/datastream.h -->
# sources/distributed-fs/ceph-client/fs/befs/datastream.h

Purpose: exposes BeFS datastream block mapping and read helpers to VFS and B+tree code.

Important APIs/types/functions: declarations for `befs_read_datastream`, `befs_fblock2brun`, `befs_read_lsymlink`, `befs_count_blocks`, and `BAD_IADDR`.

Control flow: callers use these functions to map file logical blocks, read arbitrary datastream positions, read long symlink content, and compute inode `i_blocks`.

State and persistence: no state in the header; all state is in caller-provided datastreams and returned buffer_heads.

Dependencies and integration: bridges `linuxvfs.c`, `btree.c`, and `datastream.c`.

Risks: caller ownership of returned buffer_heads must be respected; BeFS return codes are not Linux errnos.

Test signals: compile and mount coverage for regular file reads, B+tree directory operations, and long symlinks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/befs/datastream.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/befs/debug.c -->
# sources/distributed-fs/ceph-client/fs/befs/debug.c

Purpose: provides BeFS error/warning/debug logging and optional detailed dump helpers for superblocks, inodes, B+tree superblocks, and B+tree nodes.

Important APIs/types/functions: `befs_error`, `befs_warning`, `befs_debug`, `befs_dump_inode`, `befs_dump_super_block`, `befs_dump_index_entry`, and `befs_dump_index_node`.

Control flow: error and warning logs always format messages with superblock id; debug and dump functions emit only when `CONFIG_BEFS_DEBUG` is enabled.

State and persistence: no persistent state; dumps convert on-disk endian fields at log time without mutating them.

Dependencies and integration: used throughout BeFS parsing, mapping, and VFS code to report corruption and diagnostics.

Risks: debug dumps must avoid trusting malformed fields too deeply. Log volume can be high with debug enabled.

Test signals: build with `CONFIG_BEFS_DEBUG`; mount with `debug`; inject bad magic, bad inode, and B+tree errors to confirm diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/befs/debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/befs/endian.h -->
# sources/distributed-fs/ceph-client/fs/befs/endian.h

Purpose: centralizes BeFS filesystem-endian conversion for scalar and composite on-disk fields.

Important APIs/types/functions: `fs64_to_cpu`, `cpu_to_fs64`, `fs32_to_cpu`, `cpu_to_fs32`, `fs16_to_cpu`, `cpu_to_fs16`, `fsrun_to_cpu`, `cpu_to_fsrun`, and `fsds_to_cpu`.

Control flow: conversion branches on `BEFS_SB(sb)->byte_order`, which is set while loading the superblock. Composite helpers convert block runs and full datastreams into host-endian forms.

State and persistence: no state, but correctness depends on persistent superblock byte-order detection.

Dependencies and integration: used by all BeFS disk parsing and debug dumping code; includes architecture byteorder helpers.

Risks: using conversion before `byte_order` is initialized or mixing host/disk structures can corrupt addressing. Sparse bitwise fs types help catch misuse.

Test signals: mount little- and big-endian BeFS images; sparse endian checks; compare debug dumps against known disk metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/befs/endian.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/befs/inode.c -->
# sources/distributed-fs/ceph-client/fs/befs/inode.c

Purpose: validates raw BeFS inodes before the VFS inode is populated.

Important APIs/types/functions: `befs_check_inode`.

Control flow: converts inode magic, stored inode address, and flags to host order; rejects bad magic, mismatch between requested block number and inode self-address, and inodes not marked in use.

State and persistence: reads persistent inode header fields but does not mutate disk or VFS state.

Dependencies and integration: called by `befs_iget()` in `linuxvfs.c`; uses endian and address conversion helpers from `befs.h`.

Risks: validation is intentionally minimal; malformed datastreams or modes are checked later. Incorrect acceptance can lead to invalid block mapping.

Test signals: mount images with corrupt inode magic, stale self-address, and cleared `BEFS_INODE_IN_USE`; expect `befs_iget()` failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/befs/inode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/befs/inode.h -->
# sources/distributed-fs/ceph-client/fs/befs/inode.h

Purpose: declares BeFS raw inode validation.

Important APIs/types/functions: `befs_check_inode(struct super_block *, befs_inode *, befs_blocknr_t)`.

Control flow: consumed by `linuxvfs.c` when loading an inode from disk.

State and persistence: no header state; interface receives persistent raw inode data.

Dependencies and integration: ties `inode.c` validation into `befs_iget()`.

Risks: callers must pass the block number corresponding to the raw inode buffer for self-address validation.

Test signals: compile coverage and corrupt-inode mount/read tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/befs/inode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/befs/io.c -->
# sources/distributed-fs/ceph-client/fs/befs/io.c

Purpose: converts BeFS inode/block-run addresses to linear disk blocks and reads them with buffer-head I/O.

Important APIs/types/functions: `befs_bread_iaddr`.

Control flow: validates the allocation group against the mounted filesystem, converts run to block number with `iaddr2blockno()`, calls `sb_bread()`, and returns the buffer_head or NULL with diagnostics.

State and persistence: no mutation; reads persistent disk blocks into buffer cache.

Dependencies and integration: used by datastream reads and any code needing BeFS allocation group addressing.

Risks: validation only checks allocation group upper bound; corrupt start/len can still address invalid blocks unless caught elsewhere.

Test signals: read valid root inode and datastream blocks; corrupt allocation group should log an error and fail.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/befs/io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/befs/io.h -->
# sources/distributed-fs/ceph-client/fs/befs/io.h

Purpose: declares BeFS block-run read helper.

Important APIs/types/functions: `befs_bread_iaddr`.

Control flow: included by `datastream.c` and other BeFS code that reads allocation-group addressed blocks.

State and persistence: no state; returned buffer_heads represent disk cache state owned by callers.

Dependencies and integration: depends on BeFS address types from `befs.h`.

Risks: callers must release the buffer_head and pass host-endian inode addresses.

Test signals: compile and file-read coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/befs/io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/befs/linuxvfs.c -->
# sources/distributed-fs/ceph-client/fs/befs/linuxvfs.c

Purpose: connects BeFS metadata readers to the Linux VFS: mount, inode loading, regular-file reads, directory lookup/readdir, symlinks, statfs, exportfs, NLS filename conversion, and module registration.

Important APIs/types/functions: `befs_read_folio`, `befs_get_block`, `befs_lookup`, `befs_readdir`, `befs_iget`, inode cache helpers, `befs_symlink_read_folio`, `befs_utf2nls`, `befs_nls2utf`, export callbacks, mount option parsing, `befs_fill_super`, `befs_reconfigure`, `befs_statfs`, and filesystem init/exit.

Control flow: mount allocates `befs_sb_info`, copies parsed options, forces read-only, reads the superblock at PPC or x86 offset, validates it, sets blocksize and VFS ops, loads root inode, and loads NLS. Inode loading reads a raw inode block, validates it, sets mode/uid/gid/times/size/blocks, selects file/dir/symlink operations, and handles short vs long symlinks. Directory lookup and readdir query the BeFS B+tree and convert filenames when an NLS table is active.

State and persistence: in-memory superblock stores parsed persistent fields and mount options; inode private state stores persistent datastreams, inode addresses, and inline symlink data. The driver does not write BeFS data; write block creation returns errors and reconfigure disallows read-write.

Dependencies and integration: uses `super.c`, `inode.c`, `datastream.c`, `btree.c`, `io.c`, NLS APIs, buffer-head address_space operations, exportfs helpers, fs_context parser, and module registration.

Risks: filename conversion failures can make entries inaccessible. Parent export uses stored parent address fields and must remain consistent with inode numbering. Read-only enforcement is critical because lower mapping code does not implement allocation or journaling.

Test signals: mount read-only and attempted read-write; lookup/readdir with UTF-8 and mounted `iocharset`; read regular files and long/short symlinks; statfs values; NFS export file handles; corrupted superblock/inode paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/befs/linuxvfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/befs/super.c -->
# sources/distributed-fs/ceph-client/fs/befs/super.c

Purpose: loads and validates the BeFS superblock from disk into host-endian in-memory state.

Important APIs/types/functions: `befs_load_sb` and `befs_check_sb`.

Control flow: load detects little- or big-endian format from `fs_byte_order`, converts magic, block geometry, allocation group fields, journal positions, and root/indices addresses. Check verifies magic values, supported block sizes, page-size compatibility, block-shift consistency, logs an allocation-group consistency warning, and rejects dirty/journal-not-empty filesystems.

State and persistence: populates `befs_sb_info` from persistent `befs_super_block`. No disk mutation occurs.

Dependencies and integration: called during `befs_fill_super()` after reading the candidate disk superblock; relies on endian helpers after byte order selection.

Risks: byte order must be detected before conversion. Dirty filesystem rejection prevents replay-less read of potentially inconsistent metadata.

Test signals: little/big-endian images; invalid magic/block size/block shift; dirty journal images should fail mount.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/befs/super.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/befs/super.h -->
# sources/distributed-fs/ceph-client/fs/befs/super.h

Purpose: declares BeFS superblock load and validation helpers.

Important APIs/types/functions: `befs_load_sb` and `befs_check_sb`.

Control flow: used by `linuxvfs.c` during mount after raw superblock read.

State and persistence: no header state; interfaces operate on persistent disk superblocks and mounted `befs_sb_info`.

Dependencies and integration: connects `super.c` to the mount path.

Risks: callers must provide a raw superblock at the correct architecture-specific offset.

Test signals: compile and mount validation tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/befs/super.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/bfs/Kconfig -->
# sources/distributed-fs/ceph-client/fs/bfs/Kconfig

Purpose: defines configuration for SCO UnixWare BFS filesystem support.

Important APIs/types/functions: `config BFS_FS` is a tristate depending on `BLOCK` and selecting `BUFFER_HEAD`.

Control flow: enabling this option builds the `bfs` driver to read and write UnixWare `/stand` slices.

State and persistence: build-time configuration only.

Dependencies and integration: integrates BFS with block devices, buffer-head I/O, and UnixWare partition usage documented in kernel filesystem docs.

Risks: help text warns this is a niche boot filesystem and should normally be disabled unless needed.

Test signals: Kconfig build coverage as module and built-in; smoke mount of a BFS image.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/bfs/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/bfs/Makefile -->
# sources/distributed-fs/ceph-client/fs/bfs/Makefile

Purpose: declares BFS driver build composition.

Important APIs/types/functions: `obj-$(CONFIG_BFS_FS) += bfs.o` and `bfs-objs := inode.o file.o dir.o`.

Control flow: Kbuild links superblock/inode, file mapping, and directory operation objects into one BFS module/object.

State and persistence: build metadata only.

Dependencies and integration: mirrors runtime split between mount/inode persistence, file block allocation, and directory mutation.

Risks: missing any object breaks required VFS operation tables.

Test signals: BFS built-in/module compile coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/bfs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/bfs/bfs.h -->
# sources/distributed-fs/ceph-client/fs/bfs/bfs.h

Purpose: central BFS internal header defining in-core superblock/inode state, helpers, logging macro, and cross-file operation declarations.

Important APIs/types/functions: `BFS_MAX_LASTI`, `struct bfs_sb_info`, `struct bfs_inode_info`, `BFS_SB`, `BFS_I`, `bfs_iget`, `bfs_dump_imap`, `bfs_file_operations`, `bfs_aops`, `bfs_dir_inops`, and `bfs_dir_operations`.

Control flow: included by all BFS implementation files; private inode/superblock accessors are used for mount scan, writeback, directory updates, and file block allocation.

State and persistence: `bfs_sb_info` tracks total/free blocks, free inodes, last file end block, highest inode, inode bitmap, and global mutex. `bfs_inode_info` tracks disk inode number, contiguous block range, and metadata buffers for fsync.

Dependencies and integration: wraps UAPI `linux/bfs_fs.h` on-disk definitions and VFS inode embedding.

Risks: BFS has a small fixed inode namespace and contiguous allocation model; bitmap and free counters must remain serialized by `bfs_lock`.

Test signals: create/unlink/link/rename files, fill inode table, and verify statfs free counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/bfs/bfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/bfs/dir.c -->
# sources/distributed-fs/ceph-client/fs/bfs/dir.c

Purpose: implements BFS directory reading and mutation: create, lookup, hard link, unlink, rename, entry insertion, and entry lookup.

Important APIs/types/functions: `bfs_readdir`, `bfs_fsync`, exported `bfs_dir_operations`, `bfs_create`, `bfs_lookup`, `bfs_link`, `bfs_unlink`, `bfs_rename`, exported `bfs_dir_inops`, `bfs_add_entry`, `bfs_namecmp`, and `bfs_find_entry`.

Control flow: readdir scans fixed-size directory entries from the directory's contiguous block range. Create allocates a free inode bit under `bfs_lock`, initializes a regular file inode, marks it dirty, and inserts a directory entry. Lookup finds an entry and calls `bfs_iget()`. Link/unlink/rename update directory entries, timestamps, nlinks, and metadata buffer dirty tracking.

State and persistence: directory entries persist in BFS data blocks; inode allocation uses `si_imap` and `si_freei`; metadata buffer heads are tracked for fsync via `mapping_metadata_bhs`.

Dependencies and integration: uses buffer-head I/O, VFS dentry/inode helpers, global BFS mutex, file operations from `file.c`, inode writeback from `inode.c`, and on-disk formats from `linux/bfs_fs.h`.

Risks: directories have fixed capacity from their allocated blocks; create can allocate an inode and then fail to insert an entry. Rename rejects directories and supports only `RENAME_NOREPLACE`. All mutation relies on the global mutex for consistency.

Test signals: xfstests-style create/link/unlink/rename; directory full returning `-ENOSPC`; invalid f_pos alignment; fsync after metadata changes; lookup name-length boundary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/bfs/dir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/bfs/file.c -->
# sources/distributed-fs/ceph-client/fs/bfs/file.c

Purpose: implements BFS regular file operations and block mapping/allocation for a filesystem that stores each file in one contiguous block range.

Important APIs/types/functions: exported `bfs_file_operations`, `bfs_get_block`, `bfs_move_block`, `bfs_move_blocks`, `bfs_writepages`, `bfs_read_folio`, `bfs_write_begin`, `bfs_bmap`, exported `bfs_aops`, and empty `bfs_file_inops`.

Control flow: reads map logical blocks to `i_sblock + block` if inside `i_eblock`. Writes either reuse allocated range, extend trivially when the file is the last allocated file, or move the entire file to the block after `si_lf_eblk` before extending. Page-cache write paths use generic block helpers with `bfs_get_block`.

State and persistence: updates private inode start/end block range, superblock free block count, last-file end block, dirty inode state, and disk blocks copied during relocation.

Dependencies and integration: used by BFS regular inodes from `inode.c` and `dir.c`; relies on buffer-head and mpage helpers plus `bfs_lock`.

Risks: relocation copies data block by block and comments note assumptions about inode writeback racing with `i_blocks`. ENOSPC and I/O failure during moves can leave corruption risk if not handled carefully.

Test signals: append to empty and non-last files; force relocation; read after relocation; ENOSPC boundary; mmap/writeback/bmap coverage; fault injection on block copy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/bfs/file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/bfs/inode.c -->
# sources/distributed-fs/ceph-client/fs/bfs/inode.c

Purpose: implements BFS superblock mount, inode read/write/evict, statfs, inode cache, filesystem registration, and persistent inode/free-space accounting.

Important APIs/types/functions: `bfs_iget`, `find_inode`, `bfs_write_inode`, `bfs_evict_inode`, `bfs_put_super`, `bfs_statfs`, inode cache helpers, `bfs_sops`, `bfs_dump_imap`, `bfs_fill_super`, fs_context ops, and module init/exit.

Control flow: mount sets block size, reads and validates the BFS superblock, computes maximum inode number, initializes reserved inode bits, loads root inode, checks last block readability, scans all inodes to validate block ranges and build free inode/block counters. `bfs_iget()` reads an on-disk inode, reconstructs file type from `i_vtype`, loads ownership/times/ranges, and installs directory or file ops. Writeback serializes and writes the on-disk inode; eviction clears deleted inodes and frees blocks/inode bits.

State and persistence: persistent BFS inode table, superblock geometry, inode bitmap-derived free counts, contiguous file block ranges, and timestamps. In-core `si_freeb`, `si_freei`, and `si_lf_eblk` are reconstructed at mount and updated by mutations.

Dependencies and integration: depends on UAPI BFS structures/macros, directory/file operation tables, buffer-head I/O, VFS writeback/eviction, and module filesystem registration.

Risks: mount continues on unclean BFS but validates inode ranges. Free-space accounting must stay consistent with relocation and eviction. Root and regular file type reconstruction compensates for historical `i_mode` garbage bits.

Test signals: mount clean/unclean/corrupt images; read/write inode sync; delete files and verify free counters; fill inode table; statfs; malformed start/end/eoffset rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/bfs/inode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/binfmt_elf.c -->
# sources/distributed-fs/ceph-client/fs/binfmt_elf.c

Purpose: implements Linux ELF executable loading and, when enabled, ELF core dump generation.

Important APIs/types/functions: `elf_format`, `load_elf_binary`, `create_elf_tables`, `elf_map`, `elf_load`, `load_elf_phdrs`, `load_elf_interp`, GNU property parsing, `make_prot`, coredump note helpers, `fill_note_info`, `write_note_info`, `elf_core_dump`, and binfmt init/exit registration.

Control flow: exec validates ELF magic/type/arch/mmapability, loads program headers, opens and validates a `PT_INTERP` interpreter if present, processes stack/property/arch headers, starts a new exec, sets personality and ASLR, maps `PT_LOAD` segments with correct load bias and BSS zeroing, maps the interpreter, builds auxv/argv/envp stack tables, sets mm code/data/brk/stack fields, runs arch setup, finalizes exec, and starts the thread at the resolved entry. Coredump first builds ELF/note metadata and offsets, then writes headers, note segments, VMA program headers, notes, dumped memory ranges, arch extras, and extended numbering if needed.

State and persistence: mutates the current process `mm_struct`, credentials-related auxv values, personality/randomization flags, brk, VMA layout, saved ELF flags, and register state at exec. Core dump output persists process metadata, mapped file notes, thread regsets, auxv, signal info, and selected VMA contents.

Dependencies and integration: central binfmt integration with `register_binfmt`, exec credential/security flow, mmap/brk APIs, arch ELF hooks, randomization, GNU property parsing, user regsets, coredump infrastructure, LSM checks through exec/mmap paths, and optional KUnit test include.

Risks: this is a high-risk security boundary. Segment size/address overflow, `MAP_FIXED_NOREPLACE`, BSS zeroing, interpreter permissions, executable stack policy, auxv correctness, and property parsing must be precise. Core notes must respect size limits and avoid leaking unintended data.

Test signals: ELF KUnit when enabled; LTP/binfmt exec tests; PIE/static PIE/interpreter ASLR cases; malformed phdr/property/interpreter files; executable-stack binaries; core dump validation with many VMAs/threads/mapped files; architecture-specific regset and auxv checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/binfmt_elf.c -->
