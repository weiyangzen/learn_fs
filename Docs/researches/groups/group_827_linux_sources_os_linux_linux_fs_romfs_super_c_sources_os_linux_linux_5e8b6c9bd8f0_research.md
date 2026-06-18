# Group Research: group_827_linux_sources_os_linux_linux_fs_romfs_super_c_sources_os_linux_linux_5e8b6c9bd8f0

Scope: `Docs/research_subset_a.md` includes `sources/os/linux/linux`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/romfs/super.c -->
# File Research: sources/os/linux/linux/fs/romfs/super.c

ROMFS superblock, inode, directory, page-cache read, mount, and module lifecycle implementation for block-backed and MTD-backed ROMFS images.

Key functions include `romfs_read_folio()`, `romfs_readdir()`, `romfs_lookup()`, `romfs_iget()`, `romfs_fill_super()`, `romfs_get_tree()`, `romfs_kill_sb()`, and module init/exit registration. The file maps ROMFS on-disk file header types to Linux inode modes and directory entry dtypes.

Mount validation reads the first 512 bytes, checks ROMFS magic words, image size, MTD bounds, and checksum, then computes the root inode offset from the volume name length. The filesystem is forced read-only and no-atime; reconfigure also forces `SB_RDONLY`.

Directory traversal follows ROMFS linked file headers through `ri.next`, uses `romfs_dev_*` helpers from `internal.h`, handles hard-link entries by switching inode number/source offset to `ri.spec`, and emits dentries through VFS helpers.

Notable invariants: inode number is the ROMFS image offset, data offset is metadata size aligned by `ROMFH_MASK`, and all reads must stay below `romfs_maxsize()`. Error paths generally return `-EIO`, `-EINVAL`, or allocation failures; `romfs_readdir()` suppresses device-read errors by returning `0` after `goto out`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/romfs/super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/select.c -->
# File Research: sources/os/linux/linux/fs/select.c

Implements Linux `select(2)`, `pselect(2)`, `poll(2)`, and `ppoll(2)`, including native, old-time32, and compat syscall variants.

The shared wait machinery is `poll_wqueues`: `poll_initwait()`, `__pollwait()`, `pollwake()`, `poll_schedule_timeout()`, and `poll_freewait()`. Wait entries are stored inline first, then in page-sized `poll_table_page` allocations, with wakeup memory barriers pairing `pollwake()` and `poll_schedule_timeout()`.

The `select` path copies three fd bitmaps from userspace, validates selected descriptors with `max_select_fd()`, loops through ready masks in `do_select()`, writes result bitmaps back, and uses `poll_select_finish()` to restore signal masks and optionally update remaining timeout.

The `poll` path chunks userspace `struct pollfd` arrays into a stack-first `poll_list` plus page allocations, calls `do_pollfd()`/`vfs_poll()` for each entry, writes only `revents` back, and supports restart through `do_restart_poll()`.

Timeout logic converts relative timeval/timespec inputs into absolute `timespec64`, estimates scheduling slack from task niceness and `current->timer_slack_ns`, rejects invalid negative/unnormalized values, and preserves `STICKY_TIMEOUTS` behavior. Network busy-poll support is integrated through `POLL_BUSY_LOOP`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/select.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/seq_file.c -->
# File Research: sources/os/linux/linux/fs/seq_file.c

Generic kernel sequential-file framework used by procfs/debugfs-style synthetic files.

Core lifecycle APIs are `seq_open()`, `seq_read_iter()`, `seq_read()`, `seq_lseek()`, and `seq_release()`. The framework owns `struct seq_file`, serializes reads/seeks with `m->lock`, lazily allocates and grows the buffer, and drives caller-provided `seq_operations` callbacks.

Read traversal handles arbitrary `ki_pos` by replaying records via `traverse()`, supports `SEQ_SKIP`, detects buggy `.next()` implementations that do not advance position, and doubles the buffer on overflow until `MAX_RW_COUNT` prevents further growth.

Formatting helpers include `seq_printf()`, `seq_vprintf()`, `seq_escape_mem()`, pathname printers, decimal/hex fast paths, `seq_write()`, `seq_pad()`, and `seq_hex_dump()`. Single-record helpers include `single_open()`, `single_open_size()`, and `single_release()`.

Iterator helpers cover `list_head`, RCU lists, `hlist`, RCU hlists, and percpu hlists. `seq_file_init()` creates the global `seq_file` slab cache.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/seq_file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/signalfd.c -->
# File Research: sources/os/linux/linux/fs/signalfd.c

Implements `signalfd(2)` and `signalfd4(2)`, exposing pending signals as records readable from an anonymous inode file descriptor.

`struct signalfd_ctx` stores the effective blocked-signal mask. `do_signalfd4()` creates a new anon inode file or updates an existing signalfd, validates `SFD_CLOEXEC`/`SFD_NONBLOCK`, removes uncatchable `SIGKILL`/`SIGSTOP`, then inverts the mask with `signotset()` for internal matching.

`signalfd_poll()` waits on `current->sighand->signalfd_wqh` and checks private and shared pending queues under `siglock`. `signalfd_dequeue()` dequeues or sleeps interruptibly; `signalfd_read_iter()` returns one or more fixed-size `struct signalfd_siginfo` records and switches to nonblocking behavior after the first signal.

`signalfd_copyinfo()` translates `kernel_siginfo_t` layouts into the stable 128-byte userspace ABI, explicitly handling kill, timer, poll, fault, child, realtime, and syscall signal layouts.

Compat syscall wrappers convert `compat_sigset_t` and forward into the native implementation. Proc fdinfo support renders the user-visible signal mask.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/signalfd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/Kconfig -->
# File Research: sources/os/linux/linux/fs/smb/Kconfig

Top-level SMB filesystem Kconfig aggregator.

It sources client, server, and SMB Direct Kconfig files, then defines `SMBFS` as a tristate umbrella symbol selected by `CIFS` or `SMB_SERVER`. This lets common SMB code build when either client or server is enabled.

It also defines `SMB_KUNIT_TESTS`, gated by `SMBFS && KUNIT`, defaulting to `KUNIT_ALL_TESTS`, and documents that these tests are developer-only boot-time TAP-output tests.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/Makefile -->
# File Research: sources/os/linux/linux/fs/smb/Makefile

Top-level Kbuild dispatcher for SMB subdirectories.

It builds `common/` under `CONFIG_SMBFS`, `smbdirect/` under `CONFIG_SMBDIRECT`, `client/` under `CONFIG_CIFS`, and `server/` under `CONFIG_SMB_SERVER`. There is no local object logic beyond subdirectory selection.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/Kconfig -->
# File Research: sources/os/linux/linux/fs/smb/client/Kconfig

Configuration surface for the CIFS/SMB2/SMB3 kernel client.

`CONFIG_CIFS` is the main tristate and selects networking, NLS, crypto primitives, keys, DNS resolver, ASN.1/OID support, and netfs support. Its help text positions SMB3.1.1 as the preferred modern dialect while retaining older CIFS/SMB support.

Feature toggles cover extended stats, insecure legacy dialects, SPNEGO upcalls, xattrs, CIFS POSIX extensions, debug levels, unsafe key dumping, DFS upcalls, SWN witness upcalls, broken NFSD export support, SMB Direct/RDMA, fscache, SMB rootfs, compression, and SMB1 KUnit tests.

Important dependency constraints include `CIFS_POSIX` requiring insecure legacy and xattrs, `CIFS_SMB_DIRECT` requiring InfiniBand address translation and compatible built-in/module combinations, and `CIFS_FSCACHE` matching CIFS/FSCACHE linkage.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/Makefile -->
# File Research: sources/os/linux/linux/fs/smb/client/Makefile

Kbuild recipe for the CIFS/SMB client module.

The base `cifs.o` object aggregates core client sources such as tracing, VFS glue, debug, connection/session/transport, cached directories, Unicode conversion, SMB2 operations, ACLs, namespace/reparse handling, DNS resolution, ASN.1 SPNEGO parser generation, and mount context support.

Optional object groups are added for xattrs, SPNEGO, DFS, SWN netlink, fscache, SMB Direct, rootfs, legacy SMB1, and compression. SMB1 and SMB2 error mapping tables are generated by Perl scripts at build time, with generated files tracked via `targets`.

KUnit test objects are selected by `CONFIG_SMB1_KUNIT_TESTS` and `CONFIG_SMB_KUNIT_TESTS`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/asn1.c -->
# File Research: sources/os/linux/linux/fs/smb/client/asn1.c

ASN.1 decoder callbacks for CIFS SPNEGO negotiation-token parsing.

`decode_negTokenInit()` invokes the generated `cifs_spnego_negtokeninit_decoder` against a server context and returns boolean success. `cifs_gssapi_this_mech()` validates that the outer GSSAPI mechanism OID is SPNEGO, logging and returning `-EBADMSG` on unexpected OIDs.

`cifs_neg_token_init_mech_type()` records advertised mechanism support into `TCP_Server_Info` flags for Microsoft Kerberos, Kerberos user-to-user, Kerberos, NTLMSSP, and IAKERB. Unsupported OIDs are logged at FYI level but are not fatal.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/asn1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/cached_dir.c -->
# File Research: sources/os/linux/linux/fs/smb/client/cached_dir.c

Implements SMB2/SMB3 cached directory handles and cached directory-entry lifetime management.

`open_cached_dir()` is the central path: it finds or creates a `cached_fid`, converts the path to UTF-16, resolves a dentry, optionally uses a parent lease key, sends a compounded SMB2 CREATE plus QUERY_INFO, requires a lease with read caching, stores file-all-info, and returns a referenced cached handle. Replayable errors can retry with SMB2 replay markers.

The cache is keyed by path and stored under `cached_fids->entries`, protected by `cfid_list_lock`. A cached handle is usable only when `is_valid_cached_dir()` sees both `time` and `has_lease`; construction sets `has_lease` early so lease-break handling can safely consume the lease reference before the handle is visible.

Release paths are split carefully: `close_cached_dir()` is lock-safe external put, `close_cached_dir_locked()` is only for callers already holding `cfid_list_lock` and expecting at least two refs, and `smb2_close_cached_fid()` removes from lists, drops dentries, closes the SMB handle, and frees cache memory.

Invalidation occurs by name, by tcon reset, by lease break, by unmount, and by laundromat timeout. Lease breaks remove the entry, clear validity, take a tcon reference, drop the dentry asynchronously, then queue server-close work.

`free_cached_dir()` also frees cached dirents and subtracts tcon/global cache accounting. `init_cached_dirs()` initializes lists, counters, and delayed laundromat work; `free_cached_dirs()` cancels work and frees remaining active/dying entries.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/cached_dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/cached_dir.h -->
# File Research: sources/os/linux/linux/fs/smb/client/cached_dir.h

Declares CIFS cached directory data structures and public cache APIs.

`cached_dirent` stores a cached readdir entry name, position, and file attributes. `cached_dirents` tracks per-open-file dirent cache validity, failure, expected position, mutex, list, and accounting.

`cached_fid` represents a cached directory handle, including path, lease/open/list/file-info validity flags, timestamps, refcount, SMB fid, tcon, dentry, async work items, dirent cache, and embedded `smb2_file_all_info`.

`cached_fids` is the per-tcon cache container with a spinlock, active and dying lists, delayed laundromat work, and aggregate counters. The exported API opens, finds, closes, drops, invalidates, and lease-breaks cached directories.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/cached_dir.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/cifs_debug.c -->
# File Research: sources/os/linux/linux/fs/smb/client/cifs_debug.c

CIFS/SMB client debug and procfs implementation.

The file provides memory/MID dumping helpers, `/proc/fs/cifs/DebugData`, `open_files`, `open_dirs`, `Stats`, runtime toggles, security flag control, mount parameter listing, and optional SMB Direct tunables. When procfs is disabled, `cifs_proc_init()` and `cifs_proc_clean()` are empty.

DebugData walks global server/session/tcon structures under `cifs_tcp_ses_lock`, printing negotiated features, credits, dialects, compression/encryption, session security, multichannel state, tree connections, interfaces, pending MIDs, and SWN registrations. It calls protocol/server ops for dialect-specific details.

`open_files` reports tree/session/fid/flags/refcount/pid/uid/dentry plus lease cache state and lease key. `open_dirs` reports cached directory handles and, under `CONFIG_CIFS_DEBUG`, accepts write `0` to invalidate all cached dirs.

`Stats` reports allocation/resource counters and per-server/per-tcon statistics; writing a boolean resets counters and per-command timing under the appropriate locks.

Runtime proc knobs update `cifsFYI`, `traceSMB`, `linuxExtEnabled`, `lookupCacheEnabled`, and `global_secflags`. Security flag writes validate mask bits, normalize MUST-vs-MAY choices, prefer stronger MUST options, and ensure required signing implies signing allowed.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/cifs_debug.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/cifs_debug.h -->
# File Research: sources/os/linux/linux/fs/smb/client/cifs_debug.h

CIFS debug macro and declaration header.

It sets CIFS log formatting, declares dump helpers and global debug flags, and defines message classes `VFS`, `FYI`, optional `NOISY`, and `ONCE`.

With `CONFIG_CIFS_DEBUG`, `cifs_dbg()`, `cifs_server_dbg()`, and `cifs_tcon_dbg()` dispatch to rate-limited or once-only printk variants, include contextual server/tcon names where applicable, and respect `cifsFYI` for FYI output. Without debug, most macros compile to inert `if (0) pr_debug(...)` forms while `cifs_info()` remains active.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/cifs_debug.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/cifs_fs_sb.h -->
# File Research: sources/os/linux/linux/fs/smb/client/cifs_fs_sb.h

CIFS superblock-private state and mount-flag definitions.

The `CIFS_MOUNT_*` bitmask covers permission checking, UID/GID overrides, server inode numbers, direct I/O, xattrs, special-character remapping, POSIX paths/ACLs, Unix emulation, byte-range locking behavior, fscache, symlink mode, multiuser, strict I/O, backup intent, DFS disablement, SID-derived UID/mode, handle-cache disablement, read/write cache assumptions, and shutdown.

`struct cifs_sb_info` stores tcon links in an rbtree, list linkage, locks, master tlink, NLS table, parsed mount context, active count, atomic mount flags, prune work, RCU head, optional prefix path, serverino autodisable state, and root dentry.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/cifs_fs_sb.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/cifs_ioctl.h -->
# File Research: sources/os/linux/linux/fs/smb/client/cifs_ioctl.h

Userspace ioctl ABI structures and command numbers for CIFS/SMB3.

It defines packed mount/share info structs, snapshot enumeration header, passthrough query/fsctl/set-info request header, key-dump debug structures, and notify request/response structures.

Ioctls include copychunk, set integrity, get mount info, enumerate snapshots, query info, dump session/encryption keys, notify, full key dump, get tcon info, and shutdown. The file also defines shutdown mode flags for going-down behavior.

Security-sensitive note: key-dump structs expose encryption/session material and are intended for debug paths guarded elsewhere by config and ioctl handling.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/cifs_ioctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/cifs_spnego.c -->
# File Research: sources/os/linux/linux/fs/smb/client/cifs_spnego.c

SPNEGO/Kerberos request-key integration for CIFS session setup.

Defines key type `cifs.spnego`, with instantiate/destroy handlers that copy/free upcall payloads. `cifs_spnego_key_vet_description()` rejects userspace-created descriptions unless the current credentials are the private CIFS SPNEGO credentials, because descriptions contain authority-bearing kernel-originated fields.

`cifs_get_spnego_key()` builds a semicolon-delimited request-key description containing upcall version, host, IP address, security mechanism, uid, cred uid, optional username, pid, and upcall target. It then calls `request_key()` under the private `spnego_cred`.

`init_cifs_spnego()` creates a kernel credential with a private `.cifs_spnego` thread keyring, registers the key type, marks the keyring root-clearable, and stores it for scoped upcalls. `exit_cifs_spnego()` revokes the keyring, unregisters the key type, and drops credentials.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/cifs_spnego.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/cifs_spnego.h -->
# File Research: sources/os/linux/linux/fs/smb/client/cifs_spnego.h

SPNEGO upcall ABI header for CIFS.

Defines `CIFS_SPNEGO_UPCALL_VERSION` as `2` and the variable-length `cifs_spnego_msg` payload returned by userspace: version, flags, session-key length, security-blob length, and concatenated data.

Exports the `cifs.spnego` key type and declares `cifs_get_spnego_key()`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/cifs_spnego.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/cifs_swn.c -->
# File Research: sources/os/linux/linux/fs/smb/client/cifs_swn.c

Service Witness Notification client integration for CIFS high-availability shares.

Registrations are stored in a global IDR protected by `cifs_swnreg_idr_mutex`; `struct cifs_swn_reg` records registration id, refcount, network/share names, notification flags, and tcon. Registration lookup deduplicates by extracted host/share names.

`cifs_swn_send_register_message()` and `_unregister_message()` send generic-netlink multicast messages to userspace with registration id, network/share name, server IP, notification flags, and authentication info. Kerberos is represented by a flag; NTLM variants include username/password/domain when present.

Incoming `cifs_swn_notify()` validates registration id and notification type, then handles resource state changes by signaling reconnect, and client-move notifications by storing a new SWN destination address, unregistering from the old address, registering for the new one, and reconnecting.

Address handling preserves the previous SMB port while switching IPv4/IPv6 addresses. `cifs_swn_dump()` renders registrations into seq_file output, and `cifs_swn_check()` resends register messages for all current registrations.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/cifs_swn.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/cifs_swn.h -->
# File Research: sources/os/linux/linux/fs/smb/client/cifs_swn.h

Header for CIFS Service Witness Notification support.

When `CONFIG_CIFS_SWN_UPCALL` is enabled, it declares register/unregister/notify/dump/check functions and provides helpers to temporarily use `server->swn_dstaddr` as `server->dstaddr`.

When disabled, it provides no-op inline stubs so callers can compile without feature-specific conditionals.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/cifs_swn.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/cifs_unicode.c -->
# File Research: sources/os/linux/linux/fs/smb/client/cifs_unicode.c

CIFS local-codepage and UTF-16LE conversion implementation, including SMB reserved-character remapping.

Inbound conversion maps UTF-16LE server strings to the local NLS codepage through `cifs_from_utf16()`, using `cifs_mapchar()` to apply SFM/SFU reverse mappings, codepage conversion, UTF-8 surrogate/variation-sequence fallback, and `?` substitution for unknown characters.

Outbound conversion is handled by `cifs_strtoUTF16()` for direct conversion and `cifsConvertToUTF16()` when reserved-character remapping is requested. SFU maps POSIX-reserved characters to Unicode private/reserved values; SFM maps control characters and Mac-style private-use values, including end-of-component period/space handling while preserving `.` and `..`.

Length/allocation helpers include `cifs_utf16_bytes()`, `cifs_strndup_from_utf16()`, `cifs_local_to_utf16_bytes()`, and `cifs_strndup_to_utf16()`. The implementation uses unaligned little-endian access because SMB wire strings may not be naturally aligned.

Known constraints are documented in comments: slash/backslash remapping is avoided because path-building code treats those as separators.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/cifs_unicode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/cifs_unicode.h -->
# File Research: sources/os/linux/linux/fs/smb/client/cifs_unicode.h

Unicode conversion and reserved-character remapping API for CIFS.

Defines SFM private-use mappings for characters illegal or special on SMB/NTFS paths, plus remap modes `NO_MAP_UNI_RSVD`, `SFM_MAP_UNI_RSVD`, and `SFU_MAP_UNI_RSVD`.

Declares UTF-16 conversion, duplication, length, and uppercasing helpers. `cifs_remap()` derives the active remap mode from mount flags, preferring SFM mapping over SFU special-character mapping.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/cifs_unicode.h -->