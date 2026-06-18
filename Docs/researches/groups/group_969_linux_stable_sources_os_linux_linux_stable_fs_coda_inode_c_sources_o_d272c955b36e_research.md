# Group Research: group_969_linux_stable_sources_os_linux_linux_stable_fs_coda_inode_c_sources_o_d272c955b36e

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/coda/inode.c -->
# File Research: sources/os/linux/linux-stable/fs/coda/inode.c

This file implements Coda filesystem superblock setup, mount-context parsing, inode-cache lifecycle, and common inode attributes operations.

Key responsibilities:
- Defines `coda_super_operations` with custom inode allocation/free, eviction, `put_super`, and `statfs`.
- Manages `coda_inode_cachep` via `coda_init_inodecache()` and `coda_destroy_inodecache()`.
- Parses new mount API parameter `fd=` and legacy binary mount data to select a Coda pseudo-device minor.
- `coda_fill_super()` binds a `struct venus_comm` pseudo-device channel to the superblock, requests the root fid from Venus, creates the root inode, and installs `s_root`.
- Restricts Coda mounts to the initial PID namespace through `coda_get_tree()`.
- Implements `coda_getattr()` and `coda_setattr()` as VFS-facing wrappers around Venus revalidation/setattr upcalls.
- Provides `coda_file_inode_operations`.

Important control flow:
- Mount setup: `coda_init_fs_context()` allocates `struct coda_fs_context`, `coda_parse_param()` or `coda_parse_monolithic()` sets `idx`, `coda_get_tree()` calls `get_tree_nodev()`, and `coda_fill_super()` validates `vc_inuse`/`vc_sb`.
- On failure after assigning `vc->vc_sb`, `coda_fill_super()` clears `vc_sb` and `sb->s_fs_info` under `vc_mutex`.
- `coda_put_super()` detaches the superblock from the pseudo-device state and destroys the channel mutex.

Dependencies:
- Depends on `coda_comms[]` and pseudo-device lifecycle from `psdev.c`.
- Depends on Venus RPC helpers in `upcall.c`, including `venus_rootfid()`, `venus_setattr()`, and `venus_statfs()`.
- Depends on inode/cache helpers from other Coda files such as `coda_cnode_make()`, `coda_revalidate_inode()`, and cache invalidation helpers.

Risks and invariants:
- A pseudo-device minor can have only one mounted superblock at a time.
- Mounting is intentionally limited to the initial PID namespace.
- `coda_parse_monolithic()` preserves legacy behavior by ignoring invalid file descriptor lookup failures after validating the mount-data version.
- `coda_statfs()` deliberately returns fake capacity data when Venus statfs fails.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/coda/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/coda/pioctl.c -->
# File Research: sources/os/linux/linux-stable/fs/coda/pioctl.c

This file implements Coda pioctl handling, exposing a special ioctl endpoint for Coda control operations routed to Venus.

Key responsibilities:
- Defines `coda_ioctl_inode_operations` and `coda_ioctl_operations`.
- Rejects execute permission on the pioctl inode through `coda_ioctl_permission()`.
- Implements `coda_pioctl()` to copy `PioctlData` from userspace, resolve the userspace path, ensure the target inode belongs to the same Coda superblock, and forward the operation to `venus_pioctl()`.

Important control flow:
- `copy_from_user()` reads ioctl arguments.
- `user_path_at()` resolves `data.path`, honoring `data.follow`.
- The target inode’s superblock must match the ioctl inode’s superblock.
- The target inode’s Coda fid is passed to Venus with the ioctl command and pioctl data.

Dependencies:
- Relies on `venus_pioctl()` from `upcall.c`.
- Relies on `ITOC()`/Coda inode private state for target fid extraction.

Risks and invariants:
- Cross-filesystem pioctl targets are rejected with `-EINVAL`.
- Userspace path handling is delegated to VFS lookup, including follow behavior.
- Bad userspace argument copying returns `-EINVAL`, not `-EFAULT`, matching the local convention in this file.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/coda/pioctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/coda/psdev.c -->
# File Research: sources/os/linux/linux-stable/fs/coda/psdev.c

This file implements the Coda pseudo-device character driver, module initialization/exit, and the bidirectional request/reply queues between kernel Coda VFS code and the Venus userspace cache manager.

Key responsibilities:
- Defines global `coda_comms[MAX_CODADEVS]`, `coda_hard`, and `coda_timeout`.
- Implements pseudo-device file operations: read, write, poll, ioctl, open, and release.
- Registers `/dev/cfsN` devices for Coda communication.
- Initializes and tears down Coda module state, including inode cache, char device, sysctl table, and filesystem registration.

Important control flow:
- `coda_psdev_open()` allows opens only from the initial PID and user namespaces, validates the minor, and initializes one `venus_comm` slot if unused.
- `coda_psdev_read()` waits for `vc_pending`, moves synchronous requests to `vc_processing`, and copies request data to Venus.
- `coda_psdev_write()` handles two paths:
  - Downcalls, identified by `DOWNCALL(hdr.opcode)`, are copied into a temporary buffer and passed to `coda_downcall()`.
  - Upcall replies are matched by `unique` in `vc_processing`, copied into the waiting request buffer, marked `CODA_REQ_WRITE`, and wake the sleeping requester.
- `CODA_OPEN_BY_FD` replies convert a Venus-provided fd into a kernel `struct file *` using `fget()`.
- `coda_psdev_release()` aborts all pending and processing synchronous requests and frees async requests.

Dependencies:
- `coda_downcall()` is implemented in `upcall.c`.
- Sysctl init/cleanup is implemented in `sysctl.c`.
- Filesystem type and inode cache setup are provided by `inode.c`.

Risks and invariants:
- Only one opener per pseudo-device slot is allowed.
- Request queues are protected by `vc_mutex`; readers also use `vc_waitq`.
- `coda_psdev_write()` returns `-ESRCH` if a Venus reply does not match an outstanding processing request.
- Release aborts waiters so kernel callers do not sleep forever when Venus exits.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/coda/psdev.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/coda/symlink.c -->
# File Research: sources/os/linux/linux-stable/fs/coda/symlink.c

This file implements Coda symlink page filling through a Venus `readlink` upcall.

Key responsibilities:
- Defines `coda_symlink_filler()` as the address-space `read_folio` handler for symlinks.
- Defines `coda_symlink_aops`.

Important control flow:
- Retrieves the owning inode from `folio->mapping->host`.
- Extracts the Coda fid from `struct coda_inode_info`.
- Calls `venus_readlink()` into the folio page buffer with a maximum length of `PAGE_SIZE`.
- Completes the folio read with success based on the Venus call result.

Dependencies:
- Depends on `venus_readlink()` from `upcall.c`.
- Used by Coda inode creation paths for symlink inodes.

Risks and invariants:
- The symlink target is fetched lazily from Venus into the page cache.
- Venus must NUL-terminate or otherwise respect the length protocol enforced by `venus_readlink()`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/coda/symlink.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/coda/sysctl.c -->
# File Research: sources/os/linux/linux-stable/fs/coda/sysctl.c

This file registers Coda runtime tunables under the `coda` sysctl directory.

Key responsibilities:
- Exposes `timeout`, `hard`, and `fake_statfs` sysctl entries.
- Implements `coda_sysctl_init()` and `coda_sysctl_clean()`.

Important control flow:
- `coda_sysctl_init()` registers the table only if `fs_table_header` is not already set.
- `coda_sysctl_clean()` unregisters and clears the header.

Dependencies:
- Uses globals declared through `coda_int.h`: `coda_timeout`, `coda_hard`, and `coda_fake_statfs`.

Risks and invariants:
- `timeout` and `hard` are writable by normal root-style sysctl permissions.
- `fake_statfs` is mode `0600`, making it more restricted.
- Cleanup is idempotent around the stored header pointer.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/coda/sysctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/coda/upcall.c -->
# File Research: sources/os/linux/linux-stable/fs/coda/upcall.c

This file implements Coda upcalls from the kernel to Venus and downcalls from Venus back to the kernel.

Key responsibilities:
- Provides Venus RPC wrappers for root fid, getattr, setattr, lookup, open/close, create, mkdir, remove, rmdir, rename, link, symlink, fsync, access, pioctl, statfs, and access-intent notifications.
- Implements `coda_upcall()`, the central request queueing and reply-wait mechanism.
- Implements `coda_downcall()` for Venus-initiated cache invalidation and fid replacement.
- Handles interrupt and timeout behavior for synchronous upcalls.

Important control flow:
- `alloc_upcall()` allocates and initializes a request header with opcode, pid, pgid, and fsuid in the initial namespaces.
- Each `venus_*()` wrapper builds a specific `union inputArgs` packet, embeds names at offsets when needed, calls `coda_upcall()`, copies output values, and frees the request buffer.
- `venus_access_intent()` may issue asynchronous finalizer calls by passing `outSize == NULL`.
- `coda_upcall()`:
  - Requires `vc_inuse`.
  - Allocates `struct upc_req`, assigns a unique sequence number, appends it to `vc_pending`, and wakes Venus.
  - Returns immediately for async requests.
  - Waits for synchronous replies via `coda_waitfor_upcall()`.
  - Maps positive Venus result codes to negative kernel errno.
  - If interrupted after Venus read the request, sends an async `CODA_SIGNAL` request.
- `coda_downcall()` validates message size by opcode, locates the mounted superblock, resolves affected fids to inodes, and applies Coda cache/dcache invalidation semantics.

Dependencies:
- Queue endpoints are consumed by `psdev.c`.
- Cache invalidation depends on `coda_cache_clear_all()`, `coda_flag_inode()`, `coda_flag_inode_children()`, `coda_replace_fid()`, and dcache pruning helpers.
- Uses Coda wire structs and opcodes from `<linux/coda.h>`.

Risks and invariants:
- Certain opcodes such as close/store/access-intent/release are made effectively uninterruptible until Venus reads them, avoiding reference-count or data-loss problems.
- Name-bearing upcalls manually pack NUL-terminated names into variable-size request buffers; length calculations and word-boundary padding are central correctness points.
- `venus_pioctl()` validates in/out sizes against `VC_MAXDATASIZE` and validates returned offset/length before copying to userspace.
- Downcalls intentionally split global flushes, per-user purges, directory zaps, file zaps, fid purges, and fid replacement semantics.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/coda/upcall.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/compat_binfmt_elf.c -->
# File Research: sources/os/linux/linux-stable/fs/compat_binfmt_elf.c

This file adapts the native ELF binary-format and coredump implementation for 32-bit compatibility ELF support on 64-bit kernels.

Key responsibilities:
- Defines `ELF_COMPAT` and remaps ELF layout types to 32-bit types.
- Remaps coredump note and signal-info types to compat variants.
- Rebinds architecture hooks to `COMPAT_*` forms when present.
- Renames local symbols generated by `binfmt_elf.c` to compat-prefixed names.
- Includes `binfmt_elf.c` to compile a compat version from the shared implementation.

Important control flow:
- There is no standalone runtime control flow; behavior is macro-driven at compile time.
- Architecture-specific compat definitions in `asm/elf.h` determine which hooks are overridden.

Dependencies:
- Requires `linux/elfcore-compat.h`, architecture compat ELF definitions, and `binfmt_elf.c`.
- Depends on `compat_elf_check_arch` being defined by architecture headers.

Risks and invariants:
- Macro remapping must occur before including `binfmt_elf.c`.
- Symbol renaming prevents duplicate local symbol ambiguity and separates native vs compat registration paths.
- Compat coredump layout must match the target 32-bit ABI, not the host kernel ABI.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/compat_binfmt_elf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/configfs/Kconfig -->
# File Research: sources/os/linux/linux-stable/fs/configfs/Kconfig

This file declares the `CONFIG_CONFIGFS_FS` build option for configfs.

Key responsibilities:
- Adds a tristate option named “Userspace-driven configuration filesystem”.
- Documents configfs as the converse of sysfs: userspace creates kernel configuration objects rather than only viewing kernel-created objects.

Dependencies:
- The selected option controls compilation through `fs/configfs/Makefile`.

Risks and invariants:
- Configfs is presented as complementary to sysfs, not a replacement.
- As a tristate, configfs can be built-in, modular, or disabled.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/configfs/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/configfs/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/configfs/Makefile

This file defines how configfs is built.

Key responsibilities:
- Builds `configfs.o` when `CONFIG_CONFIGFS_FS` is enabled.
- Composes `configfs.o` from `inode.o`, `file.o`, `dir.o`, `symlink.o`, `mount.o`, and `item.o`.

Dependencies:
- Mirrors the functional split of configfs into mount setup, inode/dentry helpers, directory object lifecycle, file attributes, symlinks, and generic item reference handling.

Risks and invariants:
- All listed objects are required for the configfs module/built-in object.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/configfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/configfs/configfs_internal.h -->
# File Research: sources/os/linux/linux-stable/fs/configfs/configfs_internal.h

This header declares configfs internal structures, flags, shared locks, helpers, and operation tables.

Key responsibilities:
- Defines `struct configfs_fragment`, used to gate operations during directory teardown.
- Defines `struct configfs_dirent`, the internal tree node for directories, attributes, binary attributes, symlinks, and root.
- Defines dirent type/state flags such as `CONFIGFS_DIR`, `CONFIGFS_ITEM_ATTR`, `CONFIGFS_USET_DEFAULT`, `CONFIGFS_USET_DROPPING`, and `CONFIGFS_USET_CREATING`.
- Declares shared locks `configfs_symlink_mutex` and `configfs_dirent_lock`.
- Declares exported-internal functions for creating inodes, dirents, links, attributes, pinning the filesystem, dropping dentries, and setattr.
- Provides inline conversions from dentries to config items and attributes.
- Provides reference helpers `configfs_get()` and `configfs_put()` for dirents.

Dependencies:
- Used by every configfs implementation file.
- Depends on public configfs types from `<linux/configfs.h>`.

Risks and invariants:
- `CONFIGFS_PINNED` and `CONFIGFS_NOT_PINNED` classify children differently for lookup and lifetime.
- Dirent release frees persistent attributes and fragment references for non-root entries.
- `configfs_get_config_item()` only returns an item if the dentry is still hashed, preventing stale item access.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/configfs/configfs_internal.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/configfs/dir.c -->
# File Research: sources/os/linux/linux-stable/fs/configfs/dir.c

This file implements configfs directory behavior, config item/group attachment and detachment, dependency management, registration APIs, readdir, lookup, mkdir, and rmdir.

Key responsibilities:
- Maintains the configfs dirent tree under `configfs_dirent_lock`.
- Creates and removes configfs directories, attributes, default groups, and symlinks’ dirent linkage.
- Implements VFS inode operations for configfs directories and root directories.
- Implements configfs item/group lifecycle transitions for userspace-created and kernel-registered groups.
- Exports subsystem/group registration and dependency APIs.

Important control flow:
- Dirent creation:
  - `configfs_new_dirent()` allocates and inserts a dirent, rejecting insertion if parent is dropping.
  - Pinned children are added at the tail; unpinned attributes are added at the head so lookup can stop at pinned entries.
- Lookup:
  - `configfs_lookup()` only instantiates unpinned attribute files and refuses entries while parent hierarchy is still `CONFIGFS_USET_CREATING`.
- Item/group attach:
  - `configfs_attach_item()` creates a directory and populates attributes.
  - `configfs_attach_group()` additionally marks `CONFIGFS_USET_DIR` and recursively creates default groups.
  - `configfs_dir_set_ready()` clears `CONFIGFS_USET_CREATING` recursively after successful setup.
- Userspace mkdir:
  - `configfs_mkdir()` checks group operations, pins subsystem and new item modules, invokes `make_group()` or `make_item()`, links the object, attaches it to VFS, marks readiness, and rolls back on error.
- Userspace rmdir:
  - Rejects default groups.
  - Uses `configfs_symlink_mutex` plus `configfs_dirent_lock` to block symlink races.
  - Checks dependents and recursive emptiness/default-group state via `configfs_detach_prep()`.
  - Marks the fragment dead and detaches attributes/groups before unlinking object references.
- Dependency APIs:
  - `configfs_depend_item()` pins configfs, finds the subsystem dentry, and increments `s_dependent_count`.
  - `configfs_undepend_item()` decrements the dependency count.
  - `configfs_depend_item_unlocked()` handles cross-subsystem locking when called from callbacks.
- Registration APIs:
  - `configfs_register_subsystem()` links a subsystem under root and attaches its group.
  - `configfs_unregister_subsystem()` requires the subsystem directory to be empty and tears it down.
  - `configfs_register_group()`/`unregister_group()` handle kernel-created child groups.
- Directory iteration:
  - `configfs_dir_open()` creates a cursor dirent.
  - `configfs_readdir()` emits visible children and keeps cursor position stable using list movement.
  - `configfs_dir_lseek()` repositions the cursor.

Dependencies:
- Calls inode helpers from `inode.c`, attribute helpers from `file.c`, symlink helpers from `symlink.c`, and item reference helpers from `item.c`.
- Uses `configfs_pin_fs()` from `mount.c` for dependency and subsystem registration paths.
- Uses public configfs group/item callbacks from `struct config_item_type`.

Risks and invariants:
- Mutating dirent linkage requires the relevant inode lock plus `configfs_dirent_lock`, in that order.
- `CONFIGFS_USET_CREATING`, `CONFIGFS_USET_DROPPING`, and `CONFIGFS_USET_IN_MKDIR` prevent userspace and teardown races.
- Default groups require special lockdep depth handling to avoid false recursive inode-lock reports.
- `s_dependent_count` blocks rmdir while external kernel users depend on an item.
- Error handling is complex because VFS dentries/inodes may already be visible once partial attach succeeds.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/configfs/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/configfs/file.c -->
# File Research: sources/os/linux/linux-stable/fs/configfs/file.c

This file implements configfs regular text attributes and binary attributes.

Key responsibilities:
- Defines `struct configfs_buffer`, the per-open file state for configfs attributes.
- Implements text attribute read/write via `show()` and `store()` callbacks.
- Implements binary attribute buffered reads and writes via `read()` and `write()` callbacks.
- Creates attribute dirents for items through `configfs_create_file()` and `configfs_create_bin_file()`.

Important control flow:
- Text reads allocate a 4 KiB page and call `attr->show()` under fragment read lock unless the fragment is dead.
- Text writes copy at most `SIMPLE_ATTR_SIZE - 1`, NUL-terminate the buffer, then call `attr->store()`.
- Binary reads first query size with `read(item, NULL, 0)`, enforce `cb_max_size`, allocate a vmalloc buffer, then perform a second read to fill it.
- Binary writes grow a vmalloc buffer as offsets advance and defer the actual callback write until file release.
- `__configfs_open_file()` validates fragment liveness, item/attribute presence, module ownership, permissions, and required callbacks.
- Release drops the module reference and frees buffers.

Dependencies:
- Uses `configfs_fragment` from directory lifecycle to prevent operations after teardown.
- Attribute metadata comes from public configfs item types and `configfs_attribute` / `configfs_bin_attribute`.

Risks and invariants:
- Text attributes are limited to 4096 bytes regardless of architecture page size.
- Binary attributes do not support switching between read and write modes in the same open file.
- Binary `release()` ignores the callback result by design.
- Fragment death changes operations to `-ENOENT`, preventing callbacks into detached objects.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/configfs/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/configfs/inode.c -->
# File Research: sources/os/linux/linux-stable/fs/configfs/inode.c

This file implements configfs inode creation, persistent attribute metadata, and dentry dropping helpers.

Key responsibilities:
- Implements `configfs_setattr()` to apply VFS setattr and persist non-default mode/uid/gid/timestamps in the dirent.
- Creates new configfs inodes with `configfs_new_inode()`.
- Creates uninstantiated dentry inodes with `configfs_create()`.
- Provides `configfs_get_name()` for dirents.
- Provides `configfs_drop_dentry()` to unhash and unlink attribute dentries.

Important control flow:
- First setattr allocates `sd->s_iattr` with default metadata, then records changed fields after `simple_setattr()` succeeds.
- `configfs_new_inode()` uses `ram_aops`, generic configfs inode operations, and either persistent `s_iattr` or default attributes.
- `configfs_create()` rejects null or already-positive dentries, allocates an inode, updates parent timestamps, and assigns lockdep class for default groups when configured.
- `configfs_drop_dentry()` handles positive dentries under dentry lock and performs `__simple_unlink()` from the parent.

Dependencies:
- Used by directory, file, mount, and symlink implementations.
- Lockdep class depth is supplied by `dir.c`.

Risks and invariants:
- Configfs persists chmod/chown/timestamp changes in dirents, not in backing storage.
- Setgid stripping follows normal capability/group checks.
- `configfs_get_name()` depends on dirent type: directories and links use dentry names; attributes use `ca_name`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/configfs/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/configfs/item.c -->
# File Research: sources/os/linux/linux-stable/fs/configfs/item.c

This file implements generic configfs item and group reference-counting utilities.

Key responsibilities:
- Initializes config items and groups.
- Sets item names using either the fixed `ci_namebuf` or dynamically allocated storage.
- Exports get/put helpers for config items.
- Cleans up items on final reference drop.
- Searches child items in a config group.

Important control flow:
- `config_item_set_name()` first tries `ci_namebuf`, then uses `kvasprintf()` if the formatted name is too long.
- `config_item_cleanup()` frees dynamic names, calls the item type’s `release()` callback, and drops group/parent references.
- `config_group_find_item()` scans `cg_children` under the caller-held subsystem mutex and returns a referenced item on match.

Dependencies:
- Used by configfs directory lifecycle and by configfs clients.
- Public exports form part of the configfs API.

Risks and invariants:
- `config_item_put()` is the only final-release path and delegates to kref.
- If a type provides `release()`, it is responsible for object-specific cleanup after generic cleanup steps.
- Group child lists require external locking by `cg_subsys->su_mutex`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/configfs/item.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/configfs/mount.c -->
# File Research: sources/os/linux/linux-stable/fs/configfs/mount.c

This file implements configfs filesystem registration, root superblock creation, filesystem pinning, and module lifecycle.

Key responsibilities:
- Defines configfs magic, root group, root dirent, and dirent cache.
- Implements `configfs_fill_super()` for `get_tree_single()`.
- Exposes `configfs_pin_fs()` and `configfs_release_fs()` for internal users that need the configfs root.
- Registers configfs as a filesystem and creates the sysfs mount point `kernel_kobj/config`.

Important control flow:
- `configfs_fill_super()` creates the root inode, root dentry, initializes root group state, attaches root dirent, installs default dentry ops, and marks the root dentry `DCACHE_DONTCACHE`.
- `configfs_init()` creates `configfs_dir_cachep`, creates the sysfs mount point, and registers the filesystem.
- `configfs_exit()` unregisters the filesystem, removes the sysfs mount point, and destroys the dirent cache.
- `configfs_free_inode()` frees symlink bodies stored in `inode->i_link`.

Dependencies:
- Uses inode helpers from `inode.c` and directory operations from `dir.c`.
- Exposes pinning used by subsystem registration and dependency APIs.

Risks and invariants:
- `configfs_root` is static and is not freed like regular dirents.
- `simple_pin_fs()` maintains a shared internal mount and reference count.
- Root group identity is used by `configfs_is_root()`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/configfs/mount.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/configfs/symlink.c -->
# File Research: sources/os/linux/linux-stable/fs/configfs/symlink.c

This file implements configfs symlink creation and unlink semantics.

Key responsibilities:
- Defines `configfs_symlink_mutex`.
- Resolves symlink targets to configfs items at syscall time.
- Builds relative symlink bodies from the link parent to the target item.
- Calls client `allow_link()` and `drop_link()` callbacks.
- Updates target dirent link counts to block unsafe removal.

Important control flow:
- `configfs_symlink()`:
  - Rejects not-ready parent directories.
  - Requires the parent item type to provide `allow_link`.
  - Temporarily unlocks the parent inode to resolve `symname` via `kern_path()`, then relocks and revalidates the dentry.
  - Calls `allow_link()`, then creates the link under `configfs_symlink_mutex`.
- `create_link()`:
  - Ensures target dirent is ready and not dropping.
  - Increments target `s_links`.
  - Computes a relative target path and calls `configfs_create_link()`.
  - Rolls back link count and references on failure.
- `configfs_unlink()` removes the symlink dirent, drops the dentry, invokes `drop_link()` before decrementing target link count, and releases references.

Dependencies:
- Uses directory/inode helpers from `dir.c` and `inode.c`.
- Depends on public configfs item callbacks.

Risks and invariants:
- Configfs symlinks are unusual: the target is resolved at symlink creation time and pins/removal-blocks a config item.
- The file contains explicit warnings that these semantics differ from normal symlink behavior and require careful locking.
- Target paths are bounded by `PATH_MAX`.
- Symlink targets must be on the same configfs superblock.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/configfs/symlink.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/coredump.c -->
# File Research: sources/os/linux/linux-stable/fs/coredump.c

This file implements Linux core dump orchestration, destination parsing, usermode-helper and socket delivery, VMA selection, dump writing helpers, and coredump sysctls.

Key responsibilities:
- Parses `kernel.core_pattern` into file, pipe, socket, or socket-request coredump destinations.
- Coordinates multithreaded process termination and coredump synchronization.
- Creates destination files, pipes to usermode helpers, or AF_UNIX socket connections.
- Invokes binary-format-specific `core_dump()` callbacks.
- Exports helper functions used by core writers: `dump_emit()`, `dump_skip_to()`, `dump_skip()`, `dump_user_range()`, and `dump_align()`.
- Registers sysctls for core naming, pipe limits, note size limits, VMA sorting, and supported modes.
- Snapshots VMAs and computes dump sizes according to `coredump_filter`/MMF flags.

Important control flow:
- `vfs_coredump()` audits, checks dumpability/binfmt support, prepares credentials, waits for other threads, calls `do_coredump()`, then cleans up.
- `coredump_parse()` expands `%` tokens in `core_pattern`, including pid variants, uid/gid, signal, time, hostname, executable names, core limit, CPU, and pipe pidfd fd number.
- Destination setup:
  - `coredump_file()` validates limits, SUID safety, ownership/mode preservation, regular-file type, and truncation.
  - `coredump_pipe()` spawns a usermode helper with stdin connected to a pipe and optionally installs pidfd fd 3.
  - Socket mode connects to a Unix stream socket, registers pidfs coredump metadata, and optionally negotiates request/ack flags.
- Dump writing:
  - `coredump_write()` snapshots VMAs, calls the binfmt core writer under `file_start_write()`, emits pending skip padding if needed, and frees the snapshot.
  - `dump_emit()` and `dump_skip()` maintain logical dump position and file position while respecting size limits and fatal interruption.
  - `dump_user_range()` walks user pages, writes present pages, and creates sparse holes for missing pages.
- VMA snapshot:
  - `vma_dump_size()` applies special mapping, DONTDUMP, DAX, hugetlb, shared/private, anonymous/file-backed, and ELF-header rules.
  - `dump_vma_snapshot()` takes metadata under mmap write lock, verifies ELF header placeholders after unlocking, sums dump size, and optionally sorts by dump size.

Dependencies:
- Relies on binfmt `core_dump()` implementations, especially ELF.
- Integrates with pidfs, proc connector, audit, fsnotify, sysctl, security/dumpability, usermode helper, AF_UNIX, and MM/VMA internals.

Risks and invariants:
- SUID-safe mode requires pipe, socket, or fully qualified file path and may dump as root fsuid.
- `core_pipe_limit` limits concurrent helper-backed dumps and controls whether the crashing task waits.
- Socket paths must be absolute, under initial mount namespace semantics, not contain `..`, not contain spaces, and fit `UNIX_PATH_MAX`.
- `dump_interrupted()` stops dumping on fatal signal or freezer activity.
- VMA metadata holds file references and must be released by `free_vma_snapshot()`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/coredump.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/cramfs/Kconfig -->
# File Research: sources/os/linux/linux-stable/fs/cramfs/Kconfig

This file declares CramFs build options.

Key responsibilities:
- Defines `CONFIG_CRAMFS` as compressed ROM filesystem support and selects `ZLIB_INFLATE`.
- Defines `CONFIG_CRAMFS_BLOCKDEV` for block-device-backed images.
- Defines `CONFIG_CRAMFS_MTD` for directly mapped physical-memory/MTD images.

Dependencies:
- `CRAMFS_BLOCKDEV` depends on `CRAMFS && BLOCK`.
- `CRAMFS_MTD` depends on `CRAMFS && CRAMFS <= MTD`.

Risks and invariants:
- Help text documents CramFs as readonly, small, RAM-efficient, and intentionally limited.
- MTD mode supports `mount -t cramfs mtd:<name>`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/cramfs/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/cramfs/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/cramfs/Makefile

This file defines CramFs build composition.

Key responsibilities:
- Builds `cramfs.o` when `CONFIG_CRAMFS` is enabled.
- Composes it from `inode.o` and `uncompress.o`.

Dependencies:
- `inode.o` contains VFS/mount/read logic.
- `uncompress.o` wraps zlib inflate support.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/cramfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/cramfs/inode.c -->
# File Research: sources/os/linux/linux-stable/fs/cramfs/inode.c

This file implements the CramFs readonly filesystem VFS integration, mount paths, inode construction, block reading, directory lookup, folio reads, decompression, and direct MTD mapping support.

Key responsibilities:
- Defines in-memory superblock state `struct cramfs_sb_info`.
- Creates VFS inodes from on-disk `struct cramfs_inode`.
- Reads CramFs image data from either block devices or linearly mapped MTD memory.
- Supports optional direct physical-memory mmap for suitable uncompressed MTD-backed files.
- Parses and validates the CramFs superblock.
- Implements directory iteration, lookup, page-cache folio filling, statfs, mount, remount, and kill-super behavior.

Important control flow:
- Inode creation:
  - `cramino()` derives stable inode numbers from data offsets when possible.
  - `get_cramfs_inode()` assigns file operations by file type, sets uid/gid/mode, size, blocks, and zero timestamps.
- Image reads:
  - `cramfs_blkdev_read()` maintains a two-entry static read buffer cache over groups of pages.
  - `cramfs_direct_read()` returns pointers into linearly mapped memory, or zero page for out-of-range.
  - `cramfs_read()` selects direct MTD or block-device path.
- Direct mapping:
  - `cramfs_get_block_range()` verifies a run of direct, uncompressed, contiguous blocks.
  - `cramfs_physmem_mmap()` attempts full or partial PFN insertion for mapped MTD images, falling back to normal paging when unsuitable.
- Mount:
  - `cramfs_read_super()` reads magic at offset 0 or 512, validates endianness, flags, root mode, root offset, and fsid data.
  - `cramfs_blkdev_fill_super()` allocates super info and invalidates static read buffers.
  - `cramfs_mtd_fill_super()` maps one page, reads size, then remaps the whole image.
  - `cramfs_finalize_super()` creates the root inode/dentry and marks readonly.
- File reads:
  - `cramfs_read_folio()` resolves block pointer format, supports direct/uncompressed blocks, compressed blocks with optional two-byte length, holes, previous direct pointer edge cases, decompression, and zero-fill tail.
- Directory operations:
  - `cramfs_readdir()` emits padded directory entries.
  - `cramfs_lookup()` scans entries, optionally using sorted-directory early exit.

Dependencies:
- Uses zlib wrapper `cramfs_uncompress_block()` from `uncompress.c`.
- Uses CramFs on-disk definitions from `<uapi/linux/cramfs_fs.h>`.
- Uses MTD helpers when configured and block-device helpers when configured.

Risks and invariants:
- Global `read_mutex` protects static read buffers and serialized decompression/read parsing.
- The block-device cache is static and shared, so buffer invalidation on mount matters.
- Filesystem is always mounted readonly.
- CramFs has intentionally limited metadata fidelity: no real timestamps and weak directory nlink precision.
- Direct mmap is possible only for direct, uncompressed, contiguous, page-aligned physical data and avoids mapping a shared dirty tail page.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/cramfs/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/cramfs/internal.h -->
# File Research: sources/os/linux/linux-stable/fs/cramfs/internal.h

This header declares the CramFs zlib wrapper interface.

Key responsibilities:
- Declares `cramfs_uncompress_block()`.
- Declares `cramfs_uncompress_init()`.
- Declares `cramfs_uncompress_exit()`.

Dependencies:
- Implemented by `uncompress.c`.
- Used by `inode.c`.

Risks and invariants:
- The interface exposes a module-global decompression stream lifecycle.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/cramfs/internal.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/cramfs/uncompress.c -->
# File Research: sources/os/linux/linux-stable/fs/cramfs/uncompress.c

This file wraps zlib inflate for CramFs block decompression.

Key responsibilities:
- Maintains a single static `z_stream`.
- Initializes and frees zlib workspace.
- Decompresses one compressed CramFs block into a destination buffer.

Important control flow:
- `cramfs_uncompress_init()` allocates the zlib workspace on the first user and increments `initialized`.
- `cramfs_uncompress_block()` resets the stream, inflates with `Z_FINISH`, and returns decompressed byte count.
- If reset fails, it reinitializes the stream.
- `cramfs_uncompress_exit()` decrements `initialized` and frees workspace when it reaches zero.

Dependencies:
- Uses Linux zlib inflate APIs.
- Called under the CramFs read mutex in `inode.c`.

Risks and invariants:
- Decompression is explicitly single-threaded due to the shared stream.
- Inflate failures are logged and returned as `-EIO`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/cramfs/uncompress.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/crypto/Kconfig -->
# File Research: sources/os/linux/linux-stable/fs/crypto/Kconfig

This file declares fscrypt build options.

Key responsibilities:
- Defines `CONFIG_FS_ENCRYPTION` for per-file filesystem encryption.
- Selects crypto primitives and key support needed by fscrypt core.
- Defines `CONFIG_FS_ENCRYPTION_ALGS`, a tristate option filesystems select to pull default encryption algorithms.
- Defines `CONFIG_FS_ENCRYPTION_INLINE_CRYPT` for inline encryption hardware support.

Dependencies:
- Filesystems such as ext4, f2fs, ubifs, and cephfs use this feature.
- Inline crypt depends on `FS_ENCRYPTION && BLK_INLINE_ENCRYPTION`.

Risks and invariants:
- `FS_ENCRYPTION_ALGS` intentionally pulls generic implementations only; optimized arch implementations remain separate.
- Non-default modes such as Adiantum may require explicit crypto API configuration.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/crypto/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/crypto/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/crypto/Makefile

This file defines fscrypt build composition.

Key responsibilities:
- Builds `fscrypto.o` when `CONFIG_FS_ENCRYPTION` is enabled.
- Core objects: `crypto.o`, `fname.o`, `hkdf.o`, `hooks.o`, `keyring.o`, `keysetup.o`, `keysetup_v1.o`, and `policy.o`.
- Adds `bio.o` when block support is enabled.
- Adds `inline_crypt.o` when inline encryption is enabled.

Dependencies:
- This group covers only a subset: `bio.c`, `crypto.c`, and `fname.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/crypto/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/crypto/bio.c -->
# File Research: sources/os/linux/linux-stable/fs/crypto/bio.c

This file implements block-device-oriented fscrypt helpers for bio decryption and encrypted zeroout.

Key responsibilities:
- Provides `fscrypt_decrypt_bio()` for decrypting completed read bios into page-cache folios.
- Provides `fscrypt_zeroout_range()` for writing ciphertext that decrypts to zeroes over a contiguous encrypted file range.
- Provides an inline-crypto zeroout path when the inode uses block inline encryption.

Important control flow:
- `fscrypt_decrypt_bio()` iterates all folios in a bio and calls `fscrypt_decrypt_pagecache_blocks()` for each segment.
- `fscrypt_zeroout_range_inline_crypt()` builds write bios over `ZERO_PAGE(0)`, attaches fscrypt bio crypto context, submits with blk crypto, and waits for all completions.
- Non-inline `fscrypt_zeroout_range()`:
  - Computes data-unit size and indices.
  - Allocates up to 16 bounce pages, with the first allocation allowed to block via mempool-backed fscrypt allocation.
  - Encrypts zero pages per data unit into bounce pages.
  - Submits synchronous write bios and reuses the bio until the range is complete.
  - Frees bounce pages and bio on exit.

Dependencies:
- Uses core fscrypt helpers from `crypto.c`.
- Uses inline crypto helpers from other fscrypt files when configured.
- Assumes a single block device through `inode->i_sb->s_bdev`.

Risks and invariants:
- `len` must be nonzero and aligned to data-unit size/file logical block expectations.
- The physical blocks must be contiguous.
- Each data unit uses a different IV, so zeroout must encrypt per data unit instead of writing reusable ciphertext.
- Bio status is converted to errno/blk_status in the appropriate direction.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/crypto/bio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/crypto/crypto.c -->
# File Research: sources/os/linux/linux-stable/fs/crypto/crypto.c

This file implements core fscrypt content encryption/decryption operations, IV generation, bounce-page allocation, initialization, and logging.

Key responsibilities:
- Maintains the fscrypt read-decryption workqueue.
- Maintains a mempool-backed bounce-page pool for ciphertext pages.
- Provides IV generation for supported fscrypt policy flags.
- Encrypts/decrypts single data units using the kernel skcipher API.
- Encrypts page-cache folio blocks into bounce pages for writeback.
- Decrypts page-cache folio blocks after reads.
- Provides in-place encrypt/decrypt helpers for arbitrary filesystem blocks.
- Initializes fscrypt global caches and keyring support.

Important control flow:
- `fscrypt_generate_iv()` zeroes the IV and then applies policy-specific construction:
  - `IV_INO_LBLK_64` combines inode number and logical index.
  - `IV_INO_LBLK_32` uses hashed inode plus index.
  - `DIRECT_KEY` copies file nonce.
  - Always stores final index little-endian in `iv->index`.
- `fscrypt_crypt_data_unit()` builds one-entry scatterlists for source/destination pages and invokes encrypt or decrypt.
- `fscrypt_encrypt_pagecache_blocks()` validates locked non-large folio and alignment, allocates a bounce page, encrypts each data unit, and stores the source folio in page private metadata.
- `fscrypt_decrypt_pagecache_blocks()` validates locked folio and alignment, then decrypts each data unit in place.
- `fscrypt_initialize()` lazily creates the bounce-page pool only for filesystems that need bounce pages.
- `fscrypt_init()` creates a high-priority unbound read workqueue, an inode-info cache, and fscrypt keyring state.

Dependencies:
- Depends on `fscrypt_private.h`, crypto skcipher API, mempool, and keyring initialization from another fscrypt file.
- Exported helpers are consumed by filesystem writeback/read paths and `bio.c`.

Risks and invariants:
- Data-unit length must be positive and aligned to `FSCRYPT_CONTENTS_ALIGNMENT`.
- Page-cache encryption assumes locked, non-large folios.
- Bounce page allocation requires filesystems to advertise `needs_bounce_pages`.
- In-place block helpers reject filesystems that support sub-block data units.
- Initialization uses acquire/release ordering around the global bounce-page pool pointer.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/crypto/crypto.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/crypto/fname.c -->
# File Research: sources/os/linux/linux-stable/fs/crypto/fname.c

This file implements fscrypt filename encryption, decryption, no-key name encoding/decoding, encrypted filename sizing, name matching, SipHash directory hashing, and encrypted dentry revalidation.

Key responsibilities:
- Encrypts plaintext filenames into on-disk encrypted names.
- Decrypts encrypted disk names into user-presentable plaintext when keys are available.
- Encodes no-key names using base64url plus optional SHA-256 abbreviation when keys are unavailable.
- Decodes no-key lookup names back into enough information to find directory entries.
- Matches lookup names against directory entries, including abbreviated long no-key names.
- Provides keyed SipHash for casefolded/encrypted directory hashing.
- Revalidates no-key dentries after encryption keys may have appeared.

Important control flow:
- `fscrypt_fname_encrypt()` pads plaintext to the encrypted length, generates IV index 0, and encrypts in place.
- `fname_decrypt()` decrypts into caller buffer and trims trailing NUL padding with `strnlen()`.
- `__fscrypt_fname_encrypted_size()` enforces minimum 16-byte message length and policy-selected padding.
- `fscrypt_fname_disk_to_usr()`:
  - Passes through `.` and `..`.
  - Rejects too-short encrypted names.
  - Decrypts if the key is present.
  - Otherwise builds `struct fscrypt_nokey_name` with dirhashes, up to 149 ciphertext bytes, and SHA-256 of the remainder if needed, then base64url encodes it.
- `fscrypt_setup_filename()`:
  - Leaves unencrypted or dot names unchanged.
  - Loads encryption info.
  - If key is present, encrypts user plaintext into `fname->disk_name`.
  - If key is absent and lookup is allowed, decodes a no-key name and either sets the full disk name or stores hash/abbreviation data.
  - If key is absent for create-style operations, returns `-ENOKEY`.
- `fscrypt_match_name()` compares direct disk names or verifies abbreviated long no-key names with SHA-256.
- `fscrypt_d_revalidate()` invalidates no-key dentries once the directory key becomes available.

Dependencies:
- Uses IV generation from `crypto.c`.
- Uses key setup/encryption-info helpers from other fscrypt files.
- Uses SHA-256, base64url, SipHash, and skcipher APIs.

Risks and invariants:
- Encrypted filenames shorter than 16 bytes are invalid on disk.
- No-key names are designed to avoid illegal filename characters and stay within `NAME_MAX`.
- SHA-256 is only used for long ciphertext names that cannot fit in full no-key form.
- `DCACHE_NOKEY_NAME` dentries are valid only while the encryption key remains unavailable.
- Callers must release allocations with `fscrypt_free_filename()` or related cleanup paths outside this file.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/crypto/fname.c -->