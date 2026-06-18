# subset-b-005673 Research

Grouped research for the requested HFS+, hostfs, and HPFS source files. Each section preserves the original source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfsplus/wrapper.c -->
# sources/distributed-fs/ceph-client/fs/hfsplus/wrapper.c

Purpose: this file finds and reads the real HFS+ volume header, including HFS wrappers, partition maps, and multisession CD media. It also provides `hfsplus_submit_bio()`, the low-level block I/O helper used by HFS+ code that needs sector-granular reads or writes against the mounted block device.

Important APIs and types: `struct hfsplus_wd` holds wrapper-derived allocation block size/start and embedded extent information. `hfsplus_submit_bio()` aligns the requested HFS+ sector to `hfsplus_min_io_size(sb)`, returns the in-buffer offset for reads, and delegates to `bdev_rw_virt()`. `hfsplus_read_wrapper()` initializes `HFSPLUS_SB(sb)` fields such as `min_io_size`, `s_vhdr`, `s_backup_vhdr`, `alloc_blksz`, `blockoffset`, `part_start`, `sect_count`, and `fs_shift`.

Control flow: mount setup starts with `sb_min_blocksize()`, asks `hfsplus_get_last_session()` for the partition/session window, allocates volume-header buffers, then repeatedly reads sector 2 relative to the current partition. If the signature is HFS+ or HFSX it proceeds; if it is an HFS wrapper it parses `HFSP_WRAPOFF_*` fields and jumps back with an adjusted embedded start/count; otherwise it calls `hfs_part_find()` and retries. It then reads the secondary volume header at `part_start + part_size - 2`, checks matching signatures, validates the allocation block size, and sets the final VFS block size with alignment against the partition offset.

State and persistence: this code mutates only superblock in-memory mount state and allocates buffers that later represent on-disk headers. Persistent writes are not performed here, but incorrect offsets would make all later metadata I/O target the wrong sectors.

Dependencies and integration: it depends on block-device helpers, CD-ROM TOC/multisession APIs, `hfsplus_fs.h`, `hfsplus_raw.h`, and partition-map discovery. `hfsplus_read_wrapper()` is an early mount prerequisite for the rest of HFS+ metadata parsing.

Risks: the reread loop depends on valid wrapper/partition metadata and has multiple `-EINVAL` exits for malformed media. The block-size power-of-two check is essential because `hfsplus_submit_bio()` uses bit masking for alignment. The function frees buffers on failure but leaves successful ownership to later superblock teardown.

Test signals: mount images with plain HFS+, HFSX, HFS-wrapped HFS+, partition-map-contained volumes, invalid secondary headers, non-power-of-two block sizes, and multisession CD options. I/O tests should include block devices whose logical block size exceeds `HFSPLUS_SECTOR_SIZE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfsplus/wrapper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfsplus/xattr.c -->
# sources/distributed-fs/ceph-client/fs/hfsplus/xattr.c

Purpose: this is the main HFS+ extended-attribute implementation. It wires xattr handlers, lazily creates the attributes B-tree, maps Linux namespaces to HFS+ attribute names, handles the special Finder Info pseudo-xattr stored in catalog records, and implements set/get/list/remove operations for inline attribute records.

Important APIs and functions: `hfsplus_xattr_handlers[]` exposes OS X, user, trusted, and security handlers. `__hfsplus_setxattr()` and `__hfsplus_getxattr()` operate on fully prefixed names. `hfsplus_setxattr()` and `hfsplus_getxattr()` prepend namespace prefixes for handler callers. `hfsplus_listxattr()` walks the attribute B-tree. `hfsplus_removexattr()` deletes attribute records and updates catalog flags. `hfsplus_create_attributes_file()` creates and opens the HFS+ attributes file/tree when the first non-Finder xattr is written.

Control flow: setting first rejects resource-fork inodes, treats `NULL` values as remove requests, opens a catalog find context, and handles `HFSPLUS_XATTR_FINDER_INFO_NAME` by editing folder/file Finder info directly in the catalog. Other names require a valid attributes tree; if missing, creation is attempted through an atomic `attr_tree_state` transition. Existing attributes are replaced unless `XATTR_CREATE` was requested; absent attributes are created unless `XATTR_REPLACE` was requested. Catalog flags `HFSPLUS_XATTR_EXISTS` and, for ACL names, `HFSPLUS_ACL_EXISTS` are then set. Getting mirrors this: Finder Info comes from catalog fields, while real attributes are found in the attr B-tree and only inline data records are supported. Listing includes Finder Info only if nonzero bits exist, then iterates all attr keys for the inode until the CNID changes.

State and persistence: the file mutates the attributes file contents, B-tree nodes, catalog record flags, inode ctime, and dirty flags on catalog/attribute tree inodes. Attribute-tree creation initializes header and map nodes, extends the attributes file, marks it dirty, and transitions `attr_tree_state` between empty/creating/valid/failed.

Dependencies and integration: it relies on HFS+ catalog and attribute helpers (`hfs_find_init`, `hfsplus_find_cat`, `hfsplus_attr_exists`, `hfsplus_create_attr`, `hfsplus_replace_attr`, `hfsplus_delete_attr`), bnode record accessors, NLS conversion, Linux xattr namespaces, and capability checks for trusted listing.

Risks: fork-data and extents xattr records return `-EOPNOTSUPP`, so large or non-inline HFS+ attributes are not usable. Name buffers are sized by `NLS_MAX_CHARSET_SIZE * HFSPLUS_ATTR_MAX_STRLEN + 1`; callers must keep names within HFS+ limits. Attribute-tree creation uses atomic state but comments admit `-EAGAIN` is possible if locking assumptions change. Catalog flag updates can become stale if attr deletion partially fails.

Test signals: exercise create/replace/remove/list with all namespaces, Finder Info exact-size validation for files and folders, ACL flag setting/clearing, trusted listing with and without `CAP_SYS_ADMIN`, absent attr trees, first-xattr attr-tree creation, ENOSPC during creation, inline size limits, unsupported fork/extents records, and resource-fork xattr rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfsplus/xattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfsplus/xattr.h -->
# sources/distributed-fs/ceph-client/fs/hfsplus/xattr.h

Purpose: this header is the HFS+ xattr subsystem contract. It declares the namespace-specific xattr handlers and the helper functions used by HFS+ inode/security code to set, get, list, and initialize extended attributes.

Important APIs and types: the file includes `<linux/xattr.h>` and declares `hfsplus_xattr_osx_handler`, `hfsplus_xattr_user_handler`, `hfsplus_xattr_trusted_handler`, `hfsplus_xattr_security_handler`, plus the sentinel-terminated `hfsplus_xattr_handlers[]` table consumed by superblock inode operations. The function declarations distinguish fully formed names (`__hfsplus_setxattr()`, `__hfsplus_getxattr()`) from namespace-wrapper calls (`hfsplus_setxattr()`, `hfsplus_getxattr()`) that take `prefix` and `prefixlen`.

Control flow role: there is no runtime control flow in this header, but it defines the layering used by the `.c` files. Namespace handlers in `xattr_user.c`, `xattr_trusted.c`, and `xattr_security.c` pass suffix names plus Linux namespace prefixes into `hfsplus_setxattr()`/`hfsplus_getxattr()`. Security initialization calls `hfsplus_init_security()`, which eventually uses the fully qualified setter.

State and persistence behavior: all persistence is delegated to the implementation. The declarations imply that callers provide an inode and name/value buffers; implementation code persists values into the HFS+ attributes B-tree or catalog fields and marks metadata dirty.

Dependencies and integration: consumers include HFS+ superblock setup, inode creation paths that need security labels, and VFS xattr dispatch. The header also couples handler modules to constants from `hfsplus_fs.h` and Linux namespace prefixes used by the implementation.

Risks: the split API means callers must choose the correct function. Passing an already prefixed name to the prefixing wrappers can duplicate prefixes, while passing an unprefixed name to the internal helpers can create OS X-style unnamespaced attributes. The header exposes no validation helpers, so name bounds and namespace checks are enforced only in `xattr.c`.

Test signals: build tests should verify all handler objects are defined exactly once and that superblock xattr handler registration links. Behavioral tests should cover both wrapper and internal paths, especially security initialization where names are constructed before calling `__hfsplus_setxattr()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfsplus/xattr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfsplus/xattr_security.c -->
# sources/distributed-fs/ceph-client/fs/hfsplus/xattr_security.c

Purpose: this file implements the `security.*` xattr handler for HFS+ and the LSM initialization hook used when new inodes are created.

Important APIs and functions: `hfsplus_security_getxattr()` and `hfsplus_security_setxattr()` pass `XATTR_SECURITY_PREFIX` and `XATTR_SECURITY_PREFIX_LEN` into the common HFS+ xattr helpers. `hfsplus_initxattrs()` iterates the `struct xattr` array produced by LSMs, constructs full `security.<name>` strings, and writes them with `__hfsplus_setxattr()`. `hfsplus_init_security()` calls `security_inode_init_security()` with that callback. `hfsplus_xattr_security_handler` exposes the VFS handler.

Control flow: normal VFS get/set calls enter the handler and delegate directly to `hfsplus_getxattr()` or `hfsplus_setxattr()`. During inode creation, LSM code calls the init callback with one or more name/value pairs; empty names are skipped, each valid name is prefixed and written, and the loop stops at first error.

State and persistence: the file itself stores no state. It triggers persistent HFS+ xattr writes through `__hfsplus_setxattr()`, which may create the attributes file and update catalog flags. Security labels therefore become part of the on-disk HFS+ attributes tree.

Dependencies and integration: it depends on Linux security hooks, NLS sizing, HFS+ xattr helpers, and Linux xattr namespace constants. It integrates with inode creation paths through `hfsplus_init_security()` and with VFS xattr dispatch through the exported handler object.

Risks: `xattr_name` uses the same maximum HFS+ attribute string allocation as the common implementation. Very long LSM-generated names must fit that bound once prefixed. Initialization stops on the first failed label, so partial label sets can be created if an earlier write succeeds and a later one fails. The comment header says `xattr_trusted.c` even though the file implements security labels, which is documentation noise rather than behavior.

Test signals: create files under SELinux/Smack-style configurations, verify security labels persist and list/get correctly, inject multiple init labels with one failing write, and test empty-name entries. Mounts where the attributes tree is absent should exercise lazy creation from the security initialization path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfsplus/xattr_security.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfsplus/xattr_trusted.c -->
# sources/distributed-fs/ceph-client/fs/hfsplus/xattr_trusted.c

Purpose: this file provides the HFS+ `trusted.*` xattr namespace handler.

Important APIs and functions: `hfsplus_trusted_getxattr()` delegates reads to `hfsplus_getxattr()` with `XATTR_TRUSTED_PREFIX`. `hfsplus_trusted_setxattr()` delegates writes/removes to `hfsplus_setxattr()` with the same prefix. `hfsplus_xattr_trusted_handler` registers the handler prefix and callbacks for VFS xattr dispatch.

Control flow: VFS dispatch supplies an unprefixed trusted xattr suffix. The handler constructs the full namespace indirectly by passing the suffix and trusted prefix to the common HFS+ wrapper, which allocates a full name, calls the internal HFS+ xattr implementation, and frees the temporary name.

State and persistence: this file has no local state. Successful writes persist into the HFS+ attributes B-tree and cause catalog xattr flags and inode ctime to be updated by the common implementation.

Dependencies and integration: it depends on Linux trusted xattr namespace constants, NLS sizing through included HFS+ headers, and the common HFS+ xattr helpers. Listing permissions for trusted attributes are enforced in `xattr.c` via `can_list()`, not here.

Risks: trusted attributes should only be visible to privileged callers; this file relies on the VFS xattr framework and common listing helper for permission behavior rather than adding checks in each callback. Prefix construction inherits the common fixed-size buffer constraints.

Test signals: set/get/remove `trusted.*` attributes as privileged users, verify unprivileged list behavior through common listing, confirm `XATTR_CREATE`/`XATTR_REPLACE` semantics, and verify that deleting the last trusted xattr clears the catalog `HFSPLUS_XATTR_EXISTS` flag through `hfsplus_removexattr()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfsplus/xattr_trusted.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfsplus/xattr_user.c -->
# sources/distributed-fs/ceph-client/fs/hfsplus/xattr_user.c

Purpose: this file provides the HFS+ `user.*` xattr namespace handler.

Important APIs and functions: `hfsplus_user_getxattr()` and `hfsplus_user_setxattr()` are thin wrappers around `hfsplus_getxattr()` and `hfsplus_setxattr()` with `XATTR_USER_PREFIX`. `hfsplus_xattr_user_handler` registers the prefix and callbacks with the VFS.

Control flow: VFS xattr operations enter this handler with a suffix such as `comment`. The common helper builds `user.comment`, performs HFS+ validation and B-tree/catalog work, and returns the resulting byte count or errno.

State and persistence: local state is absent. Persistent state is the HFS+ attribute record plus catalog flags maintained by `xattr.c`.

Dependencies and integration: it depends on `hfsplus_fs.h`, `xattr.h`, NLS sizing, and Linux xattr namespace constants. It is part of `hfsplus_xattr_handlers[]`, so superblock xattr support must include the common handler table.

Risks: this layer performs no policy checks; mount options or VFS-level user xattr restrictions must be enforced elsewhere if present. Buffer sizing and unsupported non-inline HFS+ attribute formats are inherited from `xattr.c`.

Test signals: set/get/list/remove ordinary `user.*` attributes, test zero-length values, `XATTR_CREATE` and `XATTR_REPLACE`, removal by setting a `NULL` value through VFS, absent attributes returning `-ENODATA`, and behavior on resource-fork inodes returning `-EOPNOTSUPP`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfsplus/xattr_user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hostfs/Makefile -->
# sources/distributed-fs/ceph-client/fs/hostfs/Makefile

Purpose: this Makefile builds UML hostfs support. It defines the kernel-side hostfs object composition and includes the UML-specific build rules needed for user-space syscall wrapper objects.

Important build variables: `hostfs-objs := hostfs_kern.o` builds the main `hostfs.o` module/builtin object from the kernel VFS implementation. `hostfs-builtin-$(CONFIG_HOSTFS) += hostfs_user.o hostfs_user_exp.o` adds the user-space helper and export objects when `CONFIG_HOSTFS` is enabled. `obj-y := $(hostfs-builtin-y) $(hostfs-builtin-m)` ensures those helper objects are built into the UML environment. `obj-$(CONFIG_HOSTFS) += hostfs.o` controls the actual filesystem object.

Control flow: Kbuild evaluates `CONFIG_HOSTFS`, builds the kernel half as `hostfs.o`, builds the helper/export objects when enabled, then includes `$(srctree)/arch/um/scripts/Makefile.rules` so UML can compile mixed kernel/user helper code correctly.

State and persistence: there is no runtime state, but the build layout determines whether hostfs can link its kernel code against exported wrapper symbols.

Dependencies and integration: this file is specific to the UML architecture. It integrates with Kbuild, `CONFIG_HOSTFS`, and `arch/um/scripts/Makefile.rules`. The split mirrors the source split: `hostfs_kern.c` calls APIs declared in `hostfs.h`; `hostfs_user.c` implements them; `hostfs_user_exp.c` exports them.

Risks: omitting `hostfs_user.o` or `hostfs_user_exp.o` would leave unresolved symbols or unavailable wrappers. The `obj-y` assignment for helper objects is unusual compared with ordinary filesystem Makefiles and should not be normalized without understanding UML build rules.

Test signals: build UML with `CONFIG_HOSTFS=y` and as module if supported, check that `hostfs.o` links with all `hostfs_user` symbols, and build with `CONFIG_HOSTFS=n` to ensure no stale helper objects are included unexpectedly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hostfs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hostfs/hostfs.h -->
# sources/distributed-fs/ceph-client/fs/hostfs/hostfs.h

Purpose: this header defines the ABI between the UML kernel-side hostfs implementation and the user-space syscall wrapper layer.

Important APIs and types: `struct hostfs_timespec`, `struct hostfs_iattr`, and `struct hostfs_stat` are wrapper-safe representations of timestamps, setattr input, and stat results. The prototypes cover stat/access/open/dir iteration/read/write/lseek/fsync/dup-close/create/setattr/symlink/unlink/mkdir/rmdir/mknod/link/readlink/rename/statfs. Attribute validity bits such as `HOSTFS_ATTR_MODE` are included through generated UML offsets.

Control flow role: `hostfs_kern.c` never directly calls libc syscalls; it builds host paths and delegates to these prototypes. `hostfs_user.c` implements the calls with host syscalls and converts errors to negative errno. `hostfs_user_exp.c` exports the symbols for GPL use.

State and persistence: the structs carry host metadata into VFS inode state and requested VFS changes back to host syscalls. Persistent effects happen when implementations call host filesystem operations.

Dependencies and integration: it includes `<os.h>` and `<generated/asm-offsets.h>`, marking it as UML-specific rather than generic kernel filesystem code. It is included by both kernel and user helper sources, so field layout changes affect both sides.

Risks: the header forms a narrow ABI; type or semantic drift can break inode identity, setattr, or statfs conversions. `hostfs_stat` includes both `dev/rdev` and birth time, which kernel code uses to distinguish reused inode numbers; dropping those fields would create aliasing hazards.

Test signals: compile both hostfs halves after struct changes, verify stat data maps correctly for regular files, symlinks, special files, and filesystems with/without birth time, and test setattr bits individually to ensure generated `HOSTFS_ATTR_*` constants match user wrapper behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hostfs/hostfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hostfs/hostfs_kern.c -->
# sources/distributed-fs/ceph-client/fs/hostfs/hostfs_kern.c

Purpose: this is the kernel-side UML host filesystem. It presents a VFS filesystem whose backing store is a host directory tree and delegates host operations through the wrapper API in `hostfs.h`.

Important APIs and types: `struct hostfs_fs_info` stores the mounted host root path. `struct hostfs_inode_info` extends VFS inodes with a shared host fd, open mode bits, open mutex, host device, and birth time. File, directory, inode, address-space, superblock, fs-context, and filesystem-type operation tables wire hostfs into VFS.

Control flow: mount option parsing builds `host_root_path` from the global `root_ino` plus per-mount suffix. `hostfs_fill_super()` sets anonymous superblock properties, stats/loads the root inode, resolves root symlinks, and installs `s_root`. Lookup and creation convert dentries to host paths using `dentry_path_raw()` plus the configured root prefix. `hostfs_iget()` stats a path and uses `iget5_locked()` with inode-number/device/type/btime matching to avoid stale aliasing. Open accumulates read/write capability in one shared fd per inode, using `replace_file()` when a wider mode is needed. Page-cache reads and writes call `read_file()`/`write_file()` against that fd. Directory iteration opens the host directory each time and emits `readdir()` results.

State and persistence: hostfs keeps no independent on-disk state. VFS inode metadata mirrors host stat results and persistent changes are host syscalls: create, unlink, mkdir, rmdir, mknod, link, symlink, rename, chmod/chown/truncate/times, data writes, and fsync. `append` mode globally prevents unlink and size truncation and opens files with `O_APPEND`.

Dependencies and integration: it depends on UML setup hooks, `hostfs_user.c` wrappers, Linux VFS/page-cache/fs_context APIs, and `HOSTFS_SUPER_MAGIC`. It is registered as `hostfs` with `MODULE_ALIAS_FS`.

Risks: path confinement is string-prefix based: constructed paths prepend `host_root_path`, so correctness depends on VFS path resolution and no unexpected escape through host symlinks except the explicit root symlink follow. A single fd per inode can be widened across opens; mutex coverage is limited to mode/fd replacement. Writeback assumes valid open fds. `hostfs_permission()` combines host `access()` with generic permission, which can diverge from the UML user namespace model.

Test signals: mount with empty and non-empty roots, root symlink backing paths, append mode, concurrent read/write opens, writeback and fsync, rename with `RENAME_NOREPLACE`/`RENAME_EXCHANGE`, special files, statfs, permission checks, inode reuse on host filesystems, and page-cache truncation via setattr.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hostfs/hostfs_kern.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hostfs/hostfs_user.c -->
# sources/distributed-fs/ceph-client/fs/hostfs/hostfs_user.c

Purpose: this file is the UML user-space syscall wrapper implementation behind hostfs. It converts host libc/syscall results into the negative errno interface used by `hostfs_kern.c`.

Important APIs and functions: `stat_file()` uses `statx()` with `AT_SYMLINK_NOFOLLOW` and optional `AT_EMPTY_PATH`, then `statx_to_hostfs()` fills `struct hostfs_stat`. File operations wrap `open64`, `pread64`, `pwrite64`, `lseek64`, `fsync`/`fdatasync`, `dup2`, and `close`. Directory operations wrap `opendir`, `seekdir`, `readdir`, and `closedir`. Metadata and namespace functions wrap `chmod/fchmod`, `chown/fchown`, `truncate/ftruncate`, `utimes/futimes`, `symlink`, `unlink`, `mkdir`, `rmdir`, `mknod`, `link`, `readlink`, `rename`, `renameat2`, and `statfs64`.

Control flow: each wrapper performs a host syscall, returns `-errno` on failure, and otherwise normalizes return values for kernel-side callers. `set_attr()` applies mode, ownership, size, and time changes in ordered blocks. For explicit atime/mtime setting, it stats current times first, modifies only requested fields, then calls `futimes()` or `utimes()`.

State and persistence: all persistent state lives in the host filesystem. This file performs direct host mutations for hostfs VFS operations. It also advances read/write offsets passed by pointer after successful pread/pwrite.

Dependencies and integration: it depends on libc/POSIX headers, UML `os_makedev()`, and `hostfs.h` struct definitions. `rename2_file()` conditionally defines syscall numbers for x86 and falls back to `-EINVAL` when unsupported or unavailable.

Risks: `open_file()` panics on impossible mode combinations, relying on kernel-side callers to pass valid read/write booleans. `set_attr()` comments that ctime is not handled; caller-visible ctime comes from later stat refreshes. The time-setting block reads `attrs->ia_atime` and `ia_mtime` only when corresponding `*_SET` bits are present. `rename2_file()` portability depends on syscall number availability.

Test signals: wrapper-level tests should cover negative errno mapping, symlink stat behavior, birth-time fallback when `STATX_BTIME` is absent, partial reads/writes, append-mode open effects, individual setattr fields, `renameat2` unsupported kernels, special-device creation, and statfs field conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hostfs/hostfs_user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hostfs/hostfs_user_exp.c -->
# sources/distributed-fs/ceph-client/fs/hostfs/hostfs_user_exp.c

Purpose: this file exports the hostfs user-wrapper symbols for GPL kernel use in the UML build.

Important APIs: it includes `<linux/module.h>` and `hostfs.h`, then calls `EXPORT_SYMBOL_GPL()` for every wrapper implemented by `hostfs_user.c`: stat/access/open/dir iteration/read/write/lseek/fsync/replace/close/create/setattr/symlink/unlink/mkdir/rmdir/mknod/link/readlink/rename/rename2/statfs.

Control flow: there is no runtime logic beyond module symbol registration. The export table must match both the declarations in `hostfs.h` and the implementations in `hostfs_user.c`.

State and persistence: no state is held or changed here. Its effect is link-time/runtime symbol availability for the kernel-side hostfs object.

Dependencies and integration: this file is tied to the UML hostfs Makefile, which builds `hostfs_user_exp.o` together with `hostfs_user.o` when `CONFIG_HOSTFS` is enabled. `hostfs_kern.c` depends on these exported symbols resolving.

Risks: missing an export causes link or module-load failures; exporting a stale name causes compile failure if prototypes change. Over-exporting would expand the callable surface for GPL modules, so the list should stay limited to the hostfs wrapper ABI.

Test signals: build hostfs after adding/removing wrapper prototypes, check module symbol resolution, and run `modpost`/Kbuild diagnostics for missing or unused exports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hostfs/hostfs_user_exp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hpfs/Kconfig -->
# sources/distributed-fs/ceph-client/fs/hpfs/Kconfig

Purpose: this Kconfig entry exposes Linux HPFS filesystem support as `CONFIG_HPFS_FS`.

Important settings: `config HPFS_FS` is a tristate named "OS/2 HPFS file system support". It depends on `BLOCK` and selects `BUFFER_HEAD` and `FS_IOMAP`, matching the implementation’s reliance on block devices, buffer-head mapping, mpage helpers, and iomap fiemap.

Control flow: kernel configuration determines whether HPFS is unavailable, built-in, or a module named `hpfs`. The help text explains that HPFS is used by OS/2/Warp hard disk partitions and points to `Documentation/filesystems/hpfs.rst`.

State and persistence: no runtime state is defined here, but enabling write support through the filesystem driver exposes persistent HPFS mutation paths in the implementation.

Dependencies and integration: the `Makefile` consumes `CONFIG_HPFS_FS` to build `hpfs.o`. `select FS_IOMAP` is required by `file.c` fiemap code, while `select BUFFER_HEAD` is required by almost every HPFS metadata mapper.

Risks: dependency changes can silently break build coverage. Removing `BLOCK` would be invalid because HPFS maps physical sectors. Dropping selected helpers would cause compile failures or missing feature paths.

Test signals: configure `n`, `m`, and `y`; build all three; verify the module name is `hpfs`; and run configuration dependency checks for architectures where block or buffer-head support may be optional.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hpfs/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hpfs/Makefile -->
# sources/distributed-fs/ceph-client/fs/hpfs/Makefile

Purpose: this Makefile defines the HPFS object composition for Kbuild.

Important build variables: `obj-$(CONFIG_HPFS_FS) += hpfs.o` builds the filesystem object when configured. `hpfs-objs` aggregates implementation files: allocation, anode allocation tree, buffer mapping, dentry operations, directory VFS operations, dnode tree handling, extended attributes, file I/O, inode operations, metadata mapping, name handling, namei mutations, and superblock support.

Control flow: when `CONFIG_HPFS_FS` is enabled, Kbuild compiles each listed object and links them into `hpfs.o`, which is then built-in or modular based on the tristate value.

State and persistence: no runtime state exists in the Makefile, but object inclusion controls which persistent metadata paths are present in the driver. Omitting any listed object would leave unresolved cross-file calls declared in `hpfs_fn.h`.

Dependencies and integration: it pairs with `Kconfig` and the central HPFS private header. The object order is conventional and does not encode runtime ordering, but it documents subsystem boundaries.

Risks: adding a new exported helper to `hpfs_fn.h` requires updating this list if implemented in a new source file. Accidentally removing `super.o` would break mount registration even though it is not part of this work item.

Test signals: build HPFS as built-in and module; verify all objects link; run `nm` or modpost checks after file additions/removals; and ensure no object relies on being linked only in one configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hpfs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hpfs/alloc.c -->
# sources/distributed-fs/ceph-client/fs/hpfs/alloc.c

Purpose: this file manages HPFS free-space allocation, directory-band allocation, object initialization for dnodes/fnodes/anodes, and block discard trimming.

Important APIs and functions: `hpfs_alloc_sector()`, `hpfs_alloc_if_possible()`, and `hpfs_free_sectors()` manipulate main free-space bitmaps. `hpfs_alloc_dnode()`, `hpfs_alloc_fnode()`, and `hpfs_alloc_anode()` allocate and initialize core metadata objects. `hpfs_check_free_dnodes()` reserves safety for dnode splits/deletes. `hpfs_trim_fs()` scans free runs and issues discard. Internal `hpfs_claim_*` helpers maintain cached free counts unless corruption is detected.

Control flow: allocation searches near the requested sector, then outward across bitmap bands, using `alloc_in_bmp()` to find aligned free bit runs and clear bits. It adapts forward preallocation with `sb_max_fwd_alloc`. Dnodes prefer the directory band when enough free dnodes remain, otherwise they fall back to general sectors. Freeing sets bitmap bits back to free, crossing bitmap boundaries as needed. Trim separately scans the directory-band bitmap and main bitmaps, under `hpfs_lock()`, and calls `sb_issue_discard()` for free runs meeting limits.

State and persistence: bitmap bits are persistent metadata; dirtying quad buffers commits allocation/free state. Superblock cached counts `sb_n_free`, `sb_n_free_dnodes`, `sb_c_bitmap`, and `sb_max_fwd_alloc` are updated in memory. Newly allocated metadata sectors are zeroed and initialized with magic values and default headers.

Dependencies and integration: it depends on `map.c` bitmap mappers, `buffer.c` quad-buffer dirtying, `hpfs_error()`, and structure definitions from `hpfs.h`. File growth, directory mutation, EA growth, and object creation all call into this allocator.

Risks: HPFS uses inverted bitmap semantics where `1` means free and `0` means allocated. Corruption checks are optional through `sb_chk`; without them, invalid bitmap state can propagate. Dnode operations rely on `hpfs_check_free_dnodes()` to avoid mid-split ENOSPC corruption. Preallocation failure after main allocation logs an error and may leave earlier sectors allocated.

Test signals: allocate/free single sectors and four-sector dnodes, stress bitmap-boundary crossing, directory-band exhaustion, ENOSPC during dnode split, free-count underflow/overflow detection, trim ranges overlapping the directory band, readonly trim rejection, and fatal signal interruption during discard.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hpfs/alloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hpfs/anode.c -->
# sources/distributed-fs/ceph-client/fs/hpfs/anode.c

Purpose: this file implements HPFS allocation B+ trees stored in fnodes and anodes. These trees map file-relative sectors or EA-relative sectors to disk sectors and support extension, truncation, and removal.

Important APIs and functions: `hpfs_bplus_lookup()` maps a logical sector through internal and leaf nodes. `hpfs_add_sector_to_btree()` extends an allocation tree and splits full nodes. `hpfs_remove_btree()` frees every data extent and anode in a tree. `hpfs_ea_read()`, `hpfs_ea_write()`, and `hpfs_ea_remove()` reuse the same mapping logic for external EA storage. `hpfs_truncate_btree()` releases sectors beyond a new length. `hpfs_remove_fnode()` removes file/directory content, EAs, and the fnode itself.

Control flow: lookup descends internal nodes by comparing `file_secno`, then scans leaf extents for the requested sector, optionally caching the found run in `hpfs_inode_info`. Adding first tries to extend the last physical extent contiguously; otherwise it allocates a sector, inserts a new leaf entry, and recursively splits/promotes anodes if no free entries remain. Removal and truncation are iterative to avoid stack overflow and use up pointers to walk back up the tree.

State and persistence: this code mutates B+ tree headers, extent arrays, anode parent pointers, fnode root trees, and bitmap allocation state. Buffers are marked dirty after structural changes. Removing fnodes also frees directory dtrees or file data trees and indirect EAs.

Dependencies and integration: it depends on `alloc.c` for sectors/anodes, `map.c` for fnodes/anodes, `buffer.c`, and corruption-cycle detection through `hpfs_stop_cycles()`. `file.c`, `ea.c`, `inode.c`, and `namei.c` call these helpers for data and metadata lifecycle.

Risks: tree splitting is intricate and must keep `first_free`, used/free counts, `BP_internal`, `BP_fnode_parent`, and `up` pointers consistent. Several failure exits after partial allocation rely on freeing temporary sectors/anodes correctly. Truncation intentionally does not join anodes, which can leave sparse tree shape but should remain valid.

Test signals: grow files through contiguous and fragmented extents, force fnode-to-anode and anode-to-root splits, lookup after splits, truncate to zero and middle of extents, remove fragmented files, remove directories through `hpfs_remove_fnode()`, test EA reads/writes through direct and anode-backed storage, and run with strict checks to catch cycle/up-pointer errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hpfs/anode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hpfs/buffer.c -->
# sources/distributed-fs/ceph-client/fs/hpfs/buffer.c

Purpose: this file centralizes HPFS sector mapping, read-ahead, hotfix remapping, and four-sector dnode buffer handling.

Important APIs and functions: `hpfs_search_hotfix_map()` maps a bad original sector to its spare replacement. `hpfs_search_hotfix_map_for_range()` clips contiguous ranges before a hotfix. `hpfs_prefetch_sectors()` performs safe read-ahead. `hpfs_map_sector()` and `hpfs_get_sector()` read or allocate single-sector buffers. `hpfs_map_4sectors()` and `hpfs_get_4sectors()` produce a contiguous 2048-byte view over four sectors. `hpfs_brelse4()` and `hpfs_mark_4buffers_dirty()` release/dirty quad buffers.

Control flow: single-sector mapping asserts the global HPFS lock, optionally prefetches, maps through the hotfix table, and reads or gets a buffer. Quad mapping maps four aligned sectors; if their `b_data` pointers are contiguous it returns the first buffer directly, otherwise it allocates a 2048-byte bounce buffer and copies data in/out on dirtying.

State and persistence: read paths populate buffer cache. Write paths mark buffer heads dirty, and for non-contiguous quad buffers copy the synthetic view back to the four underlying sectors before dirtying. Hotfix tables are read-only in-memory mount state loaded elsewhere.

Dependencies and integration: every HPFS metadata mapper uses these functions. Dnodes are exactly four 512-byte sectors, so directory-tree code depends heavily on quad-buffer behavior. File I/O and allocation code also use range clipping to avoid merging across hotfixed sectors.

Risks: all functions require `hpfs_lock()` except prefetch helpers; misuse can trigger lock assertions or races. Quad buffers must always be released with `hpfs_brelse4()` and dirtied with `hpfs_mark_4buffers_dirty()` before release when modified. Hotfix range clipping is necessary for correct contiguous I/O mapping.

Test signals: map/read/write dnodes on devices where four sector buffers are contiguous and non-contiguous, simulate hotfix entries and range clipping, test read errors, verify dirty copy-back from bounce buffers, and run lockdep-style checks for callers missing the HPFS mutex.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hpfs/buffer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hpfs/dentry.c -->
# sources/distributed-fs/ceph-client/fs/hpfs/dentry.c

Purpose: this file implements HPFS dcache name hashing and comparison. It gives the VFS case-insensitive, HPFS-specific filename semantics.

Important APIs and functions: `hpfs_hash_dentry()` adjusts trailing dots/spaces, uppercases through the mounted HPFS code page, and sets the qstr hash. `hpfs_compare_dentry()` validates lookup names with `hpfs_chk_name()` and compares existing and candidate names through `hpfs_compare_names()`. `hpfs_dentry_operations` exports these as `.d_hash` and `.d_compare`.

Control flow: hash generation preserves `.` and `..` special cases but otherwise trims OS/2-cleared suffix characters before hashing. Comparison trims the existing dentry string, validates the incoming name, and returns mismatch on invalid or non-equal names.

State and persistence: no persistent state is changed. The code reads the superblock code-page table and mutates the transient qstr hash.

Dependencies and integration: it depends on `name.c` for adjustment, validation, upcase, and comparison. Superblock setup installs these dentry operations so lookups match HPFS on-disk ordering and case behavior.

Risks: hashing and comparison must stay aligned; otherwise dentries can be missed or aliased incorrectly. The code intentionally does not reject too-long names during hashing, leaving validation to compare/lookup paths.

Test signals: lookup names differing only by case, trailing dots/spaces, long-name flags, invalid characters, `.`/`..`, and non-ASCII bytes mapped through the HPFS code page table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hpfs/dentry.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hpfs/dir.c -->
# sources/distributed-fs/ceph-client/fs/hpfs/dir.c

Purpose: this file implements HPFS directory VFS operations: release, seek, readdir, lookup, and the directory file-operations table.

Important APIs and functions: `hpfs_readdir()` walks dnode trees and emits directory entries. `hpfs_dir_lseek()` validates HPFS synthetic directory positions. `hpfs_lookup()` maps a child name to a dentry/inode. `hpfs_dir_release()` unregisters active readdir positions. `hpfs_dir_ops` exposes directory file operations and shared fsync/ioctl hooks.

Control flow: readdir handles synthetic positions for `.` and `..`, registers the file position for mutation tracking, maps dirents by encoded position, skips first/last sentinel entries, translates names according to mount lowercase settings, and emits entries. Lookup validates the name, searches the dnode tree with `map_dirent()`, creates or reuses an inode by fnode sector, initializes it from either directory/fnode data or directory-entry fast data, rejects unsupported HPFS386 ACL/XPERM entries on writable mounts, and fills timestamps/size/EA metadata from the dirent.

State and persistence: read paths do not persist changes, but `hpfs_add_pos()` and `hpfs_del_pos()` maintain in-memory lists of active directory offsets so dnode mutations can adjust them. Lookup may initialize inode state and cache allocation information.

Dependencies and integration: it depends on dnode traversal/mutation helpers, name validation, inode initialization, EA settings, and HPFS global locking. The file integrates directory reads with `namei.c` mutations that update tracked offsets.

Risks: HPFS directory positions encode dnode sector and entry index; invalid seeks can land in corrupt trees, so strict validation is needed. Cycle detection under `sb_chk` prevents infinite traversal. The lookup fast path for regular files avoids fnode I/O unless EAs require it, so directory-entry metadata must be trustworthy.

Test signals: readdir empty and large directories, lseek to valid/invalid encoded offsets, concurrent create/delete while reading, lowercase mount option, strict-check corrupt dnodes, lookup of files with EAs versus without, unsupported ACL/XPERM entries, and inode timestamp/size initialization from dirents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hpfs/dir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hpfs/dnode.c -->
# sources/distributed-fs/ceph-client/fs/hpfs/dnode.c

Purpose: this file maintains HPFS directory dnode B-trees. It inserts, removes, searches, balances, counts, and maps directory entries while preserving active readdir positions.

Important APIs and functions: `hpfs_add_pos()`/`hpfs_del_pos()` track live directory offsets. `hpfs_add_de()` inserts a dirent into one dnode. `hpfs_add_dirent()` descends the dnode tree and inserts, calling `hpfs_add_to_dnode()` for split handling. `hpfs_remove_dirent()` deletes entries and rebalances through `move_to_top()` and `delete_empty_dnode()`. `map_pos_dirent()`, `map_dirent()`, and `map_fnode_dirent()` locate entries by encoded position, name, or fnode. `hpfs_count_dnodes()` and `hpfs_remove_dtree()` traverse directory trees.

Control flow: insertion descends by case-folded name order. If the target dnode has space, it inserts in-place and adjusts tracked positions. If full, it builds a temporary oversized dnode, splits entries around the midpoint into a new dnode, promotes a separator upward, and creates a new root when needed. Removal deletes the target dirent, pulls a replacement from a subtree if necessary, deletes empty dnodes, and updates parent/down pointers. Search and readdir mapping walk down/up through dnode pointers and sentinel entries.

State and persistence: dnode contents, parent pointers, root flags, fnode root-dnode pointers, directory inode size/blocks, and bitmap allocation are mutated. Active `f_pos` pointers stored in `hpfs_inode_info->i_rddir_off` are updated to keep directory streams coherent across changes.

Dependencies and integration: it depends on allocation, quad-buffer mapping, name comparison, fnode mapping, and strict corruption checks. `dir.c` uses mapping functions; `namei.c` uses add/remove; `inode.c` uses count and map-by-fnode when writing metadata.

Risks: this is one of the highest-risk HPFS areas. Mid-split ENOSPC can corrupt trees, so callers preflight with `hpfs_check_free_dnodes()`. Pointer and position substitutions use magic temporary positions `4` and `5`; mistakes can break readdir. Balancing code handles obscure dnode shapes and logs but may proceed on unbalanced trees.

Test signals: insert until dnode splits, split root and non-root dnodes, delete leaf/internal entries, delete empty directories with nested empty dnodes, rename while readdir is active, strict-check bad up/down pointers, map by fnode with long truncated names, and fsck validation after create/delete storms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hpfs/dnode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hpfs/ea.c -->
# sources/distributed-fs/ceph-client/fs/hpfs/ea.c

Purpose: this file implements HPFS extended attribute read, write/update, allocation growth, and removal logic for EAs stored in fnodes, external sector runs, or anode-backed storage.

Important APIs and functions: `hpfs_read_ea()` reads a named EA into a caller buffer. `hpfs_get_ea()` allocates and returns a named EA value. `hpfs_set_ea()` updates or creates fixed-size EA values. `hpfs_ea_ext_remove()` removes external EA lists and nested indirect values. Internal helpers read/write indirect EA values through `hpfs_ea_read()`/`hpfs_ea_write()`.

Control flow: reads first scan fnode-resident EAs, then scan external EA storage by repeatedly reading the fixed EA header and name/value pointer fields. Indirect values are followed through `ea_sec()`, `ea_len()`, and `ea_in_anode()`. Setting updates existing EAs only when the new size matches the existing size. Creating prefers available fnode space, otherwise migrates small EAs to external storage and grows the external run, relocating it if contiguous extension fails. Anode-backed EA list creation is mostly disabled/commented; value/list growth may use existing anode paths when already present.

State and persistence: it mutates fnode EA offsets/sizes, fnode flags, external EA sectors, bitmap allocation, and inode `i_ea_size`. On failure it attempts to truncate/free newly allocated external sectors and reset empty EA pointers.

Dependencies and integration: it depends on HPFS raw EA layout helpers from `hpfs_fn.h`, allocation/anode helpers, buffer mapping, and error reporting. `inode.c` uses EAs for UID/GID/MODE/DEV/SYMLINK support, while `anode.c` removes EAs during fnode deletion.

Risks: the file explicitly notes rarely used EA growth code. It cannot resize existing EAs and silently leaves mismatched-size updates unchanged. Large external EAs have a hard bailout around 30000 bytes. Corrupt EA length/name fields can cause early errors; strict fnode checks catch some but not all malformed external chains.

Test signals: read/write inline EAs, migrate inline to external storage, update same-size UID/GID/MODE/DEV/SYMLINK EAs, attempt mismatched-size updates, indirect values, external EA deletion with nested indirect data, contiguous and relocated external growth, ENOSPC cleanup, and corrupt EA-list termination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hpfs/ea.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hpfs/file.c -->
# sources/distributed-fs/ceph-client/fs/hpfs/file.c

Purpose: this file implements HPFS regular-file VFS operations, page-cache block mapping, writeback, truncate, fsync, and fiemap.

Important APIs and functions: `hpfs_bmap()` maps file sectors through the fnode/anode allocation tree, using inode extent cache. `hpfs_get_block()` is the buffer-head mapper for mpage read/write and block bmap. `hpfs_truncate()` truncates allocation trees and writes inode metadata. `hpfs_iomap_begin()` supports read-only fiemap. `hpfs_write_begin()`/`hpfs_write_end()` integrate generic buffered writes with allocation and dirty metadata. `hpfs_file_ops`, `hpfs_file_iops`, and `hpfs_aops` expose VFS behavior.

Control flow: reads and readahead call mpage helpers with `hpfs_get_block()`. Existing mappings use `hpfs_bmap()`, hotfix clipping, and `map_bh()`. Write allocation is only allowed exactly at `mmu_private`, enforcing contiguous logical file extension. New sectors are added via `hpfs_add_sector_to_btree()`, inode block count and `mmu_private` are advanced, and the buffer is marked new. Write-end marks the inode dirty so close/release writes metadata. Fiemap uses iomap on existing mappings only.

State and persistence: data sectors are allocated/freed through allocation B+ trees and bitmaps. Inode size, `i_blocks`, `mmu_private`, cached extent fields, and dirty state are mutated. Fsync flushes page-cache writes and synchronizes the block device.

Dependencies and integration: it depends on `anode.c`, `alloc.c`, `buffer.c` hotfix helpers, `inode.c` metadata writing, Linux mpage/iomap/fiemap APIs, and global HPFS locking.

Risks: the write path rejects non-EOF block allocation with `BUG()`; correctness depends on generic buffered write sequencing and `mmu_private`. Write failures must truncate page cache and allocation back to inode size. Fiemap is read-only and rejects write/zero iomap flags. Hotfixes can reduce contiguous mapping lengths.

Test signals: buffered reads/writes, append growth sector by sector, fragmented allocation, write failure cleanup, truncate shrink, fsync after data/metadata updates, fiemap over mapped and hole ranges, bmap around EOF, hotfix range clipping, and close-triggered metadata writeback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hpfs/file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hpfs/hpfs.h -->
# sources/distributed-fs/ceph-client/fs/hpfs/hpfs.h

Purpose: this header documents and defines the HPFS on-disk format used by the driver. It contains sector-number typedefs, magic values, packed metadata structures, and inline helpers for flags in fnodes, btrees, and EAs.

Important types: `secno`, `dnode_secno`, `fnode_secno`, and `anode_secno` represent partition-relative sectors. The raw structures include `hpfs_boot_block`, `hpfs_super_block`, `hpfs_spare_block`, code-page directory/data blocks, `dnode`, `hpfs_dirent`, `bplus_header`, `fnode`, `anode`, and `extended_attribute`. Inline helpers include `bp_internal()`, `bp_fnode_parent()`, `fnode_in_anode()`, `fnode_is_dir()`, `ea_indirect()`, and `ea_in_anode()`.

Control flow role: the header has no runtime flow, but every mapper and mutator uses these layout definitions to interpret 512-byte sectors and four-sector dnodes. `GET_BTREE_PTR()` converts from embedded fixed btree headers to full variable btree views.

State and persistence: all structures here are persistent HPFS metadata. Fields encode free-space bitmaps, hotfix maps, directory trees, allocation extents, parent pointers, timestamps, EA locations, and file sizes. Endianness annotations and bitfield branches determine how bytes are interpreted on little- and big-endian builds.

Dependencies and integration: `hpfs_fn.h` includes this header and layers kernel runtime state and prototypes on top. Most `.c` files rely on the exact field offsets in this file when reading/writing buffers.

Risks: layout changes can corrupt disk interpretation. Bitfields are endian-sensitive, flexible arrays depend on exact offsets, and comments note parts of HPFS are conjectural. `static_assert` guards the bplus flexible-array offset, but most other layout assumptions rely on source discipline.

Test signals: compile on little- and big-endian configurations if supported, run structure-size/offset checks, mount known HPFS images, fsck after metadata mutations, validate code-page parsing, and test EA/fnode/dnode interpretation against crafted images with boundary field values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hpfs/hpfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hpfs/hpfs_fn.h -->
# sources/distributed-fs/ceph-client/fs/hpfs/hpfs_fn.h

Purpose: this is the HPFS private runtime header. It defines in-memory superblock/inode state, helper macros/inlines, cross-file function prototypes, time conversion helpers, and the global locking API.

Important types and helpers: `struct hpfs_inode_info` extends VFS inodes with directory root dnode, parent fnode, file extent cache, EA state bits, active readdir offsets, and dirty state. `struct hpfs_sb_info` stores mount options, bitmap pointers, free counts, code-page table, hotfix mappings, and the filesystem mutex. `struct quad_buffer_head` represents four sector buffers plus a contiguous view. Inlines parse dirents and EAs, compute dirent sizes, copy dirent metadata, scan bitmap bits, convert local/GMT HPFS time, and assert/take/release `hpfs_mutex`.

Control flow role: the prototypes define subsystem boundaries across allocation, anode, buffer, dentry, directory, dnode, EA, file, inode, map, name, namei, and superblock code. The locking comment establishes the design: VFS-entry methods take one whole-filesystem mutex rather than fine-grained locks.

State and persistence: the header itself persists nothing, but its state structs are the in-memory control plane for all persistent operations. Inline helpers directly interpret on-disk data inside mapped buffers.

Dependencies and integration: it includes kernel mutex, pagemap, buffer-head, slab, signal, blkdev, and unaligned helpers, and includes `hpfs.h` for raw layout. Every HPFS `.c` file includes this header.

Risks: helper inlines operate on raw variable-length records; bad lengths can create pointer errors if callers did not map/validate structures first. `tstbits()` encodes bitmap semantics used by allocator and trim. The global mutex is simple but easy to forget in new VFS paths; `hpfs_lock_assert()` catches some internal misuse.

Test signals: build all HPFS objects after prototype changes, run strict-check mounts to exercise dirent/EA inlines, validate time conversion with `timeshift`, test lock assertions, and ensure active readdir offset tracking is initialized/freed on inode lifecycle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hpfs/hpfs_fn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hpfs/inode.c -->
# sources/distributed-fs/ceph-client/fs/hpfs/inode.c

Purpose: this file initializes, reads, writes, sets attributes on, and evicts HPFS VFS inodes.

Important APIs and functions: `hpfs_init_inode()` initializes default inode and private fields from mount options. `hpfs_read_inode()` maps the fnode and derives VFS type, mode, uid/gid, size, nlink, operations, and EA-derived special cases. `hpfs_write_inode()` and `hpfs_write_inode_nolock()` synchronize inode state back to fnodes and directory entries. `hpfs_setattr()` validates and applies VFS setattr. `hpfs_evict_inode()` removes fnodes for deleted inodes.

Control flow: reading first loads the fnode. If EAs are enabled, it checks `UID`, `GID`, `SYMLINK`, `MODE`, and `DEV` EAs, which can turn the inode into a symlink or special file. Directories get `hpfs_dir_iops`, dnode root, block/size counts from `hpfs_count_dnodes()`, and nlink from subdir count. Regular files get file ops, size from fnode, and address-space ops. Writing finds the parent dirent via `map_fnode_dirent()`, updates fnode file size and dirent timestamps/size/read-only/EA size, writes EA metadata if enabled, updates the `.` dirent for directories, and dirties buffers.

State and persistence: inode private flags cache EA-backed uid/gid/mode. Persistent updates include fnode fields, directory entry timestamps/sizes/EA size, EA records for UID/GID/MODE/DEV, allocation truncation, and fnode deletion on final eviction.

Dependencies and integration: it uses `map.c`, `ea.c`, `dnode.c`, `file.c`, `dir.c`, global HPFS locking, and Linux setattr helpers. `file.c` marks inodes dirty and release calls writeback through this file.

Risks: `hpfs_setattr()` disallows extending files through truncate and limits uid/gid to 16-bit EA encoding. Root inode writes are skipped. Parent lookup during write can fail, leaving metadata unsynchronized. EA writing uses two-byte values even from `__le32` temporaries for UID/GID/MODE, matching HPFS limits but easy to misread.

Test signals: read regular/dir/symlink/special-file inodes from EAs, chmod/chown/truncate shrink, reject growth via setattr, writeback timestamps and read-only bit, eviction after unlink/rmdir, root inode no-op write, and mount options for default uid/gid/mode/eas.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hpfs/inode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hpfs/map.c -->
# sources/distributed-fs/ceph-client/fs/hpfs/map.c

Purpose: this file maps HPFS metadata structures from disk into memory and performs lightweight structural validation when checks are enabled.

Important APIs and functions: `hpfs_map_dnode_bitmap()`, `hpfs_map_bitmap()`, and `hpfs_prefetch_bitmap()` access allocation bitmaps. `hpfs_load_code_page()` loads the case-conversion table. `hpfs_load_bitmap_directory()` reads the bitmap directory into memory. `hpfs_load_hotfix_map()` loads spare-sector remappings. `hpfs_map_fnode()`, `hpfs_map_anode()`, and `hpfs_map_dnode()` map and validate core metadata objects. `hpfs_fnode_dno()` returns a directory fnode’s root dnode.

Control flow: bitmap mapping validates the band index and bitmap-sector pointer, maps four sectors, and prefetches the next bitmap. Code-page loading reads the directory, selects the first code-page data entry, copies the uppercasing table, and synthesizes a lowercasing table. Fnode/anode/dnode mappers call lower-level buffer mapping, check magic values, count/free-node consistency, `first_free` offsets, EA boundaries, self pointers, dnode dirent sizes, last sentinel entries, and down pointers depending on `sb_chk`.

State and persistence: mapping itself is read-oriented, but it returns writable buffer-backed pointers that callers later dirty. Loaded bitmap directories, code-page tables, and hotfix maps become in-memory superblock state.

Dependencies and integration: it depends on `buffer.c`, raw HPFS structures, EA/dirent inline parsers, and `hpfs_error()`. Superblock mount setup uses loaders; all mutation paths use mappers before changing metadata.

Risks: validation is conditional. With low check levels, malformed media may reach later pointer arithmetic. Code-page loading trusts selected table bounds after a few checks. Hotfix map length is capped at 256; invalid spare counts are rejected.

Test signals: mount images with valid and invalid bitmap directories, code-page directories, hotfix maps, fnodes, anodes, and dnodes; run with checks off/normal/strict; test non-contiguous bitmap sectors; verify lower-case table synthesis; and craft malformed dirent lengths and EA boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hpfs/map.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hpfs/name.c -->
# sources/distributed-fs/ceph-client/fs/hpfs/name.c

Purpose: this file implements HPFS filename validation, case conversion, comparison, lowercasing for presentation, long-name detection, and trailing-character adjustment.

Important APIs and functions: `hpfs_chk_name()` validates and trims names. `hpfs_translate_name()` returns the original name or an allocated lowercase copy for readdir. `hpfs_compare_names()` performs case-insensitive HPFS ordering. `hpfs_is_name_long()` determines the HPFS `not_8x3` flag. `hpfs_adjust_length()` trims trailing dots and spaces to match OS/2 behavior. `hpfs_upcase()` exposes code-page-aware uppercase conversion.

Control flow: validation rejects names over 254 bytes, empty adjusted names, disallowed control/reserved characters, and `.`/`..`. Comparison uppercases each byte via the mounted code-page table and compares lexicographically, with the HPFS last sentinel sorting after all real names. Translation optionally lowercases names for display when the mount uses lowercase mode.

State and persistence: no persistent state is changed. The functions read `sb_cp_table` and may allocate temporary display-name buffers.

Dependencies and integration: dentry hashing/comparison, directory lookup, dnode insertion/search, and readdir all depend on these semantics. `hpfs_is_name_long()` feeds the `not_8x3` dirent flag written by `hpfs_add_de()`.

Risks: `hpfs_is_name_long()` appears to test `no_dos_char(name[i])` inside the extension loop instead of `name[j]`, which is a subtle risk for DOS-name classification. Lowercase translation can return the original pointer on allocation failure, so callers must free only when the pointer differs.

Test signals: validate reserved characters and trailing dots/spaces, compare case variants and non-ASCII code-page bytes, display lowercase mode, long-name flag for 8.3 and non-DOS characters, and sentinel comparisons during dnode search.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hpfs/name.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hpfs/namei.c -->
# sources/distributed-fs/ceph-client/fs/hpfs/namei.c

Purpose: this file implements HPFS namespace mutation operations: mkdir, create, mknod, symlink, unlink, rmdir, symlink read, and rename.

Important APIs and functions: `hpfs_mkdir()`, `hpfs_create()`, `hpfs_mknod()`, `hpfs_symlink()`, `hpfs_unlink()`, `hpfs_rmdir()`, `hpfs_rename()`, and `hpfs_symlink_read_folio()` back the exported `hpfs_dir_iops` and `hpfs_symlink_aops`. `hpfs_update_directory_times()` updates parent directory timestamps and writes metadata immediately.

Control flow: create-like operations validate names, take `hpfs_lock()`, allocate fnodes and sometimes dnodes, prepare a dirent, create and initialize a VFS inode, insert the dirent into the parent dnode tree, fill fnode fields, write EAs if needed, insert the inode into the hash, update parent times, and instantiate the dentry. Error paths unwind allocated fnodes/dnodes and inodes. Unlink/rmdir locate the dirent, reject sentinel or wrong-type entries, remove from the dnode tree, update link counts, and update directory times. Rename validates flags/names, handles overwrite of non-directory targets, copies old dirent metadata with the new name/hidden flag, inserts/removes dirents as needed, updates parent directory link counts for moved directories, and rewrites the fnode parent/name fields.

State and persistence: namespace operations mutate directory dnode trees, fnodes, bitmap allocation, directory and file timestamps, link counts, symlink EAs, and inode parent tracking. Symlink targets are stored as the `SYMLINK` EA and read through the symlink address-space operation.

Dependencies and integration: it depends on allocation, dnode add/remove, inode initialization/writeback, EA writing/reading, name validation, and global locking. VFS exclusion is assumed for rename ordering.

Risks: many operations can fail after partial allocation, so unwind correctness is critical. Special files and symlinks require `sb_eas >= 2`; otherwise they return `-EPERM`. Rename over directories is rejected even though comments mention empty non-busy directories. Directory tree removal can return `2` for ENOSPC during delete rebalancing.

Test signals: create files/directories under ENOSPC, duplicate names, read-only mode bits, hidden dot names, special files and symlinks with EAs disabled/enabled, unlink and rmdir empty/non-empty dirs, rename within and across directories, overwrite non-directory targets, invalid rename flags, symlink page read, link-count updates, and fsck after mutation sequences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hpfs/namei.c -->
