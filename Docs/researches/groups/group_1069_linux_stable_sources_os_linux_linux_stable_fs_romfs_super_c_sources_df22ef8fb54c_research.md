# Group Research: group_1069_linux_stable_sources_os_linux_linux_stable_fs_romfs_super_c_sources_df22ef8fb54c

Scope: `Docs/research_subset_a.md` subset A. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/romfs/super.c -->
# File Research: sources/os/linux/linux-stable/fs/romfs/super.c

## Purpose

Implements the Linux ROMFS filesystem driver, including read-only inode lookup, directory iteration, file/symlink folio reads, superblock validation, block/MTD mount plumbing, inode-cache lifecycle, and module registration.

## Main Responsibilities

- Defines ROMFS inode mode/type mapping and dentry type mapping from ROMFS file-header type bits.
- Implements `romfs_read_folio()` for reading regular-file and symlink data from the underlying ROMFS image via `romfs_dev_read()`, with zero-fill beyond EOF.
- Implements directory traversal:
  - `romfs_readdir()` walks the ROMFS linked list of directory entries, follows hard-link entry inode numbers for `dir_emit()`, and emits VFS dentry types.
  - `romfs_lookup()` scans directory entries by name using `romfs_dev_strcmp()` and returns `d_splice_alias()` on a resolved inode.
- Implements `romfs_iget()`:
  - Follows ROMFS hard-link file-header chains before instantiating the inode.
  - Computes metadata and data offsets from fixed header size plus padded filename length.
  - Sets inode mode, size, timestamps, block count, inode/file operations, address-space ops, and special inode device numbers.
- Implements superblock operations:
  - `romfs_alloc_inode()` and `romfs_free_inode()` use the ROMFS inode slab cache.
  - `romfs_statfs()` reports ROMFS magic, name length, block size, total image size, and fsid based on block device or MTD device identity.
  - `romfs_reconfigure()` forces read-only remount.
- Implements mount-time validation in `romfs_fill_super()`:
  - Sets block size, maximum file size, flags, magic, noatime, readonly, time range, and super ops.
  - Reads the first 512 bytes, validates ROMFS magic words, image size, MTD bounds, and initial checksum.
  - Logs image name and storage backend, computes root header position, and creates the root dentry.
- Supports block and MTD backends through `romfs_get_tree()` using `get_tree_mtd()` and/or `get_tree_bdev()` depending on configuration.
- Implements filesystem registration and cleanup through `init_romfs_fs()` and `exit_romfs_fs()`.

## Key Data/Control Flow

- ROMFS inode numbers are image offsets masked by `ROMFH_MASK`.
- Directory entries are a singly linked list through the `next` file-header field.
- Regular file data starts at `ROMFS_I(inode)->i_dataoffset`, computed from the header plus padded filename.
- The root inode position is derived from the superblock header and volume-name length.
- The filesystem is always mounted read-only with no atime updates.

## Integration Notes

- Depends on ROMFS device helpers from the ROMFS internal layer, especially `romfs_dev_read()`, `romfs_dev_strnlen()`, `romfs_dev_strcmp()`, and `romfs_maxsize()`.
- Uses VFS helpers such as `iget_locked()`, `unlock_new_inode()`, `d_make_root()`, `d_splice_alias()`, `generic_file_llseek()`, `generic_read_dir()`, and `page_symlink_inode_operations`.
- Uses MTD/block mount helpers and explicitly releases MTD and block device references in `romfs_kill_sb()`.

## Correctness and Risk Notes

- Mount validation relies on the initial ROMFS checksum over `min(image_size, 512)`.
- `romfs_iget()` has an inline note that per-inode checksum validation is not performed there.
- Directory iteration returns success even if traversal ended through the normal `out` path; underlying read errors end iteration rather than surfacing a negative return from `romfs_readdir()`.
- Read paths convert any negative backend read result to `-EIO`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/romfs/super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/select.c -->
# File Research: sources/os/linux/linux-stable/fs/select.c

## Purpose

Implements Linux `select()`, `pselect6()`, `poll()`, and `ppoll()` syscall machinery, including wait-queue registration, fd-set copying, timeout accounting/restart behavior, busy-poll integration, signal-mask handling, and compat/time32 variants.

## Main Responsibilities

- Provides timeout helpers:
  - `__estimate_accuracy()` and `select_estimate_accuracy()` compute timer slack.
  - `poll_select_set_timeout()` validates relative time values and converts them to absolute `timespec64` deadlines.
  - `poll_select_finish()` restores saved signal masks, optionally writes remaining timeout to userspace, and handles `STICKY_TIMEOUTS`.
- Implements poll wait table lifecycle:
  - `poll_initwait()` initializes `struct poll_wqueues`.
  - `poll_get_entry()` allocates inline or page-backed wait entries.
  - `__pollwait()` attaches file waiters to wait queues.
  - `pollwake()` and `__pollwake()` filter wake events, set `triggered`, and wake the polling task with ordering barriers.
  - `poll_freewait()` removes waiters and drops file references.
- Implements `select()`:
  - Copies input fd bitmaps from userspace, validates open fds with `max_select_fd()`, scans each selected fd with `vfs_poll()`, writes result bitmaps back, and handles `-ERESTARTNOHAND`.
  - Uses stack storage for small fd sets and `kvmalloc()` for larger sets.
- Implements `pselect6()`:
  - Reads optional timespec and packed userspace signal-mask pointer/size.
  - Installs temporary user signal mask using `set_user_sigmask()`.
  - Shares core select execution and finish logic.
- Implements `poll()`/`ppoll()`:
  - Copies user `struct pollfd` arrays into a stack/page-linked `poll_list`.
  - Calls `do_pollfd()` for each fd, storing `revents`.
  - Copies only `revents` back to userspace.
  - Supports syscall restart through `do_restart_poll()` and `current->restart_block`.
- Implements compat syscall variants for 32-bit fd-set word layout and time32/time64 interfaces under `CONFIG_COMPAT`.

## Key Data/Control Flow

- `do_select()` and `do_poll()` share the same wait queue model:
  - First pass registers waiters through `poll_table->_qproc`.
  - Once an event is found, `_qproc` is cleared to avoid registering unnecessary waiters.
  - If no events are ready, the task sleeps with `poll_schedule_timeout()`.
- `select_poll_one()` converts fd-set interest bits into poll keys and returns `EPOLLNVAL` for bad fds.
- `do_pollfd()` demangles user `POLL*` bits into internal `EPOLL*` bits and always includes `EPOLLERR` and `EPOLLHUP`.
- Busy-poll support uses `POLL_BUSY_LOOP`, `net_busy_loop_on()`, `busy_loop_current_time()`, and `busy_loop_timeout()` before sleeping.
- Timeout pointers represent absolute deadlines; zero timeout disables queue registration and makes the call nonblocking.

## Compatibility and ABI Notes

- Legacy `select()` uses `struct __kernel_old_timeval`; `pselect6()` and `ppoll()` use `struct __kernel_timespec`.
- 32-bit time variants use `old_timespec32`/`old_timeval32`.
- Compat select converts between `compat_ulong_t` fd bitmaps and native unsigned-long bitmaps with `compat_get_bitmap()`/`compat_put_bitmap()`.
- `old_select` syscall wrappers unpack architecture-specific argument structs when enabled.

## Correctness and Risk Notes

- `kern_select()` explicitly rejects negative `tv_sec` or `tv_usec` before normalization to prevent crafted negative values from saturating into effectively infinite deadlines.
- Poll wakeup uses paired memory barriers so event data written before wakeup is visible after the polling task wakes and clears `triggered`.
- `nfds` for `poll()` is capped by `RLIMIT_NOFILE`.
- Userspace timeout update failures after a successful wait can change restart behavior to avoid repeated faults on readonly timeout memory.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/select.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/seq_file.c -->
# File Research: sources/os/linux/linux-stable/fs/seq_file.c

## Purpose

Provides the generic `seq_file` framework used by procfs/debugfs/sysfs-like virtual files to expose sequential records safely through read, read_iter, lseek, formatting helpers, and standard list/hlist iterator helpers.

## Main Responsibilities

- Initializes and releases `struct seq_file`:
  - `seq_file_init()` creates the slab cache.
  - `seq_open()` allocates and attaches a `seq_file` to a file and records the sequence operation table.
  - `seq_release()` frees the dynamic buffer and seq_file object.
- Implements sequential read behavior:
  - `seq_read()` adapts legacy read into `seq_read_iter()`.
  - `seq_read_iter()` serializes with `m->lock`, preserves buffered remainder, grows buffers on overflow, advances sequence positions, and copies output to an iterator.
  - `traverse()` seeks to an arbitrary byte offset by replaying sequence output.
  - `seq_lseek()` supports `SEEK_SET` and `SEEK_CUR` by using `traverse()`.
- Provides formatting/output helpers:
  - `seq_printf()`, `seq_vprintf()`, optional `seq_bprintf()`, `seq_putc()`, `__seq_puts()`, `seq_write()`, `seq_pad()`, `seq_hex_dump()`.
  - Decimal and hex fast-path helpers: `seq_put_decimal_ull_width()`, `seq_put_decimal_ull()`, `seq_put_hex_ll()`, and `seq_put_decimal_ll()`.
  - `seq_escape_mem()` uses `string_escape_mem()` and `seq_commit()`.
- Provides path formatting helpers:
  - `mangle_path()` escapes selected characters.
  - `seq_path()`, `seq_file_path()`, `seq_path_root()`, and `seq_dentry()` print VFS paths into seq buffers.
- Provides single-record helpers:
  - `single_start()`, `single_open()`, `single_open_size()`, `single_release()`.
  - `seq_open_private()`, `__seq_open_private()`, and `seq_release_private()` manage per-open private data.
- Provides iterator helpers for lists, RCU lists, hlists, RCU hlists, and percpu hlist arrays.

## Key Data/Control Flow

- `seq_read_iter()` treats `m->count`/`m->from` as buffered output remaining from a prior read.
- If the caller reads from an offset that does not match `m->read_pos`, the file is replayed with `traverse()` to reconstruct the correct sequence position.
- Overflow is represented by setting `m->count = m->size`; readers detect it with `seq_has_overflowed()` and allocate a larger buffer.
- A positive return from `show()` means `SEQ_SKIP`; the produced record is discarded without treating it as an error.
- A buggy `next()` implementation that does not advance the position is rate-limited logged and compensated by incrementing `m->index`.

## Integration Notes

- Exports most helpers for filesystem and subsystem users.
- Uses `kvmalloc()` for sequence buffers so large virtual-file records can fall back to vmalloc.
- Relies on caller-provided `seq_operations` for locking of underlying data structures; this file serializes only per-open seq_file state.
- RCU iterator helpers require callers to hold the appropriate RCU read-side lock.

## Correctness and Risk Notes

- Buffer allocation rejects sizes over `MAX_RW_COUNT`.
- `seq_path_root()` returns `SEQ_SKIP` when the path is outside the supplied root.
- Several helpers set overflow state rather than returning immediate errors; callers should use `seq_has_overflowed()` or seq_file read retry behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/seq_file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/signalfd.c -->
# File Research: sources/os/linux/linux-stable/fs/signalfd.c

## Purpose

Implements `signalfd` and `signalfd4`, exposing selected pending signals as records readable from an anonymous inode file descriptor.

## Main Responsibilities

- Defines `struct signalfd_ctx`, storing the signalfd signal mask.
- Implements lifecycle and readiness:
  - `signalfd_release()` frees per-file context.
  - `signalfd_poll()` waits on the current sighand signalfd waitqueue and reports `EPOLLIN` if matching private or shared pending signals exist.
  - `signalfd_cleanup()` wakes pollfree waiters when a sighand is detached.
- Converts kernel signal info to ABI records:
  - `signalfd_copyinfo()` fills fixed-size `struct signalfd_siginfo` according to `siginfo_layout()`.
  - Handles kill, timer, poll, fault, child, realtime, and syscall signal layouts.
- Implements reads:
  - `signalfd_dequeue()` dequeues matching signals, optionally sleeps, and handles nonblocking and interruptible waits.
  - `signalfd_read_iter()` emits one or more `signalfd_siginfo` records, requiring the read size to include at least one full record.
- Implements fdinfo support under `CONFIG_PROC_FS` by rendering the inverse mask shown as `sigmask`.
- Implements syscall creation/update:
  - `do_signalfd4()` validates flags, removes uncatchable signals from the mask, inverts it for internal matching, creates an anonymous inode fd, or updates an existing signalfd context.
  - `signalfd4()` and `signalfd()` copy native masks from userspace.
  - Compat syscalls copy `compat_sigset_t` masks.

## Key Data/Control Flow

- The user-supplied mask is normalized by deleting `SIGKILL` and `SIGSTOP`, then inverted with `signotset()` before storage.
- Poll and dequeue operate under `current->sighand->siglock` while checking/dequeueing pending signals.
- Blocking reads add a waitqueue entry to `current->sighand->signalfd_wqh`, set `TASK_INTERRUPTIBLE`, and loop until a matching signal, pending interruption, or error.
- Multi-record reads make the first dequeue obey file nonblocking/nowait state and subsequent dequeues nonblocking to avoid partial-read blocking.

## ABI and Integration Notes

- The signalfd record size is compile-time asserted to 128 bytes.
- Uses `anon_inode_getfile_fmode()` and `FD_ADD()` for new fd creation.
- Reusing an fd requires that it already be backed by `signalfd_fops`.
- `SFD_CLOEXEC` and `SFD_NONBLOCK` are compile-time checked against `O_CLOEXEC` and `O_NONBLOCK`.

## Correctness and Risk Notes

- Updating an existing signalfd mask is done under `siglock` and wakes the signalfd waitqueue.
- Synchronous fault-specific layouts are treated as generic fault layouts if such signals are injected and caught through signalfd.
- `copy_to_iter_full()` failure returns `-EFAULT`; partial records are not exposed.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/signalfd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/Kconfig -->
# File Research: sources/os/linux/linux-stable/fs/smb/Kconfig

## Purpose

Top-level SMB filesystem Kconfig file that includes SMB client, server, and SMB Direct configuration and defines shared SMBFS and SMB KUnit test configuration symbols.

## Main Contents

- Sources:
  - `fs/smb/client/Kconfig`
  - `fs/smb/server/Kconfig`
  - `fs/smb/smbdirect/Kconfig`
- Defines `SMBFS` as an internal tristate enabled when either the CIFS client or SMB server is built in or as a module.
- Defines `SMB_KUNIT_TESTS`, depending on `SMBFS && KUNIT`, defaulting to `KUNIT_ALL_TESTS`.

## Integration Notes

- `SMBFS` is used by the top-level SMB Makefile to include common SMB code.
- `SMB_KUNIT_TESTS` gates shared SMB KUnit test builds and is further consumed by client-specific tests.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/smb/Makefile

## Purpose

Top-level Kbuild dispatch for SMB-related filesystem subdirectories.

## Main Contents

- Builds `common/` when `CONFIG_SMBFS` is enabled.
- Builds `smbdirect/` when `CONFIG_SMBDIRECT` is enabled.
- Builds `client/` when `CONFIG_CIFS` is enabled.
- Builds `server/` when `CONFIG_SMB_SERVER` is enabled.

## Integration Notes

This file connects the Kconfig aggregation in `fs/smb/Kconfig` to the concrete SMB common, client, server, and RDMA transport build directories.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/Kconfig -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/Kconfig

## Purpose

Defines kernel configuration for the CIFS/SMB2/SMB3 client filesystem, including core dependencies, security options, debug facilities, DFS/SWN upcalls, RDMA, FS-Cache, root filesystem support, compression, and SMB1-specific KUnit tests.

## Main Options

- `CIFS`
  - Tristate SMB3/CIFS network filesystem client.
  - Depends on `INET`.
  - Selects NLS, UCS2 utilities, crypto primitives, keys, DNS resolver, ASN.1/OID support, and netfs support.
- `CIFS_STATS2`
  - Enables extended timing/statistics for debug and slow-response reporting.
- `CIFS_ALLOW_INSECURE_LEGACY`
  - Allows legacy SMB1/CIFS and SMB2.0 dialect use.
- `CIFS_UPCALL`
  - Enables Kerberos/SPNEGO request-key upcall support.
- `CIFS_XATTR`
  - Enables CIFS extended attribute support.
- `CIFS_POSIX`
  - Enables old CIFS POSIX extensions and POSIX ACL support for legacy CIFS when xattrs and insecure legacy support are enabled.
- `CIFS_DEBUG`, `CIFS_DEBUG2`, `CIFS_DEBUG_DUMP_KEYS`
  - Enable baseline debug, extra debug, and unsafe key dumping support.
- `CIFS_DFS_UPCALL`
  - Enables DFS namespace support and userspace resolution upcalls.
- `CIFS_SWN_UPCALL`
  - Enables Service Witness Protocol userspace daemon integration.
- `CIFS_NFSD_EXPORT`
  - Broken option for exporting CIFS mounts through nfsd.
- `CIFS_SMB_DIRECT`
  - Enables SMB Direct/RDMA support and selects `SMBDIRECT`.
- `CIFS_FSCACHE`
  - Enables local FS-Cache support when CIFS and FSCACHE linkage is compatible.
- `CIFS_ROOT`
  - Enables experimental SMB root filesystem support.
- `CIFS_COMPRESSION`
  - Enables SMB 3.1.1 compression support.
- `SMB1_KUNIT_TESTS`
  - Enables SMB1-specific KUnit tests when shared SMB tests and insecure legacy support are enabled.

## Integration Notes

- Most optional symbols directly control object inclusion in `fs/smb/client/Makefile`.
- Several options have security-sensitive defaults or warnings: insecure legacy support defaults to yes, key dumping defaults to no, POSIX legacy defaults to no, compression defaults to no.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/Makefile

## Purpose

Kbuild file for the CIFS/SMB2/SMB3 VFS client module, defining core object composition, optional feature objects, generated error-mapping tables, ASN.1 generated dependencies, and SMB KUnit test objects.

## Main Contents

- Adds `-I$(src)` to `ccflags-y` for trace-event include resolution.
- Builds `cifs.o` when `CONFIG_CIFS` is enabled.
- Core `cifs-y` includes VFS, connection, directory, file, inode, transport, Unicode, cached-dir, SMB2, ACL, fs-context, DNS, SPNEGO NegTokenInit ASN.1, namespace, and reparse support objects.
- Generated ASN.1 dependencies:
  - `asn1.o` depends on `cifs_spnego_negtokeninit.asn1.h`.
  - The generated ASN.1 object depends on generated C and header files.
- Optional objects:
  - `xattr.o` for `CONFIG_CIFS_XATTR`.
  - `cifs_spnego.o` for `CONFIG_CIFS_UPCALL`.
  - `dfs_cache.o` and `dfs.o` for `CONFIG_CIFS_DFS_UPCALL`.
  - `netlink.o` and `cifs_swn.o` for `CONFIG_CIFS_SWN_UPCALL`.
  - `fscache.o`, `smbdirect.o`, `cifsroot.o`, compression objects, and legacy SMB1 objects under their matching options.
- Generates SMB1 mapping tables from `nterr.h` and `smberr.h` using `gen_smb1_mapping` when legacy support is configured.
- Generates SMB2 mapping table from `../common/smb2status.h` using `gen_smb2_mapping`.
- Builds SMB1 and SMB2 map-error KUnit test objects under test config symbols.

## Integration Notes

- `targets` includes generated mapping tables so Kbuild tracks and cleans them.
- The file is the practical map from Kconfig feature selection to CIFS client code presence.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/asn1.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/asn1.c

## Purpose

Implements CIFS SPNEGO NegTokenInit ASN.1 decoder callbacks that detect server-supported authentication mechanisms from a security blob.

## Main Responsibilities

- `decode_negTokenInit()` runs the generated `cifs_spnego_negtokeninit_decoder` over a server security blob and returns boolean success.
- `cifs_gssapi_this_mech()` validates that the top-level GSSAPI mechanism OID is SPNEGO and rejects unexpected OIDs with `-EBADMSG`.
- `cifs_neg_token_init_mech_type()` parses mechanism OIDs from NegTokenInit and sets capability booleans on `struct TCP_Server_Info`:
  - `sec_mskerberos`
  - `sec_kerberosu2u`
  - `sec_kerberos`
  - `sec_ntlmssp`
  - `sec_iakerb`
- Logs unsupported or unexpected OIDs using CIFS debug logging and OID string formatting.

## Integration Notes

- Depends on generated header `cifs_spnego_negtokeninit.asn1.h`.
- Uses kernel OID registry helpers `look_up_OID()` and `sprint_oid()`.
- The decoded server security capability flags feed later session setup and upcall selection.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/asn1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/cached_dir.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/cached_dir.c

## Purpose

Implements CIFS/SMB3 cached directory handles and cached directory-entry lifecycle, using SMB2 leases to reuse directory FIDs safely while handling lease breaks, reconnects, unmount cleanup, and periodic expiration.

## Main Responsibilities

- Creates and finds cached directory records:
  - `find_or_create_cached_dir()` searches `cfids->entries` by path, returns only valid leased entries, enforces `max_cached_dirs`, and creates new records when allowed.
  - `init_cached_dir()` allocates a `cached_fid`, duplicates the path, initializes work items, lists, mutexes, and kref.
- Resolves dentries:
  - `path_no_prefix()` strips CIFS prefix path when needed.
  - `path_to_dentry()` walks positive dentries from the CIFS root without permissions checks.
- Opens and populates cached handles:
  - `open_cached_dir()` converts paths to UTF-16, reserves/creates a cache slot, opens the directory with a lease, compounds `SMB2 CREATE` with `SMB2 QUERY_INFO`, validates lease/read-caching state, records file IDs and file-all-info, and returns a referenced cached FID.
  - `open_cached_dir_by_dentry()` finds an existing valid cached handle by dentry pointer.
  - Parent lease keys are supplied for SMB3 when a cached parent dentry is found.
- Drops cached handles:
  - `close_cached_dir()` drops a kref without holding `cfid_list_lock`.
  - `close_cached_dir_locked()` drops a reference while the list lock is held, with a `refcount >= 2` invariant.
  - `smb2_close_cached_fid()` removes the entry from lists, drops dentry, closes the server FID if open, and frees cached state.
  - `drop_cached_dir_by_name()` finds and invalidates a cached directory for removal paths.
- Handles broad invalidation:
  - `close_all_cached_dirs()` detaches dentries during unmount and flushes pending dentry-drop work.
  - `invalidate_all_cached_dirs()` moves entries to the dying list after session loss and schedules the laundromat.
  - `cached_dir_lease_break()` handles SMB lease breaks by removing the entry from lookup lists and queuing asynchronous cleanup.
- Implements periodic cleanup:
  - `cfids_laundromat_worker()` moves dying/expired cached FIDs to a local list, drops dentries, queues server close work when needed, and reschedules itself.
  - `free_cached_dirs()` cancels the laundromat and frees all remaining entries at tcon teardown.
- Tracks cached directory-entry memory accounting and decrements tcon/global counters when freeing cached entries.

## Key Data/Control Flow

- A cached FID is usable only when `is_valid_cached_dir()` sees both `time` and `has_lease`.
- New cache entries temporarily set `has_lease = true` during construction so an early lease break can consume the lease reference safely before the entry is fully valid.
- `open_cached_dir()` does not hold `cfid_list_lock` while sending SMB requests because reconnects may occur.
- On success, the cached FID gets a normal caller reference and a lease reference; on errors, it is removed from the list and references are unwound.
- Replayable SMB errors are retried through `smb2_should_replay()` and replay flags on both compounded requests.

## Concurrency and Lifetime Notes

- `cfids->cfid_list_lock` guards `entries`, `dying`, `num_entries`, and list membership flags.
- Krefs serialize final close/free; `kref_put_lock()` is used where the release function must remove entries while holding the spinlock.
- Dentry drops and server closes may be offloaded to `cfid_put_wq` and `serverclose_wq`.
- Tcon references are manually incremented/traced when queued work may outlive the immediate caller.

## Correctness and Risk Notes

- Lease state is central: entries without read-caching leases are rejected.
- Prefix-path stripping avoids double-prefixing when dentry lookup calls back into CIFS path construction.
- Unmount cleanup has an explicit OOM warning path where not all dentries may be dropped, risking "Dentry still in use" diagnostics.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/cached_dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/cached_dir.h -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/cached_dir.h

## Purpose

Declares CIFS cached directory-handle and cached directory-entry structures plus the public cached-dir helper API.

## Main Contents

- `struct cached_dirent`
  - Represents one cached directory entry with name, length, logical position, and CIFS file attributes.
- `struct cached_dirents`
  - Holds per-open-file directory entry cache state, including validity/failure flags, associated file, mutex, expected position, entry list, and byte/entry accounting.
- `struct cached_fid`
  - Represents a cached directory FID with list membership, path, lease/open state, file-all-info validity, timestamps, kref, SMB FID, tcon, dentry, work items, cached dirents, and embedded `smb2_file_all_info`.
- `struct cached_fids`
  - Per-tcon cache container with spinlock, active and dying lists, laundromat delayed work, and aggregate directory-entry accounting.
- Declares global directory-cache byte accounting `cifs_dircache_bytes_used`.
- Defines `is_valid_cached_dir()` as `time && has_lease`.
- Declares open, close, drop, invalidate, free, and lease-break functions implemented in `cached_dir.c`.

## Integration Notes

- Includes only declarations and data shapes; actual locking/lifetime behavior is implemented in `cached_dir.c`.
- Structures are tightly coupled to CIFS tcon/session, SMB2 FID, lease, and file-all-info types.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/cached_dir.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/cifs_debug.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/cifs_debug.c

## Purpose

Implements CIFS/SMB client debug dumping, `/proc/fs/cifs` diagnostics and tunables, statistics reset/reporting, open-file/open-directory reporting, security-flag control, mount-parameter introspection, and optional RDMA debug tunables.

## Main Responsibilities

- Raw debug helpers:
  - `cifs_dump_mem()` prints hex dumps.
  - `cifs_dump_mids()` prints pending MID request details under `CONFIG_CIFS_DEBUG2`.
- Tcon/server/session formatting:
  - `cifs_debug_tcon()` reports share mount count, filesystem type, device info, path limits, status, encryption, POSIX extensions, witness, sparse behavior, reconnect state, and DFS origin path.
  - `cifs_dump_channel()` reports multichannel connection details.
  - `cifs_dump_iface()` reports server interface speed, RSS/RDMA capabilities, IP address, cleanup state, channel allocation, and connection state.
- `/proc/fs/cifs/open_files`:
  - `cifs_debug_files_proc_show()` lists tree/session/FID/flags/count/pid/uid/name plus lease state, lease key, and optional MID.
- `/proc/fs/cifs/open_dirs`:
  - `cifs_debug_dirs_proc_show()` lists cached directory handles and per-cache dirent accounting.
  - Under `CONFIG_CIFS_DEBUG`, writes of `0` invalidate all cached directories across CIFS mounts.
- `/proc/fs/cifs/DebugData`:
  - `cifs_debug_data_proc_show()` prints CIFS version, compiled feature set, buffer size, active request count, servers, sessions, channels, shares, interfaces, pending MIDs, compression/encryption state, and SWN registrations.
- `/proc/fs/cifs/Stats`:
  - `cifs_stats_proc_show()` reports allocation/resource counts, reconnect counts, active XID stats, per-server request stats, and per-tcon operation stats.
  - `cifs_stats_proc_write()` resets statistics and reconnect counters.
- Proc tunables:
  - `cifsFYI` controls CIFS debug verbosity bitmask.
  - `traceSMB` toggles SMB tracing.
  - `LinuxExtensionsEnabled` toggles legacy Linux extensions.
  - `LookupCacheEnabled` toggles lookup-cache behavior.
  - `SecurityFlags` validates and sets global security policy flags.
  - `mount_params` lists supported SMB3 mount parameters and parameter types.
- Proc registration:
  - `cifs_proc_init()` creates `/proc/fs/cifs` entries.
  - `cifs_proc_clean()` removes them.
  - Stubs are provided when `CONFIG_PROC_FS` is disabled.

## Key Data/Control Flow

- Most proc output walks the global `cifs_tcp_ses_list`, then nested session, tcon, open-file, channel, and MID lists.
- Global/session/tcon locks are taken around list traversal and mutable fields:
  - `cifs_tcp_ses_lock`
  - `server->srv_lock`
  - `ses->ses_lock`
  - `ses->chan_lock`
  - `ses->iface_lock`
  - `tcon->tc_lock`
  - `tcon->open_file_lock`
  - `server->mid_queue_lock`
  - cached-dir list locks
- Feature lines are controlled by compile-time Kconfig symbols.
- Security flag writes support boolean shortcuts and numeric flags, reject zero/unsupported flags, normalize MUST flags, and imply MAY_SIGN when signing is required.

## Security and Exposure Notes

- Key dumping is controlled by separate Kconfig (`CIFS_DEBUG_DUMP_KEYS`) elsewhere, but debug output still exposes session IDs, user IDs, server names, share names, FIDs, and network addresses.
- `/proc/fs/cifs/open_files` is mode `0400`; writable debug/tunable entries are generally `0644` or `0600` for `open_dirs` with debug enabled.
- `SecurityFlags` writes directly affect global CIFS module security behavior.

## Integration Notes

- Relies heavily on `seq_file` helpers from `fs/seq_file.c`.
- Integrates optional DFS, SMB Direct, SWN, compression, stats2, legacy, POSIX, upcall, and xattr features through preprocessor gates.
- Calls `cifs_swn_dump()` so witness registrations appear in DebugData.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/cifs_debug.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/cifs_debug.h -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/cifs_debug.h

## Purpose

Defines CIFS debug/logging macros, debug levels, exported debug-control variables, and debug helper prototypes.

## Main Contents

- Resets `pr_fmt` to prefix messages with `CIFS:`.
- Declares debug helpers:
  - `cifs_dump_mem()`
  - `cifs_dump_mids()`
  - `dump_smb()`
- Declares global controls:
  - `traceSMB`
  - `cifsFYI`
- Defines debug-level bits:
  - `CIFS_INFO`, `CIFS_RC`, `CIFS_TIMER`
  - message classes `VFS`, `FYI`, optional `NOISY`, and `ONCE`.
- Under `CONFIG_CIFS_DEBUG`, defines:
  - `cifs_info()`
  - `cifs_dbg()`
  - `cifs_server_dbg()`
  - `cifs_tcon_dbg()`
  - Each supports rate-limited or once-only logging and routes VFS messages to error logs, FYI/NOISY to debug logs.
- Without `CONFIG_CIFS_DEBUG`, debug macros compile to unreachable `pr_debug()` forms while preserving format checking; `cifs_info()` remains active.

## Integration Notes

- `cifs_server_dbg()` takes `server->srv_lock` to safely print the hostname.
- `cifs_tcon_dbg()` tolerates null tcon/tree names.
- Used throughout CIFS client code for consistent logging policy.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/cifs_debug.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/cifs_fs_sb.h -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/cifs_fs_sb.h

## Purpose

Defines CIFS superblock mount flags and `struct cifs_sb_info`, the CIFS per-superblock state container.

## Main Contents

- Mount flag bit definitions for permission behavior, uid/gid override, server inode numbers, direct I/O, xattr disable, special-character remapping, POSIX paths/ACLs, Unix emulation, byte-range lock behavior, CIFS ACLs, dynamic permissions, sync behavior, FS-Cache, Minshall+French symlinks, multiuser, strict I/O, PID forwarding, backup uid/gid intent, prefix-path mounting, SID-derived uid/mode, handle-cache disable, DFS disable, read-only/read-write cache assumptions, and shutdown state.
- `struct cifs_sb_info` fields:
  - tcon link tree and lock.
  - superblock tcon list link.
  - master tlink.
  - local NLS table.
  - parsed mount context.
  - active count and atomic mount flags.
  - delayed tlink pruning work.
  - RCU head.
  - optional prefix path.
  - serverino-autodisabled state.
  - root dentry after mount completion.

## Integration Notes

- The mount flags are consumed by path conversion, permission, cache, DFS, handle-cache, ACL, xattr, and I/O behavior throughout the CIFS client.
- `cifs_remap()` in `cifs_unicode.h` interprets the special-character remapping flags from this header.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/cifs_fs_sb.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/cifs_ioctl.h -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/cifs_ioctl.h

## Purpose

Defines userspace ABI structures and ioctl numbers for CIFS/SMB3 mount information, tcon information, snapshots, passthrough query/set/fsctl operations, debug key dumping, notifications, copychunk, integrity, and shutdown.

## Main Contents

- `struct smb_mnt_fs_info`
  - Packed mount/share/filesystem metadata including version, protocol, tcon flags, volume serial/time, share caps/flags, sector info, chunk size, filesystem attributes, component length, device type/characteristics, maximal access, and POSIX capabilities.
- `struct smb_mnt_tcon_info`
  - Packed tree ID and session ID.
- `struct smb_snapshot_array`
  - Snapshot enumeration header with flexible trailing snapshot data.
- `struct smb_query_info`
  - Passthrough query/set/fsctl parameters plus variable trailing buffer.
- `struct smb3_key_debug_info`
  - Legacy fixed-size key dump structure for common 16-byte keys.
- `struct smb3_full_key_debug_info`
  - Variable-size key dump structure supporting longer session/encryption keys.
- `struct smb3_notify` and `struct smb3_notify_info`
  - Change-notify request and response structures.
- Defines ioctl numbers using magic `0xCF` for CIFS operations and `'X',125` for shutdown.
- Defines shutdown behavior flags:
  - default
  - log flush only
  - no log flush

## Security and ABI Notes

- Key dump ioctls intentionally expose session/encryption key material and should be gated by build/runtime policy in users of this header.
- All structs are packed, making field ordering and sizes ABI-sensitive.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/cifs_ioctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/cifs_spnego.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/cifs_spnego.c

## Purpose

Implements CIFS SPNEGO request-key integration for Kerberos-like session setup, including a private key type, private credential/keyring setup, authority-checked key descriptions, and construction of cifs.upcall request descriptions.

## Main Responsibilities

- Defines key type `cifs.spnego`:
  - `cifs_spnego_key_instantiate()` duplicates upcall payload into key storage.
  - `cifs_spnego_key_destroy()` frees payload.
  - `cifs_spnego_key_vet_description()` rejects userspace-created descriptions unless current credentials are the private CIFS SPNEGO credentials.
  - Uses `user_describe()` for key description.
- Implements `cifs_get_spnego_key()`:
  - Builds a key description containing upcall version, hostname, server IP, selected security mechanism, linux uid, credential uid, optional username, pid, and upcall target.
  - Supports IPv4 and IPv6 server addresses.
  - Selects `sec=krb5`, `sec=mskrb5`, or `sec=iakerb`, defaulting to `krb5` if server auth flags are unknown.
  - Calls `request_key()` under `spnego_cred`.
  - Traces Kerberos auth result and optionally dumps returned blobs under debug.
- Implements initialization and cleanup:
  - `init_cifs_spnego()` creates kernel credentials, allocates a private `.cifs_spnego` thread keyring, registers the key type, and configures request-key caching.
  - `exit_cifs_spnego()` revokes the keyring, unregisters the key type, and releases credentials.

## Key Data/Control Flow

- The private `spnego_cred` is both a request credential and a gate: only code executing with it can create valid `cifs.spnego` keys.
- The key description is treated as authority-bearing input to userspace `cifs.upcall`.
- Upcall target is explicitly encoded as `mount` or `app`.
- Returned key payload is expected to contain `struct cifs_spnego_msg` from `cifs_spnego.h`.

## Security Notes

- `vet_description` prevents arbitrary userspace `add_key()`/`request_key()` from injecting privileged CIFS SPNEGO descriptions.
- The request keyring is root-owned, root-clearable, and not quota-accounted.
- Debug blob dumping can expose authentication material when extra debugging is enabled.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/cifs_spnego.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/cifs_spnego.h -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/cifs_spnego.h

## Purpose

Declares the CIFS SPNEGO upcall ABI message, version, key type, and key acquisition helper.

## Main Contents

- Defines `CIFS_SPNEGO_UPCALL_VERSION` as `2`.
- Defines `struct cifs_spnego_msg`:
  - version
  - flags
  - session-key length
  - security-blob length
  - flexible payload containing session key followed by security blob
- Declares external key type `cifs_spnego_key_type`.
- Declares `cifs_get_spnego_key()`.

## Integration Notes

- Used by CIFS session setup and `cifs_spnego.c`.
- The structure is part of the contract with the userspace request-key helper.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/cifs_spnego.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/cifs_swn.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/cifs_swn.c

## Purpose

Implements CIFS client integration with the SMB Service Witness Protocol userspace daemon through generic netlink, tracking witness registrations and reacting to resource state changes or client-move notifications.

## Main Responsibilities

- Maintains witness registrations:
  - Global IDR `cifs_swnreg_idr` maps registration IDs to `struct cifs_swn_reg`.
  - `cifs_find_swn_reg()` matches tcons by extracted network and share names.
  - `cifs_get_swn_reg()` reuses or allocates registrations, assigns IDs, stores notify flags, and records the tcon.
  - `cifs_put_swn_reg()` drops references and calls `cifs_swn_reg_release()` on the final put.
- Sends netlink messages:
  - `cifs_swn_send_register_message()` builds `CIFS_GENL_CMD_SWN_REGISTER` messages with registration ID, network name, share name, IP, notify flags, and Kerberos or NTLM authentication info.
  - `cifs_swn_send_unregister_message()` builds unregister messages.
  - `cifs_swn_check()` re-sends register messages for all registrations, used for retry/health checks.
- Handles authentication attributes:
  - `cifs_swn_auth_info_krb()` marks Kerberos auth.
  - `cifs_swn_auth_info_ntlm()` sends username, password, and domain when present.
- Handles notifications:
  - `cifs_swn_notify()` validates registration ID and notification type attributes.
  - Resource changes call `cifs_swn_resource_state_changed()` and trigger reconnect for available/unavailable states.
  - Client-move notifications parse an address and call `cifs_swn_client_move()`.
- Handles witness-directed reconnect:
  - `cifs_swn_reconnect()` stores a new destination address/port, toggles `use_swn_dstaddr`, unregisters old witness state, registers new witness state, and signals cifsd reconnect.
  - `cifs_swn_store_swn_addr()` preserves the old server port when storing the new address.
- Provides `cifs_swn_dump()` for DebugData witness registration reporting.

## Key Data/Control Flow

- Registration identity is network name plus share name extracted from `tcon->tree_name`.
- Scaleout shares enable IP notifications via `SMB2_SHARE_CAP_SCALEOUT`.
- Register messages use the stored SWN destination address if a move/reconnect target is active; otherwise they use the server destination address.
- `cifs_swn_register()` intentionally returns success even if sending the register message fails, because the echo task can retry.
- Reconnect stores the alternate destination while holding the server lock and avoids doing work if the notified address is already the current destination.

## Concurrency and Lifetime Notes

- `cifs_swnreg_idr_mutex` protects the registration IDR, registration lookup, allocation, refcount put, and debug dumping.
- Registrations hold raw `tcon` pointers and assume tcon lifetime is managed by the caller/register-unregister integration.

## Security and Exposure Notes

- NTLM witness registration messages may include username, password, and domain attributes to the userspace daemon.
- Kerberos mode sends only a Kerberos auth flag.
- Notification attributes are validated for presence before use, but the code trusts the registered userspace netlink family path for delivery semantics.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/cifs_swn.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/cifs_swn.h -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/cifs_swn.h

## Purpose

Declares the CIFS Service Witness Protocol interface and provides no-op stubs when SWN upcall support is not configured.

## Main Contents

- Forward declares `struct cifs_tcon`, `struct sk_buff`, and `struct genl_info`.
- Under `CONFIG_CIFS_SWN_UPCALL`, declares:
  - `cifs_swn_register()`
  - `cifs_swn_unregister()`
  - `cifs_swn_notify()`
  - `cifs_swn_dump()`
  - `cifs_swn_check()`
- Defines inline server destination helpers:
  - `cifs_swn_set_server_dstaddr()` switches `server->dstaddr` to `server->swn_dstaddr` when `use_swn_dstaddr` is set.
  - `cifs_swn_reset_server_dstaddr()` clears `use_swn_dstaddr`.
- Without `CONFIG_CIFS_SWN_UPCALL`, provides no-op or false-returning inline stubs.

## Integration Notes

- Lets the rest of CIFS call witness hooks unconditionally while compiling out behavior when the feature is disabled.
- Destination-address helpers are still part of the conditional SWN behavior because they modify reconnect target selection.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/cifs_swn.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/cifs_unicode.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/cifs_unicode.c

## Purpose

Implements CIFS Unicode and local-codepage conversion helpers, including UTF-16LE wire-format conversion, SFU/SFM reserved-character remapping, surrogate-pair/IVS handling for UTF-8, and allocation helpers for converted strings.

## Main Responsibilities

- Converts reserved Unicode/private-use characters back to local characters:
  - `convert_sfu_char()` handles SFU mapchars for colon, asterisk, question, pipe, greater-than, and less-than.
  - `convert_sfm_char()` handles SFM private-use mappings, control characters, and special trailing space/period mappings.
- Converts UTF-16LE from server to local codepage:
  - `cifs_mapchar()` maps one UTF-16 character or UTF-8 surrogate/IVS sequence to local bytes, falling back to `?`.
  - `cifs_from_utf16()` converts a bounded UTF-16LE buffer into a null-terminated local string with overflow checks.
  - `cifs_utf16_bytes()` computes converted byte length excluding the null terminator.
  - `cifs_strndup_from_utf16()` allocates and converts server strings, or duplicates non-Unicode strings.
- Converts local strings to UTF-16LE wire format:
  - `cifs_strtoUTF16()` converts local strings using the supplied NLS table, with a UTF-8 fast path through `utf8s_to_utf16s()`.
  - `convert_to_sfu_char()` and `convert_to_sfm_char()` map local reserved characters to SFU/SFM Unicode values.
  - `cifsConvertToUTF16()` converts path strings to UTF-16LE while optionally applying SFU/SFM remapping and handling UTF-8 surrogate pairs/IVS.
  - `cifs_local_to_utf16_bytes()` computes required UTF-16 byte length.
  - `cifs_strndup_to_utf16()` allocates and converts local strings to null-terminated UTF-16LE.

## Key Data/Control Flow

- `cifs_from_utf16()` walks 16-bit words with unaligned little-endian reads and keeps a three-word lookahead for surrogate/IVS conversion.
- Destination overflow is avoided by switching to temporary conversion near the end of the output buffer and breaking before the null terminator would be overrun.
- UTF-8 surrogate/IVS support is only attempted when the active codepage name is `"utf8"`.
- `cifsConvertToUTF16()` treats SFM trailing space/period remapping per path component, while preserving special `.` and `..` symlink components.
- Slash/backslash remapping is explicitly not supported because path builders use separators internally.

## Integration Notes

- Uses CIFS mount flags through `cifs_remap()` in `cifs_unicode.h` to choose no remap, SFU remap, or SFM remap.
- Uses kernel NLS table callbacks `char2uni()` and `uni2char()`.
- Wire format is little-endian UTF-16 as required by SMB paths and names.

## Correctness and Risk Notes

- Conversion failures fall back to question mark rather than returning errors in most paths.
- `cifsConvertToUTF16()` allocates a small temporary UTF-16 buffer for UTF-8 surrogate handling; if unavailable, it falls back to `?`.
- `cifs_strndup_to_utf16()` sizes allocation using conversion byte count but calls conversion with `strlen(src)`, so callers must pass properly null-terminated strings.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/cifs_unicode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/cifs_unicode.h -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/cifs_unicode.h

## Purpose

Declares CIFS Unicode conversion APIs and constants for SFM/SFU reserved-character remapping.

## Main Contents

- Defines SFM private-use code points for double quote, asterisk, question mark, colon, greater-than, less-than, pipe, slash, trailing space, and trailing period.
- Defines remap modes:
  - `NO_MAP_UNI_RSVD`
  - `SFM_MAP_UNI_RSVD`
  - `SFU_MAP_UNI_RSVD`
- Declares conversion helpers:
  - `cifs_from_utf16()`
  - `cifs_utf16_bytes()`
  - `cifs_strtoUTF16()`
  - `cifs_strndup_from_utf16()`
  - `cifsConvertToUTF16()`
  - `cifs_strndup_to_utf16()`
  - `cifs_toupper()`
- Defines `cifs_remap()` inline helper:
  - Returns SFM remap if `CIFS_MOUNT_MAP_SFM_CHR` is set.
  - Returns SFU remap if `CIFS_MOUNT_MAP_SPECIAL_CHR` is set.
  - Otherwise returns no remapping.

## Integration Notes

- Includes NLS and UCS2 utility headers.
- Ties path/name conversion behavior directly to CIFS superblock mount flags from `cifs_fs_sb.h`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/cifs_unicode.h -->