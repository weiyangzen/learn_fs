# Group Research: group_774_linux_sources_os_linux_linux_fs_lockd_svc_c_sources_os_linux_linux_f_ddc675d583cf

Scope: `Docs/research_subset_a.md` includes `sources/os/linux/linux`. This grouped report covers the requested Linux lockd/VFS locking, mbcache, and Minix filesystem files.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/lockd/svc.c -->
# File Research: sources/os/linux/linux/fs/lockd/svc.c

## Purpose
Central lockd service module for Linux NFS/NLM locking. It owns RPC service lifecycle, listener setup, per-network-namespace activation, grace period timing, sysctl/module configuration, generic RPC dispatch, and netlink server parameters.

## Key Points
- Exports `lockd_up()` and `lockd_down()` for NFS/NFSD users.
- Maintains global service state with `nlmsvc_mutex`, `nlmsvc_users`, and `nlmsvc_serv`.
- Runs the `lockd()` service thread, retrying blocked locks via `nlmsvc_retry_blocked()` before `svc_recv()`.
- Creates IPv4/IPv6 UDP and TCP listeners, then destroys per-net transports on shutdown or setup failure.
- Starts/ends lock recovery grace periods using `locks_start_grace()` and `locks_end_grace()`.
- Defines `nlmsvc_dispatch()` for decode, procedure call, and encode handling across NLM versions.
- Registers pernet state, generic netlink family, procfs, sysctls, and IP address notifiers.

## Risks
Lifecycle correctness depends on balanced global and per-net user counts. `lockd_down_net()` treats underflow as fatal with `BUG()`. Callback procedures bypass normal client setup and must do host lookup in individual handlers.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/lockd/svc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/lockd/svc4proc.c -->
# File Research: sources/os/linux/linux/fs/lockd/svc4proc.c

## Purpose
Implements server-side NLM version 4 RPC procedures. It adapts generated NLMv4 XDR types to legacy lockd internal structures, performs host/file lookup, invokes shared lock/share engines, handles async callbacks, and exports `nlmsvc_version4`.

## Key Points
- Uses wrapper structs with xdrgen type first, plus legacy `nlm_lock`, `nlm_cookie`, or `nlm_reboot` state.
- Converts generated `nlm4_lock` and `netobj` values into internal lockd forms.
- Implements TEST, LOCK, CANCEL, UNLOCK, GRANTED, GRANTED_RES, SM_NOTIFY, SHARE, UNSHARE, NM_LOCK, and FREE_ALL.
- Implements `_MSG` async procedures by filling an allocated `nlm_rqst` and sending async callback replies.
- `nlm4svc_lookup_file()` validates file handle size and 64-bit range overflow, initializes `file_lock`, and attaches `nlmsvc_lock_operations`.
- SHARE/UNSHARE use pseudo lock state with `LOCKD_SHARE_SVID`.

## Risks
Decoded data often points into RPC buffers. Cookie and file handle size checks are strict. Grace-period and reclaim semantics are enforced per procedure.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/lockd/svc4proc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/lockd/svclock.c -->
# File Research: sources/os/linux/linux/fs/lockd/svclock.c

## Purpose
Server-side lock state engine for lockd, especially blocked locks. It bridges NLM requests to VFS byte-range locks, manages blocked request lists, handles VFS callbacks, sends GRANTED callbacks, and processes GRANTED_RES replies.

## Key Points
- Maintains global `nlm_blocked` retry list under `nlm_blocked_lock`.
- Creates and frees `struct nlm_block` records with krefs and per-file list membership.
- Implements `nlmsvc_lock()`, `nlmsvc_testlock()`, `nlmsvc_unlock()`, and `nlmsvc_cancel_blocked()`.
- Provides `nlmsvc_lock_operations` for VFS async lock notifications and owner refcounting.
- Uses `vfs_lock_file()`, `vfs_test_lock()`, `vfs_cancel_lock()`, and `locks_delete_block()`.
- Retries due work from `nlmsvc_retry_blocked()`, including deferred RPC revisits and GRANTED callback retransmission.

## Risks
This is highly race-sensitive: VFS callbacks, RPC callbacks, CANCEL, UNLOCK, and retry processing can all touch the same block. Comments note tolerated list traversal races and a concern that RPC release can indirectly grab a mutex.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/lockd/svclock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/lockd/svcproc.c -->
# File Research: sources/os/linux/linux/fs/lockd/svcproc.c

## Purpose
Implements NLM version 1 and version 3 server procedures. It performs common host/file lookup, invokes lock/share/resource engines, supports async callback-style procedures, and exports `nlmsvc_version1` and `nlmsvc_version3`.

## Key Points
- `nlmsvc_retrieve_args()` looks up host, optionally monitors it, opens the file, and initializes the VFS `file_lock`.
- `cast_status()` maps internal or v4-only statuses into legacy protocol-safe statuses.
- Implements TEST, LOCK, CANCEL, UNLOCK, GRANTED, SHARE, UNSHARE, NM_LOCK, FREE_ALL, SM_NOTIFY, and GRANTED_RES.
- `_MSG` procedures compute a result and send async callback responses.
- Shares the same 24-entry procedure table for v3, while v1 exposes procedures 0 through 16.
- Integrates with `xdr.c`, `svclock.c`, `svcshare.c`, and `svcsubs.c`.

## Risks
Status mapping is intentionally lossy for older protocol versions. Missing `nlmsvc_ops` causes real file operations to fail as denied-no-locks.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/lockd/svcproc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/lockd/svcshare.c -->
# File Research: sources/os/linux/linux/fs/lockd/svcshare.c

## Purpose
Manages NLM DOS-style share reservations on server-side `nlm_file` objects.

## Key Points
- `nlmsvc_share_file()` adds or updates a share reservation keyed by host and owner handle.
- Conflict detection uses `(access & existing_mode) || (mode & existing_access)`.
- New shares allocate one object plus inline owner-handle bytes.
- `nlmsvc_unshare_file()` removes matching reservations and returns success even if none existed.
- `nlmsvc_traverse_shares()` removes all shares matching a host predicate.

## Risks
The share list is a simple singly linked list and relies on higher-level serialization. Owner bytes have the same lifetime as the allocated share object.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/lockd/svcshare.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/lockd/svcsubs.c -->
# File Research: sources/os/linux/linux/fs/lockd/svcsubs.c

## Purpose
Support routines for lockd server file tracking, file open/close/refcount handling, lock/share/block traversal, host resource cleanup, and exported cleanup by superblock or IP address.

## Key Points
- Maintains a 128-bucket global `nlm_files` hash table protected by `nlm_file_mutex`.
- `nlm_lookup_file()` finds or creates `nlm_file` objects and opens needed read/write file pointers through `nlmsvc_ops->fopen()`.
- `nlm_release_file()` deletes file objects only after refs, blocks, shares, and VFS lockd locks are gone.
- Traverses inode `flc_posix` lists to remove lockd-owned POSIX locks.
- Calls into `nlmsvc_traverse_blocks()` and `nlmsvc_traverse_shares()`.
- Exports `nlmsvc_unlock_all_by_sb()` and `nlmsvc_unlock_all_by_ip()`.

## Risks
Because `fs/locks.c` can split/merge locks without lockd-specific notification, this file must inspect VFS lock contexts to determine whether a file is still in use.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/lockd/svcsubs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/lockd/svcxdr.h -->
# File Research: sources/os/linux/linux/fs/lockd/svcxdr.h

## Purpose
Inline helpers for encoding and decoding basic NLM service XDR primitives.

## Key Points
- Encodes/decodes status values, strings, cookies, and owner handles.
- Enforces `NLM_MAXSTRLEN`, `NLM_MAXCOOKIELEN`, and `XDR_MAX_NETOBJ`.
- Treats zero-length cookies as a 4-byte zero cookie for HPUX compatibility.
- Decoded strings and owners point into the XDR stream.

## Risks
Linux limits cookies to 32 bytes even though the protocol allows larger opaque cookies.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/lockd/svcxdr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/lockd/trace.c -->
# File Research: sources/os/linux/linux/fs/lockd/trace.c

## Purpose
Tracepoint definition compilation unit for lockd trace events.

## Key Points
- Defines `CREATE_TRACE_POINTS`.
- Includes `trace.h` so declarations are instantiated exactly once.

## Risks
This file must stay minimal; defining tracepoints in more than one C file would create duplicate definitions.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/lockd/trace.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/lockd/trace.h -->
# File Research: sources/os/linux/linux/fs/lockd/trace.h

## Purpose
Declares lockd trace events for NLM client lock operations.

## Key Points
- Sets `TRACE_SYSTEM lockd`.
- Defines symbolic NLM status formatting, with v4-specific statuses under `CONFIG_LOCKD_V4`.
- Declares reusable `nlmclnt_lock_event`.
- Defines concrete events: `nlmclnt_test`, `nlmclnt_lock`, `nlmclnt_unlock`, and `nlmclnt_grant`.
- Captures owner-handle hash, svid, file-handle hash, range, remote address, and status.

## Risks
Trace output hashes opaque values rather than exposing full owner handles or file handles.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/lockd/trace.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/lockd/xdr.c -->
# File Research: sources/os/linux/linux/fs/lockd/xdr.c

## Purpose
Legacy NLM server XDR encode/decode implementation for v1/v3-style lockd procedures.

## Key Points
- Converts 32-bit protocol offsets/lengths to and from `loff_t`.
- Decodes file handles constrained to exactly `NFS2_FHSIZE`.
- Decodes lock, test, lock, cancel, unlock, result, reboot, share, and notify arguments.
- Encodes TEST replies, generic replies, void replies, and SHARE replies.
- Initializes embedded VFS `file_lock` state during lock decode.
- SHARE decode uses `LOCKD_SHARE_SVID`.

## Risks
File handle handling is stricter than the protocol’s variable-length description. Share argument range checks are explicitly noted as missing.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/lockd/xdr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/lockd/xdr.h -->
# File Research: sources/os/linux/linux/fs/lockd/xdr.h

## Purpose
Defines legacy lockd/NLM XDR constants, structures, status aliases, and function prototypes for v1/v3 server paths.

## Key Points
- Defines NSM private data sizes, NLM cookie/string limits, and big-endian status aliases.
- Defines `nlm_lock`, `nlm_cookie`, `nlm_args`, `nlm_res`, and `nlm_reboot`.
- Declares decode/encode functions implemented in `xdr.c`.
- `nlm_lock` carries both protocol fields and embedded VFS `file_lock`.

## Risks
The protocol permits larger cookies than Linux stores. Callers must distinguish original protocol range fields from normalized VFS lock range fields.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/lockd/xdr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/locks.c -->
# File Research: sources/os/linux/linux/fs/locks.c

## Purpose
Linux VFS implementation of POSIX locks, OFD locks, BSD `flock()`, and leases/delegations/layout leases.

## Key Points
- Allocates and frees file lock contexts, locks, and leases.
- Maintains per-inode lists for flock, POSIX/OFD, and lease state.
- Maintains per-CPU global lock lists for `/proc/locks`.
- Maintains a blocked-lock graph and owner hash for wait handling and POSIX deadlock detection.
- Implements POSIX range conflict detection, merging, splitting, replacement, unlock, and wait insertion.
- Implements flock locking and wait behavior.
- Implements lease add/delete/break/timeout/get/set behavior and notifier hooks.
- Exports `vfs_lock_file()`, `vfs_test_lock()`, `vfs_cancel_lock()`, `locks_delete_block()`, `locks_remove_posix()`, and `locks_remove_file()`.

## Important Integration
Lockd relies directly on this file for server-side NLM behavior. Its async lock contract requires filesystems returning `FILE_LOCK_DEFERRED` to call `lm_grant()` later and not grant before returning deferred.

## Risks
Close/fcntl races are explicitly handled by fd-table revalidation. Lease breaking can block, time out, downgrade, or remove leases. `/proc/locks` must traverse blocked lock trees while respecting pid namespaces.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/locks.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/mbcache.c -->
# File Research: sources/os/linux/linux/fs/mbcache.c

## Purpose
Simple reusable key/value cache used by ext2/ext4 for extended attribute block/value deduplication.

## Key Points
- Keys need not be unique, but key/value pairs are expected to be unique.
- Uses fixed-size hash buckets with bit locks plus a global list protected by `c_list_lock`.
- `mb_cache_entry_create()` rejects duplicate key/value entries and triggers shrink when over capacity.
- Lookup helpers find reusable entries by key or exact entries by key/value.
- `mb_cache_entry_delete_or_get()` deletes only unused entries or returns a referenced busy entry.
- Shrinker scans entries, preserves recently referenced or busy entries, and frees unused entries.
- Module init/exit owns the entry slab cache.

## Risks
Correctness depends on atomic refcount transitions between hash references, lookup references, and deletion. Destroy assumes external users can no longer reach the cache.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/mbcache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/minix/Kconfig -->
# File Research: sources/os/linux/linux/fs/minix/Kconfig

## Purpose
Declares Linux Minix filesystem build configuration.

## Key Points
- `CONFIG_MINIX_FS` is tristate, depends on `BLOCK`, and selects `BUFFER_HEAD`.
- Help text describes Minix as legacy/educational and warns about restrictions.
- Defines endian helper configs for architecture-specific Minix handling.

## Risks
Root filesystem support cannot be modular. Endian helper choices affect bitmap/index interpretation elsewhere in the driver.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/minix/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/minix/Makefile -->
# File Research: sources/os/linux/linux/fs/minix/Makefile

## Purpose
Build wiring for the Linux Minix filesystem.

## Key Points
- Builds `minix.o` when `CONFIG_MINIX_FS` is enabled.
- Composite objects are `bitmap.o`, `itree_v1.o`, `itree_v2.o`, `namei.o`, `inode.o`, `file.o`, and `dir.o`.

## Risks
The object list covers allocation, inode tree, namespace, inode, file, and directory support; omitting an object would remove core functionality.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/minix/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/minix/bitmap.c -->
# File Research: sources/os/linux/linux/fs/minix/bitmap.c

## Purpose
Minix block and inode bitmap operations plus raw inode location helpers.

## Key Points
- Counts free bits in inode and zone bitmaps.
- Allocates and frees blocks with bounds checks and bitmap updates.
- Locates raw Minix v1 and v2/v3 inode records on disk.
- Clears deleted inode mode/link count on disk.
- Allocates and frees inode numbers.
- Initializes new VFS inodes with owner, timestamps, private Minix data, inode hash insertion, and dirty marking.

## Risks
A single static `bitmap_lock` serializes bitmap operations. Corruption or out-of-range values generally print warnings and return errors/zero rather than repair.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/minix/bitmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/minix/dir.c -->
# File Research: sources/os/linux/linux/fs/minix/dir.c

## Purpose
Minix directory file operations and directory-entry manipulation.

## Key Points
- Provides directory llseek, generic read, shared iteration, and fsync operations.
- Implements readdir over mapped folios and supports old Minix and Minix v3 entry formats.
- Finds entries by name, adds links, deletes entries, updates links, and returns inode numbers by name.
- Creates `.` and `..` entries for new directories.
- Checks whether a directory is empty except for valid `.` and `..`.
- Handles synchronous directory updates through writeback and metadata sync.

## Risks
Directory modification depends on careful folio lock/map/release handling. `minix_add_link()` intentionally scans one page past current directory pages to support expansion.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/minix/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/minix/file.c -->
# File Research: sources/os/linux/linux/fs/minix/file.c

## Purpose
Minix regular-file operations, fsync behavior, and inode attribute updates.

## Key Points
- `minix_fsync()` calls `mmb_fsync()` over Minix metadata buffer heads.
- Regular files use generic llseek, read, write, mmap preparation, and splice-read helpers.
- `minix_setattr()` validates attributes, handles size changes with `truncate_setsize()` and `minix_truncate()`, copies attributes, and marks the inode dirty.
- Inode ops provide setattr and getattr.

## Risks
Size changes must update VFS size before Minix block truncation. Most data I/O behavior is generic; filesystem-specific correctness depends on block mapping and truncation code elsewhere.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/minix/file.c -->