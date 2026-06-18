# Group Research: group_727_linux_sources_os_linux_linux_fs_coda_inode_c_sources_os_linux_linux__eb4367279c3a

Scope: `Docs/research_subset_a.md` includes `sources/os/linux/linux`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/coda/inode.c -->
# File Research: sources/os/linux/linux/fs/coda/inode.c

## Purpose
Implements Coda filesystem superblock, mount context, inode-cache, root setup, filesystem registration metadata, and common inode operations for getattr/setattr/statfs.

## Main Elements
- Inode cache lifecycle: `coda_init_inodecache()`, `coda_destroy_inodecache()`, `coda_alloc_inode()`, and `coda_free_inode()` manage `struct coda_inode_info` allocation and initialization.
- Mount parsing: supports modern `fd=` fs parameter and legacy binary `struct coda_mount_data`, mapping a Coda pseudo-device file descriptor to a `coda_comms[]` index.
- Superblock setup: `coda_fill_super()` validates the pseudo-device, binds `venus_comm` to the superblock, initializes superblock fields, asks Venus for the root fid, and builds the root inode/dentry.
- Superblock teardown: `coda_put_super()` clears `vc_sb` and `s_fs_info`; `coda_evict_inode()` truncates pages, clears inode state, and clears Coda cache state.
- VFS operations: `coda_getattr()`, `coda_setattr()`, and `coda_statfs()` route metadata operations to Venus and update VFS attributes on success.
- Filesystem type: `coda_fs_type` uses `get_tree_nodev`, `kill_anon_super`, `FS_BINARY_MOUNTDATA`, and rejects mounts outside the initial pid namespace.

## Dependencies And Integration
This file ties Coda VFS objects to the userspace Venus daemon through `venus_rootfid()`, `venus_setattr()`, and `venus_statfs()`. It depends on `coda_psdev.h` for device communications, `coda_linux.h` for inode/fid helpers, and `coda_cache.h` for cache invalidation. Module initialization and character-device setup live in `psdev.c`.

## Risk Notes
Mount correctness depends on exclusive pseudo-device binding under `vc_mutex`; stale `vc_sb` state would break communication with Venus. The legacy binary mount parser intentionally ignores some `fd` errors for compatibility. `coda_put_super()` destroys `vc_mutex`, so lifecycle ordering with pseudo-device release is sensitive.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/coda/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/coda/pioctl.c -->
# File Research: sources/os/linux/linux/fs/coda/pioctl.c

## Purpose
Implements Coda pioctl support, allowing userspace control operations to be routed through a special ioctl file into Venus for a target Coda path.

## Main Elements
- `coda_ioctl_inode_operations`: denies execute permission and delegates setattr to `coda_setattr()`.
- `coda_ioctl_operations`: exposes `coda_pioctl()` through `.unlocked_ioctl`.
- `coda_pioctl()`: copies `PioctlData` from userspace, resolves the supplied path with optional symlink following, verifies the target inode belongs to the same Coda superblock, then calls `venus_pioctl()` with the target fid.
- `coda_ioctl_permission()`: allows non-exec accesses and rejects `MAY_EXEC`.

## Dependencies And Integration
Bridges VFS ioctl entry points to `venus_pioctl()` in `upcall.c`. Uses normal pathname resolution via `user_path_at()` and Coda inode conversion through `ITOC()`.

## Risk Notes
The path argument comes from userspace and must resolve to the same mounted Coda instance; otherwise the ioctl is rejected. The actual command and payload validation is split between this wrapper and `venus_pioctl()`, where payload size and copy-in/copy-out checks are enforced.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/coda/pioctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/coda/psdev.c -->
# File Research: sources/os/linux/linux/fs/coda/psdev.c

## Purpose
Implements Coda's pseudo-device character driver, module initialization, communication queues between the kernel and Venus, and sysctl/filesystem/device registration.

## Main Elements
- Global communication state: `coda_comms[MAX_CODADEVS]` stores per-device pending/processing queues, waitqueue, sequence counter, mount binding, and open state.
- Device operations: `coda_psdev_open()`, `release()`, `read()`, `write()`, `poll()`, and `ioctl()` implement the Venus communication ABI.
- Kernel-to-Venus request delivery: `coda_psdev_read()` waits for queued upcalls, copies request data to userspace, and moves synchronous requests to `vc_processing`.
- Venus-to-kernel replies/downcalls: `coda_psdev_write()` distinguishes downcalls from replies, dispatches invalidations via `coda_downcall()`, or matches replies by `unique` to wake sleeping upcall waiters.
- Open/release lifecycle: only one opener per pseudo-device is allowed; release aborts or frees pending and processing requests.
- Module setup: `init_coda()` creates the inode cache, registers the char device and class devices, initializes sysctls, and registers `coda_fs_type`.

## Dependencies And Integration
This file is the runtime transport for `upcall.c`. It owns the pseudo-device major `CODA_PSDEV_MAJOR`, exposes `/dev/cfsN` devices, and initializes Coda-wide sysctls from `sysctl.c` and filesystem registration from `inode.c`.

## Risk Notes
Queue state is protected by `vc_mutex`; request matching relies on unique IDs assigned in `coda_upcall()`. `CODA_OPEN_BY_FD` replies convert a Venus fd into a kernel `struct file *` via `fget()`, so bad fd handling is critical. Release races must wake synchronous waiters and free async requests without leaking request buffers.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/coda/psdev.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/coda/symlink.c -->
# File Research: sources/os/linux/linux/fs/coda/symlink.c

## Purpose
Implements Coda symlink page-cache reads by asking Venus for the symlink target.

## Main Elements
- `coda_symlink_filler()`: obtains the inode's Coda fid, calls `venus_readlink()`, stores the target text into the folio, and completes the folio read.
- `coda_symlink_aops`: exports `.read_folio` for symlink inodes.

## Dependencies And Integration
Used by Coda symlink inode setup elsewhere in the Coda filesystem. It depends on `ITOC()` for inode-private fid lookup and `venus_readlink()` from `upcall.c`.

## Risk Notes
The read buffer is a single page and `venus_readlink()` caps and NUL-terminates returned data. Folio completion uses the Venus result directly; failure leaves the folio not uptodate.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/coda/symlink.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/coda/sysctl.c -->
# File Research: sources/os/linux/linux/fs/coda/sysctl.c

## Purpose
Registers and unregisters Coda runtime sysctls.

## Main Elements
- Sysctls under `coda`: `timeout`, `hard`, and `fake_statfs`.
- `coda_sysctl_init()`: registers the table once.
- `coda_sysctl_clean()`: unregisters the table and clears the saved header.

## Dependencies And Integration
Exposes globals declared in `coda_int.h`: `coda_timeout`, `coda_hard`, and `coda_fake_statfs`. Called from module init/exit in `psdev.c`.

## Risk Notes
`timeout` and `hard` directly affect signal interruption behavior in `coda_upcall()` waits. `fake_statfs` is privileged `0600`, reflecting that it can alter filesystem reporting behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/coda/sysctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/coda/upcall.c -->
# File Research: sources/os/linux/linux/fs/coda/upcall.c

## Purpose
Implements the Coda kernel-to-Venus upcall wrappers, asynchronous/synchronous request transport, signal handling around Venus waits, pioctl marshalling, statfs/access-intent support, and Venus downcall invalidation handling.

## Main Elements
- Request allocation: `alloc_upcall()` fills opcode, pid, process group, and uid in a union request buffer.
- Venus operation wrappers: `venus_rootfid()`, `getattr()`, `setattr()`, `lookup()`, `open()`, `close()`, `mkdir()`, `rename()`, `create()`, `rmdir()`, `remove()`, `readlink()`, `link()`, `symlink()`, `fsync()`, `access()`, `pioctl()`, `statfs()`, and `access_intent()`.
- Variable-size payloads: lookup/create/remove/link/symlink/rename/pioctl build offset-based string or data payloads expected by the Coda userspace protocol.
- Upcall core: `coda_upcall()` assigns unique IDs, queues requests on `vc_pending`, wakes Venus, waits for replies when synchronous, maps Venus result codes to Linux errors, and sends `CODA_SIGNAL` async notifications on interrupted already-read requests.
- Signal policy: `coda_waitfor_upcall()` blocks most signals initially, allows interruption after `coda_timeout` for interruptible operations, and keeps close/store/access-intent/release harder to interrupt.
- Downcalls: `coda_downcall()` validates downcall payload sizes and handles cache invalidations or fid replacement for `CODA_FLUSH`, `PURGEUSER`, `ZAPDIR`, `ZAPFILE`, `PURGEFID`, and `REPLACE`.

## Dependencies And Integration
This is the main Coda protocol layer between VFS code and the Venus daemon. It uses `venus_comm` queues serviced by `psdev.c`, Coda dentry/inode cache helpers, fid-to-inode lookup, VFS dcache pruning, and exported protocol structs from `<linux/coda.h>`.

## Risk Notes
Protocol marshalling depends on exact union sizes, offsets, NUL termination, and Coda ABI command-size adjustments. Interrupted upcalls have subtle state transitions depending on whether Venus already read the request. Downcalls may invalidate dentries/inodes concurrently with VFS operations, so payload validation and locking around `vc_sb` are important.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/coda/upcall.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/compat_binfmt_elf.c -->
# File Research: sources/os/linux/linux/fs/compat_binfmt_elf.c

## Purpose
Builds 32-bit compatible ELF executable and core-dump support on 64-bit kernels by macro-specializing the common `binfmt_elf.c` implementation.

## Main Elements
- Defines `ELF_COMPAT` and maps ELF layout types to `elf32_*` types.
- Maps coredump ABI types to compat variants: `compat_long_t`, `compat_siginfo_t`, compat prstatus/prpsinfo, and 32-bit timeval conversion.
- Redirects architecture hooks to compat versions when provided, including arch check, platform string, hwcaps, personality setup, dynamic base, thread start, additional pages, and read-implies-exec behavior.
- Renames local symbols such as `elf_format` and init/exit functions to compat names.
- Includes `binfmt_elf.c` to compile the shared implementation under the compat macro environment.

## Dependencies And Integration
Depends on architecture-provided compat macros from `asm/elf.h` and common ELF core definitions from `linux/elfcore-compat.h`. It avoids duplicating ELF loader logic while producing a separate compat binary-format registration.

## Risk Notes
Correctness depends on architecture headers defining compat hooks consistently. Since it macro-includes `binfmt_elf.c`, subtle macro leakage or missing compat definitions can change loader/core behavior across ABIs.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/compat_binfmt_elf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/configfs/Kconfig -->
# File Research: sources/os/linux/linux/fs/configfs/Kconfig

## Purpose
Defines the `CONFIG_CONFIGFS_FS` option for the userspace-driven configuration filesystem.

## Main Elements
- `CONFIGFS_FS`: tristate option named "Userspace-driven configuration filesystem".
- Help text explains configfs as the converse of sysfs: userspace creates filesystem objects that create/manage kernel configuration objects.

## Dependencies And Integration
Enables building the `configfs` filesystem module or built-in support used by subsystems exposing `config_item` hierarchies.

## Risk Notes
No dependency constraints are encoded here; subsystems using configfs must handle their own dependencies and object lifetimes.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/configfs/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/configfs/Makefile -->
# File Research: sources/os/linux/linux/fs/configfs/Makefile

## Purpose
Builds the configfs composite object when `CONFIG_CONFIGFS_FS` is enabled.

## Main Elements
- `obj-$(CONFIG_CONFIGFS_FS) += configfs.o`.
- Composite objects: `inode.o`, `file.o`, `dir.o`, `symlink.o`, `mount.o`, and `item.o`.

## Dependencies And Integration
Mirrors the split of configfs responsibilities across mount, inode, directory, file, symlink, and config-item helper code.

## Risk Notes
Object ordering is simple, but exported symbols across these files depend on all components being linked into `configfs.o`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/configfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/configfs/configfs_internal.h -->
# File Research: sources/os/linux/linux/fs/configfs/configfs_internal.h

## Purpose
Defines configfs internal data structures, flags, shared locks, prototypes, and dentry-to-config object helper functions.

## Main Elements
- `struct configfs_fragment`: reference-counted fragment with rwsem and dead flag used to gate attribute access during teardown.
- `struct configfs_dirent`: internal tree node with refcount, children/sibling lists, link/dependent counters, element pointer, type flags, mode, dentry, optional persistent attributes, lockdep depth, and fragment pointer.
- Dirent flags: root/dir/item attributes/bin attributes/links/userspace-created dirs/default groups/dropping/in-mkdir/creating and pinned/not-pinned classes.
- Shared globals: `configfs_symlink_mutex`, `configfs_dirent_lock`, and `configfs_dir_cachep`.
- Cross-file prototypes for inode creation, dirent creation, file creation, mount pinning, symlink operations, and exported inode/file/dentry operations.
- Helpers: `to_item()`, `to_attr()`, `to_bin_attr()`, `configfs_get_config_item()`, dirent release, `configfs_get()`, and `configfs_put()`.

## Dependencies And Integration
This is the private contract for the configfs implementation. It links public `struct config_item`, `config_group`, and attribute APIs from `<linux/configfs.h>` to VFS dentries/inodes and internal dirents.

## Risk Notes
Dirent refcounting and fragment lifetime underpin nearly all configfs teardown safety. The pinned/not-pinned distinction affects lookup and readdir ordering, so flag misuse can make attributes invisible or incorrectly retained.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/configfs/configfs_internal.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/configfs/dir.c -->
# File Research: sources/os/linux/linux/fs/configfs/dir.c

## Purpose
Implements configfs directory tree management: dirent allocation/linkage, item/group attach and detach, mkdir/rmdir, default groups, dependency pins, directory iteration, and subsystem/group registration APIs.

## Main Elements
- Global locking: `configfs_dirent_lock` protects dirent linkage, symlink linkage, dropping flags, and traversal state; `configfs_subsystem_mutex` serializes root-level subsystem link/unlink when no parent subsystem exists.
- Dentry cleanup: `configfs_d_iput()` clears `sd->s_dentry` only for the dying dentry and drops dirent references.
- Fragment lifecycle: `new_fragment()`, `get_fragment()`, and `put_fragment()` provide teardown coordination with attribute files.
- Dirent creation/removal: `configfs_new_dirent()`, `configfs_make_dirent()`, `configfs_remove_dirent()`, `configfs_dirent_exists()`, and ready-state helpers manage internal tree nodes.
- Directory creation and lookup: `configfs_create_dir()` creates item directories; `configfs_lookup()` lazily instantiates attribute files and hides unready attaching hierarchies.
- Attach/detach flows: `configfs_attach_item()`, `configfs_attach_group()`, `configfs_detach_item()`, `configfs_detach_group()`, `detach_attrs()`, and `detach_groups()` populate/remove attributes and default groups.
- Default groups: `create_default_group()`, `populate_groups()`, and `configfs_remove_default_groups()` fake mkdir for kernel-created default children and mark them default.
- Hierarchy links: `link_obj()`, `unlink_obj()`, `link_group()`, and `unlink_group()` maintain `ci_parent`, `ci_group`, `cg_children`, and subsystem pointers with config-item references.
- Dependency APIs: `configfs_depend_item()`, `configfs_depend_item_unlocked()`, and `configfs_undepend_item()` prevent external users from racing item removal by incrementing dirent dependent counts.
- VFS mkdir/rmdir: `configfs_mkdir()` calls client `make_group()` or `make_item()`, links the object, pins module owners, attaches VFS nodes, and rolls back on error; `configfs_rmdir()` rejects default groups, checks dependents/links, marks fragments dead, detaches VFS state, and calls client cleanup callbacks.
- Directory operations: open/close allocate a cursor dirent; `configfs_readdir()` emits live entries while maintaining cursor position; `configfs_dir_lseek()` repositions the cursor.
- Registration APIs: `configfs_register_group()`, `unregister_group()`, `register_default_group()`, `unregister_default_group()`, `register_subsystem()`, and `unregister_subsystem()` create/remove kernel-driven groups and top-level subsystems.

## Dependencies And Integration
This is the core of configfs and integrates with `file.c` for attribute files, `inode.c` for inode allocation/attributes, `symlink.c` for link operations, `mount.c` for filesystem pinning, module refcounts, VFS locking, fsnotify, and public configfs client callbacks.

## Risk Notes
The highest-risk code is mkdir/rmdir interaction with default group population, symlink creation, dependency pins, and fragment death. Lock ordering spans inode rwsems, `configfs_symlink_mutex`, subsystem mutexes, and `configfs_dirent_lock`; mistakes can deadlock or allow teardown while callbacks are active. Error rollback after partially attached groups must undo both VFS and config-item references.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/configfs/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/configfs/file.c -->
# File Research: sources/os/linux/linux/fs/configfs/file.c

## Purpose
Implements configfs regular and binary attribute file operations, including open-time permission/callback validation, read/write buffering, binary deferred writes, and attribute dirent creation.

## Main Elements
- `struct configfs_buffer`: per-open state for text/bin attribute callbacks, buffer memory, current count/position, read/write mode flags, item/module references, and max binary size.
- Text reads/writes: `fill_read_buffer()`, `configfs_read_iter()`, `fill_write_buffer()`, `flush_write_buffer()`, and `configfs_write_iter()` implement PAGE-sized text attribute show/store behavior.
- Binary reads: `configfs_bin_read_iter()` first calls the binary read callback with `NULL` to get size, allocates a vmalloc buffer, fills it, then serves user reads.
- Binary writes: `configfs_bin_write_iter()` grows an in-memory buffer and copies user data; `configfs_release_bin_file()` invokes the binary write callback on close.
- Open/release: `__configfs_open_file()` validates live fragments, item/type/callbacks, inode mode, and module owner; `configfs_release()` drops module and buffer resources.
- File operations: `configfs_file_operations` and `configfs_bin_file_operations`.
- Creation helpers: `configfs_create_file()` and `configfs_create_bin_file()` add attribute dirents under an item directory.

## Dependencies And Integration
Attribute access is guarded by the parent dirent fragment semaphore from `dir.c`, which prevents callbacks after teardown. Callback definitions come from `struct configfs_attribute`, `configfs_bin_attribute`, and item type operations.

## Risk Notes
Text writes reject partial-write semantics by sending one copied buffer to `store()`. Binary files do not support switching between read and write modes on the same open. Fragment death returns `-ENOENT`, protecting callbacks during rmdir/unregister; bypassing that would risk use-after-free of client items.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/configfs/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/configfs/inode.c -->
# File Research: sources/os/linux/linux/fs/configfs/inode.c

## Purpose
Implements configfs inode creation and persistent inode attribute handling.

## Main Elements
- `configfs_setattr()`: persists changed uid/gid/timestamps/mode into `sd->s_iattr`, calls `simple_setattr()`, and handles setgid clearing rules.
- `configfs_new_inode()`: allocates a new inode, assigns a unique inode number, uses `ram_aops`, installs default operations, and applies saved or default attributes.
- Lockdep support: `configfs_set_inode_lock_class()` assigns lock classes for nested default-group inodes.
- `configfs_create()`: validates dentry state, creates a configfs inode, and applies lock class metadata.
- `configfs_get_name()`: returns the VFS dentry name for dirs/links or attribute `ca_name` for text/bin attributes.

## Dependencies And Integration
Used by `dir.c`, `file.c`, `symlink.c`, and `mount.c` whenever configfs materializes VFS objects. Persistent attributes are stored on `struct configfs_dirent`.

## Risk Notes
`sd->s_iattr` allocation happens lazily on first setattr and must remain tied to dirent lifetime. Lockdep class depth for default groups is important to avoid false or real recursive inode-lock issues during group attach/detach.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/configfs/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/configfs/item.c -->
# File Research: sources/os/linux/linux/fs/configfs/item.c

## Purpose
Provides public helper routines for initializing, naming, reference-counting, cleaning up, and searching configfs items and groups.

## Main Elements
- Initialization: `config_item_init()`, `config_item_init_type_name()`, `config_group_init_type_name()`, and `config_group_init()`.
- Naming: `config_item_set_name()` stores short names in `ci_namebuf` and allocates longer names dynamically.
- References: `config_item_get()`, `config_item_get_unless_zero()`, and `config_item_put()` wrap `kref`.
- Cleanup: `config_item_cleanup()` frees dynamic names, calls item release callbacks, and drops group/parent references.
- Lookup: `config_group_find_item()` searches a group's `cg_children` by name and returns a referenced item.

## Dependencies And Integration
These helpers are exported to configfs clients and are used internally by `dir.c` to maintain hierarchy references. Cleanup callbacks come from `config_item_type`.

## Risk Notes
Name storage must avoid leaking old dynamic names on rename. Reference ownership is shared between parent links, child lists, and client callbacks; a missing put or double put would corrupt configfs object lifetime.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/configfs/item.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/configfs/mount.c -->
# File Research: sources/os/linux/linux/fs/configfs/mount.c

## Purpose
Implements configfs filesystem registration, superblock/root creation, filesystem pinning, mount-point setup, and module init/exit.

## Main Elements
- Superblock operations: `configfs_ops` uses `simple_statfs`, `inode_just_drop`, and custom inode free for symlink target memory.
- Root objects: static `configfs_root_group` and `configfs_root` dirent represent the configfs root.
- `configfs_fill_super()`: initializes superblock fields, creates the root inode/dentry, initializes the root group, attaches root dirent data, and marks dentries as not cacheable.
- Mount context: `configfs_get_tree()` uses `get_tree_single()`; `configfs_fs_type` registers the filesystem.
- Pinning: `configfs_pin_fs()` and `configfs_release_fs()` wrap `simple_pin_fs()` for code that needs the configfs tree without a user mount.
- Module lifecycle: `configfs_init()` creates the dirent slab cache, creates `/sys/kernel/config`, and registers the filesystem; `configfs_exit()` reverses this.

## Dependencies And Integration
Top-level support for `dir.c` subsystem/group registration and dependency APIs. It integrates with sysfs for the mount point, VFS single-superblock mounting, and the shared dirent slab.

## Risk Notes
Root dirent is statically allocated and intentionally not freed like normal dirents. Pin counts protect callers that manipulate configfs outside direct VFS operations; imbalance would keep configfs mounted or allow root access after teardown.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/configfs/mount.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/configfs/symlink.c -->
# File Research: sources/os/linux/linux/fs/configfs/symlink.c

## Purpose
Implements configfs symlink semantics, which act as resolved object links that pin target config_items and notify client callbacks.

## Main Elements
- Path construction: `item_depth()`, `item_path_length()`, `fill_item_path()`, and `configfs_get_target_path()` build a relative symlink body from parent item to target item.
- Link creation: `create_link()` checks target readiness, increments target link count, computes symlink body, and calls `configfs_create_link()`.
- Target resolution: `get_target()` resolves the user-supplied symlink target path, requires it to be on the same configfs superblock, and returns a referenced config item.
- `configfs_symlink()`: validates parent item operations, temporarily unlocks the parent inode to resolve the target, calls client `allow_link()`, serializes with `configfs_symlink_mutex`, creates the link, and calls `drop_link()` on failure after allow.
- `configfs_unlink()`: removes link dirent/VFS link, calls client `drop_link()`, decrements target link count, and drops target dirent/item references.
- `configfs_symlink_inode_operations`: uses `simple_get_link` and configfs setattr.

## Dependencies And Integration
Works with `dir.c` for link dirent creation/removal and rmdir link-count checks. Client behavior is supplied by `ct_item_ops->allow_link()` and `drop_link()`.

## Risk Notes
The file explicitly documents unusual ABI semantics: symlink targets are resolved at syscall time and make targets busy from rmdir's perspective. Locking is delicate because target lookup cannot be done while holding the parent directory lock without deadlock risk.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/configfs/symlink.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/coredump.c -->
# File Research: sources/os/linux/linux/fs/coredump.c

## Purpose
Implements Linux VFS coredump orchestration: core pattern expansion, file/pipe/socket targets, process-thread coordination, dump writing helpers, sysctls, and VMA dump selection/snapshotting.

## Main Elements
- Core target model: `struct core_name` tracks generated target name, type (`file`, `pipe`, `socket`, socket request), wait/dump mask, pipe-limit state, and whether a dump was produced.
- Pattern expansion: `coredump_parse()` processes `core_pattern`, handles `%` specifiers for pids/uids/gids/signal/time/hostname/executable/core limit/cpu/pidfd, splits pipe argv, and validates socket paths.
- Thread-group coordination: `zap_process()`, `zap_threads()`, `coredump_wait()`, and `coredump_finish()` stop sibling threads, wait for them to quiesce, and release them after dumping.
- Pipe helper support: `umh_coredump_setup()` installs pipe stdin and optional pidfd fd 3; `coredump_pipe()` enforces recursion and `core_pipe_limit`, spawns the helper, and captures its write pipe.
- Socket support: under `CONFIG_UNIX`, `coredump_sock_connect()`, request/ack helpers, `coredump_sock_request()`, and `coredump_socket()` connect to AF_UNIX handlers and negotiate whether kernel/userspace/reject/wait handling is requested.
- File target support: `coredump_file()` opens/unlinks/truncates regular core files, enforces suid-safe absolute path rules, owner/mode preservation, regular-file-only behavior, and minimum coredump size.
- Main flow: `vfs_coredump()` snapshots credentials/dumpability/limits, waits for coredump ownership, then `do_coredump()` selects target, unshares files, writes via `binfmt->core_dump()`, handles socket shutdown/waiting, and cleans up.
- Dump helpers: `dump_emit()`, `dump_skip_to()`, `dump_skip()`, `dump_align()`, and `dump_user_range()` are exported helpers used by binary-format core writers.
- Sysctls: registers `kernel.core_uses_pid`, `core_pattern`, `core_pipe_limit`, `core_file_note_size_limit`, `core_sort_vma`, and readonly `core_modes`.
- VMA policy: `always_dump_vma()`, `vma_dump_size()`, `coredump_next_vma()`, `dump_vma_snapshot()`, and `free_vma_snapshot()` decide which VMAs to dump, optionally sort by size, and hold file references for core metadata.

## Dependencies And Integration
Integrates process signal state, binfmt core dump callbacks, VFS file creation/writes, pipes, usermode helpers, pidfs, AF_UNIX sockets, sysctls, LSM/security audit, namespaces, mm/VMA iteration, and tracepoints.

## Risk Notes
Core dumping sits at process-death time and must avoid deadlocks, recursion, stale pid references, unsafe suid dumps, and partial output confusion. Socket mode adds protocol validation and initial namespace/path restrictions. VMA snapshotting takes the mmap write lock and later probes possible ELF headers outside the lock, so interruption and lifetime handling are key.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/coredump.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/cramfs/Kconfig -->
# File Research: sources/os/linux/linux/fs/cramfs/Kconfig

## Purpose
Defines build options for the compressed ROM filesystem driver.

## Main Elements
- `CRAMFS`: tristate read-only compressed filesystem support, selecting `ZLIB_INFLATE`.
- `CRAMFS_BLOCKDEV`: optional block-device image support, default enabled when block support exists.
- `CRAMFS_MTD`: optional direct physical-memory/MTD mapped image support, default enabled when blockdev mode is unavailable.

## Dependencies And Integration
Controls whether `inode.o` can mount cramfs images via normal block devices, MTD direct mapping, or both.

## Risk Notes
The help text emphasizes cramfs format limits: read-only, 256MB filesystem, 16MB files, limited uid/gid support, no hard links, and no timestamps.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/cramfs/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/cramfs/Makefile -->
# File Research: sources/os/linux/linux/fs/cramfs/Makefile

## Purpose
Builds the cramfs module or built-in filesystem object.

## Main Elements
- `obj-$(CONFIG_CRAMFS) += cramfs.o`.
- Composite objects: `inode.o` and `uncompress.o`.

## Dependencies And Integration
Links VFS/image handling with zlib decompression wrappers.

## Risk Notes
No conditional object split is used for blockdev versus MTD; feature differences are compiled through Kconfig conditionals in `inode.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/cramfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/cramfs/inode.c -->
# File Research: sources/os/linux/linux/fs/cramfs/inode.c

## Purpose
Implements the cramfs read-only filesystem: mount/fill-super paths, block or direct-MTD image reads, inode construction, directory lookup/readdir, file folio reads/decompression, optional direct physical mmap, statfs, and filesystem registration.

## Main Elements
- Superblock state: `struct cramfs_sb_info` stores magic, image size, block/file counts, feature flags, and optional linear virtual/physical MTD mapping.
- Inode numbering/building: `cramino()` derives stable inode numbers; `get_cramfs_inode()` initializes regular, directory, symlink, and special-file inodes from on-disk cramfs inodes.
- Image reads: blockdev mode uses a small private two-buffer cache in `cramfs_blkdev_read()`; MTD mode uses `cramfs_direct_read()` over a linearly mapped image; `cramfs_read()` selects the mode.
- Direct mapping support: `cramfs_get_block_range()`, `cramfs_last_page_is_shared()`, `cramfs_physmem_mmap()`, and NOMMU helpers map uncompressed direct-pointer ranges from MTD images when safe.
- Mount teardown/reconfigure: `cramfs_kill_sb()` unmaps MTD or releases block devices; `cramfs_reconfigure()` enforces readonly.
- Superblock validation: `cramfs_read_super()` reads the superblock at offset 0 or 512, checks magic/endian/features/root directory/root offset, and fills in format metadata.
- Fill-super variants: `cramfs_blkdev_fill_super()` initializes blockdev state; `cramfs_mtd_fill_super()` maps one page, validates size, remaps the full image, then finalizes root.
- Directory operations: `cramfs_readdir()` iterates padded directory entries; `cramfs_lookup()` scans entries, using sorted directory flag for early exits.
- Data read path: `cramfs_read_folio()` decodes block-pointer tables, handles direct/uncompressed/compressed/hole blocks, validates compressed block lengths, decompresses with zlib wrapper, and zero-fills page tails.
- Registration: `cramfs_fs_type` supports MTD first then blockdev fallback and uses `FS_REQUIRES_DEV`.

## Dependencies And Integration
Integrates VFS superblock/inode/dentry APIs, block-device page-cache reads, MTD direct mapping APIs, zlib decompression via `uncompress.c`, and cramfs on-disk structures from `uapi/linux/cramfs_fs.h`.

## Risk Notes
Cramfs trusts compact on-disk metadata after validation; malformed block pointers, zero namelens, bad compressed sizes, or unsupported flags produce errors. The global `read_mutex` serializes access to shared read buffers and single zlib stream. Direct mmap must reject writable VMAs, unaligned physical data, and shared last pages containing unrelated filesystem data.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/cramfs/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/cramfs/internal.h -->
# File Research: sources/os/linux/linux/fs/cramfs/internal.h

## Purpose
Declares cramfs decompression interfaces used by the filesystem implementation.

## Main Elements
- `cramfs_uncompress_block()`: decompress one block.
- `cramfs_uncompress_init()`: initialize shared zlib state.
- `cramfs_uncompress_exit()`: release shared zlib state.

## Dependencies And Integration
Included by `inode.c` and implemented by `uncompress.c`.

## Risk Notes
The interface hides the fact that decompression state is global and single-threaded; callers must serialize around it.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/cramfs/internal.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/cramfs/uncompress.c -->
# File Research: sources/os/linux/linux/fs/cramfs/uncompress.c

## Purpose
Wraps zlib inflate for cramfs block decompression with shared global stream initialization and teardown.

## Main Elements
- Static zlib `stream` and `initialized` reference count.
- `cramfs_uncompress_block()`: resets the stream, inflates one compressed block into the destination, reports zlib errors, and returns decompressed byte count or `-EIO`.
- `cramfs_uncompress_init()`: allocates zlib workspace with `vmalloc()` and initializes inflate state on first user.
- `cramfs_uncompress_exit()`: ends inflate and frees workspace on final user.

## Dependencies And Integration
Used by `cramfs_read_folio()` in `inode.c`. The global stream is serialized by `read_mutex` in the caller.

## Risk Notes
The file explicitly notes decompression is single-threaded. Reset failure attempts to end and reinitialize the zlib stream, but decompression errors still abort the folio read.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/cramfs/uncompress.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/crypto/Kconfig -->
# File Research: sources/os/linux/linux/fs/crypto/Kconfig

## Purpose
Defines filesystem encryption and optional inline encryption build configuration.

## Main Elements
- `FS_ENCRYPTION`: core per-file encryption support, selecting crypto, skcipher, AES/SHA libraries, and keys.
- `FS_ENCRYPTION_ALGS`: tristate algorithm bundle for default fscrypt modes, selecting AES, CBC, CTS, and XTS.
- `FS_ENCRYPTION_INLINE_CRYPT`: optional fscrypt inline crypto support depending on block inline encryption.

## Dependencies And Integration
Used by filesystems such as ext4, f2fs, ubifs, and cephfs to enable fscrypt support and required algorithms.

## Risk Notes
The default algorithm option does not select every possible fscrypt algorithm or architecture-optimized implementation; deployments using non-default modes must enable those crypto API algorithms separately.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/crypto/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/crypto/Makefile -->
# File Research: sources/os/linux/linux/fs/crypto/Makefile

## Purpose
Builds the fscrypt support library.

## Main Elements
- Core `fscrypto.o` objects: `crypto.o`, `fname.o`, `hkdf.o`, `hooks.o`, `keyring.o`, `keysetup.o`, `keysetup_v1.o`, and `policy.o`.
- Adds `bio.o` when `CONFIG_BLOCK` is enabled.
- Adds `inline_crypt.o` when `CONFIG_FS_ENCRYPTION_INLINE_CRYPT` is enabled.

## Dependencies And Integration
Defines which fscrypt components are linked for encryption policy/key/content/name/block integration.

## Risk Notes
Filesystems using block-device fscrypt helpers depend on `bio.o`; inline crypto hooks are feature-gated separately.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/crypto/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/crypto/bio.c -->
# File Research: sources/os/linux/linux/fs/crypto/bio.c

## Purpose
Provides block-device fscrypt helpers for decrypting read bios and writing encrypted zeroes to ranges of encrypted files.

## Main Elements
- `fscrypt_decrypt_bio()`: iterates all folios in a completed read bio and decrypts pagecache blocks, setting `bio->bi_status` on failure.
- Inline-crypto zeroout: `fscrypt_zeroout_range_inline_crypt()` builds bios of `ZERO_PAGE()` segments, attaches fscrypt bio crypto contexts, submits via `blk_crypto_submit_bio()`, and waits for all completions.
- Completion support: `struct fscrypt_zero_done`, `fscrypt_zeroout_range_done()`, and end_io callback aggregate async write status.
- Software zeroout: `fscrypt_zeroout_range()` encrypts zero data units into bounce pages, writes them via synchronous bios, and reuses allocated pages in batches.
- Exported symbols: `fscrypt_decrypt_bio()` and `fscrypt_zeroout_range()`.

## Dependencies And Integration
Integrates fscrypt content crypto from `crypto.c`, block bios, blk-crypto inline contexts, filesystem block-device `s_bdev`, and bounce-page allocation.

## Risk Notes
Zeroout must write ciphertext that decrypts to zero per data unit; it cannot simply write identical ciphertext blocks because IVs differ. The helper assumes contiguous logical/physical blocks and a single block device. Inline and software paths have different submission/completion behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/crypto/bio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/crypto/crypto.c -->
# File Research: sources/os/linux/linux/fs/crypto/crypto.c

## Purpose
Implements fscrypt content encryption/decryption primitives, bounce-page allocation, IV generation, read-decrypt workqueue setup, initialization, and logging.

## Main Elements
- Global resources: preallocated bounce-page mempool, high-priority unbound read workqueue, fscrypt inode-info slab cache, and init mutex.
- Workqueue: `fscrypt_enqueue_decrypt_work()` queues read-decrypt work.
- Bounce pages: `fscrypt_alloc_bounce_page()` and `fscrypt_free_bounce_page()` allocate/free ciphertext pages from a mempool and store original folio pointers in page private data.
- IV generation: `fscrypt_generate_iv()` handles normal IVs, `IV_INO_LBLK_64`, `IV_INO_LBLK_32`, and `DIRECT_KEY` nonce-based modes.
- Data-unit crypto: `fscrypt_crypt_data_unit()` performs skcipher encrypt/decrypt for one data unit with scatterlists and generated IV.
- Pagecache encryption: `fscrypt_encrypt_pagecache_blocks()` encrypts aligned pagecache blocks into a bounce page for writeback.
- In-place crypto: `fscrypt_encrypt_block_inplace()` and `fscrypt_decrypt_block_inplace()` handle filesystem blocks outside the pagecache, rejecting subblock data-unit filesystems.
- Pagecache decryption: `fscrypt_decrypt_pagecache_blocks()` decrypts aligned data units in locked, not-yet-uptodate folios.
- Initialization: `fscrypt_initialize()` lazily creates the bounce-page pool only for filesystems needing it; `fscrypt_init()` allocates the workqueue/slab and initializes the keyring.
- Logging: `fscrypt_msg()` rate-limits fscrypt messages with optional inode context.

## Dependencies And Integration
Used by fscrypt-enabled filesystems, `bio.c`, filename crypto, key setup, and block writeback/read paths. It depends on crypto skcipher APIs, mempools, folios/pages, and fscrypt policy/key state.

## Risk Notes
Alignment to crypto data-unit size is strictly enforced. Bounce-page mempool use is designed to avoid writeback deadlocks, but only the first page can safely use reclaiming allocation. IV generation must stay synchronized with I/O merging limits and policy flags.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/crypto/crypto.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/crypto/fname.c -->
# File Research: sources/os/linux/linux/fs/crypto/fname.c

## Purpose
Implements fscrypt filename encryption/decryption, no-key filename presentation and lookup, encrypted filename length calculation, SipHash dirhashing, and encrypted dentry revalidation.

## Main Elements
- Filename encryption: `fscrypt_fname_encrypt()` pads plaintext to the encrypted length, generates filename IV, and encrypts in-place into the output buffer.
- Filename decryption: `fname_decrypt()` decrypts ciphertext names and strips trailing NUL padding with `strnlen()`.
- Length calculation: `__fscrypt_fname_encrypted_size()` and `fscrypt_fname_encrypted_size()` enforce minimum 16-byte encrypted names and policy padding.
- Buffer helpers: `fscrypt_fname_alloc_buffer()` and `fscrypt_fname_free_buffer()` allocate/free buffers large enough for decrypted or no-key encoded names.
- No-key names: `struct fscrypt_nokey_name` stores dirhashes, up to 149 ciphertext bytes, and SHA-256 of the remainder; `fscrypt_fname_disk_to_usr()` base64url-encodes this when the key is unavailable.
- Lookup setup: `fscrypt_setup_filename()` prepares disk names for unencrypted dirs, keyed encrypted dirs, or keyless lookup using decoded no-key names.
- Matching: `fscrypt_match_name()` compares full disk names or validates abbreviated no-key names with SHA-256.
- Directory hash: `fscrypt_fname_siphash()` computes SipHash over plaintext names using the directory's secret dirhash key.
- Dentry validation: `fscrypt_d_revalidate()` invalidates no-key dentries once the directory key becomes available, while handling RCU lookup constraints.

## Dependencies And Integration
Works with fscrypt key setup, policy flags, skcipher content primitives from `crypto.c`, Linux base64url helpers, SHA-256, SipHash, dcache flags, and filesystem directory lookup/create paths.

## Risk Notes
No-key names must be reversible enough to find entries without exposing illegal path characters or exceeding `NAME_MAX`. Long names rely on SHA-256 collision resistance for matching. Key availability changes can make cached no-key dentries stale, so revalidation is required.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/crypto/fname.c -->