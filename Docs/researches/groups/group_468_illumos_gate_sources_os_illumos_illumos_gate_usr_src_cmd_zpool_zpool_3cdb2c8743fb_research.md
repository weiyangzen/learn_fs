# Group Research: group_468_illumos_gate_sources_os_illumos_illumos_gate_usr_src_cmd_zpool_zpool_3cdb2c8743fb

Scope confirmed against `Docs/research_subset_a.md`: `sources/os/illumos/illumos-gate` is included in subset A. All 16 listed files were read completely. This group spans illumos ZFS userland vdev-spec construction, common kernel filesystem header installation, autofs kernel mount/daemon plumbing, bootfs synthetic read-only boot-module exposure, and ctfs synthetic contract filesystem nodes.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/cmd/zpool/zpool_vdev.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/cmd/zpool/zpool_vdev.c

## Purpose

`zpool_vdev.c` converts `zpool` command-line vdev arguments into the nvlist vdev tree passed to libzfs/kernel ZFS. It performs userland validation before pool create/add/split operations: syntax, device/file existence, in-use checks, replication consistency, ashift validation, whole-disk labeling, spare/cache/log/special/dedup handling, and final root-vdev construction.

## File Shape

- Size: 1,697 lines, 43,952 bytes.
- SHA-256: `50591ca6abd1fd855cc3fc5cc0408bc3a23509019386449813555334d260356b`.
- Public entry points in this file: `construct_spec()`, `split_mirror_vdev()`, and `make_root_vdev()`.
- Main local helpers: `make_leaf_vdev()`, `check_device()`, `check_disk()`, `check_slice()`, `check_file()`, `is_whole_disk()`, `get_replication()`, `check_replication()`, `make_disks()`, `is_device_in_use()`, `is_grouping()`, and `num_normal_vdevs()`.

## Core Behavior

- `make_leaf_vdev()` accepts full paths or `/dev/dsk` shorthand, distinguishes block devices from regular files, detects whole disks by probing the backup slice, records `ZPOOL_CONFIG_PATH`, `ZPOOL_CONFIG_TYPE`, `ZPOOL_CONFIG_IS_LOG`, optional allocation bias, optional `WHOLE_DISK`, optional `DEVID`, and optional `ASHIFT`.
- `is_grouping()` recognizes topological or class markers: `raidz`, `raidzN`, `mirror`, `spare`, `log`, `special`, `dedup`, and `cache`; it also enforces minimum and maximum child counts.
- `construct_spec()` walks the argv stream and builds a root nvlist with top-level children plus optional `SPARES` and `L2CACHE` arrays. It treats `log`, `special`, and `dedup` as allocation-class prefixes, supports mirrored class devices, and rejects duplicate `spare`, `log`, or `cache` grouping declarations.
- `check_slice()`, `check_disk()`, `check_device()`, and `check_file()` delegate in-use detection to libdiskmgt and libzfs, rejecting devices used by swap, active pools, reserved spares, or non-overridable consumers.
- `get_replication()` and `check_replication()` verify that new top-level vdevs are internally consistent and, when adding to an existing pool, compatible with the pool's current replication model. Logs are ignored for this consistency check, and raidz/mirror combinations are permitted only when their failure tolerance matches.
- `make_disks()` labels whole disks through `zpool_label_disk()`, rewrites the path to the selected pool slice, fills in a devid after labeling, recurses through children/spares/cache, and rejects boot-label creation on non-whole-disk or multi-vdev boot pools.
- `split_mirror_vdev()` optionally builds a target spec for `zpool split`, labels target disks unless dry-run, rejects grouping keywords as split devices, and calls `zpool_vdev_split()`.
- `make_root_vdev()` is the main validation pipeline: build spec, read current pool config if any, check device usage, check replication if requested, require at least one normal top-level vdev on create, optionally label whole disks, and return the completed root nvlist.

## Dependencies And Contracts

- Uses libnvpair nvlist schema keys from ZFS, including `ZPOOL_CONFIG_CHILDREN`, `TYPE`, `PATH`, `DEVID`, `WHOLE_DISK`, `IS_LOG`, `ALLOCATION_BIAS`, `NPARITY`, `ASHIFT`, `SPARES`, and `L2CACHE`.
- Uses libdiskmgt for in-use and overlap checks; failures from libdiskmgt are warnings except concrete in-use reports.
- Uses `zpool_in_use()`, `zpool_read_label()`, `zpool_label_disk()`, and `zpool_vdev_split()` from libzfs/libzutil-facing code.
- Relies on illumos device naming conventions under `ZFS_DISK_ROOT`, `ZFS_RDISK_ROOT`, and backup slice `s2`.

## Maintenance Notes

Changes here affect user-visible `zpool create`, `zpool add`, and `zpool split` validation behavior. Error wording is part of CLI ergonomics, and several checks are intentionally stricter than kernel acceptance to prevent accidental device reuse. Be careful with allocation-class state in `construct_spec()`: `log`, `special`, and `dedup` are sticky prefixes until another grouping/prefix resets them.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/cmd/zpool/zpool_vdev.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/Makefile -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/Makefile

## Purpose

This Makefile installs common kernel filesystem headers into the proto/root include tree and defines header standards-check targets for the `uts/common/fs` directory.

## File Shape

- Size: 63 lines, 1,556 bytes.
- SHA-256: `fdf4c485cfd98e3434b2710499166e3d81f052c460a45cc06cda8079410f865b`.
- Includes `../../../Makefile.master`.
- Installs `fs_subr.h` and `fs_reparse.h` into `$(ROOT)/usr/include/sys`.
- Installs `proc/prdata.h` into `$(ROOT)/usr/include/sys/proc`.

## Core Behavior

- Defines `ROOTDIR`, `ROOTDIRS`, `ROOTHDRS`, and `ROOTPROCHDRS`.
- Provides pattern install rules for top-level fs headers and `proc` headers using `$(INS.file)`.
- Defines `.check` rules using `$(DOT_H_CHECK)`.
- Enables `.KEEP_STATE` and parallel checking for `$(CHECKHDRS)`.
- `install_h` creates target include directories and installs headers.
- `check` runs standards checks over all listed headers.

## Maintenance Notes

This file is header-install plumbing, not filesystem runtime code. Add new exported headers here only when they are part of the installed system header surface; private implementation headers should remain out of `HDRS`/`PROCHDRS`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/autofs/auto_subr.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/autofs/auto_subr.c

## Purpose

`auto_subr.c` contains the main support routines for the illumos autofs kernel filesystem. It coordinates in-kernel autofs nodes with per-zone `automountd` instances through doors, creates worker threads for mount requests and periodic unmounting, validates untrusted daemon action lists, manages fnnode lifetimes, and implements bottom-up autofs subtree unmount logic.

## File Shape

- Size: 2,654 lines, 69,593 bytes.
- SHA-256: `1f3340643356767defff044a22d978070145a525186947c73f16a8c099048788`.
- Major exported/support functions include `auto_unblock_others()`, `auto_wait4mount()`, `auto_lookup_aux()`, `auto_new_mount_thread()`, `auto_calldaemon()`, `auto_makefnnode()`, `auto_freefnnode()`, `auto_disconnect()`, `auto_enter()`, `auto_search()`, `unmount_subtree()`, `unmount_tree()`, `auto_do_unmount()`, `auto_nobrowse_option()`, and `auto_log()`.

## Core Behavior

- Synchronizes mount and lookup operations with `MF_INPROG`, `MF_LOOKUP`, `MF_WAITING`, and `fn_cv_mount`; interrupted mounts are converted to `EAGAIN` so another thread can retry.
- `auto_calldaemon()` marshals requests with XDR, calls the zone-local automountd door via `door_ki_upcall_limited()`, retries hard calls when the daemon is unavailable, handles door revocation and buffer overflow responses, decodes response XDR, and respects zone shutdown.
- `auto_lookup_request()` and `auto_mount_request()` build autofs protocol requests from `fninfo_t`, including direct-map key handling, subdir, options, and caller UID.
- `auto_mount_thread()` is the worker entry point for mount triggers: it asks automountd for actions, performs them, records `fn_error`, wakes waiters, and releases held vnode/credential/name state.
- `auto_perform_actions()` validates every daemon-provided action before executing it. It accepts only autofs mount actions with relative `.`/`./...` directories, no parent traversal, expected path strings, and correct `autofs_args`; invalid action lists from a zone-local daemon are rejected with a global warning.
- Kernel-created autofs trigger mounts are marked with `MF_IK_MOUNT`; trigger lists and saved action lists allow subordinate autofs trigger nodes to be unmounted and remounted as a unit.
- `auto_makefnnode()`, `auto_enter()`, `auto_search()`, `auto_disconnect()`, and `auto_freefnnode()` implement the in-memory autofs directory tree, odd inode allocation, credential-sensitive `thisuser` symlink matching, reference/link counting, and vnode lifecycle.
- `unmount_subtree()` performs a timestamp-marked depth-first traversal over fnnode children, trigger lists, and mounted autofs roots so nodes are processed bottom-up.
- `try_unmount_node()` checks reference counts, timeouts, in-progress flags, trigger busy state, and mount coverage before unmounting. It remounts triggers on failure when necessary.
- `auto_do_unmount()` is the per-zone periodic unmount scheduler. It waits with zone-shutdown awareness, limits concurrent unmount worker threads, and exits cleanly during zone teardown.

## Dependencies And Contracts

- Depends on `sys/fs/autofs.h` structures (`fnnode_t`, `fninfo_t`, `autofs_globals`, flags), autofs protocol XDR routines from `auto_xdr.c`, and VFS/vnode primitives.
- Uses zone-specific storage and zone-local door handles established by `AUTOFS_SETDOOR`.
- Assumes each zone owns its own autofs tree and automountd. Cross-zone triggers are disallowed elsewhere, and this file assumes most daemon communication is for the current zone unless forced global-zone cleanup is in progress.
- Uses `domount()`, `dounmount()`, `lookuppnvp()`, `VFS_ROOT()`, `vn_mountedvfs()`, vnode locks, and GFS/NFS-related interfaces indirectly through mount actions.

## Maintenance Notes

This file contains several explicit CPR/suspend-safety caveats because worker paths may block in RPC, memory allocation, VFS calls, or network filesystems. Lock ordering is delicate: fnnode mutexes, fnnode rwlocks, vnode VFS locks, and vnode reference counts are all used to avoid races with lookup, mount, unmount, and inactive paths. Treat daemon-provided action validation as a security boundary because non-global zones run their own automountd instances.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/autofs/auto_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/autofs/auto_sys.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/autofs/auto_sys.c

## Purpose

`auto_sys.c` implements the `autofssys()` syscall dispatcher used by autofs userland, mainly for registering the automountd door handle and forcing cleanup of a zone's autofs mounts.

## File Shape

- Size: 101 lines, 2,816 bytes.
- SHA-256: `19bfaf365e061e30db3857fc7f765c7ee2305b57c9af451ee2709cd8400557f7`.
- Single entry point: `autofssys(enum autofssys_op opcode, uintptr_t arg)`.

## Core Behavior

- `AUTOFS_UNMOUNTALL` is restricted to callers with filesystem unmount privilege in the global zone. It looks up the target zone by ID, fetches its autofs globals, and calls `unmount_tree(fngp, B_TRUE)` for forced in-kernel cleanup. Absence of autofs globals is treated as success because there are no mounts to clean.
- `AUTOFS_SETDOOR` initializes current-zone autofs globals if needed, copies in a door ID, replaces any existing door handle, stores the new `door_ki_lookup()` result, and records the automountd process ID.
- Unknown opcodes return `EINVAL`; copy failures return `EFAULT`; authorization failures return `EPERM`.

## Dependencies And Contracts

- Uses `autofs_minor_lock` to serialize zone-specific global initialization and door handle replacement.
- Relies on `autofs_zone_init()` from `auto_vfsops.c` and `unmount_tree()` from `auto_subr.c`.
- Uses zone-specific data key `autofs_key`.

## Maintenance Notes

This syscall is a small but important control boundary. `AUTOFS_UNMOUNTALL` deliberately allows the global zone to clean another zone's autofs state during shutdown, while `AUTOFS_SETDOOR` is per-current-zone and creates the daemon communication endpoint used by the rest of autofs.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/autofs/auto_sys.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/autofs/auto_vfsops.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/autofs/auto_vfsops.c

## Purpose

`auto_vfsops.c` registers autofs as a kernel filesystem and syscall provider, defines autofs mount options, manages per-zone autofs global state, and implements autofs VFS operations: mount, unmount, root, and statvfs.

## File Shape

- Size: 832 lines, 20,992 bytes.
- SHA-256: `a3bde715e28ff1e1d605e7f6c831130b0b96ddc8768b615efc988e337f21c5b4`.
- Module entry points: `_init()`, `_fini()`, `_info()`.
- VFS init and operations: `autofs_init()`, `auto_mount()`, `auto_unmount()`, `auto_root()`, `auto_statvfs()`.
- Per-zone lifecycle: `autofs_zone_init()` and `autofs_zone_destructor()`.

## Core Behavior

- Registers both filesystem ops and the `autofssys` syscall, including 32-bit syscall registration when `_SYSCALL32_IMPL` is enabled.
- Defines mount options for `direct`, `indirect`, `ignore`, `nest`, `browse`, `nobrowse`, and `restrict`, with mutually canceling direct/indirect and browse/nobrowse options.
- `autofs_zone_init()` allocates `autofs_globals`, creates the persistent per-zone root fnnode, initializes daemon and unmount-thread locks, and starts the zone's periodic unmounter thread.
- `autofs_zone_destructor()` asserts only the persistent root fnnode remains, releases any daemon door handle, adjusts the root vnode count for `auto_freefnnode()`, destroys locks, and frees globals.
- `autofs_restrict_opts()` appends inherited restricted mount options to option strings when the `restrict` option is present.
- `auto_mount()` enforces mount privilege, rejects cross-zone global-zone mounts, rejects zone shutdown, initializes zone globals, copies native or 32-bit mount arguments, supports remount updates for directness/timeouts/options/map, allocates and fills `fninfo_t`, creates a unique device ID, copies address/path/options/map/subdir/key, initializes loopback `knconf`, creates the root fnnode, and links user-level mounts into the per-zone top-level autofs list.
- `auto_unmount()` denies forced unmount, checks root vnode/dirent busyness, unlinks root fnnodes from the per-zone list when applicable, releases the root node, and frees `fninfo_t` allocations.
- `auto_statvfs()` returns synthetic empty filesystem stats with the autofs type name and `MAXNAMELEN`.

## Dependencies And Contracts

- Uses `zone_key_create()` for per-zone global state but avoids a constructor because zone-specific construction starts kernel threads.
- Relies on `auto_makefnnode()` and `auto_do_unmount()` from `auto_subr.c` and `auto_vnodeops_template` from `auto_vnops.c`.
- Uses `/dev/ticotsord` lookup to populate loopback transport config for automountd-related communication.

## Maintenance Notes

The module intentionally cannot unload (`_fini()` returns `EBUSY`). Mount argument copying is split for kernel-space, native user-space, and 32-bit user-space callers; all three paths must stay structurally aligned with `struct autofs_args`. The global zone path check prevents mounting autofs for a different zone through a visible zone path.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/autofs/auto_vfsops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/autofs/auto_vnops.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/autofs/auto_vnops.c

## Purpose

`auto_vnops.c` defines vnode operations for autofs. Its primary role is to trigger mounts on demand and then forward ordinary vnode operations to the mounted filesystem, while providing local behavior for unresolved autofs directories, readdir, symlinks, inactive cleanup, and locking.

## File Shape

- Size: 1,540 lines, 34,874 bytes.
- SHA-256: `9dff016484193c69dda9d89ef5b7ffa5c1fe5cd2ce3f9c3e9a8030f132970c12`.
- Defines `auto_vnodeops` and `auto_vnodeops_template`.
- Implements vnode ops including open, close, getattr, setattr, access, lookup, create, remove, link, rename, mkdir, rmdir, readdir, symlink, readlink, fsync, inactive, rwlock, rwunlock, and seek.
- Core helper: `auto_trigger_mount()`.

## Core Behavior

- Most mutating and passthrough vnode ops call `auto_trigger_mount()` on the relevant autofs vnode. If a real filesystem is mounted there, the operation forwards to the mounted root; otherwise unsupported operations return `ENOSYS` or appropriate errors.
- `auto_getattr()` can pre-trigger on `ATTR_TRIGGER`, forwards attributes to mounted roots when present, and has recursion protection using `fn_seen` and `fn_thread`.
- `auto_lookup()` implements direct and indirect map lookup semantics. It handles `.`, `..`, covered vnodes, existing fnnodes, creation of indirect-map placeholder nodes, daemon lookup requests, daemon mount requests, and waiting/retry behavior for concurrent lookup/mount work.
- `auto_readdir()` emits synthetic `.`/`..` and existing kernel fnnodes first, then optionally calls automountd for browse entries using `AUTOFS_READDIR`. It filters daemon entries that duplicate in-kernel entries and honors global `autofs_nobrowse`, per-mount `nobrowse`, direct maps, existing triggers, and delayed indirect behavior.
- `auto_readlink()` serves symlink targets materialized by daemon lookup actions and updates access/reference times.
- `auto_inactive()` disconnects and frees fnnodes when the last vnode reference disappears and the node has no subdirectories.
- `auto_trigger_mount()` enforces same-zone mount triggering, waits for existing lookup/mount work, detects already covered vnodes, recovers from forcibly unmounted mountpoints with triggers, and starts mount worker threads for direct or delayed-indirect triggers.

## Dependencies And Contracts

- Depends on fnnode flags and synchronization from `auto_subr.c`.
- Uses `auto_wait4mount()`, `auto_lookup_aux()`, `auto_new_mount_thread()`, `auto_search()`, `auto_enter()`, `auto_disconnect()`, `auto_freefnnode()`, `auto_nobrowse_option()`, and `unmount_subtree()`.
- Uses VFS root crossing, vnode VFS locks, VOP forwarding, and `fs_subr` default error handlers.

## Maintenance Notes

This file is race-sensitive. Lookup and trigger behavior depends on exact interactions among `MF_LOOKUP`, `MF_INPROG`, vnode holds, fnnode rwlocks, and VFS locks. Cross-zone trigger rejection in `auto_trigger_mount()` is a security constraint. `auto_readdir()` offset handling must remain compatible with both kernel-created entries and daemon cookies beginning at `AUTOFS_DAEMONCOOKIE`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/autofs/auto_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/autofs/auto_xdr.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/autofs/auto_xdr.c

## Purpose

`auto_xdr.c` provides hand-written XDR routines for the autofs kernel-to-automountd protocol. It is not generated by rpcgen because kernel readdir support needs custom encoding/decoding and rpcgen recursion is avoided in kernel code.

## File Shape

- Size: 510 lines, 12,304 bytes.
- SHA-256: `181ac31285e80ff2f4288aee87b2383f8be885a1ac9d9c475eaa70998f0a8a36`.
- Encodes/decodes unmount requests, lookup/mount arguments, action lists, mount arguments, lookup/mount results, and readdir arguments/results.

## Core Behavior

- `xdr_umntrequest()` encodes linked unmount requests with directness, resource, mountpoint, fstype, options, and continuation booleans.
- `xdr_action_list()` decodes and frees non-recursive action-list chains, allocating nodes with `kmem_zalloc()` and freeing with `kmem_free()`.
- `xdr_mounta()` decodes mount requests from automountd, including embedded `autofs_args`, and normalizes `datalen` to the native kernel `struct autofs_args` size after decode.
- `xdr_autofs_lookupargs()`, `xdr_autofs_lookupres()`, and `xdr_autofs_mountres()` marshal daemon lookup/mount request and response unions.
- `xdr_autofs_putrddirres()` encodes directory entries with request-size accounting, omitting inode-zero entries and marking EOF false if the request buffer fills.
- `xdr_autofs_getrddirres()` decodes over-the-wire directory entries into `dirent64` records, handles buffer overflow by stopping early with EOF false, records the next offset, and zero-fills name padding.
- `xdr_autofs_rddirres()` dispatches readdir result encode/decode only when the result status is `AUTOFS_OK`.

## Dependencies And Contracts

- Uses autofs protocol constants and structures from `sys/fs/autofs.h`.
- Uses kernel XDR routines and `dirent64` record sizing macros.
- Allocations happen in kernel memory and are paired with `xdr_free()` paths used by `auto_subr.c`.

## Maintenance Notes

The readdir wire format is custom and size-sensitive. Any change to `dirent64` packing, autofs protocol limits, or daemon-side protocol definitions must be reflected here and in automountd. Keep decode/free paths non-recursive to avoid unbounded kernel stack use.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/autofs/auto_xdr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/bootfs/bootfs_construct.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/bootfs/bootfs_construct.c

## Purpose

`bootfs_construct.c` builds the in-memory vnode tree for bootfs from boot-time module metadata stored as properties on the root devinfo node. It also owns the bootfs node cache constructor/destructor and tree teardown.

## File Shape

- Size: 356 lines, 8,675 bytes.
- SHA-256: `57af068dd81b9937b35a73205b51a42f240bad7057ed404a54e2748d613e8349`.
- Defines global `bootfs_node_cache`.
- Key functions: `bootfs_node_constructor()`, `bootfs_node_destructor()`, `bootfs_construct()`, and `bootfs_destruct()`.

## Core Behavior

- Defines template attributes for directories and regular files. Both are read-only/executable mode `0555`, owned by uid/gid 0, with attributes filled in during node initialization.
- `bootfs_node_init()` reinitializes the cached vnode, marks it `VNOSWAP`, assigns vnode ops and filesystem pointer, copies the name, initializes an AVL directory for directory nodes, fills timestamps, fsid, node id, block size, and inserts the node into the filesystem-wide list.
- `bootfs_mkroot()` creates the root directory vnode, sets `VROOT`, points parent to itself, increments directory stats, and publishes the vnode with `vn_exists()`.
- `bootfs_mknode()` creates or reuses directory nodes in the parent AVL tree. Directory name collisions are reused; file collisions return `EEXIST`. File nodes record the physical-memory address and size, update file/byte stats, and set `va_size`/`va_nblocks`.
- `bootfs_construct_entry()` canonicalizes module paths enough to skip leading slashes and `.` components and to honor `..` by walking to the parent, then creates intermediate directories and the final file. Empty names, all-slash names, and trailing slash names are discarded as `EINVAL`.
- `bootfs_construct()` scans `module-addr-%d`, `module-size-%d`, and `module-name-%d` devinfo properties from index 0 upward until any property is missing/zero. It counts invalid paths as discards and duplicate files as duplicates.
- `bootfs_destruct()` removes every node from the filesystem list, asserts only the filesystem's hold remains, releases the vnode, frees the name, and returns the node to the cache.

## Dependencies And Contracts

- Depends on `bootfs_t` and `bootfs_node_t` from `sys/fs/bootfs_impl.h`.
- Uses devinfo root properties populated by early boot/loader handoff.
- Uses AVL trees for per-directory children and a list for all nodes on a mounted bootfs instance.

## Maintenance Notes

Bootfs constructs all nodes at mount time because the boot module set is small and static. Path handling is intentionally simple; it does not create a general-purpose filesystem namespace and preserves "first file wins" behavior for duplicate module names.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/bootfs/bootfs_construct.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/bootfs/bootfs_vfsops.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/bootfs/bootfs_vfsops.c

## Purpose

`bootfs_vfsops.c` registers bootfs as a kernel filesystem and implements its VFS operations. Bootfs exposes boot-loader supplied modules as a read-only filesystem backed by memory already resident at boot.

## File Shape

- Size: 321 lines, 8,454 bytes.
- SHA-256: `8b93d8ae78b203908e2756481bd6cb57b62a45ff6c913898cdc8d81cef6da1f6`.
- Module entry points: `_init()`, `_info()`, `_fini()`.
- VFS operations: `bootfs_mount()`, `bootfs_unmount()`, `bootfs_root()`, `bootfs_statvfs()`.
- Init: `bootfs_init()`.

## Core Behavior

- `bootfs_mount()` checks mount privilege, requires a directory mountpoint, rejects remount, rejects busy non-overlay mountpoints, sets the resource name to `bootfs`, allocates `bootfs_t`, captures the mount path, allocates a minor number, creates a per-mount kstat, sets read-only/no-setuid/notrunc/unlinkable VFS flags, initializes node list and stats, and calls `bootfs_construct()`.
- `bootfs_unmount()` checks unmount privilege, rejects forced unmount, walks all bootfs nodes to ensure no vnode has more than the filesystem's own hold, deletes kstat, destructs nodes, frees mount path, minor ID, list, and `bootfs_t`.
- `bootfs_root()` returns a held root vnode for the mounted instance.
- `bootfs_statvfs()` reports page-sized block/fragments, no free blocks, file count from kstats, fsid, base type `bootfs`, and an empty filesystem string.
- `_init()` creates the node kmem cache, minor id space, module lock, and installs the filesystem module.
- `_fini()` refuses unload while active mounts exist, removes module linkage, frees vfs/vnode ops, destroys id space, mutex, and kmem cache.

## Dependencies And Contracts

- Shares global `bootfs_major`, `bootfs_node_cache`, and `bootfs_vnodeops` with the construct/vnode files.
- Uses `id_space_t` for minor allocation and kstat named counters for mounted instance statistics.
- Calls `bootfs_construct()`/`bootfs_destruct()` from `bootfs_construct.c`.

## Maintenance Notes

Bootfs is read-only and intentionally avoids swap-backed semantics: the module bytes are already memory-resident. The active mount counter `bootfs_nactive` is checked at unload time in this file; any changes to mount/unmount lifetime should keep that counter semantics correct.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/bootfs/bootfs_vfsops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/bootfs/bootfs_vnops.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/bootfs/bootfs_vnops.c

## Purpose

`bootfs_vnops.c` implements vnode operations for bootfs directories and regular files. It serves directory traversal, reads, attributes, access checks, page faults, and mmap for boot-time module contents.

## File Shape

- Size: 547 lines, 12,107 bytes.
- SHA-256: `f0196775f50b471c8139459d05002510edd3d2a61224b78767726a66a37c5adc`.
- Defines `bootfs_vnodeops` and `bootfs_vnodeops_template`.
- Key vnode ops: `bootfs_read()`, `bootfs_getattr()`, `bootfs_access()`, `bootfs_lookup()`, `bootfs_readdir()`, `bootfs_getpage()`, `bootfs_map()`, and `bootfs_pathconf()`.

## Core Behavior

- `bootfs_read()` rejects directories/non-regular nodes and negative offsets, reads only up to EOF, uses segmap to fault pages, copies data with `uiomove()`, releases segmap, and updates access time.
- `bootfs_getattr()` returns the node's stored `vattr_t` while preserving the caller's requested mask.
- `bootfs_access()` applies ordinary vnode access policy against stored uid/gid/mode.
- `bootfs_lookup()` supports `.`, `..`, rejects xattr lookup, requires a directory, and finds children in the parent AVL tree by name.
- `bootfs_readdir()` emits `.` and `..`, then AVL-ordered children. Directory offsets are based on name lengths, with `.` at 0, `..` at 1, and real entries starting at 3.
- `bootfs_rwlock()` rejects write locks; bootfs is immutable.
- `bootfs_seek()` validates regular-file offsets against file size and always allows directory seek.
- `bootfs_getapage()` creates or looks up a page for the vnode offset, locates the source physical page from `bvn_addr + off`, copies it into the vnode page with `ppcopy()`, and returns it through page-list plumbing.
- `bootfs_getpage()` handles single-page or multi-page requests via `bootfs_getapage()`/`pvn_getpages()`, and permits reads up to file size plus page offset.
- `bootfs_map()` supports private mappings of regular files through `segvn_create`, rejects writable shared mappings, invalid offsets, non-regular vnodes, and `VNOMAP`.
- `bootfs_pathconf()` reports timestamp resolution of 1 and delegates other queries to `fs_pathconf()`.

## Dependencies And Contracts

- Depends on physical-memory page copying (`page_numtopp_nolock()`, `ppcopy()`), segmap, segvn, and VM page-list helpers.
- Directory lookup and readdir depend on AVL ordering established in `bootfs_construct.c`.
- Read and mmap semantics assume boot module memory remains valid for the lifetime of the mounted bootfs.

## Maintenance Notes

This vnode implementation is immutable: no create/remove/write/setattr operations are exposed. Page-fault code copies from physical pages instead of using a normal backing store; changes to boot module address representation or lifetime must update `bootfs_getapage()`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/bootfs/bootfs_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ctfs/ctfs_all.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ctfs/ctfs_all.c

## Purpose

`ctfs_all.c` implements the `/system/contract/all` synthetic directory, which presents all visible contracts in a zone as numeric symlink entries.

## File Shape

- Size: 157 lines, 3,941 bytes.
- SHA-256: `764fbab06e5731b0bb4371c698877876ca1ac606c1ce8ab0c0d94858f49ac35d`.
- Public creator: `ctfs_create_adirnode()`.
- Operation vector: `ctfs_tops_adir`.

## Core Behavior

- `ctfs_create_adirnode()` creates a GFS dynamic directory with custom readdir and lookup callbacks.
- `ctfs_adir_getattr()` reports a read-only directory whose size is `2 + total contracts across all contract types`; timestamps are based on the filesystem mount time.
- `ctfs_adir_do_lookup()` parses the lookup name as a numeric contract ID, verifies no trailing characters, looks up the contract in the caller's zone, and returns a symlink vnode created by `ctfs_create_symnode()`.
- `ctfs_adir_do_readdir()` uses `contract_lookup()` beginning at the current offset in the vnode's zone, emits the next contract ID as both name and inode-derived symlink target entry, and advances the offset.

## Dependencies And Contracts

- Uses GFS directory helpers, contract global lookup/count APIs, and CTFS inode macros.
- Only contracts visible in `VTOZONE(vp)->zone_uniqid` are exposed.

## Maintenance Notes

The directory is dynamically generated and not cached by a static dirent table. Numeric name parsing uses `stoi()` and requires the full name to be numeric.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ctfs/ctfs_all.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ctfs/ctfs_cdir.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ctfs/ctfs_cdir.c

## Purpose

`ctfs_cdir.c` implements per-contract directories under `/system/contract/<type>/<ctid>`. Each such directory contains `ctl`, `status`, and `events` entries for operating on that contract.

## File Shape

- Size: 165 lines, 4,488 bytes.
- SHA-256: `dc2665cd2eecf5af7af5a118231ea047ac5f5b05a38c8ba78a58331d52570cad`.
- Public creator: `ctfs_create_cdirnode()`.
- Operation vector: `ctfs_tops_cdir`.

## Core Behavior

- Defines static GFS entries: `ctl`, `status`, and `events`.
- `ctfs_create_cdirnode()` first checks whether the contract already has a vnode for the target VFS. If not, it creates a GFS directory, assigns its contract-directory inode, holds the contract, and links the vnode into the contract's vnode list.
- `ctfs_cdir_getattr()` reports a read-only directory with link/size count covering `.`/`..` plus the three control entries; ctime comes from contract creation time, and atime/mtime come from the contract event queue.
- `ctfs_cdir_do_inode()` derives child file inode numbers from the contract ID and static child index.
- `ctfs_cdir_inactive()` removes the directory vnode from the contract's vnode list, releases the contract, and frees private node data once GFS says the directory is inactive.

## Dependencies And Contracts

- Relies on `contract_vnode_get()`/`contract_vnode_set()` for per-contract vnode caching.
- Child nodes are created by `ctfs_create_ctlnode()`, `ctfs_create_statnode()`, and `ctfs_create_evnode()`.

## Maintenance Notes

The cdir vnode transitively holds the contract for its child files. Inactive ordering matters: the vnode must be removed from `ct_vnodes` while holding `ct_lock`, then the contract reference can be dropped.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ctfs/ctfs_cdir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ctfs/ctfs_ctl.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ctfs/ctfs_ctl.c

## Purpose

`ctfs_ctl.c` implements the per-contract `ctl` and `status` files. `ctl` accepts contract control ioctls, while `status` returns common or detailed contract status to libcontract consumers.

## File Shape

- Size: 336 lines, 8,264 bytes.
- SHA-256: `0b87d8d455f1379550aedf36a7c7a0588370ac51ef4cc302b2562db4aab1ade1`.
- Public creators: `ctfs_create_ctlnode()` and `ctfs_create_statnode()`.
- Operation vectors: `ctfs_tops_ctl` and `ctfs_tops_stat`.

## Core Behavior

- Control and status nodes store a pointer to the parent cdir's contract; the parent directory provides the transitive contract hold.
- `ctfs_ctl_access()` permits write access only to the contract owner or to the regent process for abandoned inherited contracts. Read or execute access to `ctl` is denied.
- `ctfs_ctl_open()` requires exactly `FWRITE | FOFFMAX` and passes the control access check.
- `ctfs_ctl_ioctl()` implements `CT_CABANDON`, `CT_CACK`, `CT_CNACK`, `CT_CNEWCT`, `CT_CQREQ`, and `CT_CADOPT`, copying event IDs from userland where needed and calling the corresponding contract subsystem functions.
- `ctfs_stat_ioctl()` implements `CT_SSTATUS`. For `CTD_COMMON`, it fills a status struct under `ct_lock`; for detailed levels up to `CTD_ALL`, it asks the contract type for an nvlist, packs it natively, copies it to the caller if the provided buffer is large enough, and updates `ctst_nbytes`.
- Shared getattr logic sets file type, link count, zero size, ctime from contract creation, and atime/mtime from the event queue.

## Dependencies And Contracts

- Relies on libcontract ioctl constants and `STRUCT_*` model macros for native/32-bit status structs.
- Uses contract core APIs: abandon, ack/nack, newct, qack, adopt, common status, and type-specific status callbacks.
- Uses `nvlist_pack()` with `NV_ENCODE_NATIVE` for detailed status payloads.

## Maintenance Notes

`ctl` is write-only and control-oriented; `status` is read-only but still ioctl-driven. Permission rules in `ctfs_ctl_access()` are part of contract ownership semantics and should stay in sync with contract lifecycle behavior.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ctfs/ctfs_ctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ctfs/ctfs_event.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ctfs/ctfs_event.c

## Purpose

`ctfs_event.c` implements ctfs event endpoints: per-contract `events` files and per-type `bundle`/`pbundle` files. These files expose contract event queues through ioctl and poll operations.

## File Shape

- Size: 498 lines, 12,022 bytes.
- SHA-256: `6a060ecae6a9ff0cd2f054d3bb2efa297a0845f01735dc6c64624cac72341f78`.
- Public creators: `ctfs_create_evnode()`, `ctfs_create_pbundle()`, and `ctfs_create_bundle()`.
- Operation vectors: `ctfs_tops_event` and `ctfs_tops_bundle`.

## Core Behavior

- `ctfs_endpoint_open()` validates read-only large-file open flags with optional `FNONBLOCK`, initializes the endpoint listener once, records nonblocking mode, and adds the listener to the target contract event queue.
- `ctfs_endpoint_inactive()` removes active listeners and cleans poll state.
- `ctfs_endpoint_ioctl()` handles `CT_ERESET`, `CT_ERECV`, `CT_ECRECV`, `CT_ENEXT`, and `CT_ERELIABLE` using common contract event queue listener helpers. It passes zone unique ID and optional receive credential checks.
- `ctfs_endpoint_poll()` reports `POLLIN` when the listener has a current position, otherwise returns a pollhead for wakeup.
- Per-contract `events` nodes require `secpolicy_contract_observer()` for access/open and attach to the contract's `ct_events` queue.
- Bundle nodes attach to either the type-wide bundle queue or the current process's process-bundle queue. Bundle ioctl receive privilege checking is enabled for ordinary bundle queues and skipped for process-bundle queues as encoded by the queue list number.
- Inactive handlers hold the parent vnode while tearing down endpoint listeners, preventing destruction order issues with active listeners.

## Dependencies And Contracts

- Uses contract event queue APIs: `cte_add_listener()`, `cte_remove_listener()`, `cte_reset_listener()`, `cte_get_event()`, `cte_next_event()`, and `cte_set_reliable()`.
- Uses pollhead state embedded in endpoint listeners.
- Uses contract type bundle accessors `contract_type_bundle()` and `contract_type_pbundle()`.

## Maintenance Notes

Endpoint setup is one-shot per vnode instance; the code assumes bundle nodes are opened immediately after lookup rather than cloned on open. Listener cleanup ordering is important because contracts must not be destroyed while listeners remain attached.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ctfs/ctfs_event.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ctfs/ctfs_latest.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ctfs/ctfs_latest.c

## Purpose

`ctfs_latest.c` implements the `/system/contract/<type>/latest` pseudo-file. It acts as a doorway to the `status` file for the current LWP's latest contract of that type.

## File Shape

- Size: 183 lines, 4,218 bytes.
- SHA-256: `3f05dc4acecb06dd3859fe6524758f57756ea8bcc8576a165a90b73661278d3e`.
- Public creator: `ctfs_create_latenode()`.
- Operation vector: `ctfs_tops_latest`.

## Core Behavior

- `ctfs_latest_nested_open()` indexes `ttolwp(curthread)->lwp_ct_latest` by the parent type directory index. If a latest contract exists, it creates/gets that contract's cdir vnode, looks up its `status` child, releases the cdir vnode, and returns the held status vnode.
- `ctfs_latest_access()` denies write/execute, then succeeds only when a latest contract status vnode can be opened.
- `ctfs_latest_open()` requires `FREAD | FOFFMAX`, replaces the latest vnode with the nested status vnode, and opens that status vnode.
- `ctfs_latest_getattr()` forwards getattr to the nested status vnode when one exists; otherwise it returns bland read-only regular-file attributes with mount-time timestamps.
- Close, ioctl, readdir, and lookup are invalid/not-directory operations for the latest vnode itself.

## Dependencies And Contracts

- Relies on per-LWP latest-contract tracking and parent GFS file index matching contract type index.
- Uses `ctfs_create_cdirnode()` and GFS lookup of `status`.

## Maintenance Notes

`latest` is intentionally not a normal status file; it is a dynamic indirection based on the calling LWP. Open replaces the vnode pointer with the real status vnode, which is important for callers expecting to use normal status ioctls afterward.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ctfs/ctfs_latest.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ctfs/ctfs_root.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ctfs/ctfs_root.c

## Purpose

`ctfs_root.c` is the central implementation file for the contract filesystem. It registers the ctfs module, creates VFS operations, builds vnode operation vectors for all ctfs node types, implements mount/unmount/root/statvfs, and provides common vnode helpers.

## File Shape

- Size: 521 lines, 12,422 bytes.
- SHA-256: `4406ef5d531f69c5abae939da321e15fdcd94a749d1aa50877fee468161eaf57`.
- Module entry points: `_init()`, `_info()`, `_fini()`.
- Defines global vnodeops pointers for root, all directory, symlink, type directory, template, contract directory, ctl, status, event, bundle, and latest nodes.
- Defines `ctfs_opsvec`, `ctfs_vfstops`, and `ctfs_tops_root`.
- Common exported helpers: `ctfs_common_getattr()`, `ctfs_open()`, `ctfs_close()`, `ctfs_access_dir()`, `ctfs_access_readonly()`, and `ctfs_access_readwrite()`.

## Core Behavior

- `ctfs_init()` registers VFS ops, builds all GFS vnode operation vectors with `gfs_make_opsvec()`, and allocates a unique major number.
- `ctfs_mount()` checks mount privilege and mountpoint suitability, allocates `ctfs_vfs_t`, assigns a unique device/minor, initializes VFS fields, dynamically builds the root directory entries from all registered contract types plus `all`, and creates the GFS root vnode.
- `ctfs_unmount()` checks privilege, rejects forced unmount, refuses unmount while the root vnode has active transitive holds, releases the root vnode, and frees VFS-private data.
- `ctfs_root()` returns a held root vnode.
- `ctfs_statvfs()` reports synthetic filesystem stats based on total contracts across all types, available/free file counts as `INT_MAX - total`, base type from `vfssw`, and filesystem string `contract`.
- `ctfs_common_getattr()` fills uid/gid/rdev/block accounting/fsid/nodeid fields common to all ctfs nodes.
- `ctfs_open()` enforces large-file-aware non-writable opens for directories and similar nodes.
- Access helpers implement directory read/execute only, read-only files, and read-write non-executable files.
- Root attributes report a read-only directory with entries for every contract type plus `all`.

## Dependencies And Contracts

- Uses GFS for synthetic directory/file mechanics and per-node operation vectors.
- Uses contract type registry globals `ct_types` and `ct_ntypes`.
- Uses CTFS inode macros to provide stable synthetic inode numbers.

## Maintenance Notes

The filesystem structure under `/system/contract` is public, but individual file behavior is private/unstable and expected to be accessed through libcontract. Adding new ctfs node types requires updating the ops vector definitions here as well as the relevant type-directory dirent construction in companion files.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ctfs/ctfs_root.c -->