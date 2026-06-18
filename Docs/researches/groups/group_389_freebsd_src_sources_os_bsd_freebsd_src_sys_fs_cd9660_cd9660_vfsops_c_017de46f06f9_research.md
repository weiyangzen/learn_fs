# Group Research: group_389_freebsd_src_sources_os_bsd_freebsd_src_sys_fs_cd9660_cd9660_vfsops_c_017de46f06f9

Scope checked against `Docs/research_subset_a.md`. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/cd9660/cd9660_vfsops.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/cd9660/cd9660_vfsops.c

Read completely: 850 lines.

Purpose: implements FreeBSD `cd9660` VFS mount-layer operations for ISO9660 media, including mount argument translation, GEOM-backed device opening, volume descriptor parsing, root vnode lookup, statfs, file-handle conversion, and vnode construction.

Key entry points:
- `cd9660_cmount()` converts legacy `struct iso_args` into kernel mount options such as `from`, `uid`, `gid`, masks, `ssector`, RRIP/Joliet/kiconv toggles.
- `cd9660_mount()` forces read-only mounts, resolves the block device, verifies access or mount privilege, and either calls `iso_mountfs()` or validates updates.
- `iso_mountfs()` is the core mount routine: opens the device through GEOM, validates sector/logical block sizes, scans volume descriptors from sector `16 + ssector`, recognizes primary, supplementary/Joliet, High Sierra, and end descriptors, initializes `struct iso_mnt`, applies mount options, detects RRIP, handles kiconv, and selects filesystem type.
- `cd9660_unmount()` flushes vnodes, closes iconv handles, closes GEOM consumer, releases device vnode/cdev refs, and frees mount state.
- `cd9660_root()`, `cd9660_statfs()`, `cd9660_fhtovp()`, `cd9660_vget()`, and `cd9660_vget_internal()` provide VFS root/stat/filehandle/vnode lookup behavior.

Important data flow:
- `mp->mnt_data` is set to an allocated `struct iso_mnt` only after descriptor and block-size validation.
- Root directory record data is copied from the selected primary or Joliet descriptor into `isomp->root`.
- RRIP support is detected by reading the root directory block and calling `cd9660_rrip_offset()`.
- NFS filehandles use `struct ifid` and feed back into `VFS_VGET()`.

Concurrency/lifetime notes:
- Vnode creation uses `vfs_hash_get()`/`vfs_hash_insert()` with a custom 64-bit inode comparator.
- `cd9660_vget_internal()` allows duplicate vnode creation races and resolves them through the hash insertion result.
- Error paths carefully release buffers, GEOM consumer, `iso_mnt`, and device references.

Research notes:
- Mounts are always read-only and local.
- Joliet is used only when RRIP is not active.
- The inode scheme is constrained by 32-bit `ino_t` assumptions noted in comments for NFS/export cases.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/cd9660/cd9660_vfsops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/cd9660/cd9660_vnops.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/cd9660/cd9660_vnops.c

Read completely: 870 lines.

Purpose: implements vnode operations for `cd9660` ISO9660 files, directories, symlinks, FIFOs, and buffer/page reads.

Key entry points:
- `cd9660_setattr()` rejects write-like metadata changes for read-only regular files/directories while allowing size no-ops for special nodes.
- `cd9660_access()` enforces read-only semantics for regular files, dirs, and symlinks, applies mount masks and uid/gid overrides, then calls `vaccess()`.
- `cd9660_open()` creates a vnode VM object sized from `iso_node`.
- `cd9660_getattr()` fills `vattr` from ISO/RRIP metadata and dynamically computes symlink size for zero-sized RRIP symlinks.
- `cd9660_ioctl()` supports `FIOGETLBA`.
- `cd9660_read()` maps file offsets to logical ISO blocks, uses clustered or sequential read-ahead, and moves data to userspace.
- `cd9660_readdir()` parses ISO directory records, validates record boundaries, supports RRIP names, ISO translation, Joliet names, associated-file pairing, and directory cookies.
- `cd9660_readlink()` extracts RRIP symbolic link target data from the directory record’s SUSP/RRIP fields.
- `cd9660_strategy()` maps logical vnode blocks to underlying device blocks via `iso_start`.
- `cd9660_getpages()` uses `vfs_bio_getpages()` by default, falling back to generic vnode pager via sysctl.

Important structures:
- `struct isoreaddir` maintains readdir state, saved/associated entries, cookies, offsets, and EOF handling.
- VOP vectors `cd9660_vnodeops` and `cd9660_fifoops` bind cd9660-specific and fifo-special behavior.

Behavior notes:
- Directory parsing defends against zero-length records, too-short records, and records crossing logical-block boundaries.
- POSIX pathconf reports 32-bit file size, link max 1, RRIP `NAME_MAX`, and RRIP symlink limits.
- `cd9660_vptofh()` serializes inode and start block into `struct ifid`.

Research notes:
- This file is the main bridge from on-disk ISO records to FreeBSD VFS semantics.
- RRIP materially changes name, symlink, mode, and inode interpretation.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/cd9660/cd9660_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/cd9660/iso.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/cd9660/iso.h

Read completely: 369 lines.

Purpose: defines ISO9660, Joliet, High Sierra, directory-record, extended-attribute, mount-state, filehandle, and endian conversion structures/macros used by the cd9660 filesystem.

Key definitions:
- `ISODCL()` models ISO fixed byte-position fields.
- `struct iso_volume_descriptor`, `iso_primary_descriptor`, `iso_supplementary_descriptor`, and `iso_sierra_primary_descriptor` describe volume descriptors.
- `struct iso_directory_record` represents variable-length directory entries; `ISO_DIRECTORY_RECORD_SIZE` is fixed at 33 because `sizeof` is unsafe for the trailing name field.
- `struct iso_extended_attributes` describes ISO extended attribute blocks.
- `enum ISO_FTYPE` identifies default ISO9660, plain 9660, RRIP, Joliet, ECMA, and High Sierra modes.
- `struct iso_mnt` is the in-kernel cd9660 mount state.
- `struct ifid` is the cd9660 filehandle payload.

Kernel-facing helpers:
- `VFSTOISOFS()`, `blkoff()`, `lblktosize()`, `lblkno()`, and `blksize()` wrap mount-state block math.
- Prototypes expose vnode, name conversion, directory inode, and rune helpers.

Endian helpers:
- `isonum_711`, `712`, `713`, `721`, `722`, `723`, `731`, `732`, and `733` decode ISO 7.x numeric encodings.
- Both-byte-order ISO fields currently return the little-endian half.

Research notes:
- The header is the contract between raw ISO media bytes and the rest of cd9660.
- `struct iso_mnt` includes GEOM consumer/bufobj pointers, root record copy, RRIP skip offsets, Joliet level, iconv handles, masks, uid/gid overrides, and block geometry.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/cd9660/iso.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/cd9660/iso_rrip.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/cd9660/iso_rrip.h

Read completely: 87 lines.

Purpose: declares Rock Ridge Interchange Protocol analysis flags, the RRIP analysis context, and kernel RRIP helper APIs for cd9660.

Key definitions:
- `ISO_SUSP_*` bit flags identify SUSP/RRIP fields such as attributes, device numbers, symbolic links, alternate names, child/parent links, relocated directories, timestamps, continuation areas, offsets, stop records, and unknown records.
- `ISO_RRIP_ANALYZE` carries state for RRIP analysis: target `iso_node`, requested fields, continuation area location/length, mount, inode pointer, output buffer/length, max length, and continuation status.

Exported kernel APIs:
- `cd9660_rrip_analyze()` fills an `iso_node` from RRIP fields.
- `cd9660_rrip_getname()` extracts alternate names and inode updates for readdir.
- `cd9660_rrip_getsymname()` extracts symlink targets.
- `cd9660_rrip_offset()` detects SUSP/RRIP offset for a directory record.

Research notes:
- This is only the interface; implementation lives elsewhere.
- The VFS and vnode files rely on this header to switch cd9660 from plain ISO semantics to Unix-like RRIP metadata.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/cd9660/iso_rrip.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/cuse/cuse.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/cuse/cuse.c

Read completely: 2036 lines.

Purpose: implements FreeBSD CUSE, a userspace character-device framework. It exposes `/dev/cuse` as a server control device and lets privileged userland servers create character devices whose open/read/write/ioctl/poll/mmap operations are forwarded to that server.

Major structures:
- `struct cuse_server` tracks a server process, command queue, created devices, connected clients, allocated shared memory, refcount, lock/cv, and select/kqueue state.
- `struct cuse_server_dev` maps a userland `struct cuse_dev *` to a kernel `struct cdev`.
- `struct cuse_client` stores per-open state, command slots, buffers, flags, and the associated server/device.
- `struct cuse_client_command` represents in-flight open/close/read/write/ioctl/poll/signal/sync work with sx/cv synchronization.
- `struct cuse_memory` tracks mmap-able swap-backed VM objects by allocation number.

Server-side behavior:
- `/dev/cuse` open allocates a `cuse_server`, initializes queues, locks, and kqueue state, and inserts it into the global server list.
- Server ioctls fetch commands, synchronize completions, create/destroy devices, allocate/free device units, allocate/free shared memory, transfer data, query signals, set per-file handles, and wake pollers.
- Device creation uses `make_dev_credf()` after `PRIV_DRIVER` checks and sanitizes devnode names.
- Server close marks all clients/devices closing, wakes waiters, drains references, destroys devnodes, frees memory, and removes global state.

Client-side behavior:
- Client open rejects same-process server/client opens, creates per-client command slots, queues `CUSE_CMD_OPEN`, and waits for server completion.
- Read/write use `UIO_NOCOPY` and queue commands; small transfers use optimized kernel-side copy buffers, large transfers use process-to-process copying.
- Ioctl marshals fixed-size data through `ioctl_buffer` and exposes zero-length ioctl pointer values through `data_pointer`.
- Poll and kqueue route readiness through server commands and explicit wakeups.
- mmap maps server-allocated VM objects by allocation-number encoded offsets.

Concurrency/lifetime notes:
- Global server list uses `cuse_global_mtx`; per-server state uses `pcs->mtx`; per-command serialization uses `sx`.
- Command wait paths handle signals by queuing `CUSE_CMD_SIGNAL`.
- Process address-space copying uses `proc_rwmem()` with `PHOLD/PRELE`.
- Close/destruction paths are careful to wake blocked clients and avoid server self-destruction deadlocks.

Research notes:
- CUSE is a full bidirectional RPC layer between kernel cdev operations and userland.
- Error conversion maps negative `CUSE_ERR_*` protocol values to kernel `errno`.
- Static allocation limits are defined by `CUSE_BUFFER_MAX`, `CUSE_DEVICES_MAX`, and `CUSE_ALLOC_BYTES_MAX`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/cuse/cuse.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/cuse/cuse_defs.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/cuse/cuse_defs.h

Read completely: 87 lines.

Purpose: defines public CUSE protocol constants shared by CUSE kernel and userland code.

Key definitions:
- `CUSE_VERSION` is `0x000125`.
- Negative `CUSE_ERR_*` values represent server-returned errors such as busy, would-block, invalid, no memory, fault, signal, other, not loaded, and no device.
- `CUSE_POLL_*` defines read/write/error readiness bits.
- `CUSE_FFLAG_*` maps open and operation flags, including read, write, nonblock, and 32-bit compat peer.
- `CUSE_CMD_*` enumerates command types: open, close, read, write, ioctl, poll, signal, sync.
- `CUSE_MAKE_ID()` and `CUSE_ID_MASK` build device-unit allocation namespaces.
- Named ID namespaces exist for default, webcamd, Sundtek, cx88, and uhidd users.

Research notes:
- This header is protocol ABI rather than implementation.
- Command and error constants are consumed directly by `cuse.c`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/cuse/cuse_defs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/cuse/cuse_ioctl.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/cuse/cuse_ioctl.h

Read completely: 90 lines.

Purpose: defines CUSE control-device ioctl ABI structures and ioctl numbers for `/dev/cuse`.

Key structures:
- `struct cuse_data_chunk` describes data transfer between local and peer pointers with length.
- `struct cuse_alloc_info` describes mmap shared-memory page allocation by `page_count` and `alloc_nr`.
- `struct cuse_command` is the server-visible command record: device pointer, flags, per-file handle, data pointer, argument, and command code.
- `struct cuse_create_dev` describes user-requested device creation, owner/group/mode, and devnode name.

Key limits:
- `CUSE_BUFFER_MAX` is 4096 bytes.
- `CUSE_DEVICES_MAX` is 64.
- Reserved ioctl-buffer pointer window is `0x10000` to `0x20000`.
- Allocation numbers are limited by `CUSE_ALLOC_UNIT_MAX`; offsets use `CUSE_ALLOC_UNIT_SHIFT`.

Ioctls:
- Defines get command, read/write data, sync command, get signal, allocate/free memory, set per-file handle, create/destroy device, allocate/free units, select wakeup, and ID-based unit allocation/free.

Research notes:
- This is the ABI contract that `cuse.c` implements.
- Pointer fields are `uintptr_t`, supporting cross-process and compat handling.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/cuse/cuse_ioctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/deadfs/dead_vnops.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/deadfs/dead_vnops.c

Read completely: 167 lines.

Purpose: implements vnode operations for dead/revoked vnodes. Deadfs gives stable behavior for file descriptors or vnodes whose backing object has gone away.

Key behavior:
- `dead_vnodeops` maps most operations to `VOP_EBADF`, `VOP_PANIC`, `VOP_NULL`, or small local handlers.
- `dead_lookup()` always returns `ENOTDIR`.
- `dead_open()` and `dead_close()` silently succeed.
- `dead_read()` returns EOF for tty vnodes and `ENXIO` otherwise.
- `dead_write()` returns `ENXIO`.
- `dead_poll()` returns `POLLHUP` plus readable bits for standard poll requests, or `POLLNVAL` for unsupported event bits.
- `dead_rename()` fails with `EXDEV` after `vop_rename_fail()`.
- `dead_getwritemount()` returns no writable mount.
- `dead_unset_text()` succeeds.

Research notes:
- Devfs uses `dead_read`, `dead_write`, and `dead_poll` for character-device vnode fallbacks.
- The file is intentionally small and defensive: dead vnodes should not perform real filesystem mutation or lookup.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/deadfs/dead_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/devfs/devfs.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/devfs/devfs.h

Read completely: 215 lines.

Purpose: public/private devfs definitions for rules, dirents, mount state, ioctl ABI, and kernel helper prototypes.

Key rule definitions:
- `DEVFS_MAGIC` validates rule ABI payloads.
- `devfs_rnum`, `devfs_rsnum`, and `devfs_rid` identify rules and rulesets; `rid2rsn()`, `rid2rn()`, and `mkrid()` pack/unpack IDs.
- `struct devfs_rule` is pointer-free and shared with userland. It includes condition flags (`DRC_DSWFLAGS`, `DRC_PATHPTRN`) and action flags (`DRA_BACTS`, `DRA_UID`, `DRA_GID`, `DRA_MODE`, `DRA_INCSET`).
- Rule ioctls cover add/delete/apply/get-next and ruleset use/apply/get-next.

Key kernel structures:
- `struct devfs_dirent` models synthetic `/dev` tree entries: cdev pointer, inode, flags, embedded dirent, children list, parent, permissions, labels, timestamps, vnode, symlink target, and use count.
- `struct devfs_mount` tracks mount index, root dirent, generation, hold count, lock, and active ruleset.

Key prototypes:
- Rule application/cleanup/ioctl helpers.
- Vnode allocation, fqpn generation, deletion, population, cleanup, unmount finalization.
- Directory creation/find helpers and controlling-tty reference helpers.

Research notes:
- `DE_WHITEOUT`, `DE_COVERED`, and `DE_USER` are important for rules and user-created symlink overlay behavior.
- `DEVFS_ROOTINO` is fixed at 2.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/devfs/devfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/devfs/devfs_devs.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/devfs/devfs_devs.c

Read completely: 751 lines.

Purpose: manages global character-device registration and per-mount synthetic devfs dirent population.

Key global state:
- `cdevp_list` is the global active-device list protected by `dev_lock()/devmtx`.
- `devfs_inos` allocates devfs inode numbers.
- `devfs_generation` tracks device-list changes for mount population.
- `devfs_rule_depth` controls nested ruleset include depth.

Key functions:
- `sysctl_devname()` maps a device number to a registered device name.
- `devfs_alloc()` allocates and initializes `struct cdev_priv`/`struct cdev`.
- `devfs_free()` releases credentials, inode, dirent arrays, locks, and private storage.
- `devfs_dev_exists()` checks for path conflicts with active devices and referenced directories.
- `devfs_find()` looks up child dirents while ignoring inactive character devices.
- `devfs_newdirent()` allocates dirents with embedded `struct dirent`, timestamps, link count, and MAC labels.
- `devfs_vmkdir()` creates synthetic directories plus `.` and `..`, links into parents, and applies rules.
- `devfs_delete()` dooms a dirent, revokes associated vnode, frees symlink/MAC/inode state, and may prune empty parents.
- `devfs_cleanup()` and `devfs_purge()` remove all per-mount dirents on unmount.
- `devfs_populate()` walks `cdevp_list`, removes inactive entries, creates missing mount dirents, handles aliases as symlinks, applies rules, and updates mount generation.
- `devfs_create()` marks a cdev active, assigns inode, references it, inserts into global list, and bumps generation.
- `devfs_destroy()` clears active state and bumps generation.

Important behavior:
- Each `cdev_priv` owns an array of per-mount dirent pointers indexed by `dm_idx`; `devfs_metoo()` grows that array.
- Inactive devices are garbage-collected only when their `cdp_inuse` drops to zero.
- Device names containing slashes create intermediate devfs directories.

Research notes:
- This file is the core bridge from kernel cdev registration to visible `/dev` filesystem entries.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/devfs/devfs_devs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/devfs/devfs_dir.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/devfs/devfs_dir.c

Read completely: 175 lines.

Purpose: tracks referenced devfs directory paths to prevent device creation path conflicts and to prune directory references when user symlinks or entries are removed.

Key structures:
- `struct dirlistent` stores a directory string, refcount, and list link.
- `devfs_dirlist` is protected by `dirlist_mtx`.

Key functions:
- `devfs_dir_find()` returns true if any tracked directory path contains the queried path.
- `devfs_dir_findent_locked()` finds an exact tracked path under lock.
- `devfs_dir_ref()` inserts or increments a directory reference, ignoring empty paths.
- `devfs_dir_ref_de()` derives a fully qualified devfs path from a dirent and references it.
- `devfs_dir_unref()` decrements and removes/free entries at refcount zero.
- `devfs_dir_unref_de()` dereferences by dirent-derived path.
- `devfs_pathpath()` returns true if path `p1` contains path `p2`, treating exact match or directory prefix as containment.

Research notes:
- The directory list is separate from the per-mount dirent tree.
- It is used by device creation/path conflict checks in `devfs_devs.c`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/devfs/devfs_dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/devfs/devfs_int.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/devfs/devfs_int.h

Read completely: 102 lines.

Purpose: declares devfs internals shared only by `kern/kern_conf.c` and devfs implementation files.

Key structures:
- `struct cdev_privdata` stores per-file cdev private data, destructor, associated `struct file`, and list link.
- `struct cdev_priv` embeds the public `struct cdev` plus active-list links, inode, flags, in-use count, per-mount dirent array, destructor callback state, fd-private data list, destructor count, and thread lock.

Important flags:
- `CDP_ACTIVE` means the cdev is live.
- `CDP_SCHED_DTR` and `CDP_UNREF_DTR` relate to destructor scheduling.
- `CDP_ON_ACTIVE_LIST` tracks membership in `cdevp_list`.

Key declarations:
- cdev allocation/create/destroy/free helpers.
- dirent directory ref/unref and path containment helpers.
- global locks and lists: `devfs_inos`, `devmtx`, `devfs_de_interlock`, `cdevpriv_mtx`, `cdevp_list`.

Research notes:
- `cdev2priv()` is the core container conversion from public `struct cdev` to devfs-owned private state.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/devfs/devfs_int.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/devfs/devfs_rule.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/devfs/devfs_rule.c

Read completely: 822 lines.

Purpose: implements devfs rulesets: privileged user-configurable rules that match devfs entries and change visibility, owner, group, mode, or include another ruleset.

Key structures:
- `struct devfs_krule` wraps user ABI `struct devfs_rule` with list linkage and parent ruleset pointer.
- `struct devfs_ruleset` stores ordered kernel rules, ruleset number, and reference count.
- `sx_rules` serializes ruleset/rule mutations and application.

Public entry points:
- `devfs_rules_apply()` applies the active mount ruleset to a newly created dirent.
- `devfs_rules_ioctl()` handles rule/ruleset ioctls after `PRIV_DEVFS_RULE`.
- `devfs_rules_cleanup()` drops a mount’s active ruleset reference.
- `devfs_ruleset_set()` changes a mount’s active ruleset.
- `devfs_ruleset_apply()` reapplies the current ruleset to a mount.

Supported ioctls:
- `DEVFSIO_RADD`, `RDEL`, `RAPPLY`, `RAPPLYID`, `RGETNEXT`.
- `DEVFSIO_SUSE`, `SAPPLY`, `SGETNEXT`.

Matching/action behavior:
- Conditions are ANDed.
- `DRC_DSWFLAGS` matches active cdev driver flags.
- `DRC_PATHPTRN` uses `fnmatch()` against device name, symlink path, or directory path.
- Actions can hide/unhide (`DE_WHITEOUT`), set uid/gid/mode, or include another ruleset recursively up to `devfs_rule_depth`.

Ruleset lifecycle:
- Ruleset 0 is special/null and is not modified.
- Rule number 0 means auto-number; numbering starts at 100 and increments by 100.
- Empty unreferenced rulesets are reaped.
- Include actions increment/decrement referenced ruleset refcounts.

Research notes:
- The file is carefully organized around locking discipline: public functions lock, static helpers assume locks.
- Temporary one-shot rule application is implemented by allocating a transient `devfs_krule`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/devfs/devfs_rule.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/devfs/devfs_vfsops.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/devfs/devfs_vfsops.c

Read completely: 244 lines.

Purpose: implements devfs VFS mount, unmount, root, and statfs operations.

Key behavior:
- `devfs_mount()` rejects rootfs mounting, parses `from`, `export`, and `ruleset` options, rejects export, validates ruleset range, and enforces jail ruleset restrictions.
- Jail mounts always use the prison’s `pr_devfs_rsnum`.
- Mount updates can switch rulesets and reapply them.
- New mounts allocate `struct devfs_mount`, assign a mount index, initialize `dm_lock`, set local/shared-lookup/no-msync flags, create a root dirent with `DEVFS_ROOTINO`, instantiate/cache the root vnode, and optionally set a ruleset.
- `devfs_unmount()` flushes vnodes, performs cleanup, drops ruleset references, clears `mnt_data`, frees mount index, and finalizes if hold count reaches zero.
- `devfs_root()` allocates a vnode for `dm_rootdir` and marks it `VV_ROOT`.
- `devfs_statfs()` returns synthetic small filesystem statistics to satisfy callers such as `df`.

VFS registration:
- `devfs_vfsops` uses `vfs_cache_root` for normal root lookup and `devfs_root` as cachedroot callback.
- Registered as `VFCF_SYNTHETIC | VFCF_JAIL`.

Research notes:
- Devfs mount state has a hold count because vnode population may temporarily drop and reacquire mount locks while unmount can race.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/devfs/devfs_vfsops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/devfs/devfs_vnops.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/devfs/devfs_vnops.c

Read completely: 2181 lines.

Purpose: implements devfs vnode and file operations for synthetic directories/symlinks and character devices, including lookup, open/close, read/write/ioctl/poll/kqueue/mmap delegation to `cdevsw`, controlling terminal handling, and per-file cdev private data.

Key support systems:
- `devfs_de_interlock` protects vnode/dirent association and use-count updates.
- `cdevpriv_mtx` protects per-file cdev private data lists.
- `devfs_timestamp()` updates timestamps cheaply unless `vfs.devfs.dotimes` is enabled.

Per-file cdev private data:
- `devfs_get_cdevpriv()`, `devfs_set_cdevpriv()`, `devfs_foreach_cdevpriv()`, `devfs_destroy_cdevpriv()`, and `devfs_clear_cdevpriv()` support drivers storing per-open state with destructors.

Vnode allocation/population:
- `devfs_populate_vp()` ensures a vnode’s mount tree is current, dropping the vnode lock around `devfs_populate()` when needed.
- `devfs_allocv()` creates or returns a vnode for a dirent, handles existing vnode races, assigns VCHR/VDIR/VLNK/VBAD type, references cdevs, selects `devfs_specops` for character devices, associates MAC labels, and handles doomed dirents/mount finalization.

Lookup/name behavior:
- `devfs_lookup()` and `devfs_lookupx()` support normal lookup, `.`/`..`, directory execute checks, clone-on-lookup through the `dev_clone` eventhandler, whiteout/covered filtering, jail visibility checks, and create/delete behavior.
- `devfs_fqpn()` constructs mount-relative full paths.
- `devfs_vptocnp()` resolves vnode-to-component names and parent vnode references.

Character-device operations:
- `devfs_open()` validates cdev, tracks usecount, calls `d_fdopen` or `d_open`, sets `f_data`, and swaps fileops to `devfs_ops_f`.
- `devfs_close()` handles controlling terminal refs, last-close detection, forced revoke flags, `D_TRACKCLOSE`, and calls driver `d_close`.
- Fileops `devfs_read_f()`, `devfs_write_f()`, `devfs_ioctl_f()`, `devfs_poll_f()`, `devfs_kqfilter_f()`, and `devfs_mmap_f()` validate the cdev via `devfs_fp_check()` and delegate to driver methods.
- `devfs_ioctl()` handles `FIODTYPE`, `FIODGNAME`, driver ioctls, `ENOIOCTL` translation, and `TIOCSCTTY` controlling-terminal assignment.

Directory/symlink operations:
- `devfs_readdir()` populates, skips covered/whiteout/jail-hidden entries, emits synthetic dirents, and reports EOF.
- `devfs_symlink()` requires `PRIV_DEVFS_SYMLINK`, creates user symlinks, can cover existing generated entries, references directories, applies rules, and allocates a vnode.
- `devfs_remove()` removes user symlinks or whiteouts generated devices.
- `devfs_readlink()` returns stored symlink target.

Reclaim/revoke:
- `devfs_reclaim()` detaches generic dirents from vnodes.
- `devfs_reclaim_vchr()` also releases cdev references and usecounts.
- `devfs_revoke()` revokes all vnodes associated with a cdev across mount dirent arrays and handles inactive cdev garbage collection.

VOP/fileops vectors:
- `devfs_vnodeops` handles non-character devfs nodes.
- `devfs_specops` handles VCHR nodes, with actual I/O routed through fileops after open.
- `devfs_ops_f` is the character-device fileops table.

Research notes:
- This is the highest-risk devfs file: it coordinates VFS locks, devfs mount locks, cdev refs, file private data, session/tty state, and driver callbacks.
- Jail checks and rules/whiteouts define what users actually see under `/dev`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/devfs/devfs_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_acl.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_acl.c

Read completely: 526 lines.

Purpose: implements ext2/ext4 POSIX.1e ACL support, guarded by `UFS_ACL`, converting between FreeBSD in-memory ACLs and ext4-compatible on-disk extended-attribute ACL format.

Key functions:
- `ext2_sync_acl_from_inode()` updates ACL entries from inode mode bits, handling `ACL_MASK` versus `ACL_GROUP_OBJ`.
- `ext2_sync_inode_from_acl()` updates inode mode from ACL permissions while preserving non-permission bits.
- `ext4_acl_from_disk()` validates ext4 ACL header/version, computes entry count, parses short and full entries, validates bounds, and fills `struct acl`.
- `ext2_getacl_posix1e()` maps ACL type to extattr namespace/name, reads the extended attribute, synthesizes minimal access/default ACLs for `ENOATTR`, decodes disk ACLs, and syncs access ACL mode bits from inode.
- `ext2_getacl()` rejects unsupported mount modes and NFSv4 ACL requests, then delegates to POSIX.1e get.
- `ext4_acl_to_disk()` computes disk size, writes ext4 ACL header and short/full entries.
- `ext2_setacl_posix1e()` validates ACLs, authorizes mutation, rejects readonly/immutable/append-only targets, writes/removes ACL extattrs, maps missing extattrs to `EOPNOTSUPP`, updates inode mode for access ACLs, calls `ext2_update()`, and sends `NOTE_ATTRIB`.
- `ext2_setacl()` gates mount ACL support and NFSv4 ACL requests.
- `ext2_aclcheck()` validates ACL type/object applicability and calls `acl_posix1e_check()`.

Important behavior:
- Access ACL deletion is rejected; default ACL deletion is allowed only on directories.
- ACL storage uses extattr names `POSIX1E_ACL_ACCESS_EXTATTR_NAME` and `POSIX1E_ACL_DEFAULT_EXTATTR_NAME`.
- Disk ACL entries omit `ae_id` for user/group object, mask, and other entries.

Research notes:
- The file bridges FreeBSD ACL VOPs to Linux/ext4-style ACL xattrs.
- A likely minor bug exists in `ext2_getacl_posix1e()`: `value` is allocated with `M_ACL` but freed with `M_TEMP` in `out`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_acl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_acl.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_acl.h

Read completely: 55 lines.

Purpose: declares ext2/ext4 ACL disk structures and VOP helper prototypes.

Key definitions:
- `EXT4_ACL_VERSION` is `0x0001`.
- `struct ext2_acl_entry` stores tag, permission, and id for user/group ACL entries.
- `struct ext2_acl_entry_short` stores only tag and permission for entries that do not carry an id.
- `struct ext2_acl_header` stores the ACL version.

Exported functions:
- `ext2_sync_acl_from_inode()`.
- `ext2_getacl()`.
- `ext2_setacl()`.
- `ext2_aclcheck()`.

Research notes:
- This header is intentionally small and tied to `ext2_acl.c`.
- It models ext4 ACL xattr layout rather than native UFS ACL storage.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_acl.h -->