# subset-b-005637 Research

Grouped research for the source files assigned to `subset-b-005637`. Each section is delimited for deterministic reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/coda/inode.c -->
# sources/distributed-fs/ceph-client/fs/coda/inode.c

Purpose: implements Coda filesystem superblock setup, fs_context parsing, inode-cache allocation, mount binding to a Venus pseudo-device slot, and generic inode attribute/statfs operations. It is the mount-time bridge between VFS and the per-device `venus_comm` objects owned by `psdev.c`.

Important APIs/types/functions: `coda_init_inodecache()` and `coda_destroy_inodecache()` manage the `coda_inode_info` slab. `coda_alloc_inode()` initializes Coda fid/cache fields and spinlocks. `coda_set_idx()`, `coda_parse_fd()`, and `coda_parse_monolithic()` accept modern `fd=` or legacy binary mount data. `coda_fill_super()` validates `vc_inuse`, rejects duplicate mounts, stores `vc_sb`, fetches `venus_rootfid()`, creates the root inode with `coda_cnode_make()`, and installs Coda super/dentry operations. `coda_getattr()`, `coda_setattr()`, and `coda_statfs()` delegate to Venus or fill fallback statfs values.

Control flow: mount parsing resolves a coda character-device minor to `ctx->idx`; `get_tree_nodev()` calls `coda_fill_super()`, which temporarily claims the `venus_comm`, initializes the anonymous superblock, asks Venus for the root fid, then creates `s_root`. Error paths clear `vc_sb` and `s_fs_info`. Unmount uses `coda_put_super()` to detach the superblock from the pseudo-device.

State and persistence: persistent kernel state is in `coda_comms[idx].vc_sb`, `sb->s_fs_info`, and per-inode `coda_inode_info`; on-disk persistence is managed by Venus, not this file. `SB_NOATIME` is enforced on mount/reconfigure.

Dependencies/integration: depends on Coda protocol structs, `coda_psdev.h`, `coda_linux.h`, cache helpers, VFS fs_context, inode slab APIs, and upcalls in `upcall.c`. Mounts are restricted to the initial PID namespace.

Risks: pseudo-device lifetime and mount lifetime must stay synchronized under `vc_mutex`; duplicate mount or dead Venus handling must not leak `vc_sb`. Attribute updates rely on Venus truncating backing container files. `coda_put_super()` destroys a mutex in a global `venus_comm`, so open/reopen sequencing around `psdev` must stay disciplined.

Test signals: mount with valid/invalid `fd=`, legacy binary mount data, duplicate mount on one minor, Venus shutdown during mount, setattr/getattr propagation, fake statfs fallback, namespace-restricted mount rejection, and slab leak checks across module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/coda/inode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/coda/pioctl.c -->
# sources/distributed-fs/ceph-client/fs/coda/pioctl.c

Purpose: implements the Coda control inode ioctl path, allowing userspace pioctl requests to target a path inside the same Coda mount and be forwarded to Venus.

Important APIs/functions: exports `coda_ioctl_inode_operations` with `.permission` and `.setattr`, plus `coda_ioctl_operations` with `.unlocked_ioctl = coda_pioctl`. `coda_ioctl_permission()` denies execute access but permits non-exec permission checks. `coda_pioctl()` copies `struct PioctlData` from userspace, resolves the embedded path with optional follow semantics, validates the target inode belongs to the same superblock, then calls `venus_pioctl()`.

Control flow: ioctl input arrives on the special pioctl file; the code copies the fixed control block, calls `user_path_at(AT_FDCWD, data.path, ...)`, rejects non-Coda or different-mount targets, extracts the target fid from `ITOC(target_inode)`, performs the Venus upcall, and releases the path.

State and persistence: no persistent local state. Effects are delegated to Venus through `venus_pioctl()`, which may read and write userspace buffers described in `PioctlData`.

Dependencies/integration: integrates VFS ioctl operations, userspace path lookup, `linux/coda.h` pioctl ABI, `coda_inode_info`, and the generic Coda upcall transport. It relies on path lookup to safely copy the user pathname from `data.path`.

Risks: `copy_from_user()` returns `-EINVAL` rather than `-EFAULT`, which is ABI behavior but less precise. The path must remain on the same Coda superblock or foreign inode fids could be sent to the wrong Venus. The command-size rewriting and data-buffer validation happen later in `venus_pioctl()`, so both pieces must stay ABI-compatible.

Test signals: ioctl with bad user pointer, missing path, follow/no-follow symlink cases, path on another filesystem, same Coda mount success, overlarge in/out pioctl buffers via `venus_pioctl()`, and permission checks on the control inode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/coda/pioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/coda/psdev.c -->
# sources/distributed-fs/ceph-client/fs/coda/psdev.c

Purpose: provides the Coda pseudo-device character driver and module init/exit path. It creates `/dev/cfsN`-style endpoints that Venus opens to exchange bidirectional upcall/downcall messages with kernel Coda VFS code.

Important APIs/types/functions: global `coda_comms[MAX_CODADEVS]` stores per-minor queues, waitqueue, sequence number, superblock pointer, and mutex. `coda_psdev_open()` initializes one `venus_comm` slot and restricts access to the initial PID/user namespaces. `coda_psdev_read()` moves queued kernel upcalls from `vc_pending` to userspace and, for synchronous requests, onto `vc_processing`. `coda_psdev_write()` receives Venus replies or downcalls, matches replies by unique id, copies output into the request buffer, converts `CODA_OPEN_BY_FD` descriptors with `fget()`, and wakes sleepers. `coda_psdev_release()` aborts and wakes all outstanding requests.

Control flow: module init creates the inode cache, registers the char major, creates device nodes, registers sysctls, then registers the Coda filesystem. Kernel VFS operations enqueue `upc_req`s through `coda_upcall()`; Venus polls/reads pending requests; Venus writes replies or invalidation downcalls; waiters resume or cache invalidation executes.

State and persistence: in-memory queues `vc_pending` and `vc_processing` persist while Venus holds the device. No on-disk state is stored here. `vc_inuse` enforces one opener per minor.

Dependencies/integration: integrates char-device VFS, poll, copy_to/from_user, device class creation, module lifecycle, Coda sysctls, Coda filesystem registration, and `coda_downcall()` in `upcall.c`.

Risks: request queue manipulation must be under `vc_mutex`; mismatched unique ids return `-ESRCH`. `CODA_OPEN_BY_FD` takes file references that later file code must release. Release must wake every blocked upcall or callers can hang. Namespace checks are important because the protocol uses initial namespace pid/uid values.

Test signals: concurrent read/write/poll behavior, nonblocking read, interrupted read, Venus reply after signal, downcall size validation, device open exclusivity, release with pending and processing requests, module load/unload cleanup, and `CIOC_KERNEL_VERSION` ioctl.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/coda/psdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/coda/symlink.c -->
# sources/distributed-fs/ceph-client/fs/coda/symlink.c

Purpose: implements Coda symlink page-cache population. Symlink contents live in Venus, and this file supplies the address-space operation that fetches them on demand.

Important APIs/functions: `coda_symlink_filler()` is the `.read_folio` callback for `coda_symlink_aops`. It obtains the inode from `folio->mapping->host`, extracts the `CodaFid` via `ITOC()`, uses a page-sized buffer at `folio_address(folio)`, and calls `venus_readlink()`.

Control flow: VFS follows or reads a symlink, the page-cache symlink machinery asks for a folio, `coda_symlink_filler()` sends a `CODA_READLINK` upcall, Venus copies the symlink target into the page, and `folio_end_read()` marks the folio success or failure.

State and persistence: no local persistent state. The folio becomes cached symlink data until invalidated by normal inode/cache behavior or Coda downcalls.

Dependencies/integration: depends on page-cache symlink support, Coda inode-private fids, and `venus_readlink()` in `upcall.c`. It is selected by inode construction for symlink cnodes elsewhere in the Coda client.

Risks: the buffer length is initialized to `PAGE_SIZE`; Venus results are truncated to leave a NUL terminator in `venus_readlink()`. Errors must call `folio_end_read()` with failure or consumers can observe stale/incomplete data. Cache invalidation from Venus must cover symlink target changes.

Test signals: readlink on valid symlinks, target length near `PAGE_SIZE`, Venus error propagation, folio uptodate state after failure, and cache invalidation after symlink update.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/coda/symlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/coda/sysctl.c -->
# sources/distributed-fs/ceph-client/fs/coda/sysctl.c

Purpose: registers Coda runtime tunables under the `coda` sysctl table when `CONFIG_SYSCTL` is enabled.

Important APIs/functions: `coda_table` exposes `timeout`, `hard`, and `fake_statfs` using `proc_dointvec`. `coda_sysctl_init()` registers the table once through `register_sysctl("coda", coda_table)`. `coda_sysctl_clean()` unregisters and clears the saved table header.

Control flow: `psdev.c` calls init during Coda module/device setup and clean during failure or module exit. Runtime reads/writes update the global variables consumed by upcall waiting and statfs behavior.

State and persistence: persistent kernel state is the sysctl table header plus globals `coda_timeout`, `coda_hard`, and `coda_fake_statfs`; values do not persist across reboot/module reload.

Dependencies/integration: depends on `linux/sysctl.h` and declarations in `coda_int.h`. `coda_timeout` and `coda_hard` control signal/timeout behavior in `upcall.c`; `coda_fake_statfs` is declared by Coda Linux support and influences statfs policy outside this file.

Risks: no min/max handlers are applied, so invalid values can be written by privileged users and later code must tolerate them. Registration is guarded only by `fs_table_header`, so init/cleanup pairing matters.

Test signals: sysctl registration/unregistration on module load/unload, reads and writes for all three knobs, negative/large timeout behavior in upcall waits, and absence of sysctl calls when built without `CONFIG_SYSCTL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/coda/sysctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/coda/upcall.c -->
# sources/distributed-fs/ceph-client/fs/coda/upcall.c

Purpose: implements the Coda kernel-to-Venus RPC layer and Venus-to-kernel downcall invalidation handling. All high-level Coda operations are marshaled into protocol packets and sent over the pseudo-device queues.

Important APIs/functions: `alloc_upcall()` fills common input headers with opcode, initial-namespace pid/pgid, and fsuid. `venus_rootfid()`, `venus_getattr()`, `venus_setattr()`, `venus_lookup()`, `venus_open()`, `venus_close()`, `venus_create()`, `venus_mkdir()`, `venus_remove()`, `venus_rmdir()`, `venus_rename()`, `venus_link()`, `venus_symlink()`, `venus_readlink()`, `venus_fsync()`, `venus_access()`, `venus_pioctl()`, `venus_statfs()`, and `venus_access_intent()` build operation-specific buffers. `coda_upcall()` queues synchronous or async `upc_req`s and waits for Venus. `coda_downcall()` handles cache invalidation and fid replacement.

Control flow: wrappers allocate a max(input, output) buffer, populate fixed fields plus inline NUL-terminated names, call `coda_upcall(coda_vcp(sb), ...)`, copy results back, and free buffers. `coda_upcall()` assigns a unique id, appends to `vc_pending`, wakes Venus, optionally waits on `uc_sleep`, maps positive Venus results to negative errno, and sends `CODA_SIGNAL` if interrupted after Venus read the request. Downcalls validate message size, find target inodes, then mark attributes/children stale, prune aliases, or replace fids.

State and persistence: uses `venus_comm` queues and sequence state; per-inode cache flags are updated for invalidation. No disk state is modified directly.

Dependencies/integration: tightly coupled to `psdev.c`, Coda protocol unions, VFS inode/dentry cache helpers, signal handling, and cache helpers in `coda_cache.h`.

Risks: packet sizing and inline string offsets must match the Coda ABI. Signal handling is subtle: close/store/access-intent are made hard to interrupt to preserve reference and data-loss invariants. Async finalizer access-intent requests transfer buffer ownership to the queue on success. Downcall size validation is essential before reading union fields.

Test signals: all Venus operation wrappers with boundary name lengths, interrupted synchronous upcalls before and after Venus read, Venus death while waiting, async access-intent finalizers, pioctl in/out bounds, and each downcall opcode invalidating expected dentries/inodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/coda/upcall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/compat_binfmt_elf.c -->
# sources/distributed-fs/ceph-client/fs/compat_binfmt_elf.c

Purpose: builds 32-bit ELF executable and core-dump support for a 64-bit kernel by macro-renaming ABI types, hooks, and local symbols before including the native `binfmt_elf.c` implementation.

Important APIs/macros: defines `ELF_COMPAT`, sets `ELF_CLASS` to `ELFCLASS32`, maps ELF header/program/note/address types to `elf32_*`, maps signal/core-note types to compat forms, maps timeval conversion to `ns_to_old_timeval32`, and requires `compat_elf_check_arch`. Optional `COMPAT_ELF_*`, `COMPAT_ARCH_*`, and `COMPAT_START_THREAD` macros override platform notes, hwcaps, ET_DYN base, personality setup, auxiliary vectors, additional pages, and start-thread behavior. Local symbols such as `elf_format` are renamed to `compat_elf_format`.

Control flow: there is no runtime logic in this file before inclusion. Preprocessor definitions specialize the shared `binfmt_elf.c` code, which then compiles a second binfmt instance for compat ELF.

State and persistence: state is the binfmt registration and core-dump behavior created by the included file. This wrapper itself stores no data.

Dependencies/integration: depends on architecture-provided compat ELF definitions in `asm/elf.h`, `linux/elfcore-compat.h`, compat signal/time types, and the native ELF loader source.

Risks: macro drift between native and compat builds can silently break 32-bit exec or core notes. Architectures must provide correct compat hooks, especially for thread start, auxv, hwcaps, and core register sets. Including a C file makes symbol-renaming completeness important.

Test signals: run 32-bit ELF binaries on supported 64-bit kernels, validate 32-bit core files and notes with debuggers, check compat auxv/hwcaps, run binfmt ELF KUnit/selftests if enabled, and compile architectures with and without optional `COMPAT_*` overrides.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/compat_binfmt_elf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/configfs/Kconfig -->
# sources/distributed-fs/ceph-client/fs/configfs/Kconfig

Purpose: declares the `CONFIG_CONFIGFS_FS` build option for the userspace-driven configuration filesystem.

Important entries: `config CONFIGFS_FS` is a tristate named "Userspace-driven configuration filesystem". The help text positions configfs as the converse of sysfs: sysfs exposes kernel objects, while configfs lets userspace create and manage kernel `config_item` objects through filesystem operations.

Control flow: no runtime control flow. Kconfig selection determines whether the configfs code is built in, built as a module, or omitted.

State and persistence: no state. The option controls availability of the `configfs` filesystem and associated APIs.

Dependencies/integration: consumed by `fs/configfs/Makefile` via `obj-$(CONFIG_CONFIGFS_FS)`. Kernel subsystems that expose configfs trees depend on this option or select it in their own Kconfig entries.

Risks: as a tristate, dependent subsystems must handle built-in versus module availability and symbol export constraints. Misconfigured systems will lack `/sys/kernel/config` and configfs APIs.

Test signals: Kconfig dependency resolution, allnoconfig disabling configfs, module and built-in builds, and dependent subsystem builds against each mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/configfs/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/configfs/Makefile -->
# sources/distributed-fs/ceph-client/fs/configfs/Makefile

Purpose: defines how the configfs filesystem is built.

Important entries: `obj-$(CONFIG_CONFIGFS_FS) += configfs.o` builds the composite object when enabled. `configfs-objs` lists `inode.o`, `file.o`, `dir.o`, `symlink.o`, `mount.o`, and `item.o`.

Control flow: no runtime logic. Kbuild links the listed objects into `configfs.o` for built-in or modular use.

State and persistence: no state.

Dependencies/integration: connects the Kconfig option to the implementation files. The object composition shows the subsystem boundaries: mount/superblock setup, item lifetime helpers, inode metadata, directory operations, attribute file operations, and symlink operations.

Risks: missing an object can create unresolved exports or a filesystem that registers without core operations. Order is conventional but symbol resolution is handled by kbuild.

Test signals: build `CONFIG_CONFIGFS_FS=y`, `m`, and `n`; check exported symbols for configfs users; and run mount/register subsystem smoke tests in both module and built-in configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/configfs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/configfs/configfs_internal.h -->
# sources/distributed-fs/ceph-client/fs/configfs/configfs_internal.h

Purpose: defines configfs-private structures, flags, globals, helpers, and cross-file prototypes shared by the implementation.

Important APIs/types: `struct configfs_fragment` carries `frag_count`, `frag_sem`, and `frag_dead` to block file callbacks during teardown. `struct configfs_dirent` stores refcount, dependency/link counts, sibling/child lists, backing element, type flags, mode, dentry, persistent iattrs, optional lockdep depth, and fragment pointer. Flags distinguish root, directories, text/bin attributes, symlinks, user-created groups, default groups, dropping/creating states, and pinned versus lookup-created entries. Inline helpers convert dentries to items/attributes, get config items safely, and refcount dirents/fragments.

Control flow: not a runtime unit, but it encodes invariants used across files: pinned entries have dentries held in core; attributes are created lazily at lookup; fragments are shared by a group subtree and marked dead before detach.

State and persistence: state is held in dirents and fragments. `s_iattr` preserves chmod/chown/timestamps while dentries/inodes come and go in the RAM filesystem.

Dependencies/integration: declares `configfs_dirent_lock`, `configfs_symlink_mutex`, `configfs_dir_cachep`, inode/file/dir/symlink operations, mount pin/release functions, and creation helpers used among `dir.c`, `file.c`, `inode.c`, `mount.c`, and `symlink.c`.

Risks: flag semantics are subtle, especially `CONFIGFS_USET_CREATING`, `DROPPING`, and `IN_MKDIR`. Refcount mistakes on dirents/fragments can produce use-after-free or leaks. `configfs_get_config_item()` depends on dentry lock and unhashed checks.

Test signals: lockdep with default groups, refcount leak tests across subsystem unregister, attribute lookup/open during rmdir, symlink/rmdir races, and chmod persistence after dentry eviction/relookup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/configfs/configfs_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/configfs/dir.c -->
# sources/distributed-fs/ceph-client/fs/configfs/dir.c

Purpose: implements configfs directory operations, config item/group attachment and detachment, mkdir/rmdir, readdir, subsystem registration, group registration, dependency pinning, and most configfs tree lifecycle rules.

Important APIs/functions: `configfs_make_dirent()`, `configfs_create_dir()`, `configfs_create_link()`, `configfs_lookup()`, `populate_attrs()`, `populate_groups()`, `configfs_mkdir()`, `configfs_rmdir()`, directory file operations, `configfs_register_group()`, `configfs_unregister_group()`, `configfs_register_default_group()`, `configfs_register_subsystem()`, `configfs_unregister_subsystem()`, `configfs_depend_item()`, `configfs_depend_item_unlocked()`, and `configfs_undepend_item()` are central. `configfs_dirent_lock` protects dirent linkage, symlink target link counts, and attach/drop state flags.

Control flow: subsystem registration pins configfs, links a root group, allocates a dentry, attaches the group, populates attributes/default groups, then marks dirents ready. User `mkdir()` validates parent readiness and `make_item`/`make_group` callbacks, pins owner modules, links the item under subsystem mutex, attaches the VFS view, and rolls back on any failure. `rmdir()` blocks links/dependents, marks the fragment dead, detaches default children and attributes, notifies clients, unlinks objects, and drops module references. Lookup instantiates attributes lazily from unpinned dirents. Readdir uses a cursor dirent to traverse under the global spinlock.

State and persistence: configfs is RAM-backed. Persistent in-memory state lives in `config_item` hierarchies, `configfs_dirent` trees, fragment death markers, child/default group lists, module references, and dependency counts.

Dependencies/integration: integrates VFS inode locks, dcache operations, module refcounting, configfs public callbacks in `include/linux/configfs.h`, `file.c` attribute creation, `inode.c` inode allocation/drop, `mount.c` pin/release, and `symlink.c` link serialization.

Risks: lock ordering is critical: inode mutex before `configfs_dirent_lock`, plus `configfs_symlink_mutex` around rmdir/link races. Recursive default-group attach/detach can stress lockdep and stack depth. Client callbacks must obey configfs reference rules; calling dependency APIs from callbacks is explicitly unsafe.

Test signals: mkdir/rmdir success and rollback, default group recursion, visible/invisible attributes, lazy attribute lookup, readdir under concurrent mutation, symlink versus rmdir races, dependent item preventing removal, subsystem unregister with non-empty tree, module reference release, and lockdep coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/configfs/dir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/configfs/file.c -->
# sources/distributed-fs/ceph-client/fs/configfs/file.c

Purpose: implements configfs regular and binary attribute file operations and helpers to attach attribute dirents to config items.

Important APIs/types/functions: `struct configfs_buffer` stores per-open buffer state, item/attribute pointers, module owner, read/write mode flags, binary buffer, and mutex. `configfs_read_iter()` and `configfs_write_iter()` serve text attributes through `show()` and `store()`, with a fixed 4096-byte simple-attribute limit. `configfs_bin_read_iter()` and `configfs_bin_write_iter()` handle variable-size binary attributes with optional `cb_max_size`; binary writes are committed on `release`. `__configfs_open_file()` validates fragment liveness, permissions, callbacks, and module references. `configfs_create_file()` and `configfs_create_bin_file()` create attribute dirents.

Control flow: open takes the fragment read semaphore, rejects dead fragments, resolves parent item and attribute, pins the attribute owner module, checks requested read/write support, and stores a buffer in `file->private_data`. Text reads fill once then copy to userspace; text writes copy a whole buffer and call `store()`. Binary reads first query size with `read(item, NULL, 0)`, allocate, then read data. Binary writes grow an in-memory buffer and call `write()` at close.

State and persistence: per-open buffers are transient. Attribute values are owned by client subsystems. `frag_dead` makes callbacks return `-ENOENT` during teardown.

Dependencies/integration: depends on configfs dirents/fragments, public `configfs_attribute` and `configfs_bin_attribute`, module refcounting, VFS iov_iter APIs, and `dir.c` population.

Risks: text partial writes are intentionally unsupported; callers must write complete values. Binary read/write modes cannot be mixed on one open. Large binary buffers can consume memory up to `cb_max_size`. Fragment locking protects object lifetime but client callbacks must still validate their own state.

Test signals: text show/store limits, write without store, read without show, open during unregister, binary size query/fill, binary write commit on release, `cb_max_size` enforcement, module unload while file open, and concurrent readers/writers on separate opens.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/configfs/file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/configfs/inode.c -->
# sources/distributed-fs/ceph-client/fs/configfs/inode.c

Purpose: provides configfs inode creation, persistent attribute metadata handling, dentry dropping, and lockdep class assignment for default groups.

Important APIs/functions: `configfs_setattr()` stores changed uid/gid/mode/timestamps in `sd->s_iattr` after `simple_setattr()`. `configfs_new_inode()` allocates a new inode, assigns `ram_aops`, default inode operations, inode number, and either default or saved attributes. `configfs_create()` validates a negative dentry, creates an inode, updates parent mtime/ctime, and assigns lock classes for default groups. `configfs_get_name()` maps dirents to directory/link dentry names or attribute names. `configfs_drop_dentry()` unhashes and unlinks instantiated attribute/link dentries.

Control flow: dir/link/attribute creation first creates a dirent, then calls `configfs_create()` to allocate the inode. Later chmod/chown calls update both inode and dirent so attributes survive dentry eviction and recreation. Removal paths call `configfs_drop_dentry()` while holding the parent inode mutex.

State and persistence: configfs is RAM-only, but `s_iattr` persists metadata for each dirent while the config item exists. Inode numbers are generated with `get_next_ino()`.

Dependencies/integration: used by `dir.c`, `file.c`, `mount.c`, and `symlink.c`; depends on VFS simple inode helpers, ram address-space ops, capabilities, and lockdep when enabled.

Risks: `sd->s_iattr` allocation happens on first setattr and must be freed with the dirent. `ATTR_MODE` must clear `S_ISGID` correctly when callers lack permissions. Dentry dropping races are coordinated with parent inode locks and dentry locks.

Test signals: chmod/chown persistence after lookup eviction, directory/link/attribute inode modes, lockdep class behavior for nested default groups, dentry drop while file open, and setattr permission/capability cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/configfs/inode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/configfs/item.c -->
# sources/distributed-fs/ceph-client/fs/configfs/item.c

Purpose: implements generic `config_item` and `config_group` lifetime, naming, initialization, reference counting, cleanup, and child lookup helpers.

Important APIs/functions: `config_item_set_name()` formats item names into `ci_namebuf` when short or dynamically allocates long names. `config_item_init_type_name()` and `config_group_init_type_name()` combine naming, type assignment, and kref/list initialization. `config_item_get()`, `config_item_get_unless_zero()`, and `config_item_put()` manage krefs. `config_item_cleanup()` frees dynamic names, calls optional `ct_item_ops->release()`, and drops group/parent references. `config_group_init()` initializes child/default lists. `config_group_find_item()` searches children by name under the caller-held subsystem mutex.

Control flow: clients allocate items/groups, initialize them here, configfs links them into parent groups in `dir.c`, and cleanup runs automatically when the final reference is dropped. Group lookup returns a referenced child.

State and persistence: state is embedded in client-owned `config_item`/`config_group` objects. Names persist until cleanup or rename through `config_item_set_name()`.

Dependencies/integration: public configfs API users depend on these exports. `dir.c` relies on `ci_parent`, `ci_group`, `ci_entry`, `cg_children`, and default group lists initialized here.

Risks: release callbacks are responsible for freeing client objects at the correct time. Long-name allocation failures can leave initialization partially named unless callers check return values. `config_group_find_item()` requires external locking; using it without `su_mutex` risks list races.

Test signals: short and long item names, repeated name changes freeing old allocations, kref final release, group child lookup under concurrent configfs operations, and client release callback ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/configfs/item.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/configfs/mount.c -->
# sources/distributed-fs/ceph-client/fs/configfs/mount.c

Purpose: registers and mounts the configfs RAM filesystem, owns the root group/dirent, the dirent slab cache, and filesystem pinning helpers used by subsystem registration.

Important APIs/functions: `configfs_fill_super()` initializes the superblock, creates the root inode/dentry, initializes `configfs_root_group`, attaches the root dirent, and installs default dentry ops. `configfs_pin_fs()` and `configfs_release_fs()` wrap `simple_pin_fs()` and `simple_release_fs()` for users that need a live root without a user mount. `configfs_init()` creates `configfs_dir_cachep`, creates `/sys/kernel/config` mount point, and registers the filesystem. `configfs_exit()` reverses these steps. `configfs_free_inode()` frees symlink bodies stored in `i_link`.

Control flow: core init registers configfs early. User mount uses `get_tree_single()` to share a singleton filesystem instance. Kernel subsystem registration pins the filesystem and creates top-level groups under the root.

State and persistence: global `configfs_mount`, `configfs_mnt_count`, `configfs_dir_cachep`, `configfs_root_group`, and `configfs_root` persist while configfs is loaded. The filesystem contents are RAM state only.

Dependencies/integration: integrates VFS single-superblock mounting, sysfs mount-point creation under `kernel_kobj`, config item initialization, inode/dir operations, and dentry ops.

Risks: root dirent is static and excluded from normal dirent freeing. Symlink bodies must be freed in inode free. Failure paths must remove the sysfs mount point and destroy the cache. Pin counts must balance or configfs can remain mounted internally.

Test signals: mount/umount, internal pin/release without user mount, module load failure injection at cache/mountpoint/register steps, symlink inode free, and top-level subsystem register/unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/configfs/mount.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/configfs/symlink.c -->
# sources/distributed-fs/ceph-client/fs/configfs/symlink.c

Purpose: implements configfs symlink creation and removal. Configfs symlinks are resolved at creation time to a target config item and keep that target busy against removal.

Important APIs/functions: `configfs_symlink_mutex` serializes symlink attach against rmdir. Path helpers compute a relative symlink body from source item to target. `get_target()` resolves the user path with `kern_path()`, requires the same superblock, and takes a target config item reference. `configfs_symlink()` validates parent item operations, temporarily drops the parent inode lock to resolve the target, calls client `allow_link()`, and creates the link. `configfs_unlink()` drops the dirent, calls optional `drop_link()`, decrements the target link count, and releases references.

Control flow: user `symlink(2)` supplies a target path. The target is looked up before relocking the parent to avoid VFS deadlocks, then the code revalidates the destination dentry and permissions. Successful creation increments `target_sd->s_links`, stores a relative path body in the symlink inode, and pins target dirent references. Unlink removes the link before decrementing target link count.

State and persistence: symlink bodies are heap strings freed by `mount.c` inode free. Target dirents track `s_links`; rmdir rejects linked targets. Links are RAM-only configfs entries.

Dependencies/integration: depends on public configfs `allow_link`/`drop_link` callbacks, dentry/path lookup, `dir.c` link creation and rmdir checks, and `inode.c` setattr.

Risks: the ABI intentionally differs from normal symlink semantics by resolving and pinning the target at creation. Locking is delicate because target lookup cannot happen with the parent directory locked. `drop_link()` ordering before decrementing target links preserves client cleanup ordering.

Test signals: valid same-configfs links, cross-superblock target rejection, missing target, target in creating/dropping state, rmdir blocked by links, unlink callback ordering, long relative paths returning `-ENAMETOOLONG`, and races with rmdir/mkdir.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/configfs/symlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/coredump.c -->
# sources/distributed-fs/ceph-client/fs/coredump.c

Purpose: implements Linux VFS core dump orchestration: pattern expansion, process/thread quiescing, output target setup for files, pipe helpers, and AF_UNIX sockets, invoking binary-format dump writers, exported dump-write helpers, coredump sysctls, and VMA dump selection.

Important APIs/functions: `vfs_coredump()` is the top-level entry from fatal signal handling. `coredump_parse()` expands `core_pattern` tokens and identifies file, pipe, socket, or socket request protocol outputs. `coredump_wait()` zaps sibling threads and waits for stable state. `coredump_file()`, `coredump_pipe()`, and `coredump_socket()` set up output. `do_coredump()` drives target setup, optional rejection, file-table unshare, `binfmt->core_dump()`, and helper waiting. Exported helpers `dump_emit()`, `dump_skip_to()`, `dump_skip()`, `dump_user_range()`, and `dump_align()` are used by ELF and other binfmt dumpers.

Control flow: `vfs_coredump()` snapshots dumpability flags, optionally switches fsuid to root for suid-safe dumps, coordinates threads, then runs `do_coredump()` under scoped creds. Output setup enforces `RLIMIT_CORE`, suid path rules, pipe recursion guard, `core_pipe_limit`, or socket request/ack masks. `coredump_write()` snapshots VMAs, calls the binfmt writer, fixes trailing sparse skips, and frees snapshots. Cleanup closes files, decrements pipe counters, frees names, and wakes killed threads.

State and persistence: sysctl globals include `core_pattern`, `core_uses_pid`, `core_pipe_limit`, `core_file_note_size_limit`, and `core_sort_vma`. Per-dump state lives in `coredump_params`, `core_name`, `core_state`, and VMA metadata. Core files or userspace processing are the persistent outputs.

Dependencies/integration: integrates signals, credentials, pidfs, usermodehelper, pipes, AF_UNIX sockets, VFS file creation/security, mm/VMA iteration, binfmt core writers, sysctls, audit, tracepoints, freezer, and proc connector behavior.

Risks: security rules for suid dumps and `core_pattern` paths are critical. Socket mode requires initial mount namespace validation and dotdot/path length checks. Thread coordination must avoid races with exit/exec. Dump helpers must honor limits and interruption. VMA snapshotting uses write mmap lock due to stack expansion concerns.

Test signals: `core_pattern` token expansion, file/pipe/socket outputs, `%F` pidfd helper behavior, suid dump mode safety, `core_pipe_limit`, socket ack rejection/wait masks, interrupted dumps, sparse output via `dump_skip`, VMA filtering flags, sysctl validation, and ELF core readability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/coredump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/cramfs/Kconfig -->
# sources/distributed-fs/ceph-client/fs/cramfs/Kconfig

Purpose: declares build options for the compressed ROM filesystem.

Important entries: `CONFIG_CRAMFS` is a tristate that selects `ZLIB_INFLATE`. `CONFIG_CRAMFS_BLOCKDEV` enables mounting images from block devices and defaults to yes when block support is available. `CONFIG_CRAMFS_MTD` enables direct mapping from physical memory through MTD and depends on compatible Cramfs/MTD build modes.

Control flow: no runtime logic. These options compile in the block-device read path, MTD direct-map path, or both.

State and persistence: no runtime state; Kconfig controls feature availability.

Dependencies/integration: links to `fs/cramfs/Makefile`; selects zlib inflate for `uncompress.c`; depends on `BLOCK` and `MTD` for the respective backends.

Risks: disabling both blockdev and MTD support leaves the filesystem type with no viable get-tree backend. The help text documents format limitations: read-only, small filesystem/file size limits, limited uid/gid/timestamps/hard links.

Test signals: build each combination of `CRAMFS`, `CRAMFS_BLOCKDEV`, and `CRAMFS_MTD`; mount block images; mount `mtd:<name>` direct images; and ensure zlib dependencies resolve for module and built-in builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/cramfs/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/cramfs/Makefile -->
# sources/distributed-fs/ceph-client/fs/cramfs/Makefile

Purpose: defines the Cramfs composite object build.

Important entries: `obj-$(CONFIG_CRAMFS) += cramfs.o` and `cramfs-objs := inode.o uncompress.o`.

Control flow: no runtime flow. Kbuild links VFS/mount/read logic with zlib wrapper logic when Cramfs is enabled.

State and persistence: no state.

Dependencies/integration: pairs with Kconfig's `ZLIB_INFLATE` selection. The split confirms that the main filesystem implementation and decompressor wrapper are compiled together into the module/built-in object.

Risks: omitting `uncompress.o` would break compressed block reads; omitting `inode.o` would register nothing. Conditional backend code is handled by C preprocessor symbols in `inode.c`, not by Makefile object selection.

Test signals: compile Cramfs as built-in and module, run modpost for zlib symbols, and mount sample images.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/cramfs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/cramfs/inode.c -->
# sources/distributed-fs/ceph-client/fs/cramfs/inode.c

Purpose: implements Cramfs VFS integration: inode construction, block-device and MTD-backed image reading, direct physical mmap support for suitable MTD images, superblock validation, directory iteration/lookup, folio decompression, statfs, mount, and module registration.

Important APIs/functions: `cramino()` computes inode numbers from on-disk inode offsets. `get_cramfs_inode()` creates VFS inodes for regular files, directories, symlinks, and special files. `cramfs_read()` dispatches to `cramfs_blkdev_read()` or `cramfs_direct_read()`. `cramfs_get_block_range()` and `cramfs_physmem_mmap()` enable direct mapping of aligned uncompressed blocks. `cramfs_read_super()` validates magic, feature flags, root inode, size/fsid, and root offset. `cramfs_readdir()`, `cramfs_lookup()`, and `cramfs_read_folio()` provide directory and file data operations.

Control flow: mount tries MTD if enabled, then blockdev if enabled. Fill-super allocates `cramfs_sb_info`, maps/reads the image, validates the superblock, and creates the root. File reads locate the block pointer for the folio, interpret direct/uncompressed flags or end-pointer layout, read compressed bytes, call `cramfs_uncompress_block()` unless uncompressed, zero-fill the folio tail, and mark read completion.

State and persistence: `cramfs_sb_info` stores image size, block/file counts, flags, and MTD mapping details. A small global two-buffer block cache is protected by `read_mutex`. The filesystem is read-only and has no writeback state.

Dependencies/integration: VFS, block device page cache, MTD `point/unpoint`, zlib decompression wrapper, UAPI Cramfs on-disk structs, generic read-only file ops, symlink page ops, and mmap helpers.

Risks: `read_mutex` serializes decompression and shared block buffers. On-disk pointer validation is crucial; bad block sizes over `2*PAGE_SIZE` or uncompressed over `PAGE_SIZE` fail. MTD direct mmap must avoid mapping shared tail pages. Old mkcramfs quirks are handled in inode number logic and root permissions.

Test signals: valid and invalid magic/endian images, shifted root offsets, sorted directory lookup, malformed namelen/block pointers, compressed and uncompressed blocks, holes, symlinks, special files, blockdev cache reuse, MTD direct mapping and fallback mmap, remount read-only, and statfs counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/cramfs/inode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/cramfs/internal.h -->
# sources/distributed-fs/ceph-client/fs/cramfs/internal.h

Purpose: declares the small internal decompression interface shared by Cramfs implementation files.

Important APIs: `cramfs_uncompress_block(void *dst, int dstlen, void *src, int srclen)`, `cramfs_uncompress_init()`, and `cramfs_uncompress_exit()`.

Control flow: `inode.c` calls init before registering the filesystem, calls block decompression from `cramfs_read_folio()`, and calls exit during module unload or registration failure.

State and persistence: no direct state in the header; `uncompress.c` owns the global zlib stream/workspace.

Dependencies/integration: used only inside `fs/cramfs`; abstracts zlib details away from inode/read logic.

Risks: because the implementation uses a single global zlib stream, callers must preserve serialization around `cramfs_uncompress_block()`; `inode.c` does this with `read_mutex`.

Test signals: compile inclusion by both Cramfs objects, init/decompress/exit ordering, and failure injection for decompressor init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/cramfs/internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/cramfs/uncompress.c -->
# sources/distributed-fs/ceph-client/fs/cramfs/uncompress.c

Purpose: wraps zlib inflate for Cramfs block decompression with a single reusable global stream.

Important APIs/functions: `cramfs_uncompress_init()` allocates zlib workspace with `vmalloc()` and initializes the stream on first user. `cramfs_uncompress_block()` resets the stream, inflates one compressed source buffer into the destination page-sized buffer, returns decompressed byte count, and logs/reset-recovers from reset errors. `cramfs_uncompress_exit()` ends the zlib stream and frees workspace when the final user exits.

Control flow: filesystem init initializes the stream. Each compressed block read sets `next_in`, `avail_in`, `next_out`, and `avail_out`, calls `zlib_inflateReset()`, then `zlib_inflate(..., Z_FINISH)`. Module exit tears down the stream.

State and persistence: global `z_stream stream` and `initialized` refcount persist while Cramfs is loaded. No filesystem data persists here.

Dependencies/integration: depends on `linux/zlib.h`, `vmalloc`, and Cramfs `internal.h`. `inode.c` serializes access with `read_mutex`.

Risks: decompression is explicitly single-threaded; using it without the external mutex would corrupt the global stream. Error logging includes kernel pointers with `%p`, subject to pointer formatting policy. `initialized` is not atomic because lifecycle is module-level.

Test signals: compressed block success, corrupt zlib stream returning `-EIO`, init allocation failure, repeated init/exit pairing, and concurrent file reads under lockdep or stress to verify serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/cramfs/uncompress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/crypto/Kconfig -->
# sources/distributed-fs/ceph-client/fs/crypto/Kconfig

Purpose: declares fscrypt build options for per-file encryption.

Important entries: `FS_ENCRYPTION` enables the framework and selects crypto, skcipher, AES/SHA helper libraries, and key support. `FS_ENCRYPTION_ALGS` pulls in default AES-CBC/CTS/XTS algorithms as a tristate for filesystems that need encryption algorithms. `FS_ENCRYPTION_INLINE_CRYPT` enables blk-crypto inline hardware support when block inline encryption is available.

Control flow: no runtime logic. Options determine whether fscrypt core, algorithm modules, block bio helpers, and inline crypto support are built.

State and persistence: no direct state; selected options affect availability of encryption policies and key setup at runtime.

Dependencies/integration: used by filesystems such as ext4, f2fs, ubifs, and CephFS. The help text notes that non-default modes such as Adiantum require explicit crypto API configuration.

Risks: enabling fscrypt without needed optimized algorithms can produce poor performance. Inline crypt depends on block-layer support and filesystem device constraints. Filesystems must select `FS_ENCRYPTION_ALGS` appropriately.

Test signals: build core only, default algorithm module combinations, inline-crypt enabled/disabled, and filesystem encryption mount/key tests across supported filesystems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/crypto/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/crypto/Makefile -->
# sources/distributed-fs/ceph-client/fs/crypto/Makefile

Purpose: defines the fscrypt composite object and conditional helpers.

Important entries: `obj-$(CONFIG_FS_ENCRYPTION) += fscrypto.o`. Core objects are `crypto.o`, `fname.o`, `hkdf.o`, `hooks.o`, `keyring.o`, `keysetup.o`, `keysetup_v1.o`, and `policy.o`. `bio.o` is included when `CONFIG_BLOCK` is enabled, and `inline_crypt.o` when `CONFIG_FS_ENCRYPTION_INLINE_CRYPT` is enabled.

Control flow: no runtime logic. Kbuild composes the framework according to block and inline-crypto availability.

State and persistence: no state.

Dependencies/integration: ties Kconfig selections to exported fscrypt APIs used by filesystems. Conditional inclusion avoids block-only helpers on non-block builds.

Risks: source-level references must stay protected by matching Kconfig guards, especially for bio and inline crypto exports. Omitting key/policy objects would break public fscrypt operations.

Test signals: compile with block disabled/enabled, inline crypto disabled/enabled, and run modpost for exported symbols consumed by filesystem modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/crypto/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/crypto/bio.c -->
# sources/distributed-fs/ceph-client/fs/crypto/bio.c

Purpose: provides block-device oriented fscrypt helpers for decrypting completed read bios and writing encrypted zero ranges.

Important APIs/functions: `fscrypt_decrypt_bio()` iterates all folios in a read bio and calls `fscrypt_decrypt_pagecache_blocks()`, setting `bio->bi_status` on failure. `fscrypt_zeroout_range()` writes ciphertext blocks that decrypt to zero for a logically and physically contiguous encrypted file range. `fscrypt_zeroout_range_inline_crypt()` handles inline-crypto in the block layer using zero pages and `fscrypt_set_bio_crypt_ctx()`.

Control flow: read completion workqueues call `fscrypt_decrypt_bio()` after disk I/O has filled page-cache folios. Zeroout chooses inline crypto when configured for the inode; otherwise it allocates bounce pages, encrypts zero data unit by data unit with `fscrypt_crypt_data_unit()`, submits synchronous write bios, resets and reuses the bio until the range is complete, then frees pages.

State and persistence: transient bios, pages, completions, and status. Persistent result is encrypted zero blocks on disk.

Dependencies/integration: depends on block layer bios, folio iteration, fscrypt inode info, inline-crypto helpers, bounce-page pool from `crypto.c`, and filesystem `s_bdev`.

Risks: caller must pass block-aligned, contiguous ranges and a filesystem with one block device. Bounce-page allocation requires the filesystem to set `needs_bounce_pages` if using non-inline zeroout. Inline bio completion must aggregate errors correctly. Data unit size and sector advancement must remain aligned.

Test signals: decrypt multi-folio bios, injected crypto failure mapping to blk_status, zero-length zeroout, inline and software zeroout, ranges crossing page boundaries, allocation failure for optional pages, submit_bio_wait errors, and ciphertext verification by reading zeros back.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/crypto/bio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/crypto/crypto.c -->
# sources/distributed-fs/ceph-client/fs/crypto/crypto.c

Purpose: implements fscrypt content encryption/decryption primitives, bounce page allocation, read decrypt workqueue setup, IV generation, framework initialization, and rate-limited fscrypt logging.

Important APIs/functions: `fscrypt_enqueue_decrypt_work()` queues bio/page decrypt work. `fscrypt_alloc_bounce_page()` and `fscrypt_free_bounce_page()` manage ciphertext pages from a mempool. `fscrypt_generate_iv()` implements policy-specific IV formats including inode+logical-block variants and direct-key nonce mode. `fscrypt_crypt_data_unit()` performs one skcipher encrypt/decrypt operation. `fscrypt_encrypt_pagecache_blocks()`, `fscrypt_decrypt_pagecache_blocks()`, `fscrypt_encrypt_block_inplace()`, and `fscrypt_decrypt_block_inplace()` are exported content helpers. `fscrypt_initialize()` lazily creates the bounce page pool for filesystems that need it. `fscrypt_init()` creates the high-priority unbound read workqueue, inode-info slab, and keyring support.

Control flow: filesystems ensure inode encryption info is set, then call page/block helpers during writeback, read completion, or compression paths. Helpers compute data unit indexes from folio index/offset or logical block number, generate IVs, and invoke the crypto API with scatterlists.

State and persistence: global workqueue, bounce page mempool, and `fscrypt_inode_info_cachep` persist for the framework lifetime. Per-inode crypto state lives in `fscrypt_inode_info` set up by keysetup code.

Dependencies/integration: crypto skcipher API, mempools, workqueues, page cache, fscrypt policy/keysetup internals, optional inline crypto, and filesystem `fscrypt_operations`.

Risks: all lengths/offsets must align to crypto data unit size and `FSCRYPT_CONTENTS_ALIGNMENT`. Large folios are rejected in encrypt-pagecache helper. Bounce-page pool must exist before use. IV generation must stay synchronized with inline-crypto I/O block limiting.

Test signals: encrypt/decrypt round trips for each policy flag, misalignment warnings/errors, bounce pool lazy init, workqueue parallel decrypt, direct-key IVs, inode+lblk IV variants, in-place helper rejection with subblock data units, and crypto API failure logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/crypto/crypto.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/crypto/fname.c -->
# sources/distributed-fs/ceph-client/fs/crypto/fname.c

Purpose: implements fscrypt filename encryption/decryption, encrypted filename sizing and buffers, no-key name presentation and lookup, name matching, SipHash dirhash calculation, and encrypted dentry revalidation.

Important APIs/types/functions: `struct fscrypt_nokey_name` encodes dirhash, up to 149 ciphertext bytes, and optional SHA-256 for long ciphertext names, then base64url encodes to stay within `NAME_MAX`. `fscrypt_fname_encrypt()` pads and encrypts plaintext filenames. `fname_decrypt()` decrypts and trims NUL padding. `fscrypt_fname_encrypted_size()` computes padded encrypted size. `fscrypt_fname_disk_to_usr()` decrypts when the key is available or emits a no-key encoded name. `fscrypt_setup_filename()` prepares lookup/create disk names from user names. `fscrypt_match_name()` compares full disk names or long no-key hashes. `fscrypt_fname_siphash()` calculates keyed plaintext dirhashes. `fscrypt_d_revalidate()` invalidates no-key dentries after keys appear.

Control flow: create/lookup calls `fscrypt_setup_filename()`. With a key, plaintext is padded to at least 16 bytes and policy padding, encrypted with IV index 0, and used as the disk name. Without a key, lookup decodes the presented no-key name and either reconstructs the full ciphertext or stores prefix/hash data for matching. Directory listing calls `fscrypt_fname_disk_to_usr()` to present decrypted or encoded names.

State and persistence: transient buffers in `fscrypt_name` and `fscrypt_str`; persistent ciphertext names live in the filesystem directory entries. Dentries may be flagged `DCACHE_NOKEY_NAME`.

Dependencies/integration: fscrypt keysetup, skcipher crypto, SHA-256, base64url, SipHash, VFS dentry validation, and filesystem directory lookup code.

Risks: no-key names must be unambiguous, legal path components, and no longer than `NAME_MAX`. Short ciphertext below the minimum indicates corruption (`-EUCLEAN`). RCU revalidation must return `-ECHILD` because key lookup can sleep. Padding policy changes affect on-disk compatibility.

Test signals: filename round trips for lengths around 1, 16, padding boundaries, and `NAME_MAX`; listing without keys; lookup/delete by no-key names; long-name SHA-256 matching; dirhash/minor hash propagation; key-added dentry invalidation; dot/dotdot handling; and malformed base64/no-key names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/crypto/fname.c -->
