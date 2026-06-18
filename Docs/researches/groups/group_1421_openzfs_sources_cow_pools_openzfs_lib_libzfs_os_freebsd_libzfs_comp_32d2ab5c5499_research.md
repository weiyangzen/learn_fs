# Group Research: group_1421_openzfs_sources_cow_pools_openzfs_lib_libzfs_os_freebsd_libzfs_comp_32d2ab5c5499

Scope confirmed against `Docs/research_subset_a.md`: all files are under `sources/cow-pools/openzfs`, which is included in subset A. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/lib/libzfs/os/freebsd/libzfs_compat.c -->
# File Research: sources/cow-pools/openzfs/lib/libzfs/os/freebsd/libzfs_compat.c

FreeBSD-specific libzfs compatibility glue. It supplies an `execvpe()` fallback for older FreeBSD, module initialization/error text, jail/unjail ioctl plumbing, next-boot bootloader command support, and kernel version retrieval.

Key interfaces:
- `libzfs_error_init()` builds FreeBSD-aware initialization errors, including module-load context.
- `libzfs_load_module()` checks `modfind("zfs")` and tries `kldload(ZFS_KMOD)`, where `ZFS_KMOD` is `zfs` in-base or `openzfs` out-of-base.
- `zfs_jail()` validates dataset type and sends `ZFS_IOC_JAIL` or `ZFS_IOC_UNJAIL`.
- `zpool_nextboot()` packages pool/device GUIDs plus command into an nvlist for `ZFS_IOC_NEXTBOOT`.
- `zfs_version_kernel()` reads `vfs.zfs.version.module` via `sysctlbyname()`.

Several Linux-style hooks are intentionally no-ops on FreeBSD: disk relabel/label helpers, `find_shares_object()`, and `zfs_destroy_snaps_nvl_os()`.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/lib/libzfs/os/freebsd/libzfs_compat.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/lib/libzfs/os/freebsd/libzfs_share_nfs.c -->
# File Research: sources/cow-pools/openzfs/lib/libzfs/os/freebsd/libzfs_share_nfs.c

FreeBSD NFS sharing backend for libshare. It writes ZFS-managed exports to `/etc/zfs/exports`, using `/etc/zfs/exports.lock` for serialized updates, and signals `mountd` after changes.

Key behavior:
- `translate_opts()` converts comma/space-separated ZFS share options into FreeBSD `exports(5)` syntax by prefixing recognized keywords with `-`.
- `nfs_enable_share_impl()` emits one export line per semicolon-separated option set, escaping mountpoints through common NFS helpers.
- `nfs_disable_share_impl()` emits nothing, relying on `nfs_toggle_share()` to rewrite the export file without the removed share.
- `nfs_commit_shares()` opens `/var/run/mountd.pid` and sends `SIGHUP` when `mountd` is running.
- `libshare_nfs_type` wires enable/disable/status/validate/commit/truncate callbacks into the common libshare layer.

Validation is minimal: empty share options are rejected, otherwise accepted for export-file translation.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/lib/libzfs/os/freebsd/libzfs_share_nfs.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/lib/libzfs/os/freebsd/libzfs_share_smb.c -->
# File Research: sources/cow-pools/openzfs/lib/libzfs/os/freebsd/libzfs_share_smb.c

FreeBSD SMB sharing backend stub. SMB support is not implemented for this platform path.

All operational callbacks either return `SA_NOT_SUPPORTED` with `"No SMB support in FreeBSD yet.\n"` on stderr, or return inactive/no-op status:
- `smb_enable_share()`, `smb_disable_share()`, and `smb_validate_shareopts()` reject use.
- `smb_is_share_active()` always returns `B_FALSE`.
- `smb_update_shares()` returns success as an unimplemented commit hook.

`libshare_smb_type` is still exported so higher-level share code has a platform-defined SMB backend.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/lib/libzfs/os/freebsd/libzfs_share_smb.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/lib/libzfs/os/freebsd/libzfs_zmount.c -->
# File Research: sources/cow-pools/openzfs/lib/libzfs/os/freebsd/libzfs_zmount.c

FreeBSD implementation of Solaris-compatible mount helpers for libzfs. It uses FreeBSD `nmount(2)` and `unmount(2)`.

Key behavior:
- `build_iovec()` appends name/value pairs for `nmount()`.
- `do_mount()` builds iovecs for update/remount, readonly, `fstype=zfs`, `fspath`, `from`, and each parsed mount option, then calls `nmount()`.
- `do_unmount()` calls `unmount()` and converts failure to `errno`.
- `zfs_mount_setattr()` falls back to full remount because FreeBSD lacks Linux `mount_setattr(2)`.
- Delegation and pool/volume disable hooks are no-ops on this platform.

Option parsing is simple and platform-specific; mount options are split using `strsep(&optstr, ",/")`.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/lib/libzfs/os/freebsd/libzfs_zmount.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/lib/libzfs/os/linux/libzfs_mount_os.c -->
# File Research: sources/cow-pools/openzfs/lib/libzfs/os/linux/libzfs_mount_os.c

Linux libzfs mount adapter. It maps ZFS mount options to Linux `MS_*` flags, performs direct `mount(2)` by default, supports an optional `/bin/mount` helper path, injects SELinux mount contexts, and updates namespace-sensitive flags with `mount_setattr(2)` when available.

Key interfaces:
- `zfs_parse_mount_options()` tokenizes comma-separated options, respecting quoted commas, and maps known names through `option_map`.
- `zfs_adjust_mount_options()` adds SELinux `context`, `fscontext`, `defcontext`, `rootcontext` options and a `mntpoint=` hint.
- `do_mount()` uses direct `mount(src, mntpt, "zfs", flags, opts)` unless `ZFS_MOUNT_HELPER` is set.
- `do_unmount()` uses `umount2()` unless helper mode is enabled.
- `zfs_mount_setattr()` selectively updates readonly/exec/setuid/devices/atime/relatime mount attributes for mounted datasets.

Legacy datasets require iterating `/proc/mounts` because they may be mounted in multiple locations. If `mount_setattr()` is missing and the dataset is not legacy, the code falls back to full remount.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/lib/libzfs/os/linux/libzfs_mount_os.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/lib/libzfs/os/linux/libzfs_pool_os.c -->
# File Research: sources/cow-pools/openzfs/lib/libzfs/os/linux/libzfs_pool_os.c

Linux pool device-labeling support. It handles EFI/GPT partition creation for whole disks, relabeling expanded devices, and post-label validation.

Key behavior:
- `zpool_relabel_disk()` opens a device, calls `efi_use_whole_disk()`, fsyncs, flushes block buffers, and tolerates `VT_ENOSPC`.
- `read_efi_label()` and `find_start_block()` inspect current vdev config to preserve an existing partition start offset when replacing or expanding devices.
- `zpool_label_disk()` creates GPT partition 0 for ZFS data and partition 8 as reserved space, aligned for logical sector size.
- `zpool_label_name()` generates unique `zfs-<hex>` partition labels from `/dev/urandom` or `rand()`.
- After writing the label, the code triggers/rescans partition state, waits for udev-visible paths, then rereads the label to validate it.

Failure paths report specific libzfs errors such as open failure, no capacity, label failure, or undersized partition.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/lib/libzfs/os/linux/libzfs_pool_os.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/lib/libzfs/os/linux/libzfs_share_nfs.c -->
# File Research: sources/cow-pools/openzfs/lib/libzfs/os/linux/libzfs_share_nfs.c

Linux NFS sharing backend. It translates Solaris/ZFS NFS share options into Linux export entries under `/etc/exports.d/zfs.exports` and commits with `exportfs -ra`.

Key components:
- `foreach_nfs_shareopt()` parses comma-separated share options; `"on"` expands to `rw,crossmnt`.
- `foreach_nfs_host_cb()` parses `rw=`/`ro=` host lists, including bracketed IPv6 literals and CIDR suffixes.
- `get_linux_shareopts_cb()` validates Linux export options, maps `anon` to `anonuid`, `root_mapping` to `root_squash,anonuid`, and `nosub` to `subtree_check`.
- `get_linux_shareopts()` always adds `no_subtree_check` and `mountpoint`.
- `nfs_add_entry()` writes escaped mountpoint lines in Linux exports syntax: `path host(sec=...,access,...opts)`.

Availability is cached by checking `/usr/sbin/exportfs`; truncation separately checks `/etc/exports.d`. Unknown or unsupported share options return syntax errors.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/lib/libzfs/os/linux/libzfs_share_nfs.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/lib/libzfs/os/linux/libzfs_share_smb.c -->
# File Research: sources/cow-pools/openzfs/lib/libzfs/os/linux/libzfs_share_smb.c

Linux SMB sharing backend using Samba usershares. It creates and deletes shares via `net usershare` and detects active shares by parsing Samba usershare files.

Key behavior:
- `smb_retrieve_shares()` scans `SMB_SHARE_DIR`, reads regular share files, and extracts `path`, `comment`, and `guest_ok`.
- `smb_enable_share_one()` normalizes ZFS dataset names into Samba-safe share names and runs `net -S <host> usershare add ... Everyone:F`.
- `smb_enable_share()` disables any existing share at the same mountpoint before creating a new one.
- `smb_disable_share()` finds active shares by path and runs `net usershare delete`.
- `smb_validate_shareopts()` only accepts `on` and `off`.
- `smb_available()` requires both the Samba `net` command and usershare directory.

Commit/update is a no-op; Samba usershare changes are effected by command execution.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/lib/libzfs/os/linux/libzfs_share_smb.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/lib/libzfs/os/linux/libzfs_util_os.c -->
# File Research: sources/cow-pools/openzfs/lib/libzfs/os/linux/libzfs_util_os.c

Linux libzfs utility glue. It provides initialization diagnostics, module autoload/wait logic, `.zfs/shares` inode discovery for diffs, kernel version reading, and user-namespace attach/detach support.

Key interfaces:
- `libzfs_error_init()` maps initialization errno values to actionable Linux messages.
- `libzfs_load_module()` tries `modprobe zfs`, checks sysfs, and waits for `/dev/zfs` via inotify and timerfd. `ZFS_MODULE_TIMEOUT` controls the wait, and containers default to zero wait.
- `find_shares_object()` stats `<mountpoint>/.zfs/shares/` and records its inode for `zfs diff`.
- `zfs_version_kernel()` reads `ZFS_SYSFS_DIR/version`.
- `zfs_userns()` validates the handle is a filesystem, opens a namespace path, and sends `ZFS_IOC_USERNS_ATTACH` or `ZFS_IOC_USERNS_DETACH`.

Snapshot-destroy OS hook is a no-op on Linux.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/lib/libzfs/os/linux/libzfs_util_os.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/lib/libzpool/Makefile.am -->
# File Research: sources/cow-pools/openzfs/lib/libzpool/Makefile.am

Automake definition for `libzpool.la`, the userland build of substantial ZFS kernel logic used by tools and tests.

Key structure:
- Includes `lib/libzpool/include/Makefile.am`.
- Defines `libzpool_la_CFLAGS`, `CPPFLAGS`, library target, and cppcheck target.
- `dist_libzpool_la_SOURCES` lists platform/userland shim files such as `abd_os.c`, `kernel.c`, `util.c`, `zfs_file_os.c`, and `zfs_debug.c`.
- `nodist_libzpool_la_SOURCES` pulls in Lua, common ZFS code, crypto/compression/checksum code, SPA/DMU/DSL/vdev/ZIO modules, and other kernel sources for userland linking.
- `btree.c` and `range_tree.c` are compiled as sources, not linked via `LIBADD`, to avoid exporting their symbols from the libzpool API.
- Links against `libicp`, `libnvpair`, `libzstd`, `libzutil`, clock/zlib/math libraries, and `-lgeom` on FreeBSD.

It also adds PowerPC AltiVec flags for the relevant raidz math object files.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/lib/libzpool/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/lib/libzpool/abd_os.c -->
# File Research: sources/cow-pools/openzfs/lib/libzpool/abd_os.c

Userland ABD OS implementation for libzpool. It simulates kernel scatter/gather ABDs using 4 KiB-aligned iovec-backed allocations.

Key behavior:
- Scatter ABDs use `struct iovec` arrays sized by `abd_iovcnt_for_bytes()`.
- `abd_alloc_struct_impl()` appends variable-length iovec storage to `abd_t` for scatter ABDs.
- `abd_alloc_chunks()` allocates each 4 KiB page with `umem_alloc_aligned()`.
- `abd_zero_scatter` is initialized as a max-block-size scatter ABD whose iovecs all point at one shared zero page.
- `abd_get_offset_scatter()` builds borrowed scatter views by copying iovec entries and setting an intra-page offset.
- Iteration maps either linear memory directly or one scatter page segment at a time.
- Borrow/return helpers allocate temporary buffers for scatter ABDs and assert unchanged data unless the copy-return path is used.

The implementation intentionally creates both linear and scatter ABDs in userland to exercise kernel-like code paths in tests.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/lib/libzpool/abd_os.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/lib/libzpool/arc_os.c -->
# File Research: sources/cow-pools/openzfs/lib/libzpool/arc_os.c

Userland ARC OS hooks for libzpool. These are simplified memory-sizing and pressure callbacks for tests/tools rather than real kernel memory-management integration.

Key behavior:
- `arc_default_max()` derives a default ARC cap from physical memory, reserving roughly 1 GiB when possible and otherwise using the minimum.
- `arc_available_memory()` normally reports abundant memory but occasionally returns `-1024` to simulate pressure.
- `arc_all_memory()` reports half of `physmem`.
- `arc_free_memory()` returns a random amount up to 20% of all memory.
- Memory throttle and hotplug registration are no-ops.

This gives libzpool enough ARC policy input to run SPA/ZIO logic in userland.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/lib/libzpool/arc_os.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/lib/libzpool/include/Makefile.am -->
# File Research: sources/cow-pools/openzfs/lib/libzpool/include/Makefile.am

Installs libzpool-specific public compatibility headers under `$(includedir)/libzpool/sys`.

Headers exported:
- `abd_os.h`
- `abd_impl_os.h`
- `trace_zfs.h`
- `zfs_bootenv_os.h`
- `zfs_context_os.h`
- `zfs_debug_os.h`

This file only defines installation paths and header list; it has no build logic beyond header distribution.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/lib/libzpool/include/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/lib/libzpool/include/sys/abd_impl_os.h -->
# File Research: sources/cow-pools/openzfs/lib/libzpool/include/sys/abd_impl_os.h

Small libzpool ABD implementation header. It defines no-op critical-section macros for userland ABD operations:
- `abd_enter_critical(flags)`
- `abd_exit_critical(flags)`

The userland implementation does not need kernel-style preemption or pagefault critical sections here.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/lib/libzpool/include/sys/abd_impl_os.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/lib/libzpool/include/sys/abd_os.h -->
# File Research: sources/cow-pools/openzfs/lib/libzpool/include/sys/abd_os.h

Defines libzpool's OS-specific ABD storage layouts:
- `struct abd_scatter` contains `abd_offset`, `abd_iovcnt`, and a variable-length `struct iovec abd_iov[1]`.
- `struct abd_linear` contains a raw `void *abd_buf`.

These layouts match `lib/libzpool/abd_os.c` and let common ABD code access linear and scatter storage through OS-specific fields.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/lib/libzpool/include/sys/abd_os.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/lib/libzpool/include/sys/trace_zfs.h -->
# File Research: sources/cow-pools/openzfs/lib/libzpool/include/sys/trace_zfs.h

Placeholder header containing only `/* keep me */`.

It exists so includes of `sys/trace_zfs.h` resolve in the libzpool userland build, without providing kernel tracing definitions.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/lib/libzpool/include/sys/trace_zfs.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/lib/libzpool/include/sys/zfs_bootenv_os.h -->
# File Research: sources/cow-pools/openzfs/lib/libzpool/include/sys/zfs_bootenv_os.h

Libzpool boot environment OS selector header. It defines:
- `BOOTENV_OS` as `BE_POSIX_VENDOR`.

This steers shared bootenv code toward the POSIX/vendor behavior for the libzpool environment.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/lib/libzpool/include/sys/zfs_bootenv_os.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/lib/libzpool/include/sys/zfs_context_os.h -->
# File Research: sources/cow-pools/openzfs/lib/libzpool/include/sys/zfs_context_os.h

Minimal libzpool OS context header. It defines:
- `HAVE_LARGE_STACKS 1`

This informs common ZFS code that the userland/libzpool environment has large stacks compared with constrained kernel stacks.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/lib/libzpool/include/sys/zfs_context_os.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/lib/libzpool/include/sys/zfs_debug_os.h -->
# File Research: sources/cow-pools/openzfs/lib/libzpool/include/sys/zfs_debug_os.h

Libzpool debug OS header. It defines:
- `SET_ERROR(err)` as a wrapper that calls `__set_error(__FILE__, __func__, __LINE__, err)` and returns `err`.

This preserves source-location error tracing in userland ZFS debug builds.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/lib/libzpool/include/sys/zfs_debug_os.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/lib/libzpool/kernel.c -->
# File Research: sources/cow-pools/openzfs/lib/libzpool/kernel.c

Userland kernel-service emulation for libzpool. It provides hostid handling, debug print routing, panic/cmn_err behavior, cache-config import, and global initialization/teardown for subsystems normally provided by the kernel.

Key behavior:
- `zone_get_hostid()` returns the emulated process hostid.
- `dprintf_setup()` consumes `debug=...` argv entries or `ZFS_DEBUG`.
- `__dprintf()` either prints immediately or stores messages through `__zfs_dbgmsg()`.
- `panic()` and `vpanic()` log as panic and abort; `LIBZPOOL_PANIC_STOP=1` sends `SIGSTOP` first.
- `spa_config_load()` reads `spa_config_path` or `ZPOOL_CACHE_BOOT`, unpacks nvlist data, and creates SPA entries.
- `kernel_init()` initializes libspl, umem OOM behavior, hostid, taskqs, ICP, zstd, SPA, fletcher, and TSD keys.
- `kernel_fini()` tears these down.

ZFS onexit, zvol minor, zfsvfs rename, and SPA OS activation hooks are stubs for userland.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/lib/libzpool/kernel.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/lib/libzpool/util.c -->
# File Research: sources/cow-pools/openzfs/lib/libzpool/util.c

Shared libzpool utility routines. It contains vdev/pool stats printing, command-line tunable handling, and pool config operations for import logic.

Key behavior:
- `show_vdev_stats()` recursively prints capacity, ops, bandwidth, and error columns for vdev trees, including logs, spares, and L2ARC.
- `show_pool_stats()` fetches pool config and prints the root vdev plus L2/cache/spare children.
- `handle_tunable_option()` supports `name`, `name=value`, `show`, `show=name`, `info`, and `info=name`.
- `refresh_config()` calls `spa_tryimport()`.
- `pool_active()` checks whether a pool is active by issuing `ZFS_IOC_POOL_STATS` against `/dev/zfs`.

FreeBSD has extra ioctl-version handling for OpenZFS vs legacy ioctl layouts.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/lib/libzpool/util.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/lib/libzpool/vdev_label_os.c -->
# File Research: sources/cow-pools/openzfs/lib/libzpool/vdev_label_os.c

Libzpool OS hook for checking reserved boot area usage during vdev attach/raidz expansion.

`vdev_check_boot_reserve()` currently always returns success. The comments explain that Linux has no known external reserved-area users, FreeBSD can use reserved boot areas for ZFS root from MBR, and current libzpool consumers cannot add disks to pools anyway.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/lib/libzpool/vdev_label_os.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/lib/libzpool/zfs_debug.c -->
# File Research: sources/cow-pools/openzfs/lib/libzpool/zfs_debug.c

In-memory debug-message support for libzpool. It keeps a bounded list of debug messages for later dumping.

Key behavior:
- `zfs_dbgmsg_init()` creates the list and mutex.
- `__set_error()` logs `SET_ERROR()` source locations when `ZFS_DEBUG_SET_ERROR` is enabled.
- `__zfs_dbgmsg()` allocates a timestamped variable-length message node and purges old entries past `zfs_dbgmsg_maxsize` defaulting to 4 MiB.
- `zfs_dbgmsg_print()` writes all messages to an fd with start/end tags, using `write()` so it is signal-handler-friendly.

The list is protected by `zfs_dbgmsgs_lock`.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/lib/libzpool/zfs_debug.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/lib/libzpool/zfs_file_os.c -->
# File Research: sources/cow-pools/openzfs/lib/libzpool/zfs_file_os.c

POSIX file wrapper used by libzpool in place of kernel file/vnode APIs.

Key behavior:
- `zfs_file_open()` opens paths with `open64()`, adds `O_DIRECT` for block devices, supports creation with temporary `umask(0)`, and optionally opens a dump file under `vn_dumpdir`.
- `zfs_file_pwrite()` intentionally splits writes randomly on sector boundaries to let ztest simulate interrupted disk writes.
- `zfs_file_pread()` optionally mirrors reads into the dump fd.
- `zfs_file_getattr()` returns size and mode via `fstat64_blk()`.
- `zfs_file_deallocate()` punches holes with Linux `fallocate()` or FreeBSD `fspacectl()` when available.
- `zfs_file_get()` and `zfs_file_put()` abort because direct fd reference ownership is unsupported in userland.

On Linux, `EINVAL` from O_DIRECT pread/pwrite causes abort to expose alignment bugs.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/lib/libzpool/zfs_file_os.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/lib/libzpool/zfs_racct.c -->
# File Research: sources/cow-pools/openzfs/lib/libzpool/zfs_racct.c

Libzpool stubs for FreeBSD resource-accounting hooks.

Functions:
- `zfs_racct_read()`
- `zfs_racct_write()`

Both accept SPA, size, IOPS, and DMU flags but intentionally do nothing in the libzpool/userland environment.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/lib/libzpool/zfs_racct.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/spl/acl_common.c -->
# File Research: sources/cow-pools/openzfs/module/os/freebsd/spl/acl_common.c

Common ACL conversion code used by the FreeBSD SPL/ZFS compatibility layer. It implements sorting, allocation helpers, POSIX draft ACL to NFSv4 ACE conversion, reverse conversion where possible, and trivial ACL creation/detection.

Key areas:
- `ksort()` and `cmp2acls()` sort `aclent_t` entries.
- Userland-only `acl_alloc()`/`acl_free()` wrap ACL container allocation.
- `ln_aent_to_ace()` converts `aclent_t` entries into allow/deny ACE sequences, including ACL mask emulation and default ACL inheritance flags.
- `ln_ace_to_aent()` converts constrained NFSv4 ACE patterns back to POSIX `aclent_t`; unsupported semantic shapes return `ENOTSUP`.
- `acl_translate()` replaces an ACL in-place with the requested flavor, either ACE or ACLENT.
- `acl_trivial_access_masks()` and `acl_trivial_create()` build owner/group/everyone ACEs from mode bits.
- `ace_trivial_common()` detects non-trivial ACEs by checking principal flags, inheritance, delete bits, and privileged write bits.

The reverse conversion is deliberately strict because many NFSv4 ACLs cannot faithfully map to POSIX draft ACL semantics.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/spl/acl_common.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/spl/callb.c -->
# File Research: sources/cow-pools/openzfs/module/os/freebsd/spl/callb.c

FreeBSD implementation of Solaris `callb` callback registration used for CPR-style thread coordination.

Key behavior:
- Maintains a global `callb_table_t` with per-class callback lists and a freelist.
- `callb_add()` and `callb_add_thread()` register callbacks for current or specified threads.
- `callb_delete()` waits if the callback is executing, unlinks it, and returns its structure to the freelist.
- `callb_execute_class()` runs callbacks in a class serially and returns the registered name for the first failure.
- `callb_generic_cpr()` updates CPR event bits and optionally waits for safe state.
- `callb_lock_table()` and `callb_unlock_table()` stop/start new registrations.

`SYSINIT` and `SYSUNINIT` initialize and drain the callback system.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/spl/callb.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/spl/list.c -->
# File Research: sources/cow-pools/openzfs/module/os/freebsd/spl/list.c

Generic intrusive doubly linked list implementation for the SPL.

Provides:
- List lifecycle: `list_create()`, `list_destroy()`.
- Insertion: head, tail, before, after.
- Removal: object, head, tail.
- Traversal: head, tail, next, previous.
- Bulk/link helpers: `list_move_tail()`, `list_link_replace()`, `list_link_init()`, `list_link_active()`, `list_is_empty()`.

The list stores the object-to-node offset and uses a sentinel head node. Assertions validate offsets and active links.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/spl/list.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/spl/spl_acl.c -->
# File Research: sources/cow-pools/openzfs/module/os/freebsd/spl/spl_acl.c

FreeBSD ACL bridge between ZFS ACE structures and FreeBSD `struct acl`.

Key behavior:
- Static mapping tables translate ZFS ACE permission bits and flags to FreeBSD ACL permission/entry flags.
- `acl_from_aces()` validates count, fills `struct acl`, maps ACE principal flags to FreeBSD tags, copies IDs for named users/groups, and maps ACE type to allow/deny/audit/alarm.
- `aces_from_acl()` performs the reverse conversion from FreeBSD ACL entries to ZFS ACEs.

It panics on unexpected ACE or FreeBSD ACL entry types because callers should provide validated ACLs.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/spl/spl_acl.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/spl/spl_atomic.c -->
# File Research: sources/cow-pools/openzfs/module/os/freebsd/spl/spl_atomic.c

Fallback 64-bit atomic implementation for FreeBSD targets without native 64-bit atomic operations.

When enabled by architecture feature checks, it provides mutex-protected:
- `atomic_add_64()`
- `atomic_dec_64()`
- `atomic_swap_64()`
- `atomic_load_64()`
- `atomic_add_64_nv()`
- `atomic_cas_64()`

Kernel builds use `MTX_SYSINIT`; non-kernel builds use a constructor-initialized `pthread_mutex_t`.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/spl/spl_atomic.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/spl/spl_cmn_err.c -->
# File Research: sources/cow-pools/openzfs/module/os/freebsd/spl/spl_cmn_err.c

FreeBSD implementation of Solaris-style `cmn_err()` logging.

Key behavior:
- `vcmn_err()` maps severities to prefixes: continuation, notice, warning, panic, or ignore.
- Panic severity formats into a local buffer and calls FreeBSD `panic()`.
- Non-panic severities print through `printf()`/`vprintf()` with a newline.
- `cmn_err()` is the variadic wrapper.

Unknown severity levels panic.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/spl/spl_cmn_err.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/spl/spl_dtrace.c -->
# File Research: sources/cow-pools/openzfs/module/os/freebsd/spl/spl_dtrace.c

Minimal FreeBSD SDT/DTrace probe definition file.

It defines one probe:
- `SDT_PROBE_DEFINE1(sdt, , , set__error, "int")`

This supports the SPL/ZFS `set_error` tracing point on FreeBSD.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/spl/spl_dtrace.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/spl/spl_kmem.c -->
# File Research: sources/cow-pools/openzfs/module/os/freebsd/spl/spl_kmem.c

FreeBSD SPL memory allocation and kmem cache compatibility layer.

Key behavior:
- `zfs_kmem_alloc()`/`zfs_kmem_free()` wrap FreeBSD malloc/free using `M_SOLARIS`, with optional debug tracking.
- `kmem_size()` reports capped kernel memory size initialized from VM counters.
- `kmem_cache_create()` maps caches to UMA zones in kernel builds, or size-backed allocations otherwise.
- `kmem_cache_alloc()`/`kmem_cache_free()` run constructors/destructors and use UMA when available.
- Reaping hooks call UMA reclaim in kernel builds and no-op in non-kernel builds.
- `calloc()` is provided as `kmem_zalloc()`.
- `kmem_vasprintf()` allocates formatted strings from kmem.
- `spl_kmem_cache_inuse()` and `spl_kmem_cache_entry_size()` query UMA zone state.
- `spl_kmem_cache_set_move()` is stubbed but asserts a non-null callback.

`KMEM_DEBUG` has tracking scaffolding but is explicitly unsupported near the UMA internals section.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/spl/spl_kmem.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/spl/spl_kstat.c -->
# File Research: sources/cow-pools/openzfs/module/os/freebsd/spl/spl_kstat.c

FreeBSD kstat compatibility layer implemented over `sysctl`.

Key behavior:
- `__kstat_create()` allocates `kstat_t`, computes data size by kstat type, creates `kstat.<module>.<class>` sysctl nodes, and initializes locks.
- Named kstats become individual sysctl procs, with handlers for numeric and string data.
- Dataset-class handlers check `zone_dataset_visible()` before exposing dataset stats.
- Raw kstats use `sbuf` output and dynamic buffer growth up to `KSTAT_RAW_MAX`; they support traditional raw callbacks and `seq_file`-style headers.
- IO kstats are formatted as a text line of read/write counters and timing fields.
- `kstat_delete()` frees sysctl context, data, lock, and kstat structure.

Unsupported kstat types panic during creation or installation.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/spl/spl_kstat.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/spl/spl_misc.c -->
# File Research: sources/cow-pools/openzfs/module/os/freebsd/spl/spl_misc.c

Miscellaneous FreeBSD SPL compatibility helpers.

Key behavior:
- Provides a Solaris-like `utsname()` backed by FreeBSD global OS strings and prison0 hostname.
- `opensolaris_utsname_init()` stores `osreldate` as the version string.
- `kmem_strdup()` allocates/copies strings with kmem.
- `ddi_copyin()` and `ddi_copyout()` bypass user copy functions for fake kernel ioctls marked `FKIOCTL`; otherwise call FreeBSD `copyin`/`copyout`.
- `spl_panic()` forwards to `vpanic()`.
- `current_is_reclaim_thread()` detects FreeBSD page daemon context via `curproc == pageproc`.

Initialization runs at tunables time.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/spl/spl_misc.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/spl/spl_policy.c -->
# File Research: sources/cow-pools/openzfs/module/os/freebsd/spl/spl_policy.c

FreeBSD implementation of Solaris-style security policy checks used by ZFS.

Key behavior:
- Maps ZFS/NFS/mount/inject/SMB and vnode operations to FreeBSD `priv_check_cred()` privileges.
- `secpolicy_fs_owner()` grants dataset super-owner behavior when `zfs_super_owner` is enabled and the mount credential matches uid and jail.
- Vnode access helpers check read/write/exec/lookup/admin privileges and owner fallbacks.
- `secpolicy_vnode_setattr()` enforces permissions for size, mode, owner/group, and timestamp changes, including setuid/setgid clearing.
- `secpolicy_setid_clear()` and `secpolicy_setid_setsticky_clear()` handle FreeBSD setid/sticky privilege rules.
- `secpolicy_fs_mount_clearopts()` forces nosuid/user mount flags when caller lacks non-user mount privilege.
- `secpolicy_xvattr()` gates system flags.

This file is central to matching Solaris policy call sites to FreeBSD credential and jail semantics.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/spl/spl_policy.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/spl/spl_procfs_list.c -->
# File Research: sources/cow-pools/openzfs/module/os/freebsd/spl/spl_procfs_list.c

FreeBSD procfs-list compatibility implemented through raw kstats/sysctl output.

Key behavior:
- `seq_printf()` writes into a small `seq_file` buffer via `vsnprintf()`.
- `procfs_list_install()` initializes the list, lock, callbacks, and creates a virtual raw kstat.
- `procfs_list_addr()` iterates list elements and returns temporary iterator cookies for raw kstat output.
- `procfs_list_data()` calls the registered show callback and frees the iterator cookie.
- `procfs_list_update()` invokes the clear callback on write.
- `procfs_list_destroy()` asserts emptiness, deletes the kstat, destroys list and mutex.
- `procfs_list_add()` assigns monotonically increasing IDs and appends entries.

`procfs_list_uninstall()` is currently empty.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/spl/spl_procfs_list.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/spl/spl_string.c -->
# File Research: sources/cow-pools/openzfs/module/os/freebsd/spl/spl_string.c

String utility compatibility for FreeBSD SPL.

Key behavior:
- Provides `strpbrk()` implementation.
- `strident_canon()` converts a string into a valid C identifier by replacing invalid characters with `_` and forcing NUL termination.
- `kmem_asprintf()` allocates a formatted string from kmem.
- `kmem_strfree()` frees such strings using their runtime length.
- `kmem_scnprintf()` wraps `vsnprintf()` but returns the number of characters actually stored, capped at `size - 1`, to support safe follow-on string operations.

The file uses simple local digit/alpha classification macros.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/spl/spl_string.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/spl/spl_sunddi.c -->
# File Research: sources/cow-pools/openzfs/module/os/freebsd/spl/spl_sunddi.c

Small subset of Solaris DDI string conversion helpers for FreeBSD.

Functions:
- `ddi_strtol()`
- `ddi_strtoull()`
- `ddi_strtoll()`

Each calls the corresponding FreeBSD/libkern conversion routine and returns 0 without detailed errno translation.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/spl/spl_sunddi.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/spl/spl_sysevent.c -->
# File Research: sources/cow-pools/openzfs/module/os/freebsd/spl/spl_sysevent.c

FreeBSD sysevent bridge for ZFS zevents. It drains ZFS events and emits FreeBSD `devctl_notify()` notifications.

Key behavior:
- `log_sysevent()` serializes nvlist members into an `sbuf`, supporting booleans, integer scalars, strings, several integer arrays, and string arrays.
- If `FM_CLASS` starts with `ESC_ZFS_`, it maps the type to `misc.fs.zfs.<suffix>`.
- `sysevent_worker()` initializes a zevent cursor, repeatedly reads events with `zfs_zevent_next()`, waits when none are available, logs each event, and exits on `ESHUTDOWN`.
- Teardown intentionally avoids `zfs_zevent_destroy()` to avoid a race with `fm_fini()` destroying `zevent_lock`; it frees the cursor directly after draining.
- `ddi_sysevent_init()` starts the worker kernel thread under `zfskern/sysevent`.

Nested nvlists are noted but not recursively logged.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/spl/spl_sysevent.c -->