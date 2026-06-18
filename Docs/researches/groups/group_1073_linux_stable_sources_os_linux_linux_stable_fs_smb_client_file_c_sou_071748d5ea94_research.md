# Group Research:

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/file.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/file.c

## Purpose
Implements CIFS/SMB client VFS file behavior: open/close, handle caching and reconnect, netfs-backed read/write paths, fsync/flush, mmap, swapfile I/O, byte-range locking, oplock/lease break handling, and address-space operations.

## Main Interfaces
- Exports `cifs_req_ops` for Linux netfs integration.
- Provides open/close helpers: `cifs_open()`, `cifs_close()`, `cifs_closedir()`, `cifs_new_fileinfo()`, `cifsFileInfo_get()`, `cifsFileInfo_put()`.
- Provides handle lookup/recovery helpers: `find_writable_file()`, `__cifs_get_writable_file()`, `find_readable_file()` family, `cifs_reopen_file()`, `cifs_reopen_persistent_handles()`.
- Provides locking operations: `cifs_lock()`, `cifs_flock()`, mandatory lock cache helpers, and legacy POSIX lock push/unlock paths under `CONFIG_CIFS_ALLOW_INSECURE_LEGACY`.
- Provides file operation bodies for strict/loose/direct I/O and mmap.
- Defines `cifs_addr_ops` and `cifs_addr_ops_smallbuf`.

## Control Flow
Netfs read/write subrequests are prepared by selecting an SMB channel, negotiating `rsize`/`wsize` when still zero, acquiring credits, and recording trace/debug metadata. Issue functions adjust credits, reopen invalid handles if needed, and call protocol-specific async read/write callbacks through `server->ops`.

Open flow builds a full path from the dentry, optionally truncates first, tries to reuse a cached handle matching flags and user constraints, falls back to legacy POSIX open when available, otherwise uses NT create/open through dialect operations. It creates `cifsFileInfo`, attaches it to inode and tcon open lists, and activates the fscache cookie. Close flow may defer SMB2 close when handle caching is useful and lease state allows it; otherwise it decrements references and closes remotely or offloads close retry work.

Reconnect flow marks open handles invalid on tree reconnect, reopens durable/persistent handles, restores byte-range locks, refreshes inode metadata only when safe, and avoids flushing in writeback-triggered reopen paths to prevent deadlocks.

## State And Synchronization
The file manages several shared lists:
- `tcon->openFileList` under `tcon->open_file_lock`.
- `cinode->openFileList` under `cinode->open_file_lock`.
- per-file lock lists under `cinode->lock_sem`.
- per-file lifetime under `cifs_file->file_info_lock` plus workqueues for final put, server close retry, deferred close, and oplock break.

The lock ordering in open/close and put paths is important: tcon lock, inode open lock, then file info lock. Oplock and deferred close paths coordinate through inode flags, delayed work, and reference increments.

## Integration Points
- Depends heavily on dialect callbacks in `server->ops` for open, close, flush, lock, async read/write, lease/oplock conversion, and negotiated sizes.
- Uses Linux netfs helpers for page cache, readahead, buffered I/O, direct/unbuffered I/O, writeback, folio invalidation, and swapfile I/O.
- Uses `fscache.h` helpers to request read access on write-only opens when local cache fill-in may be needed.
- Uses mount context flags from `fs_context.h` to select strict/direct/cache/lock behavior.

## Notable Behaviors
- Write-only opens may request read permission when fscache is active; if the server denies that, the code retries without read permission and invalidates cache.
- `O_TRUNC` is handled before open to support server and cache semantics.
- Mandatory locks can force oplock downgrade and cache invalidation.
- Strict cache mode disables local reads when no read cache lease/oplock is held.
- `closetimeo` enables deferred SMB2 close for cache-handle leases.
- Swap over SMB3 is present but explicitly marked experimental.

## Risks And Review Focus
- Credit accounting must always return credits on failed issue paths and subrequest cleanup.
- Handle lifetime is subtle around deferred close, oplock break cancellation, server-close retry work, and cached handle reuse.
- Reopen paths intentionally avoid some locks and metadata refreshes to prevent deadlock; changes here need reconnect/writeback tests.
- Lock conflict logic mixes local cached mandatory locks, POSIX locks, flock, OFD locks, and protocol-specific lock types.
- Cache invalidation must stay aligned with fscache, direct I/O, oplock downgrade, and last-close behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/fs_context.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/fs_context.c

## Purpose
Implements the SMB3/CIFS `fs_context` mount API: option declarations, option parsing, UNC parsing, default context creation, validation, mount tree creation, remount/reconfigure validation, session password synchronization, multichannel reconfiguration, cleanup, and conversion from parsed context to CIFS mount flags.

## Main Interfaces
- Defines `smb3_fs_parameters[]`, the accepted mount option table.
- Implements `smb3_init_fs_context()`, `smb3_cleanup_fs_context()`, `smb3_fs_context_dup()`.
- Implements `smb3_parse_devname()`, `smb3_fs_context_fullpath()`, and `cifs_sanitize_prepath()`.
- Implements `smb3_get_tree()` and the `smb3_fs_context_ops`.
- Implements `smb3_reconfigure()` and `smb3_verify_reconfigure_ctx()`.
- Implements `smb3_update_mnt_flags()`.

## Option Parsing
The parser supports flags, negated flags, uid/gid parameters, numeric sizes/timeouts, security flavors, dialect versions, cache modes, reparse handling, symlink handling, UNC source parsing, credentials, network addresses, multichannel settings, compression, witness, RDMA, DFS disabling, fscache, ACL modes, and legacy compatibility options.

Special parsers translate:
- `vers=` to dialect operation/value tables.
- `sec=` to authentication type and signing requirements.
- `cache=` to direct/strict/loose/read-only/single-client cache mode.
- `reparse=` and `symlink=` to CIFS reparse/symlink policies.
- `source=` to `UNC`, `prepath`, printable `source`, hostname, and RFC1001 target name.

## Defaults
`smb3_init_fs_context()` defaults to current uid/gid, strict cache semantics, server inode numbers, POSIX paths, SFM filename remapping, soft retry, SMB2.1-or-later dialect defaults through SMB3 operation/value tables, no multichannel, default actimeo values, default deferred close timeout, and autodetected Unicode/session-init behavior.

## Validation And Mount
`smb3_fs_context_validate()` enforces RDMA dialect requirements, `CONFIG_KEYS` for multiuser, valid UNC/share names, destination address resolution, port assignment, and implicit `forceuid`/`forcegid` behavior when uid/gid are specified. `smb3_get_tree()` validates under `cifs_mount_mutex` and delegates actual mounting to `cifs_smb3_do_mount()`.

## Reconfigure
Remount rejects changes to identity/protocol-critical fields such as POSIX paths, security type, multiuser, UNC, username, domain, workstation, node name, charset, Unicode mode, and RFC1001 session-init. Password updates are only allowed when a reconnect is required and not for Kerberos. The code duplicates/restores contexts to make rollback possible, synchronizes session passwords under `session_mutex`, and updates multichannel limits while preventing concurrent channel scaling through `CIFS_SES_FLAG_SCALE_CHANNELS`.

## Mount Flag Mapping
`smb3_update_mnt_flags()` translates parsed context booleans into `CIFS_MOUNT_*` flags, including DFS, permissions, uid/gid override, inode numbers, character remapping, xattrs, SFU emulation, byte-range locks, handle cache, strict sync, ACLs, backup intent, dynperm, fscache, multiuser, strict/direct I/O, and mfsymlinks.

## Risks And Review Focus
- Mount parsing mutates ownership of `param->string` with `no_free_ptr()` and manual NULLing; leaks/double-frees are the main risk.
- Reconfigure is sensitive because it steals strings between active and proposed contexts and must restore on every failure path.
- Multichannel remount updates session state and channels outside the initial session mutex after setting a scaling flag.
- Security-sensitive strings use `kfree_sensitive`; future credential fields must follow the same cleanup/duplication pattern.
- Option conflicts are partly normalized after parsing, especially `multichannel`/`max_channels`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/fs_context.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/fs_context.h -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/fs_context.h

## Purpose
Declares the CIFS/SMB3 mount context data model, mount option enums, parser support declarations, mount context lifecycle prototypes, mount lock helpers, I/O size alignment helpers, and negotiated read/write size helpers.

## Main Contents
- `cifs_errorf()` logs to both `fs_context` and CIFS VFS debug output.
- `cifs_io_align()` and `CIFS_ALIGN_{R,W,B}SIZE` normalize I/O sizes to page multiples.
- Enums cover SMB versions, cache flavors, reparse modes, symlink modes, security flavors, upcall targets, and every mount option token used by `fs_context.c`.
- `struct smb3_fs_context` stores all parsed mount state: credentials, UNC/source/prepath, names, uid/gid/modes, security, caching, protocol flags, address data, negotiated sizes, timeouts, dialect ops/values, DFS state, reparse/symlink choices, and multichannel settings.
- `cifs_symlink_type()` derives effective symlink policy from explicit `symlink=`, mfsymlinks, SFU emulation, Linux/POSIX extensions, and reparse policy.
- `cifs_mount_lock()`/`cifs_mount_unlock()` wrap the global mount mutex.
- `cifs_negotiate_rsize()`, `cifs_negotiate_wsize()`, and `cifs_negotiate_iosize()` cap and align negotiated sizes.

## Integration Points
Included by mount parsing and file I/O code. The `ctx->ops` and `ctx->vals` fields selected here drive dialect-specific behavior across the SMB client, while `rsize`/`wsize` negotiation is consumed by `file.c` netfs subrequest preparation.

## Risks And Review Focus
- `struct smb3_fs_context` must stay synchronized with duplication and cleanup logic in `fs_context.c`.
- New string fields require updates in both `smb3_fs_context_dup()` and `smb3_cleanup_fs_context_contents()`.
- New option enums must match `smb3_fs_parameters[]` and parse switch cases.
- I/O size helpers round down to page size and guarantee at least one page; callers must treat zero as “negotiate later.”
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/fs_context.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/fscache.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/fscache.c

## Purpose
Implements CIFS integration with Linux FS-Cache: volume cookie acquisition/release for tree connections and inode cookie acquisition/use/release for cached file contents.

## Main Interfaces
- `cifs_fscache_get_super_cookie()`
- `cifs_fscache_release_super_cookie()`
- `cifs_fscache_get_inode_cookie()`
- `cifs_fscache_unuse_inode_cookie()`
- `cifs_fscache_release_inode_cookie()`

## Control Flow
Volume acquisition builds a cache key from the server socket address and share name, normalizes slashes in the share name, fills coherency data from tcon resource/volume identifiers, and calls `fscache_acquire_volume()`. It serializes acquisition with `tcon->fscache_lock` and uses `tcon->fscache_acquired` to make acquisition one-shot.

Inode cookie acquisition creates a key from CIFS unique id, create time, and file type, fills coherency data from inode ctime/mtime, and calls `fscache_acquire_cookie()` with current inode size. Successful acquisition marks the mapping with `mapping_set_release_always()`.

Unuse and release paths update coherency and size when requested, then call fscache APIs to unuse or relinquish cookies.

## Integration Points
Used by mount/tree connection setup and by file open/close/cache invalidation paths in `file.c`. It relies on tcon volume identity, CIFS inode metadata, and `fscache.h` inline coherency helpers.

## Risks And Review Focus
- Cache key uniqueness depends on address plus share name; collision handling logs `-EBUSY` and leaves `tcon->fscache` NULL.
- `tcon->fscache_acquired` is set before all failure paths complete, so acquisition is intentionally not retried for some errors.
- Coherency depends on server-provided unique id/create time and local inode ctime/mtime translations.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/fscache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/fscache.h -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/fscache.h

## Purpose
Declares CIFS FS-Cache coherency structures and exposes fscache helper APIs, with no-op fallbacks when `CONFIG_CIFS_FSCACHE` is disabled.

## Main Contents
- `struct cifs_fscache_volume_coherency_data` records resource id, volume create time, and volume serial number.
- `struct cifs_fscache_inode_coherency_data` records write/change timestamps in seconds and nanoseconds.
- When fscache is enabled, declares super/inode cookie functions and inline helpers for coherency fill, cookie lookup, invalidation, and enabled checks.
- When disabled, provides inline stubs returning success/false/null as appropriate.

## Integration Points
Included by `file.c` and `fscache.c`. `cifs_invalidate_cache()` is called on direct write fallback, netfs invalidation, and cache-oplock transitions. `cifs_fscache_enabled()` influences open access masks by allowing write-only opens to request read permission for cache fill-in.

## Risks And Review Focus
- The enabled section contains duplicate prototypes for several functions; harmless but easy to miss during maintenance.
- Invalidation coherency is timestamp-based; correctness depends on callers updating inode timestamps before invalidation where needed.
- Stub behavior makes fscache-free builds compile out caching without changing higher-level call sites.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/fscache.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/gen_smb1_mapping -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/gen_smb1_mapping

## Purpose
Perl generator for SMB1 error mapping C fragments. It parses annotated definitions from `nterr.h` or `smberr.h` and emits sorted mapping table entries for SMB1 status/error translation.

## Inputs And Outputs
Usage is `gen_smb1_mapping <in-file> <out-file>`.
Supported output targets:
- `smb1_mapping_table.c`: NT status to DOS class/code mappings.
- `smb1_err_dos_map.c`: DOS-class SMB1 error to POSIX error mappings.
- `smb1_err_srv_map.c`: server-class SMB1 error to POSIX error mappings.

## Parsing Logic
For `nterr.h`, it matches `#define NT_STATUS_*` entries with comments containing `CLASS, CODE`, resolves OR-ed hex values, skips duplicate macro names, sorts by numeric value, and merges synonyms with identical numeric values into a single display string.

For `smberr.h`, it tracks the current generated error class from comments, matches `ERR*`/`Err*` defines annotated with a negative POSIX error, sorts by numeric value, and filters output by `ERRDOS` or `ERRSRV`.

## Failure Behavior
The script exits with usage error for wrong arguments, dies on unreadable files, invalid annotated comments, empty mapping input, or unsupported output filename.

## Risks And Review Focus
- The script enforces annotation format strictly for commented macros, so header comment changes can break generation.
- It assumes output filename, not an explicit mode flag, selects generation type.
- SMB1 mappings depend on generated comments in headers staying accurate and consistently formatted.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/gen_smb1_mapping -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/gen_smb2_mapping -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/gen_smb2_mapping

## Purpose
Perl generator for SMB2/SMB3 NT status to POSIX error mapping table entries, sorted by numeric NT status code.

## Inputs And Outputs
Usage is `gen_smb2_mapping <in-h-file> <out-c-file>`. It reads status definitions from the input header and writes C initializer rows to the output file.

## Parsing Logic
The script matches lines shaped like `#define STATUS_NAME cpu_to_le32(0x...) // -ERR`, excluding `STATUS_SEVERITY*`. It rejects duplicate status macro names, stores the raw code, numeric code, status name, and POSIX error, sorts by numeric code, skips zero-valued statuses, and merges adjacent synonyms with identical numeric codes into a single `"A or B"` status string.

## Failure Behavior
The script exits with format help for wrong argument count and dies on duplicate statuses or file open/close failures.

## Risks And Review Focus
- It only recognizes `//` annotations in the exact expected format.
- It writes rows without a generated-file header, so the build rule or caller must provide surrounding context if needed.
- Synonym merging depends on sorted adjacency after numeric sort, which is correct for identical numeric codes.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/gen_smb2_mapping -->