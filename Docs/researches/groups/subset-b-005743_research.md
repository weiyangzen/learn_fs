# Research: subset-b-005743

This grouped report covers the requested VFS, openpromfs, and OrangeFS source files. Each section is delimited for reconciliation into the mapped source-tree-aligned research files.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/open.c -->
## sources/distributed-fs/ceph-client/fs/open.c

### Purpose
This is the Linux VFS open and file metadata syscall implementation. It is not specific to Ceph or OrangeFS despite the source-tree prefix; it supplies the generic syscall and helper layer that filesystem implementations such as OrangeFS enter through file, inode, dentry, and address-space operations. It handles truncate/ftruncate, fallocate, access checks, cwd/root changes, chmod/chown, open/openat/openat2/creat, close, and generic open helpers.

### Important APIs, types, and functions
- `do_truncate()`, `vfs_truncate()`, `ksys_truncate()`, and `do_ftruncate()` build `struct iattr`, enforce object type, write permissions, leases, security hooks, and call `notify_change()`.
- `vfs_fallocate()` validates fallocate mode combinations, range overflow, append/immutable/swapfile restrictions, LSM and fsnotify write permissions, then calls `file->f_op->fallocate`.
- `do_faccessat()` implements `access`, `faccessat`, and `faccessat2`, optionally using temporary credentials from `access_override_creds()` for real-uid checks.
- `chmod_common()`, `vfs_fchmod()`, `do_fchmodat()`, `chown_common()`, `do_fchownat()`, and `vfs_fchown()` centralize ownership and mode updates through `notify_change()`.
- `do_dentry_open()`, `finish_open()`, `finish_no_open()`, `vfs_open()`, `dentry_open()`, `kernel_file_open()`, `file_open_name()`, `filp_open()`, and `file_open_root()` are the core open helpers.
- `build_open_how()` and `build_open_flags()` translate userspace flags and `openat2` resolve constraints into `struct open_flags`.
- `filp_close()`, `close`, `generic_file_open()`, `nonseekable_open()`, and `stream_open()` provide close and default open-mode behavior.

### Control flow
Truncate by path resolves a pathname, checks the inode type, acquires mount write access and inode write access, breaks leases, runs security hooks, then calls `do_truncate()` under the inode lock. Ftruncate starts from an already opened file and uses `super_write` scope before calling the same helper with `ATTR_FILE` and timestamp changes. Open syscalls normalize flags, copy `open_how` from userspace for `openat2`, resolve names through `do_file_open()`, allocate a `struct file`, and finish through `do_dentry_open()`. `do_dentry_open()` initializes path, inode, mapping, read/write accounting, write access, fsnotify and LSM checks, lease breaking, file operations, filesystem-specific `->open`, I/O capability bits, readahead state, and direct-I/O eligibility.

### State and persistence behavior
The file mutates VFS objects and per-file state rather than persisting its own data. Persistent effects are delegated through `notify_change()`, filesystem `->fallocate`, `->open`, `->flush`, and writeback paths. It manipulates mount write counts, inode write counts, file modes, fd table entries, working directory/root paths, and fsnotify/audit side effects.

### Dependencies and integration points
It depends on name lookup, mount idmapping, LSM hooks, fsnotify, leases, file locks, audit, fd tables, credentials, and filesystem operation vectors. OrangeFS integrates indirectly through `orangefs_file_operations`, `orangefs_dir_inode_operations`, `orangefs_setattr`, `orangefs_permission`, `orangefs_getattr`, and `orangefs_dentry_operations` when VFS helpers dispatch into filesystem callbacks.

### Risks
Flag normalization is security-sensitive, especially `O_PATH`, `O_TMPFILE`, `O_DIRECTORY|O_CREAT`, and `openat2` resolve constraints. Credential override for `access()` must stay synchronized between `access_need_override_creds()` and `access_override_creds()`. Truncate/chown/chmod paths depend on correct idmapping and delegation retry behavior. `do_dentry_open()` has many cleanup paths where path, fops, write access, and file state must remain balanced.

### Test signals
Relevant tests include LTP or xfstests coverage for open/openat2 flag validation, truncate and ftruncate permissions, fallocate modes, chmod/chown idmapped mounts, O_DIRECT capability, close flush error behavior, and filesystem-specific tests ensuring OrangeFS callbacks receive correct VFS preconditions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/open.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/openpromfs/Makefile -->
## sources/distributed-fs/ceph-client/fs/openpromfs/Makefile

### Purpose
This Makefile wires the Sun OpenPROM pseudo filesystem into the kernel build when `CONFIG_SUN_OPENPROMFS` is enabled.

### Important APIs, types, and functions
- `obj-$(CONFIG_SUN_OPENPROMFS) += openpromfs.o` declares the module or built-in object.
- `openpromfs-objs := inode.o` states that `inode.c` is the sole implementation object.

### Control flow
Kbuild evaluates the config symbol and includes `openpromfs.o`; the composite object is linked from `inode.o`.

### State and persistence behavior
No runtime state is managed here. It controls build-time inclusion only.

### Dependencies and integration points
Depends on the architecture/configuration exposing `CONFIG_SUN_OPENPROMFS` and on `inode.c` providing module init and exit hooks.

### Risks
The only material risk is build drift if additional source files are added without updating `openpromfs-objs`.

### Test signals
Build with `CONFIG_SUN_OPENPROMFS=y` and `m` should produce the expected object/module and resolve the filesystem registration symbols from `inode.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/openpromfs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/openpromfs/inode.c -->
## sources/distributed-fs/ceph-client/fs/openpromfs/inode.c

### Purpose
This file implements `openpromfs`, a single-superblock pseudo filesystem exposing OpenPROM device-tree nodes as directories and firmware properties as regular files, usually under `/proc/openprom` or equivalent mounts.

### Important APIs, types, and functions
- `struct op_inode_info` extends `struct inode` with `enum op_inode_type` and a union pointing to either `struct device_node` or `struct property`.
- `is_string()` and `property_show()` format property values as printable strings, dot-separated bytes, or dot-separated 32-bit words.
- `openpromfs_lookup()` resolves child device nodes and properties under a firmware node.
- `openpromfs_readdir()` emits `.`, `..`, child nodes, then properties.
- `openprom_alloc_inode()`, `openprom_free_inode()`, and `openprom_iget()` manage the inode slab and `iget_locked()` lookup.
- `openprom_fill_super()`, `openpromfs_get_tree()`, `openpromfs_init_fs_context()`, `init_openprom_fs()`, and `exit_openprom_fs()` register and populate the filesystem.

### Control flow
Mount calls `get_tree_single()` and `openprom_fill_super()`, which creates the root inode with `OPENPROM_ROOT_INO`, sets directory inode/file operations, and stores `of_find_node_by_path("/")` in private inode data. Lookup and readdir both take `op_mutex`, walk `device_node` child and property lists, then create or find inodes using firmware-provided `unique_id` values. Property files open through `seq_open()` and print exactly one formatted record.

### State and persistence behavior
The filesystem has no persistent storage of its own. It mirrors the in-kernel OpenPROM/OpenFirmware device tree. Inode private data stores raw pointers to `device_node` and `property` objects, and root/noatime superblock settings avoid unnecessary timestamp behavior. Property reads are generated on demand.

### Dependencies and integration points
It depends on SPARC/OpenPROM headers and APIs: `asm/openprom.h`, `asm/oplib.h`, `asm/prom.h`, and OF node/property structures. It integrates with VFS through `file_system_type`, `fs_context_operations`, `super_operations`, `inode_operations`, `file_operations`, seq_file, simple statfs, and anon superblock teardown.

### Risks
The code assumes firmware node/property lists remain valid while exposed; `op_mutex` serializes traversal but does not by itself refcount individual properties. Property formatting uses raw typed loads for 32-bit output and is endian/alignment sensitive to firmware representation. The special `security-password` property is made owner read/write while most properties are read-only, so permission tests should verify that behavior.

### Test signals
Mounting openpromfs should show root node children as directories and node properties as files. Readdir should emit stable `.`/`..` plus children before properties. Reading string, byte-array, and word-array properties should match expected formatting. Module load/unload should register/unregister cleanly and free the inode cache after `rcu_barrier()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/openpromfs/inode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/orangefs/Kconfig -->
## sources/distributed-fs/ceph-client/fs/orangefs/Kconfig

### Purpose
This Kconfig entry exposes OrangeFS, also known as PVFS, as an optional Linux filesystem.

### Important APIs, types, and functions
- `config ORANGEFS_FS` defines a tristate option named `ORANGEFS (Powered by PVFS) support`.
- `select FS_POSIX_ACL` enables POSIX ACL support for OrangeFS builds.

### Control flow
When selected as built-in or module, Kbuild includes the OrangeFS object list from the companion Makefile and compiles the VFS client.

### State and persistence behavior
No runtime state is present. The file expresses build-time feature selection.

### Dependencies and integration points
The selected ACL dependency matches OrangeFS inode operations that export `.get_inode_acl` and `.set_acl`, and the xattr-backed ACL implementation in `acl.c`.

### Risks
The help text is brief and does not mention the required userspace daemon and `/dev/pvfs2-req` interface, which can surprise operators enabling only the kernel config.

### Test signals
Kernel config tests should confirm that `CONFIG_ORANGEFS_FS=m` builds the `orangefs.ko` module and that `FS_POSIX_ACL` is enabled when OrangeFS is selected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/orangefs/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/orangefs/Makefile -->
## sources/distributed-fs/ceph-client/fs/orangefs/Makefile

### Purpose
This Makefile assembles the OrangeFS filesystem module or built-in object.

### Important APIs, types, and functions
- `obj-$(CONFIG_ORANGEFS_FS) += orangefs.o` gates the filesystem on the Kconfig option.
- `orangefs-objs` lists ACL, file, cache, utility, xattr, dcache, inode, sysfs, module, superblock, device request, namei, symlink, directory, bufmap, debugfs, and waitqueue implementation objects.

### Control flow
Kbuild links all listed objects into a single `orangefs.o`. Module entry/exit comes from `orangefs-mod.c`; filesystem registration and superblock code come from `super.o`.

### State and persistence behavior
No runtime state is stored here. The object list defines which subsystems are compiled into the module.

### Dependencies and integration points
The object list is the integration map for the OrangeFS kernel client: VFS operations, upcall/downcall transport, shared memory buffers, xattrs/ACLs, sysfs/debugfs controls, and operation wait queues.

### Risks
Because the module is split across many interdependent objects, missing one object from `orangefs-objs` would produce unresolved symbols or a runtime feature gap. The Makefile must track any future split of protocol, waitqueue, or cache code.

### Test signals
Build with `CONFIG_ORANGEFS_FS=m` and `y`; verify all symbols resolve and the produced module registers filesystem `pvfs2`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/orangefs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/orangefs/acl.c -->
## sources/distributed-fs/ceph-client/fs/orangefs/acl.c

### Purpose
This file implements OrangeFS POSIX ACL support using extended attributes as the backing store.

### Important APIs, types, and functions
- `orangefs_get_acl()` maps ACL type to `system.posix_acl_access` or `system.posix_acl_default`, fetches the xattr, and converts it with `posix_acl_from_xattr()`.
- `__orangefs_set_acl()` serializes a `struct posix_acl` with `posix_acl_to_xattr()` and calls `orangefs_inode_setxattr()`.
- `orangefs_set_acl()` updates file mode through `posix_acl_update_mode()`, writes the ACL xattr, and applies mode changes through `__orangefs_setattr_mode()`.

### Control flow
Read rejects RCU mode with `-ECHILD`, allocates a maximum-size xattr buffer to avoid a probe round trip, fetches the ACL xattr, maps missing ACLs to `NULL`, and returns conversion errors as `ERR_PTR`. Write validates the ACL type, optionally converts the ACL to an xattr blob, stores or removes the xattr, updates the cached ACL, and for access ACLs applies any mode change calculated by the POSIX ACL helper.

### State and persistence behavior
ACLs persist as OrangeFS xattrs. The VFS ACL cache is updated with `set_cached_acl()` after successful writes. Mode changes are propagated to the server through OrangeFS setattr rather than being purely local.

### Dependencies and integration points
Depends on `orangefs_inode_getxattr()`, `orangefs_inode_setxattr()`, POSIX ACL helpers, `init_user_ns`, and the OrangeFS inode operations in `inode.c` and `namei.c` that expose `.get_inode_acl` and `.set_acl`.

### Risks
Allocating `ORANGEFS_MAX_XATTR_VALUELEN` for each get avoids one network call but can be expensive. ACL and mode updates are multi-step and can partially fail after xattr success or before mode propagation. RCU permission paths must fall back because ACL reads may block on network I/O.

### Test signals
Run ACL xfstests for getfacl/setfacl, default ACL inheritance on create and mkdir, chmod interactions, ACL removal, missing ACL behavior, and daemon unavailable errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/orangefs/acl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/orangefs/dcache.c -->
## sources/distributed-fs/ceph-client/fs/orangefs/dcache.c

### Purpose
This file implements OrangeFS dentry revalidation, ensuring cached positive and negative dentries remain consistent with the distributed server namespace.

### Important APIs, types, and functions
- `orangefs_revalidate_lookup()` performs a server lookup for the parent/name pair and compares the returned handle to a positive dentry inode, or expects `-ENOENT` for a negative dentry.
- `orangefs_d_revalidate()` checks the dentry timeout, rejects RCU revalidation when blocking I/O is needed, skips root handle validation, and calls `orangefs_inode_check_changed()` for positive dentries.
- `orangefs_dentry_operations` exports `.d_revalidate`.

### Control flow
If the dentry timeout stored in `d_fsdata` has not expired, revalidation succeeds locally. Otherwise non-RCU lookup issues `ORANGEFS_VFS_OP_LOOKUP` through `service_operation()`. Positive dentries are dropped on lookup error or handle mismatch; negative dentries are trusted only when lookup still returns `-ENOENT`. Positive entries then issue getattr/change validation before final success.

### State and persistence behavior
Dentry validity is cached by storing an expiration jiffy in `dentry->d_fsdata` through `orangefs_set_timeout()`. No metadata is persisted locally; validation is always backed by server lookup/getattr once the timeout expires.

### Dependencies and integration points
Depends on `op_alloc()`, `service_operation()`, `match_handle()`, `is_root_handle()`, `orangefs_inode_check_changed()`, and timeout globals from `orangefs-kernel.h`. It integrates with VFS dcache lookup and path walk through `d_revalidate`.

### Risks
Short timeout values reduce stale dentries but increase daemon round trips. RCU path walks receive `-ECHILD`, forcing slower ref-walks. A daemon or server error drops dentries, which is conservative but can degrade lookup-heavy workloads.

### Test signals
Test cross-client create/delete/rename visibility, negative dentry invalidation, root dentry stability, RCU path fallback, and behavior when the client daemon restarts while dentries are expired.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/orangefs/dcache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/orangefs/devorangefs-req.c -->
## sources/distributed-fs/ceph-client/fs/orangefs/devorangefs-req.c

### Purpose
This file implements the `/dev/pvfs2-req` character device that connects the kernel VFS client to the OrangeFS userspace client daemon. Kernel operations are read by userspace as upcalls and completed by writes containing downcalls.

### Important APIs, types, and functions
- `orangefs_devreq_open()` enforces a single nonblocking opener in `init_user_ns`.
- `orangefs_devreq_read()` dequeues a waiting `orangefs_kernel_op_s`, copies protocol version, magic, tag, and upcall to userspace, and moves the op to the in-progress hash table.
- `orangefs_devreq_write_iter()` validates version/magic/tag, removes the matching op from the hash table, copies the downcall and optional readdir trailer, and completes the waiter.
- `orangefs_devreq_release()` handles daemon shutdown, finalizes bufmap state, marks mounts pending, purges waiting and in-progress ops, and resets version/open state.
- `dispatch_ioctl_command()` handles device metadata, bufmap mapping, remount-all, upstream marker, and debug mask ioctls.
- `orangefs_dev_init()` and `orangefs_dev_cleanup()` register and unregister the character device.

### Control flow
Userspace opens the device with `O_NONBLOCK`, queries sizes and maps shared buffers through ioctls, then polls/reads. Read skips purged/given-up operations and operations whose filesystem is pending remount, copies the upcall header and payload, then marks the op in progress. Write receives the downcall header and body, verifies protocol compatibility and stable userspace version, finds the op by tag, optionally copies a readdir trailer into kernel memory, sets error status on malformed input, and wakes the original VFS waiter.

### State and persistence behavior
Runtime state includes `open_access_count`, `orangefs_userspace_version`, in-progress op hash tables, pending mount flags on superblocks, and bufmap lifetime. There is no on-disk persistence, but release has distributed consistency effects because it marks existing mounts pending and forces remount/retry semantics after daemon restart.

### Dependencies and integration points
Depends on operation lists and hash tables from `orangefs-mod.c`, bufmap APIs, debugfs APIs, superblock list state, waitqueue purge functions, and protocol structs from `orangefs-dev-proto.h`, `upcall.h`, and `downcall.h`. VFS operations throughout OrangeFS depend on this device path through `service_operation()`.

### Risks
This is a trust boundary. Size, magic, protocol version, trailer length, and tag validation protect kernel state from malformed daemon writes. Single-opener enforcement is required because multiple daemons could otherwise race operation ownership. Release/purge paths must avoid use-after-free while marking ops purged or completing cancellations. Large readdir trailers allocate with `vzalloc()` and must be freed by directory code or error paths.

### Test signals
Exercise daemon open rejection, blocking open/read rejection, ioctl size queries, bufmap mapping, read/write protocol mismatch, readdir trailer validation, daemon crash/restart purging, remount-all, poll readiness, and compat ioctl mapping from 32-bit userspace.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/orangefs/devorangefs-req.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/orangefs/dir.c -->
## sources/distributed-fs/ceph-client/fs/orangefs/dir.c

### Purpose
This file implements OrangeFS directory file operations, including stateful readdir over daemon-returned directory trailers.

### Important APIs, types, and functions
- `struct orangefs_dir_part` and `struct orangefs_dir` store linked readdir result parts, server token, logical end position, and sticky error.
- `do_readdir()` sends `ORANGEFS_VFS_OP_READDIR`, allocates a readdir slot, handles purged retry, validates trailer size, and updates the token.
- `parse_readdir()` attaches the trailer buffer as a directory part after the response header.
- `fill_from_part()` decodes length/string/khandle records and emits dirents.
- `orangefs_dir_iterate()`, `orangefs_dir_llseek()`, `orangefs_dir_open()`, and `orangefs_dir_release()` implement VFS directory behavior.
- `orangefs_dir_operations` exports `.iterate_shared`, `.llseek`, `.open`, `.release`, and lease support.

### Control flow
Open allocates per-file directory state with token `ORANGEFS_ITERATE_START`. Iterate emits `.` and `..`, then uses high bits of `ctx->pos` as a part index and low bits as an offset within the part. If the caller seeks beyond cached parts, the code reads more from the server until it reaches the requested position or end token. Each trailer is parsed lazily as emitted. A seek to an earlier offset frees cached parts and restarts token iteration so userspace sees fresh directory contents.

### State and persistence behavior
Per-open state caches server directory result parts in vmalloc-backed trailer buffers returned by the daemon. Directory contents are not persisted locally and are discarded on release or when llseek resets the stream.

### Dependencies and integration points
Depends on `service_operation()`, readdir slot allocation from `orangefs-bufmap.c`, trailer layout from `downcall.h`, handle hashing from `orangefs-kernel.h`, and VFS `dir_context` emission. It is installed for directory inodes by `orangefs_init_iops()`.

### Risks
Directory offset encoding is custom and must remain compatible with userspace `telldir/seekdir` behavior. Corrupt trailer data or invalid offsets are mapped to `-EIO`. Trailer ownership transfers to the directory part list, so every path must either free or retain exactly once. The code uses `BUG_ON()` for impossible offset overflow, which is harsh if malformed trailers bypass validation.

### Test signals
Test large directories over multiple parts, seekdir/telldir, short userspace buffers, daemon restart during readdir, corrupt trailer handling, readdir after rename/create/delete, and release freeing all cached parts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/orangefs/dir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/orangefs/downcall.h -->
## sources/distributed-fs/ceph-client/fs/orangefs/downcall.h

### Purpose
This header defines the daemon-to-kernel response payloads for OrangeFS operations.

### Important APIs, types, and functions
- Response structs cover file I/O, lookup, create, symlink, getattr, mkdir, statfs, fs mount, xattrs, parameters, perf counters, fs keys, and features.
- `struct orangefs_downcall_s` contains `type`, `status`, optional trailer metadata, and a union of response payloads.
- `struct orangefs_readdir_response_s` defines the header at the start of readdir trailer data.

### Control flow
The daemon writes a downcall through `/dev/pvfs2-req`; `devorangefs-req.c` copies this struct into the waiting operation, then consuming subsystems read the matching union member after `service_operation()` returns.

### State and persistence behavior
The header is an in-memory protocol contract. `trailer_buf` is a kernel pointer allocated during write handling for readdir and later owned by directory iteration code.

### Dependencies and integration points
Included by `orangefs-dev-proto.h`, paired with `upcall.h`, and consumed by file, inode, superblock, directory, xattr, sysfs, and debug code. Sizes and field alignment are part of the kernel/userspace ABI.

### Risks
The structs carry fixed-size arrays and 32/64-bit fields, so padding and compatibility matter. The comment notes readdir response data lives in the trailer, making trailer size validation critical. Any ABI change must preserve userspace daemon compatibility.

### Test signals
Protocol tests should validate 32-bit and 64-bit daemon interaction, each operation type's expected response union, readdir trailer parsing, and behavior for nonzero `status`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/orangefs/downcall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/orangefs/file.c -->
## sources/distributed-fs/ceph-client/fs/orangefs/file.c

### Purpose
This file implements OrangeFS regular file operations and the synchronous direct-I/O bridge to the userspace daemon.

### Important APIs, types, and functions
- `flush_racache()` sends `ORANGEFS_VFS_OP_RA_FLUSH`.
- `wait_for_direct_io()` is the central I/O operation: allocates a bufmap slot, copies write data into shared memory, services the op, handles daemon purge/retry, copies read data out, and returns amount complete.
- `orangefs_revalidate_mapping()` invalidates stale page cache under a bitlock and timeout.
- `orangefs_file_read_iter()`, `orangefs_file_splice_read()`, and `orangefs_file_write_iter()` wrap generic file I/O with OrangeFS cache revalidation and counters.
- `orangefs_fault()` and `orangefs_file_mmap_prepare()` handle mmap faults and VMA setup.
- `orangefs_fsync()`, `orangefs_file_llseek()`, `orangefs_lock()`, and `orangefs_flush()` implement fsync, size-aware seek, local locking, and close-time writeback flush.
- `orangefs_file_operations` exports the file operation vector.

### Control flow
Buffered reads take `i_rwsem`, revalidate page cache, then call generic read/splice. Writes revalidate when writing beyond EOF, then use generic write, which reaches OrangeFS address-space operations in `inode.c`. Direct I/O and writeback call `wait_for_direct_io()`: allocate op and shared slot, populate credentials and permission workaround uid, copy data for writes, call `service_operation()`, retry with a new slot if the daemon purged the op, copy read data from shared memory, release slot and op. Fsync first writes dirty page cache then sends `ORANGEFS_VFS_OP_FSYNC`.

### State and persistence behavior
Persistent data transfer is performed by the userspace daemon/server after upcall service. Local state includes page-cache mapping timeout, bitlock serialization, read/write stats, bufmap slot usage, and per-file local locks when mounted with `local_lock`.

### Dependencies and integration points
Depends on bufmap APIs, operation service/waitqueue, OrangeFS inode private data, sysfs timeout globals, generic filemap helpers, mmap VMA operations, POSIX locks, and feature flags from superblock setup. It is installed on regular files by `orangefs_init_iops()`.

### Risks
The I/O path straddles page cache, shared memory, and a userspace daemon. Interrupt handling must avoid reporting `EINTR` after writes that may already have reached the daemon. Purged retry must revert iov_iter state for writes before recopying. The uid override to 0 for already-opened files is a semantic workaround and should be scrutinized in permission/security tests. Cache invalidation uses a custom bitlock and timeout, which can affect coherency and latency.

### Test signals
Run buffered and direct read/write tests, mmap read/write faults, write beyond EOF, fsync durability, close flush behavior, daemon restart during I/O, large I/O spanning bufmap slots, interrupted I/O, local_lock on/off behavior, and cache timeout coherency across clients.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/orangefs/file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/orangefs/inode.c -->
## sources/distributed-fs/ceph-client/fs/orangefs/inode.c

### Purpose
This file implements OrangeFS inode operations and address-space operations: page-cache read/writeback, direct I/O dispatch, mmap write faults, setattr/getattr/permission/update-time, file attributes, and inode instantiation.

### Important APIs, types, and functions
- Writeback helpers: `orangefs_writepage_locked()`, `struct orangefs_writepages`, `orangefs_writepages_work()`, `orangefs_writepages_callback()`, and `orangefs_writepages()`.
- Read helpers: `orangefs_readahead()` and `orangefs_read_folio()`.
- Page-cache mutation helpers: `orangefs_write_begin()`, `orangefs_write_end()`, `orangefs_invalidate_folio()`, `orangefs_release_folio()`, `orangefs_free_folio()`, and `orangefs_launder_folio()`.
- I/O and mmap: `orangefs_direct_IO()` and `orangefs_page_mkwrite()`.
- Metadata: `orangefs_setattr_size()`, `__orangefs_setattr()`, `__orangefs_setattr_mode()`, `orangefs_setattr()`, `orangefs_getattr()`, `orangefs_permission()`, `orangefs_update_time()`, `orangefs_fileattr_get()`, and `orangefs_fileattr_set()`.
- Inode lifecycle: `orangefs_init_iops()`, `orangefs_handle_hash()`, `orangefs_set_inode()`, `orangefs_test_inode()`, `orangefs_iget()`, and `orangefs_new_inode()`.

### Control flow
Reads from page cache issue `wait_for_direct_io(READ)` from readahead or read_folio and mark folios uptodate. Writes attach a private `orangefs_write_range` to folios recording dirty range and caller credentials, mark dirty, then writeback batches adjacent folios with matching uid/gid into a single daemon I/O where possible. Direct I/O loops in bufmap-sized chunks and updates file size/time on success. Truncate refreshes size, adjusts page cache and `i_size`, sends `ORANGEFS_VFS_OP_TRUNCATE`, and marks ctime/mtime changes. New or looked-up inodes are keyed by OrangeFS fsid/khandle through `iget5_locked()` or `insert_inode_locked4()`, then populated by getattr and assigned file/dir/symlink operation tables.

### State and persistence behavior
Inode private state holds object references, xattr cache, attr cache metadata, mapping timeout, and folio dirty-range private data. Server-persistent changes happen through truncate, setattr writeback, xattr-backed file flags, ACL helpers, and data I/O upcalls. The page cache is treated as time-limited because other clients can mutate data.

### Dependencies and integration points
Depends on `file.c` for `wait_for_direct_io()`, `orangefs-utils.c` for getattr/setattr/xattrs/error mapping, `orangefs-bufmap.c` for I/O buffer sizing, POSIX ACL helpers, generic address-space helpers, and VFS inode/file/directory operation contracts. It exports operation vectors used by namei and superblock code.

### Risks
Folio private dirty ranges are complex: invalidation, mmap writes, laundering, and batched writeback must keep range/credentials correct. Writeback grouping by uid/gid affects permission semantics. Truncate intentionally reorders `truncate_setsize` steps and must recover cleanly from server failure. `orangefs_update_time()` may block and returns `-EAGAIN` for NOWAIT. Inode number hashing can collide, so iget uses handle comparison, but user-visible inode numbers are not globally unique beyond the hash.

### Test signals
Use xfstests for buffered writeback, mmap write faults, truncate extend/shrink, partial folio invalidation, direct I/O, readahead, writeback under memory pressure, chmod/chown/time updates, fileattr flags, ACL create inheritance, hard server/daemon errors, and stale inode detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/orangefs/inode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/orangefs/namei.c -->
## sources/distributed-fs/ceph-client/fs/orangefs/namei.c

### Purpose
This file implements OrangeFS namespace inode operations for directories: lookup, create, unlink/rmdir, symlink, mkdir, and rename.

### Important APIs, types, and functions
- `orangefs_create()` sends `ORANGEFS_VFS_OP_CREATE`, creates a VFS inode from the returned handle, instantiates the dentry, and updates parent times.
- `orangefs_lookup()` sends `ORANGEFS_VFS_OP_LOOKUP`, maps success to `orangefs_iget()`, maps `-ENOENT` to a negative dentry, and uses `d_splice_alias()`.
- `orangefs_unlink()` sends `ORANGEFS_VFS_OP_REMOVE`, drops link count, and updates parent times.
- `orangefs_symlink()` sends `ORANGEFS_VFS_OP_SYMLINK`, creates a symlink inode, fixes symlink size locally, and instantiates the dentry.
- `orangefs_mkdir()` sends `ORANGEFS_VFS_OP_MKDIR`, creates a directory inode, and keeps directory nlink effectively constant.
- `orangefs_rename()` sends `ORANGEFS_VFS_OP_RENAME` and updates directory/target ctime.
- `orangefs_dir_inode_operations` exports the directory inode operation vector.

### Control flow
All namespace mutations allocate an operation, fill parent refs, names, and default attrs, call `service_operation()`, then reconcile VFS state from returned OrangeFS handles. Successful create-like operations call `orangefs_new_inode()`, `d_instantiate_new()`, and `orangefs_set_timeout()`. Parent mtime/ctime updates are performed locally through `__orangefs_setattr()` after success. Lookup always queries the server even in create-intent paths to preserve `O_EXCL` semantics.

### State and persistence behavior
Namespace state persists on the OrangeFS server via userspace daemon operations. Local dentry timeouts are refreshed after successful lookup/create/mkdir/symlink. Parent timestamps are locally marked and synced through OrangeFS setattr machinery.

### Dependencies and integration points
Depends on operation service, inode allocation in `inode.c`, timeout helpers, default sys_attr macro, and VFS dentry/inode operation contracts. Directory operation vector is installed for directory inodes by `orangefs_init_iops()`.

### Risks
Most operations are multi-phase: server mutation can succeed while local inode instantiation or ACL setup fails. Rename rejects all flags, so newer VFS rename modes are unsupported. `orangefs_mkdir()` returns `ERR_PTR(ret)` even though modern mkdir inode op signatures normally return a dentry pointer in this tree, making signature compatibility important. Parent timestamp updates are best-effort relative to the server mutation.

### Test signals
Test create/open exclusive behavior, lookup negative caching, unlink/rmdir, symlink target length and size, mkdir ACL inheritance, rename overwrite and unsupported flags, cross-client namespace visibility, daemon failure after server success, and parent timestamp changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/orangefs/namei.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/orangefs/orangefs-bufmap.c -->
## sources/distributed-fs/ceph-client/fs/orangefs/orangefs-bufmap.c

### Purpose
This file manages the shared userspace buffer map used for OrangeFS file I/O and the separate slot map used for readdir operations.

### Important APIs, types, and functions
- `struct slot_map` tracks available slots with a bitmap, count, and waitqueue.
- Slot helpers `install()`, `mark_killed()`, `run_down()`, `get()`, and `put()` manage map lifecycle and blocking slot acquisition.
- `struct orangefs_bufmap_desc` records the userspace address and grouped folios for each descriptor.
- `orangefs_bufmap_initialize()` validates daemon-provided mapping parameters, pins user pages, groups them into folios, builds descriptor mappings, publishes the global map, and installs slot maps.
- `orangefs_bufmap_finalize()` and `orangefs_bufmap_run_down()` kill, drain, unpin, and free the map.
- `orangefs_bufmap_get()`, `orangefs_bufmap_put()`, `orangefs_readdir_index_get()`, and `orangefs_readdir_index_put()` allocate/release slots.
- `orangefs_bufmap_copy_from_iovec()` and `orangefs_bufmap_copy_to_iovec()` copy between iov_iter data and mapped folios, with a fast path for two 2 MiB folios.

### Control flow
The daemon maps a page-aligned shared memory region through `ORANGEFS_DEV_MAP`. Initialization validates total size, descriptor size/count consistency, page divisibility, and alignment, then pins pages with `pin_user_pages_fast(FOLL_WRITE)`. It groups consecutive pages by folio and assigns enough folios to each descriptor. File I/O gets a free slot, copies data into or out of the descriptor, and returns the slot. Device release marks maps killed, wakes waiters, waits for outstanding slots to return, then unpins and frees all structures.

### State and persistence behavior
The global `__orangefs_bufmap` is runtime state tied to the daemon process lifetime. Pinned user pages are not persistent storage, but they are the transport for persistent file data between kernel and userspace daemon. Slot waiters use configurable `slot_timeout_secs` and a shorter wait while the map is not installed.

### Dependencies and integration points
Used by `file.c` for read/write data transfer, `dir.c` for readdir slot indexes, and `devorangefs-req.c` for map setup/teardown. Depends on GUP, folios, bitmaps, waitqueues, and protocol `ORANGEFS_dev_map_desc`.

### Risks
Pinned user memory lifetime is sensitive: unpin must happen after all users release slots. The code allows degraded folio layouts but has a special fast path for a two-THP descriptor; both paths need identical correctness. `orangefs_bufmap_size_query()` can return 0 before mapping, affecting I/O chunking if callers do not handle daemon-not-ready states. Timeout and signal behavior in slot waits is observable by file I/O.

### Test signals
Test mapping validation, partial pin failure rollback, daemon exit while slots are held, slot timeout and interrupt paths, highmem/folio layouts, fast path and generic copy path, large I/O chunking, and readdir slot exhaustion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/orangefs/orangefs-bufmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/orangefs/orangefs-bufmap.h -->
## sources/distributed-fs/ceph-client/fs/orangefs/orangefs-bufmap.h

### Purpose
This header declares the OrangeFS bufmap API used by the device, file I/O, and directory code.

### Important APIs, types, and functions
It declares map lifecycle (`orangefs_bufmap_initialize`, `orangefs_bufmap_finalize`, `orangefs_bufmap_run_down`), size query, regular I/O slot get/put, readdir slot get/put, and iov_iter copy helpers.

### Control flow
Callers initialize the map from the daemon-provided descriptor, get a slot before issuing operations that require shared memory or readdir indices, copy data as needed, and put the slot after the daemon completes the operation. Shutdown is a two-phase finalize/run-down sequence.

### State and persistence behavior
The header exposes no state directly; it abstracts the global map in `orangefs-bufmap.c`.

### Dependencies and integration points
Depends on `struct ORANGEFS_dev_map_desc` and `struct iov_iter` declarations being visible through including sources. Used by `file.c`, `inode.c`, `dir.c`, and `devorangefs-req.c`.

### Risks
The API does not encode whether a slot is regular I/O or readdir, so callers must pair the right get/put functions. Copy helpers assume a valid initialized map and buffer index.

### Test signals
Compile coverage catches declaration drift. Runtime tests should verify every get path has a matching put on success, error, interrupt, and daemon purge paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/orangefs/orangefs-bufmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/orangefs/orangefs-cache.c -->
## sources/distributed-fs/ceph-client/fs/orangefs/orangefs-cache.c

### Purpose
This file manages the slab cache for OrangeFS kernel operations and assigns unique operation tags used to match daemon downcalls to VFS waiters.

### Important APIs, types, and functions
- `op_cache_initialize()` creates a usercopy-aware `orangefs_op_cache` and initializes `next_tag_value`.
- `op_cache_finalize()` destroys the cache.
- `get_opname_string()` maps operation type constants to debug strings.
- `orangefs_new_tag()` increments the tag counter under a spinlock, skipping zero.
- `op_alloc()` allocates and initializes `struct orangefs_kernel_op_s`, sets type, tag, state, completion, list, lock, and current fsuid/fsgid in the upcall.
- `op_release()` frees the operation back to the slab.

### Control flow
Module init creates the slab before any operation can be allocated. Each VFS path calls `op_alloc(type)`, fills request-specific upcall fields, sends it through `service_operation()`, then calls `op_release()` when finished. The device write path uses the operation tag to locate the in-progress op and complete it.

### State and persistence behavior
Operation objects are transient. Tags are monotonically increasing runtime identifiers, reset at module load, and form the matching key for in-memory requests only.

### Dependencies and integration points
Depends on `orangefs_kernel_op_s` layout, protocol operation constants, current credentials, and debug logging. Used by every OrangeFS subsystem issuing upcalls.

### Risks
Tag uniqueness is only within a module lifetime and can wrap; the code resets zero to 100. Any op released while still reachable from request or hash lists would be catastrophic, so ownership conventions around cancellation and purge paths matter. Usercopy slab bounds must stay aligned with copied upcall fields.

### Test signals
Stress concurrent op allocation, tag wrap simulation, daemon downcall matching, cancellation/purge release paths, and slab init/finalize during module load failure unwinds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/orangefs/orangefs-cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/orangefs/orangefs-debug.h -->
## sources/distributed-fs/ceph-client/fs/orangefs/orangefs-debug.h

### Purpose
This header defines OrangeFS gossip debug mask bits.

### Important APIs, types, and functions
It declares `GOSSIP_*_DEBUG` bits for superblock, inode, file, directory, utility, wait, ACL, dcache, device, namei, bufmap, cache, debugfs, xattr, init, and sysfs logging, plus `GOSSIP_NO_DEBUG`, `GOSSIP_MAX_NR`, and `GOSSIP_MAX_DEBUG`.

### Control flow
Logging call sites pass these masks to `gossip_debug()`. Debugfs and module parameters convert between strings and these bitmasks.

### State and persistence behavior
No state is stored here. The bit definitions affect runtime debug state held in `orangefs_gossip_debug_mask`.

### Dependencies and integration points
Usable from kernel and non-kernel contexts, with conditional includes and an `ARRAY_SIZE` fallback. Integrated by `orangefs-debugfs.c` and all OrangeFS logging call sites.

### Risks
Mask collisions would make debug controls misleading; the header centralizes bits to avoid that. `GOSSIP_MAX_NR` must match the highest defined bit count.

### Test signals
Debugfs `kernel-debug` writes for each keyword should toggle the corresponding mask and `debug-help` should list all keywords.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/orangefs/orangefs-debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/orangefs/orangefs-debugfs.c -->
## sources/distributed-fs/ceph-client/fs/orangefs/orangefs-debugfs.c

### Purpose
This file implements OrangeFS debugfs controls under `/sys/kernel/debug/orangefs` for kernel debug masks, client debug masks, and debug keyword help.

### Important APIs, types, and functions
- `s_kmod_keyword_mask_map` maps kernel debug keywords to `GOSSIP_*` masks.
- `orangefs_debugfs_init()` creates the debugfs directory and files and normalizes the initial module debug mask.
- `orangefs_prepare_debugfs_help_string()` builds the help text from kernel keywords and, after daemon startup, client-provided keywords.
- `orangefs_debug_read()` and `orangefs_debug_write()` implement `kernel-debug` and `client-debug` file behavior.
- `orangefs_prepare_cdm_array()`, `debug_mask_to_string()`, `debug_string_to_mask()`, and helpers convert between keyword strings and masks.
- `orangefs_debugfs_new_client_mask()`, `orangefs_debugfs_new_client_string()`, and `orangefs_debugfs_new_debug()` receive daemon ioctl-provided debug information.

### Control flow
Module init builds an initial help string saying client keywords are unknown, then creates debugfs files. Writing `kernel-debug` parses the keyword string into `orangefs_gossip_debug_mask` and rewrites the displayed string. Writing `client-debug` requires the daemon to be running, converts keywords into the client's two-mask representation, and sends an `ORANGEFS_VFS_OP_PARAM` request. The daemon can later provide client keyword arrays and masks via ioctls, causing `client-debug` and `debug-help` to be rebuilt.

### State and persistence behavior
Runtime state includes kernel/client debug strings, client keyword array, debugfs dentries, help string allocation, and flags tracking whether module parameters set masks. Settings are volatile and reset on module reload, except the module parameter can seed the initial mask.

### Dependencies and integration points
Depends on debugfs, seq_file, usercopy, `service_operation()`, `is_daemon_in_service()`, protocol debug ioctl structs, and `orangefs_gossip_debug_mask` from `orangefs-mod.c`. Device ioctls call the exported update functions.

### Risks
String parsing and fixed-size buffers must avoid overflow; the code trims and bounds user input but uses several string concatenation paths. Client keyword state is daemon-supplied and must be initialized before client mask conversion. Debug file permissions are `0444` in creation calls despite write handlers, so mode semantics should be checked against `debugfs_create_file_aux_num()` behavior in this tree.

### Test signals
Test `debug-help` before and after daemon starts, write/read `kernel-debug`, invalid keyword filtering, `all` and `verbose` behavior, daemon-provided client masks, client-debug write with daemon down, and cleanup freeing debugfs entries and help memory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/orangefs/orangefs-debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/orangefs/orangefs-debugfs.h -->
## sources/distributed-fs/ceph-client/fs/orangefs/orangefs-debugfs.h

### Purpose
This header exposes debugfs lifecycle and daemon-update hooks for OrangeFS.

### Important APIs, types, and functions
It declares `orangefs_debugfs_init()`, `orangefs_debugfs_cleanup()`, `orangefs_prepare_debugfs_help_string()`, `orangefs_debugfs_new_client_mask()`, `orangefs_debugfs_new_client_string()`, and `orangefs_debugfs_new_debug()`.

### Control flow
Module init prepares help, then calls init; module exit calls cleanup. Device ioctls call the `new_*` functions when the userspace daemon supplies debug settings.

### State and persistence behavior
No state is declared in the header. State lives in `orangefs-debugfs.c`.

### Dependencies and integration points
Includes user-pointer function signatures for ioctl paths and is included by `orangefs-mod.c` and `devorangefs-req.c`.

### Risks
The header has no include guard in this snapshot, so repeated inclusion relies on compatible duplicate declarations.

### Test signals
Build coverage should catch signature drift between device ioctl dispatch and debugfs implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/orangefs/orangefs-debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/orangefs/orangefs-dev-proto.h -->
## sources/distributed-fs/ceph-client/fs/orangefs/orangefs-dev-proto.h

### Purpose
This header defines operation type constants and shared protocol limits for the OrangeFS kernel/userspace device ABI.

### Important APIs, types, and functions
- `ORANGEFS_VFS_OP_*` constants enumerate file I/O, lookup, create, metadata, mount, xattr, parameter, perf, cancel, fsync, fs key, readdirplus, and feature requests.
- `ORANGEFS_FEATURE_READAHEAD` declares the negotiated readahead feature bit.
- `ORANGEFS_MAX_DEBUG_STRING_LEN` and `ORANGEFS_MAX_DIRENT_COUNT_READDIR` set fixed protocol buffer limits.
- It includes `upcall.h` and `downcall.h`.

### Control flow
Operation allocation sets one of these op types in `upcall.type`; the daemon receives that type and returns a matching downcall type/status. Feature negotiation and sysfs support use the readahead feature flag.

### State and persistence behavior
No runtime state. The constants are a stable ABI shared by kernel and daemon.

### Dependencies and integration points
Included by `orangefs-kernel.h` and thus almost every OrangeFS file. The fixed constants must match userspace client-core definitions.

### Risks
ABI drift between kernel and daemon would break operation dispatch. The comment warns constants should remain multiples of 8 where relevant to avoid 32/64-bit interaction issues.

### Test signals
Run protocol compatibility tests across 32-bit compat and native userspace, daemon/kernel version mismatch tests, and feature negotiation tests for readahead support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/orangefs/orangefs-dev-proto.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/orangefs/orangefs-kernel.h -->
## sources/distributed-fs/ceph-client/fs/orangefs/orangefs-kernel.h

### Purpose
This is the central OrangeFS kernel header, defining core private structures, operation states, constants, inline helpers, cross-file declarations, global state, and service-operation flags.

### Important APIs, types, and functions
- Constants include default op/slot timeouts, request device name, protocol magic, max up/down sizes, and mount option bits.
- `enum orangefs_vfs_op_states` describes op lifecycle states: unknown, waiting, in progress, serviced, purged, and given up.
- `struct orangefs_kernel_op_s` contains op state, tag, shared-memory slot metadata, upcall/downcall payloads, completion, spinlock, attempts, and list node.
- `struct orangefs_inode_s`, `struct orangefs_sb_info_s`, `struct orangefs_stats`, `struct orangefs_cached_xattr`, and `struct orangefs_write_range` define per-inode, per-superblock, statistics, cached xattr, and dirty-range state.
- Inline helpers include `ORANGEFS_I()`, `ORANGEFS_SB()`, `orangefs_khandle_to_ino()`, `get_khandle_from_ino()`, `is_root_handle()`, `match_handle()`, `set_op_state_serviced()`, `set_op_state_purged()`, `fill_default_sys_attrs`, and `orangefs_set_timeout()`.
- It declares exported functions and globals across cache, module, waitqueue, superblock, inode, xattr, namei, device, file, utility, and operation service code.

### Control flow
Most OrangeFS source files include this header, allocate `orangefs_kernel_op_s` objects, fill upcalls, queue them through `service_operation()`, and inspect downcalls. State helpers drive operation transitions used by the device and waitqueue code. Inode and superblock helpers bridge VFS objects to OrangeFS private state.

### State and persistence behavior
The header defines runtime state layouts. Persistent server identity is represented by `orangefs_object_kref` stored in inodes and superblocks. Timeouts and mount flags drive local cache validity and interrupt behavior. Operation states are transient but central to daemon restart and cancellation semantics.

### Dependencies and integration points
Includes many Linux VFS, memory, mount, ACL, xattr, exportfs, and wait headers plus `orangefs-dev-proto.h`. It is the integration contract for all OrangeFS compilation units and must remain consistent with VFS API versions.

### Risks
Because this is a broad shared header, layout changes can affect slab usercopy ranges, ABI copies, waitqueue logic, and every subsystem. `set_op_state_purged()` has special cancellation behavior that frees a bufmap slot and releases the op; callers must not touch the op afterward. Timeout storage in `d_fsdata` casts jiffies through `void *`, which relies on pointer-sized storage.

### Test signals
Compile with sparse/lockdep and run module load/unload, daemon restart, cancellation, cache timeout, inode lookup, and xattr/ACL tests to cover the shared contracts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/orangefs/orangefs-kernel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/orangefs/orangefs-mod.c -->
## sources/distributed-fs/ceph-client/fs/orangefs/orangefs-mod.c

### Purpose
This file is the OrangeFS module entry point. It owns global module parameters, operation queues, filesystem registration, device/debugfs/sysfs initialization, and shutdown checks.

### Important APIs, types, and functions
- Globals include `orangefs_stats`, `hash_table_size`, `orangefs_gossip_debug_mask`, operation/slot/cache timeout parameters, `orangefs_request_mutex`, in-progress hash table, request list, locks, and waitqueue.
- `orangefs_fs_type` registers filesystem name `pvfs2`.
- `orangefs_init()` initializes op and inode caches, op hash table, fsid key table, debug help/debugfs/sysfs, request device, and filesystem registration with cleanup unwinds.
- `orangefs_exit()` unregisters the filesystem, cleans debugfs/sysfs/device/key/cache resources, asserts queues empty, and frees the hash table.
- `purge_inprogress_ops()` marks all in-progress operations purged when the daemon exits.

### Control flow
Module load normalizes negative timeout parameters to zero, sets up all global state before exposing the filesystem, then registers `/dev/pvfs2-req` and finally `pvfs2`. Failure unwinds in reverse order. Module exit unregisters first, then destroys observability/device/key/cache state. Device release calls `purge_inprogress_ops()` to wake operations that were already handed to the daemon.

### State and persistence behavior
All state is runtime kernel module state. Mounted superblocks and server data persist elsewhere, but daemon loss marks operations purged and superblocks pending remount through device release logic. Stats counters are volatile.

### Dependencies and integration points
Coordinates `orangefs-cache.c`, `super.c`, `orangefs-debugfs.c`, `orangefs-sysfs.c`, `devorangefs-req.c`, `waitqueue.c`, and VFS filesystem registration. Module parameters expose debug and timeout tuning.

### Risks
Initialization order matters because VFS calls can start after filesystem registration. Shutdown uses `BUG_ON()` if request lists are not empty, which makes leaked operations fatal. Hash table size is a module parameter with no explicit lower-bound validation, so invalid values could break hashing if set badly.

### Test signals
Test module load/unload repeatedly, failure injection at each init step, nondefault module parameters, daemon crash while operations are in progress, and queue-empty assertions after forced unmounts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/orangefs/orangefs-mod.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/orangefs/orangefs-sysfs.c -->
## sources/distributed-fs/ceph-client/fs/orangefs/orangefs-sysfs.c

### Purpose
This file implements OrangeFS sysfs controls and counters under `/sys/fs/orangefs`, including local timeout settings, daemon-backed cache/performance tunables, readahead settings, and simple read/write stats.

### Important APIs, types, and functions
- `struct orangefs_attribute` wraps sysfs attributes with OrangeFS-specific show/store callbacks.
- `orangefs_attr_show()` and `orangefs_attr_store()` dispatch generic sysfs operations and deny writes to `perf_counters` and `stats`.
- `sysfs_int_show()` and `sysfs_int_store()` expose kernel-local timeout and stats values.
- `sysfs_service_op_show()` sends `ORANGEFS_VFS_OP_PARAM` or `ORANGEFS_VFS_OP_PERF_COUNT` to the daemon to retrieve daemon-side settings and counters.
- `sysfs_service_op_store()` validates input and sends `ORANGEFS_PARAM_REQUEST_SET` operations to the daemon.
- Many `orangefs_attribute` instances define root, `acache`, `capcache`, `ccache`, `ncache`, `perf_counters`, and `stats` files.
- `orangefs_sysfs_init()` creates all kobjects and `orangefs_sysfs_exit()` releases them.

### Control flow
Module init creates `/sys/fs/orangefs`, cache subdirectories, `perf_counters`, and `stats` kobjects. Reads of local integer attributes return kernel globals directly. Reads/writes of daemon-backed attributes allocate a param/perf op, require the daemon in service, map the kobject/name to a protocol operation enum, call `service_operation()`, and format or store the returned value. Readahead attributes are rejected if `ORANGEFS_FEATURE_READAHEAD` was not negotiated.

### State and persistence behavior
Kernel-local timeout attributes mutate module globals immediately. Daemon-backed attributes mutate userspace client-core state through service operations and are not persisted by this file. Read/write stats are volatile counters updated in `file.c`.

### Dependencies and integration points
Depends on kobject/sysfs APIs, `op_alloc()`, `service_operation()`, `is_daemon_in_service()`, protocol param/perf enums, feature flags, and timeout/stat globals. Exposed controls directly influence cache invalidation, slot waits, operation waits, daemon cache behavior, and readahead.

### Risks
Mapping string attribute names to protocol operations is verbose and easy to drift. Some invalid user values are converted to `-EINVAL` after internal `rc == 0` handling. Daemon-backed sysfs operations can block and fail when the daemon is down. Cleanup must handle partially initialized kobjects and release callbacks free the global object pointers.

### Test signals
Test sysfs tree creation/removal, read/write of local timeout attributes, daemon-down behavior for service-backed files, validation ranges for cache limits and readahead settings, feature-gated readahead rejection, perf counter output, stats reads after file I/O, and failure injection during kobject creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/orangefs/orangefs-sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/orangefs/orangefs-sysfs.h -->
## sources/distributed-fs/ceph-client/fs/orangefs/orangefs-sysfs.h

### Purpose
This header declares the OrangeFS sysfs lifecycle functions.

### Important APIs, types, and functions
- `orangefs_sysfs_init()` creates the `/sys/fs/orangefs` hierarchy.
- `orangefs_sysfs_exit()` releases it.

### Control flow
`orangefs-mod.c` calls init during module load after debugfs setup and calls exit during failure unwind and module unload.

### State and persistence behavior
No state is stored in the header. Sysfs kobject state is private to `orangefs-sysfs.c`.

### Dependencies and integration points
Included by `orangefs-mod.c`; paired directly with `orangefs-sysfs.c`.

### Risks
There is no include guard in this two-line header, but duplicate extern declarations are harmless in normal C compilation.

### Test signals
Build coverage and module load/unload should confirm the declarations match the implementation and no sysfs symbols are missing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/orangefs/orangefs-sysfs.h -->
