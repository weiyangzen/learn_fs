# Group Research: group_831_linux_sources_os_linux_linux_fs_smb_client_file_c_sources_os_linux_l_3dfe408c4b2d

Scope: `Docs/research_subset_a.md` / `sources/os/linux/linux/fs/smb/client/*`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/file.c -->
# File Research: sources/os/linux/linux/fs/smb/client/file.c

## Role

Implements CIFS/SMB client VFS file operations and address-space behavior: open/close, file handle lifetime, reconnect/reopen, netfs read/write integration, byte-range locking, fsync/flush, mmap preparation, oplock/lease break handling, and experimental swapfile I/O over SMB3.

## Netfs I/O

- `cifs_req_ops` connects the SMB client to the Linux netfs library.
- `cifs_prepare_read()` / `cifs_prepare_write()` pick an SMB channel, negotiate `rsize`/`wsize` when needed, obtain credits through server ops, set subrequest limits, and wire SMB Direct segment limits when RDMA is active.
- `cifs_issue_read()` / `cifs_issue_write()` adjust credits, reopen invalid handles when possible, submit async SMB read/write vectors, and terminate subrequests on failure.
- `cifs_write_subrequest_terminated()` updates netfs remote size and zero-point state after successful direct/unbuffered writes before completing the netfs subrequest.
- Request setup stores the active `cifsFileInfo`, r/w sizes, and optionally forwards the original opener PID for `rwpidforward`.

## Open, Close, And Handle Lifetime

- `cifs_open()` builds the full path, handles direct-I/O file op replacement, performs `O_TRUNC`, tries to reuse deferred cached handles, otherwise performs legacy POSIX open when available or SMB NT-style open through `server->ops->open`.
- `cifs_nt_open()` maps POSIX open flags to SMB desired access/disposition/create options and refreshes inode metadata after open.
- `cifs_new_fileinfo()` allocates and registers `struct cifsFileInfo`, lock lists, work items, tcon/inode open-file lists, and oplock state.
- `cifsFileInfo_put()` / `_cifsFileInfo_put()` manage last-reference close, pending-open protection against missed lease breaks, list removal, server close or close-getattr, retry offload to `serverclose_wq`, and final async freeing.
- `cifs_close()` supports SMB2 deferred close when leases allow handle caching; it records modified attrs, queues delayed close work, or immediately drops the file reference.
- Directory close is separate in `cifs_closedir()`, including search buffer release and protocol-specific directory close handling.

## Reconnect And Reopen

- `cifs_mark_open_files_invalid()` marks all open files on a tcon invalid after reconnect and invalidates cached directories.
- `cifs_reopen_file()` is the central invalid-handle repair path. It rebuilds the path, reopens with legacy POSIX or SMB open, avoids create/truncate flags on reopen, retries access for FS-Cache write-only cases, optionally flushes and refreshes inode metadata, restores oplock state, and relocks server byte-range locks when reconnecting.
- `cifs_reopen_persistent_handles()` walks invalid persistent handles on a tree connection and attempts reopen without flushing.

## Locking

- Mandatory byte-range locks are tracked per file handle in `struct cifs_fid_locks` and per inode under `cinode->lock_sem`.
- `cifs_find_lock_conflict()` and helpers detect overlapping lock conflicts across open FIDs, with special cases for same-FID, same-owner, shared locks, OFD locks, and read/write conflict checks.
- `cifs_lock()` and `cifs_flock()` parse VFS lock requests, choose POSIX vs mandatory SMB locking when legacy UNIX extensions permit, and call `cifs_getlk()` or `cifs_setlk()`.
- `cifs_lock_add_if()` can cache byte-range locks locally when allowed, or block on conflicting local locks using wait queues.
- Legacy paths under `CONFIG_CIFS_ALLOW_INSECURE_LEGACY` push POSIX and mandatory locks back to the server after reconnect and unlock ranges in SMB1 batching format.
- Locking affects cache behavior: setting mandatory locks can zap mappings and downgrade oplocks to avoid stale reads.

## Read/Write, Flush, Fsync, And Mmap

- `cifs_strict_writev()` and `cifs_file_write_iter()` route buffered/direct writes through netfs, serialize writers, honor strict cache policy, flush when write caching is not available, and zap read cache after direct writes.
- `cifs_strict_readv()` chooses buffered or unbuffered netfs reads based on cache rights, direct I/O, strict mode, and byte-range lock conflicts.
- `cifs_loose_read_iter()` revalidates mappings before buffered loose-cache reads.
- `cifs_strict_fsync()` and `cifs_fsync()` write back ranges and issue SMB flushes unless `nostrictsync`/`NOSSYNC` suppresses them.
- `cifs_flush()` writes and checks mapping writeback errors on close.
- `cifs_file_strict_mmap_prepare()` and `cifs_file_mmap_prepare()` revalidate or zap mappings before installing CIFS VM ops with `netfs_page_mkwrite()`.

## Oplocks, Size Safety, And Swap

- `cifs_oplock_break()` waits for pending writers, downgrades oplock/lease state via protocol ops, breaks local leases, writes back data, optionally waits and purges cache, pushes locks, closes deferred handles when handle caching is lost, and sends the protocol oplock response if the file remains open.
- `is_size_safe_to_change()` prevents server metadata refresh from shrinking a locally writable cached inode unless direct I/O or growth makes the update safe.
- `cifs_swap_activate()`, `cifs_swap_deactivate()`, and `cifs_swap_rw()` provide experimental swapfile support using netfs unbuffered I/O and reject sparse swapfiles.
- `cifs_addr_ops` wires netfs folio read/writeback, dirty/release/invalidate/migrate hooks, swap hooks, and `noop_direct_IO`; `cifs_addr_ops_smallbuf` omits readahead for small server buffers.

## Dependencies

Depends on Linux VFS, file locking, writeback, netfs, FS-Cache, SMB Direct, CIFS superblock/inode/session/tcon state, protocol operation tables, path building, tracepoints, and optional legacy CIFS/UNIX extension support.

## Research Notes

This file is the SMB client’s main file-data control plane. Correctness hinges on synchronizing four moving parts: VFS page cache/netfs state, SMB credits and async requests, reopenable server handles, and oplock/lease-driven cache validity. Reconnect and deferred-close paths are especially sensitive because they must avoid missed lease breaks, stale cached data, and lock loss across session failure.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/fs_context.c -->
# File Research: sources/os/linux/linux/fs/smb/client/fs_context.c

## Role

Implements the SMB3/CIFS Linux `fs_context` mount API: mount option specification, option parsing, UNC/source path parsing, dialect/security/cache/symlink/reparse parsing, mount validation, superblock creation, remount/reconfigure handling, context duplication/cleanup, and conversion from parsed context fields to CIFS mount flags.

## Mount Parameter Surface

- `smb3_fs_parameters[]` declares supported mount options for the new mount API.
- Flag options cover permissions, lease/cache behavior, DFS, POSIX/UNIX extensions, byte-range locking, ACLs, signing/sealing, FS-Cache, multiuser, sharesock, persistent/resilient handles, RDMA, multichannel, compression, witness, native sockets, Unicode, NetBIOS session init, and rootfs.
- Numeric options include UID/GID, modes, port, I/O sizes, attribute cache timeouts, deferred close timeout, echo interval, max credits, cached directories, snapshot time, handle timeout, and max channels.
- String options include source, user/passwords, IP/srcaddr, domain, charset, NetBIOS names, dialect/security/cache selections, reparse/symlink policy, upcall target, and symlink root.
- Compatibility/old mount-helper options such as `cred`, `credentials`, `unc`, and `prefixpath` are ignored.

## Parsers

- `cifs_parse_security_flavors()` maps `sec=` strings to Kerberos, RawNTLMSSP, NTLMv2, or null auth; integrity variants set signing, and unsupported `krb5p` is rejected with guidance to use sealing.
- `cifs_parse_smb_version()` maps `vers=` to protocol operation/value tables and rejects insecure legacy dialects when unavailable or when mounting via the `smb3` filesystem type.
- `cifs_parse_cache_flavor()` maps `cache=` to direct I/O, strict cache, loose cache, read-only cache, or single-client read/write cache.
- `parse_reparse_flavor()` and `parse_symlink_flavor()` configure how Windows reparse points and SMB symlinks are interpreted.
- `cifs_parse_upcall_target()` selects mount-namespace vs application-namespace upcalls.
- `smb3_fs_context_parse_param()` is the main option dispatcher. It handles empty string user/password values, validates bounds, aligns rsize/wsize/bsize, parses addresses, normalizes conflicting options, enforces kernel config requirements, owns copied strings, and rejects invalid combinations such as `multiuser` with `upcalltarget=mount`.

## Path And Source Handling

- `cifs_sanitize_prepath()` removes duplicate leading/interior/trailing path delimiters and returns `NULL` for empty prefix paths.
- `smb3_parse_devname()` validates UNC syntax, extracts server hostname, UNC share path, and optional prepath, and converts UNC delimiters to backslashes.
- `smb3_fs_context_fullpath()` rebuilds the full source string from UNC plus prepath with a caller-selected delimiter.
- `smb3_fs_context_parse_monolithic()` parses legacy comma-separated mount option blobs, strips LSM options first, and tolerates doubled delimiters inside values.

## Validation And Mount Creation

- `smb3_fs_context_validate()` rejects RDMA on dialects older than SMB3, rejects multiuser without key support, warns when no dialect is specified, validates UNC/share presence, derives destination IP from UNC if `ip=` was not supplied, sets the port, and normalizes implicit/invalid `forceuid` and `forcegid`.
- `smb3_handle_conflicting_options()` reconciles `multichannel` and `max_channels`, defaulting to one channel unless multichannel is requested or implied by `max_channels > 1`.
- `smb3_get_tree()` validates the context, serializes mount with `cifs_mount_mutex`, and calls `cifs_smb3_do_mount()`.

## Reconfigure/Remount

- `smb3_verify_reconfigure_ctx()` rejects remount changes that would alter immutable session identity or protocol properties: POSIX paths, security type, multiuser, UNC, username, domain, workstation, nodename, charset, Unicode mode, and NetBIOS session init. Password changes are allowed only for expired-password reconnect and not for Kerberos.
- `smb3_reconfigure()` duplicates old context for rollback, preserves immutable strings from the active superblock context, handles password/password2 updates, carries forward previous rsize/wsize if omitted, duplicates the new context, synchronizes session passwords, optionally scales multichannel state, commits the new context atomically, updates mount flags, and triggers DFS remount handling when configured.
- `smb3_sync_session_ctx_passwords()` keeps the superblock context in sync with session passwords that may have been swapped during reconnect.
- `smb3_sync_ses_chan_max()` updates session channel maximum under `chan_lock`.

## Defaults, Cleanup, And Mount Flags

- `smb3_init_fs_context()` allocates `struct smb3_fs_context` and initializes defaults: workstation/NetBIOS names from UTS nodename, current UID/GID, 1 MiB block size, SFM remapping, owner-write modes, POSIX paths, server inode numbers, strict caching, default attribute cache and deferred-close timeouts, cached directory limit, SMB2.1+ default dialect values, echo interval, single-channel operation, default reparse/symlink policy, and Unicode autodetect.
- `smb3_cleanup_fs_context_contents()` frees all owned strings, using sensitive freeing for passwords, and is kept in sync with context duplication.
- `smb3_update_mnt_flags()` maps parsed context booleans into atomic CIFS mount flags, including DFS, permission checks, UID/GID override, char remapping, xattrs, SFU emulation, byte-range locking, handle cache, sync behavior, ACLs, backup UID/GID, dynperm, FS-Cache, multiuser, strict/direct I/O, and mfsymlinks.

## Dependencies

Uses Linux `fs_context`/`fs_parser`, security LSM mount option parsing, CIFS protocol operation/value tables, address parsing helpers, DFS optional support, session/channel locking, and mount/superblock CIFS state.

## Research Notes

This file is the policy boundary between user mount options and runtime SMB client behavior. The highest-risk paths are string ownership during parsing/reconfigure, remount rollback, credential updates during expired-password reconnect, and multichannel scaling coordination with reconnect/channel management.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/fs_context.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/fs_context.h -->
# File Research: sources/os/linux/linux/fs/smb/client/fs_context.h

## Role

Private SMB client mount-context header. It defines mount-option enums, `struct smb3_fs_context`, parser exports, context lifecycle APIs, mount locking helpers, I/O size negotiation helpers, and symlink policy resolution.

## Key Definitions

- `cifs_errorf()` logs mount parsing errors to both `fs_context` and CIFS debug output.
- `cifs_io_align()` and `CIFS_ALIGN_{W,R,B}SIZE()` clamp zero or unaligned I/O sizes to page-aligned values and report the correction.
- Enums define SMB dialect tokens, cache flavors, reparse flavors, symlink flavors, security flavors, upcall targets, and every recognized mount option ID.
- `struct smb3_fs_context` stores all parsed mount state: identity and credential strings, UNC/source/prepath fields, NetBIOS names, addresses, UID/GID/mode settings, security/upcall type, dozens of boolean policy flags, negotiated and user-requested I/O sizes, cache timeouts, protocol ops/values, destination/source addresses, NLS state, snapshot/handle settings, multichannel fields, compression/rootfs/witness flags, DFS fields, reparse/symlink policy, native socket policy, DNS domain, and symlink root.

## Inline Logic

- `cifs_symlink_type()` resolves the effective symlink strategy from explicit `symlink=`, `mfsymlinks`, SFU emulation, Linux/POSIX extensions, and reparse settings.
- `smb3_fc2context()` returns `fc->fs_private`.
- `cifs_mount_lock()` / `cifs_mount_unlock()` wrap the global mount mutex.
- `cifs_negotiate_rsize()` and `cifs_negotiate_wsize()` ask protocol ops for negotiated sizes, cap user-provided sizes to negotiated maxima, enforce at least one page, and round down to page alignment.
- `cifs_negotiate_iosize()` negotiates read and write sizes together.

## Exposed API

Exports mount initialization/cleanup, context duplication, session password sync, mount flag update, and `cifs_sanitize_prepath()` for source path parsing.

## Dependencies

Includes CIFS global definitions plus Linux parser and fs-parser headers. The structure references CIFS session/tcon, protocol operation/value tables, NLS tables, sockets, and DFS session pointers.

## Research Notes

This header is the shared contract for SMB mount setup. Most fields are long-lived superblock policy, so duplication and cleanup in `fs_context.c` must stay synchronized with the string members defined here.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/fs_context.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/fscache.c -->
# File Research: sources/os/linux/linux/fs/smb/client/fscache.c

## Role

Implements CIFS integration with Linux FS-Cache for SMB share volumes and inodes.

## Key Logic

- `struct cifs_fscache_inode_key` defines the inode cache key from server unique ID, creation time, and file type. The comment notes it must match inode comparison logic in `cifs_find_inode()`.
- `cifs_fscache_fill_volume_coherency()` fills volume coherency metadata from tcon resource ID, volume creation time, and serial number.
- `cifs_fscache_get_super_cookie()` acquires a volume cookie once per tcon under `fscache_lock`. It supports IPv4/IPv6 server addresses, extracts and sanitizes the share name for the key, builds a key of the form `cifs,<address>,<share>`, attaches coherency data, handles `-EBUSY` collisions as nonfatal no-cache cases, and traces acquisition outcome.
- `cifs_fscache_release_super_cookie()` relinquishes the volume cookie with current coherency data and clears `tcon->fscache`.
- `cifs_fscache_get_inode_cookie()` builds an inode key/coherency tuple, acquires an FS-Cache cookie under the tcon volume, and marks the mapping for release callbacks when caching is active.
- `cifs_fscache_unuse_inode_cookie()` unuses a cookie, optionally updating coherency and file size.
- `cifs_fscache_release_inode_cookie()` relinquishes the inode cookie and clears the netfs cache pointer.

## Dependencies

Uses FS-Cache and netfs cookie APIs, CIFS inode/tcon/superblock structures, share-name extraction, socket address formatting, tracepoints, and CIFS debug logging.

## Research Notes

The volume key deliberately includes network endpoint and share name, while inode keys use server identity and creation time. Cache coherency is time-based for inodes and volume metadata-based for shares, so stale-data safety depends on server-provided IDs/timestamps being stable and comparable.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/fscache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/fscache.h -->
# File Research: sources/os/linux/linux/fs/smb/client/fscache.h

## Role

Header for CIFS FS-Cache integration. It defines coherency payloads and provides either real FS-Cache declarations/helpers or no-op stubs when `CONFIG_CIFS_FSCACHE` is disabled.

## Key Definitions

- `struct cifs_fscache_volume_coherency_data` stores packed resource ID, volume creation time, and volume serial number.
- `struct cifs_fscache_inode_coherency_data` stores mtime/ctime seconds and nanoseconds as little-endian fields.
- With `CONFIG_CIFS_FSCACHE`, the header declares super-cookie and inode-cookie lifecycle functions implemented in `fscache.c`.

## Inline Helpers

- `cifs_fscache_fill_coherency()` derives inode coherency metadata from VFS ctime and mtime.
- `cifs_inode_cookie()` returns the netfs cookie from `CIFS_I(inode)->netfs`.
- `cifs_invalidate_cache()` invalidates the cookie with current coherency and file size.
- `cifs_fscache_enabled()` checks whether the inode cookie is enabled.
- Without FS-Cache support, all lifecycle, invalidation, and enabled checks compile to no-op or false/null helpers.

## Dependencies

Includes Linux swap and fscache headers plus CIFS global structures.

## Research Notes

This header lets the rest of the SMB client call cache helpers unconditionally. The conditional stubs keep file I/O code simple while making the feature entirely optional at build time.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/fscache.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/gen_smb1_mapping -->
# File Research: sources/os/linux/linux/fs/smb/client/gen_smb1_mapping

## Role

Perl generator for SMB1 error mapping C tables.

## Behavior

- Expects exactly two arguments: input header and output C file.
- Supports two input formats:
  - `nterr.h`: parses `NT_STATUS_*` defines with mapping comments containing status class and code.
  - `smberr.h`: parses `ERR*`/`Err*` defines with POSIX error comments and tracks the current error class from header comments.
- Handles backslash line continuations before matching.
- Rejects commented mapping defines that do not match the expected annotation format.
- Deduplicates NT status macro names.
- Converts numeric expressions by removing whitespace/parentheses and OR-ing hex components for NT status values.
- Fails if no mapping entries are found.
- Sorts entries numerically by value before output.

## Outputs

- `smb1_mapping_table.c`: emits NT status to DOS class/code mappings with synonym macro names merged into one string when values match.
- `smb1_err_dos_map.c`: emits SMB1 DOS-class error to POSIX error mappings.
- `smb1_err_srv_map.c`: emits SMB1 server-class error to POSIX error mappings.
- Any other output filename is rejected.

## Dependencies

Uses only core Perl facilities. The generator relies on strict source-comment conventions in CIFS headers.

## Research Notes

The script intentionally treats malformed annotated comments as build-time errors. This keeps generated mapping tables synchronized with the semantic annotations in `nterr.h` and `smberr.h`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/gen_smb1_mapping -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/gen_smb2_mapping -->
# File Research: sources/os/linux/linux/fs/smb/client/gen_smb2_mapping

## Role

Perl generator for SMB2/SMB3 NT status to POSIX error mapping tables.

## Behavior

- Expects exactly two arguments: input header and output C file.
- Reads status defines matching `#define NAME cpu_to_le32(0x...) // -ERR`.
- Skips `STATUS_SEVERITY*` defines.
- Rejects duplicate status macro names.
- Stores each status macro, string code, numeric code, and POSIX error annotation.
- Sorts all entries by numeric NT status code.
- Skips numeric code zero during output.
- Merges adjacent synonyms with the same numeric status value into a single descriptive string using `or`.
- Emits C initializer rows of `{ code, error, "status names" },`.

## Dependencies

Uses only core Perl. It depends on SMB2 status headers using the exact `cpu_to_le32(...) // -ERR` annotation form.

## Research Notes

This is a compact build-time normalization step: source headers remain annotated with protocol constants, while generated C tables get sorted, synonym-merged entries suitable for lookup/debug output.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/gen_smb2_mapping -->