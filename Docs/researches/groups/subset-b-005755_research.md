# Research Report: subset-b-005755

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/file.c -->
## sources/distributed-fs/ceph-client/fs/smb/client/file.c

Purpose: implements the CIFS/SMB client file-facing VFS behavior: open/reopen/close lifetime, netfs buffered/direct read and write dispatch, writeback integration, byte-range locking, fsync/flush, mmap, oplock and lease break handling, persistent-handle recovery, and experimental swap-file I/O over SMB3.

Important APIs and functions: the exported/requested surface includes `cifs_req_ops`, `cifs_open`, `cifs_close`, `cifs_closedir`, `cifs_file_flush`, `cifs_flush`, `cifs_fsync`, `cifs_strict_fsync`, `cifs_loose_read_iter`, `cifs_file_write_iter`, `cifs_strict_readv`, `cifs_strict_writev`, `cifs_flock`, `cifs_lock`, `cifs_reopen_persistent_handles`, `cifs_mark_open_files_invalid`, `cifs_write_subrequest_terminated`, `cifs_oplock_break`, and the address-space ops `cifs_addr_ops` and `cifs_addr_ops_smallbuf`. Central internal helpers are `cifs_prepare_read`, `cifs_issue_read`, `cifs_prepare_write`, `cifs_issue_write`, `cifs_reopen_file`, `cifs_nt_open`, `cifs_new_fileinfo`, `_cifsFileInfo_put`, lock conflict helpers, and readable/writable handle lookup helpers.

Control flow: netfs read/write requests are initialized with a `cifs_io_request`, select a session channel, negotiate or clamp rsize/wsize, acquire SMB credits, reopen invalid handles if needed, and call protocol-specific async read/write callbacks. VFS open builds the UNC-relative path, handles truncation, tries cached deferred-close handles, optionally uses legacy POSIX open, otherwise performs NT create/open, creates `cifsFileInfo`, registers it on inode and tree-connection lists, and activates fscache use. Close may defer SMB2 close when a lease and handle cache make that safe; final put removes list entries, closes or offloads server close, cancels oplock work, and frees lock/file state. Reconnect paths mark handles invalid, reopen durable/persistent handles, refresh metadata when safe, and replay byte-range locks. Lock operations first consult locally cached lock lists and then issue mandatory or legacy POSIX lock RPCs. Oplock breaks wait for pending writers, downgrade cache state, flush or invalidate mappings, push locks, close deferred handles if handle caching is lost, and acknowledge the break if a live handle remains.

State and persistence behavior: persistent state is remote SMB server state: file IDs, durable/persistent handles, locks, oplocks/leases, and cached close handles. Local state is held in `struct cifsFileInfo`, `struct cifsInodeInfo`, `struct cifs_fid_locks`, netfs request/subrequest objects, tcon open-file lists, deferred-close lists, fscache cookies, and mapping error state. `invalidHandle`, `need_reconnect`, `need_reopen_files`, oplock bits, lock lists, and netfs inode size/zero-point fields coordinate recovery and coherency. SMB credits are borrowed per subrequest and must be returned on all completion and failure paths.

Dependencies and integration points: depends on the VFS file, lock, mmap, writeback, swap, and address-space APIs; Linux netfs library; fscache helpers; CIFS inode/superblock/tcon/session structures; SMB dialect operation tables; SMB Direct segment limits; cached-directory/deferred-close helpers; DFS/path helpers; and CIFS tracepoints. It consumes mount policy from `fs_context` through flags such as strict/direct I/O, no byte-range locks, rwpidforward, fscache, and deferred close timeout.

Risks: credit accounting and XID lifetime span async paths and are easy to leak or double-return. Reopen must avoid deadlocks with rename and writeback while still preserving locks and cache coherency. Deferred close races with oplock breaks, kill_sb tree disconnect, and cached handle reuse. Mandatory byte-range lock emulation has subtle local/server consistency rules, especially with read/write cache oplocks. Cache invalidation after direct writes, lock-triggered oplock downgrade, and last-close strict-cache invalidation protect against stale data but can cause performance regressions if over-triggered.

Test signals: exercise buffered, direct, writeback, readahead, and SMB Direct reads/writes; O_WRONLY with fscache fallback; strict/loose/cache=none modes; deferred close reuse and expiration; reconnect with durable/persistent handle reopen and lock replay; oplock/lease break while dirty pages and locks exist; POSIX and mandatory locks including blocking waits and unlock ranges; fsync/flush with and without strictsync; mmap faults/page_mkwrite; forced shutdown; multichannel credit/channel selection; cached directory invalidation after reconnect; and swap activation rejection for sparse files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/fs_context.c -->
## sources/distributed-fs/ceph-client/fs/smb/client/fs_context.c

Purpose: implements the SMB3/CIFS new mount API parser, validator, context duplication/cleanup, remount/reconfigure path, mount serialization, UNC/prepath parsing, and translation from parsed mount options into CIFS superblock mount flags.

Important APIs and functions: the file defines `smb3_fs_parameters`, `smb3_init_fs_context`, `smb3_fs_context_dup`, `smb3_cleanup_fs_context_contents`, `smb3_cleanup_fs_context`, `smb3_parse_devname`, `cifs_sanitize_prepath`, `smb3_fs_context_fullpath`, `smb3_update_mnt_flags`, and `smb3_sync_session_ctx_passwords`. Important internal helpers parse dialects, security flavors, cache flavors, upcall target, reparse flavor, symlink flavor, monolithic comma-separated mount data, validation, tree acquisition, conflicting multichannel options, and reconfigure compatibility.

Control flow: `smb3_init_fs_context` allocates `struct smb3_fs_context`, seeds defaults such as SMB2.1-or-later dialect negotiation, strict cache mode, UID/GID defaults, SFM character remapping, attribute timeouts, deferred close timeout, and single-channel operation, then attaches `smb3_fs_context_ops`. Text options pass through `fs_parse` using `smb3_fs_parameters`; string options with empty user/password values are handled specially. The large option switch updates booleans, IDs, sizes, timeouts, address fields, UNC/source strings, dialect ops/values, security mode, cache mode, symlink/reparse policy, DFS, fscache, compression, RDMA, witness, multichannel, and persistent/resilient handle policy. Legacy monolithic mount data is split and fed back through the same parser. Before mount, validation enforces RDMA dialect minimums, CONFIG_KEYS for multiuser, UNC/share shape, destination address discovery, ports, and implicit forceuid/forcegid semantics. `smb3_get_tree` serializes mount creation under `cifs_mount_mutex`. Reconfigure rejects changes to identity/namespace/security fields, optionally permits password updates for expired sessions, handles rsize/wsize defaults, updates session passwords under `session_mutex`, scales multichannel sessions, swaps the active context, and refreshes mount flags.

State and persistence behavior: `struct smb3_fs_context` owns allocated strings for UNC, prepath, source, credentials, domain, hostname, iocharset, DFS fields, and symlink root, plus parsed address and policy fields. Password strings are freed with sensitive free paths. Remount uses deep copies and rollback copies to avoid losing the old active context on failure. Superblock flags are persisted in `cifs_sb->mnt_cifs_flags` and derived repeatedly from context fields.

Dependencies and integration points: integrates with Linux `fs_context` and `fs_parser`, VFS security option extraction, CIFS dialect operation/value tables, address parsing, tcon/session state, DFS remount support, multichannel session scaling, SMB Direct and optional compression/witness/fscache/rootfs configuration, and helpers in `fs_context.h` for aligned I/O sizes.

Risks: the parser has many interdependent options; conflicts such as persistent versus resilient handles, multichannel versus max_channels, multiuser versus mount upcall target, and SMB3-only RDMA must stay consistent. Context duplication and cleanup must remain field-for-field synchronized to avoid leaks, double frees, or lost credentials. Reconfigure mutates live session password and multichannel state and needs locking/rollback correctness. Monolithic comma parsing is compatibility-sensitive. Empty credentials and `sec=none` alter `nullauth` and username state.

Test signals: mount with all supported dialect strings and disabled legacy dialect builds; malformed and valid `//server/share/prepath` sources; IPv4/IPv6 `ip=` and UNC-derived address resolution; cache modes, fsc, RDMA, compression, witness, DFS off, symlink/reparse options, native socket toggles, and Unicode/NB session options; multichannel/max_channels conflict matrix; persistent/resilient conflict matrix; multiuser with CONFIG_KEYS disabled and upcalltarget=mount; remount password rotation on expired sessions; DFS remount; and memory-leak checks across parse failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/fs_context.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/fs_context.h -->
## sources/distributed-fs/ceph-client/fs/smb/client/fs_context.h

Purpose: declares the CIFS/SMB mount-context contract shared by the parser, mount code, and runtime users. It defines option IDs, dialect/cache/security parser enums, the full `struct smb3_fs_context`, mount error reporting, I/O-size alignment helpers, symlink policy resolution, mount serialization helpers, and read/write size negotiation helpers.

Important APIs and types: key types are `enum smb_version`, cache/reparse/symlink/security/upcall enums, `enum cifs_param`, and `struct smb3_fs_context`. Public helpers include `cifs_errorf`, `CIFS_ALIGN_WSIZE`, `CIFS_ALIGN_RSIZE`, `CIFS_ALIGN_BSIZE`, `cifs_symlink_type`, `smb3_fc2context`, `smb3_init_fs_context`, cleanup and duplicate prototypes, `smb3_sync_session_ctx_passwords`, `smb3_update_mnt_flags`, `cifs_sanitize_prepath`, `cifs_mount_lock`, `cifs_mount_unlock`, `cifs_negotiate_rsize`, `cifs_negotiate_wsize`, and `cifs_negotiate_iosize`.

Control flow: the header itself has mostly inline control flow. `cifs_io_align` reports unaligned mount sizes and rounds them down to page multiples with a page-size floor. `cifs_symlink_type` resolves the effective symlink implementation by checking explicit `symlink=`, then mfsymlinks, SFU emulation, negotiated POSIX/native extensions, reparse policy, and finally disabled symlinks. Negotiation helpers call dialect-specific server sizing callbacks, apply user caps if supplied, enforce a page-size minimum, and round down to page alignment.

State and persistence behavior: `struct smb3_fs_context` is the central persistent mount-policy snapshot copied into `cifs_sb_info`. It owns credential strings, UNC/source/prepath strings, NetBIOS names, destination/source addresses, UID/GID/mode policy, security and upcall choices, cache flags, POSIX/Unix extension preferences, DFS/reparse/symlink state, fscache, RDMA, multichannel, compression, witness, Unicode, timeout, size, and credit/channel limits. Its fields are later converted into superblock flags and consumed by file I/O, inode, DFS, session setup, and cache code.

Dependencies and integration points: includes CIFS global definitions plus Linux parser headers, and references `struct TCP_Server_Info`, `struct cifs_tcon`, `struct cifs_sb_info`, dialect operation/value tables, and mount-time parameter specs exported by `fs_context.c`. It is included broadly by CIFS mount and file paths to interpret cache, size, symlink, and mount-lock policy.

Risks: adding fields to `struct smb3_fs_context` requires updating duplication, cleanup, defaults, parser, reconfigure, and mount-flag derivation in `fs_context.c`. Bitfield defaults can silently change mount behavior. I/O size rounding can reduce user-requested values; callers must use `vol_rsize`/`vol_wsize` when original values matter. `cifs_symlink_type` depends on both mount options and negotiated server POSIX support, so behavior can differ before and after tree connect.

Test signals: build coverage across optional configs; mount option parser enum/spec synchronization; page-alignment warnings for rsize/wsize/bsize; symlink policy matrix for explicit symlink modes, mfsymlinks, SFU, Linux/POSIX extensions, and reparse disabled; negotiation with server min/max callbacks; and remount duplication/cleanup validation when new context fields are added.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/fs_context.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/fscache.c -->
## sources/distributed-fs/ceph-client/fs/smb/client/fscache.c

Purpose: connects CIFS/SMB tree connections and inodes to the Linux fscache/netfs cache backend. It creates per-share fscache volumes, constructs per-inode cookies keyed by stable server identity, records coherency data, and releases or unuses those cookies as files and inodes close.

Important APIs and functions: exported routines are `cifs_fscache_get_super_cookie`, `cifs_fscache_release_super_cookie`, `cifs_fscache_get_inode_cookie`, `cifs_fscache_unuse_inode_cookie`, and `cifs_fscache_release_inode_cookie`. Internal data and helpers include `struct cifs_fscache_inode_key` and `cifs_fscache_fill_volume_coherency`.

Control flow: super-cookie acquisition is guarded by `tcon->fscache_lock` and `tcon->fscache_acquired` so a tree connection only attempts acquisition once. It validates the server address family, extracts and sanitizes the share name, builds a key of the form `cifs,<server-address>,<share>`, fills volume coherency from resource ID, creation time, and serial number, then calls `fscache_acquire_volume`. A busy key is treated as a collision and leaves the tcon without a volume while still returning success. Inode-cookie acquisition builds a packed key from CIFS unique ID, creation time, and file type, fills mtime/ctime coherency via the header helper, acquires a cookie under the tcon volume, and forces release callbacks on the mapping if a cookie exists. Unuse optionally sends updated coherency and size. Release relinquishes the cookie and clears `cifsi->netfs.cache`.

State and persistence behavior: the cache backend persists data under the volume key and inode key. Runtime state lives in `tcon->fscache`, `tcon->fscache_acquired`, and `CIFS_I(inode)->netfs.cache`. Coherency metadata binds cached data to SMB volume identity and inode timestamps. The code intentionally does not retry once `fscache_acquired` is set unless the tcon is recreated.

Dependencies and integration points: depends on fscache APIs, netfs inode cache storage, CIFS tcon/session/server addresses, share-name extraction, inode unique IDs/create times, and tracepoints for tcon reference diagnostics. It is enabled by the mount option parsed in `fs_context.c` and used by file open/close and inode lifecycle paths.

Risks: the volume key must distinguish shares and server endpoints correctly; address formatting or share-name normalization changes can cause duplicate or missed cache volumes. Treating `-EBUSY` as a nonfatal collision avoids mount failure but silently disables caching for that tcon. Inode keys must match `cifs_find_inode()` comparison semantics or cached data may alias incorrectly. Coherency only records mtime/ctime at inode level, so server timestamp accuracy matters.

Test signals: fscache-enabled mounts for IPv4 and IPv6 servers, duplicate mounts to the same share causing `-EBUSY`, share names with slash normalization, regular inode cookie acquisition/release, file close with and without update coherency, stale timestamp invalidation, tcon teardown, and behavior when fscache volume acquisition fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/fscache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/fscache.h -->
## sources/distributed-fs/ceph-client/fs/smb/client/fscache.h

Purpose: declares the CIFS fscache interface and provides no-op stubs when `CONFIG_CIFS_FSCACHE` is disabled, allowing the rest of the client to call cache hooks unconditionally.

Important APIs and types: defines `struct cifs_fscache_volume_coherency_data` for share/volume coherency, `struct cifs_fscache_inode_coherency_data` for inode timestamp coherency, prototypes for super and inode cookie lifecycle functions, and inline helpers `cifs_fscache_fill_coherency`, `cifs_inode_cookie`, `cifs_invalidate_cache`, and `cifs_fscache_enabled`.

Control flow: when fscache is enabled, coherency filling snapshots inode ctime and mtime into little-endian seconds/nanoseconds fields. `cifs_inode_cookie` returns the netfs cookie embedded in `CIFS_I(inode)->netfs`. `cifs_invalidate_cache` packages current coherency and size and calls `fscache_invalidate` with caller-supplied invalidation flags. `cifs_fscache_enabled` queries the cookie state. When disabled, all lifecycle and invalidation functions become no-ops, the cookie accessor returns NULL, and enabled checks return false.

State and persistence behavior: the header defines the persistent coherency records that accompany cached CIFS data. The enabled path records cache state in the netfs inode context; disabled builds intentionally persist nothing and should not alter runtime behavior except missing cache acceleration.

Dependencies and integration points: includes Linux swap and fscache headers plus CIFS globals. It is included by file I/O, inode, and fscache implementation code. Invalidation flags passed by file paths include direct-write cases and general cache invalidation after remote or local coherency changes.

Risks: duplicate prototypes in the enabled section are harmless but make API drift easier to miss. Enabled and disabled builds have materially different behavior, so both need compile coverage. Timestamp-only inode coherency must remain aligned with the implementation and server metadata update rules. Callers must tolerate `cifs_inode_cookie()` returning NULL in disabled or failed-acquisition paths.

Test signals: build with `CONFIG_CIFS_FSCACHE=y` and `n`; direct-write invalidation via `cifs_invalidate_cache`; open/close use/unuse behavior; inode release clearing cookies; mtime/ctime coherency changes; and callers that use `cifs_fscache_enabled` to decide whether extra read access is needed for write-only opens.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/fscache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/gen_smb1_mapping -->
## sources/distributed-fs/ceph-client/fs/smb/client/gen_smb1_mapping

Purpose: Perl build helper that generates SMB1 error mapping C table fragments from annotated header definitions. It supports NT status to DOS class/code mapping and SMB1 DOS/SRV error to POSIX errno mapping.

Important APIs and functions: the script has no reusable Perl subroutines; its interface is `gen_smb1_mapping <in-file> <out-file>`. It recognizes input files ending in `nterr.h` or `smberr.h` and output targets `smb1_mapping_table.c`, `smb1_err_dos_map.c`, and `smb1_err_srv_map.c`. Main data structures are `@list` entries containing numeric value, macro name, class/code or POSIX error, and `%seen` for duplicate NT status macro names.

Control flow: argument validation requires exactly two parameters. For `nterr.h`, the script folds backslash continuations, matches `#define NT_STATUS_*` lines with structured comments containing `CLASS, CODE`, parses expressions joined by `|`, deduplicates macro names, and rejects commented NT status lines that do not match the mapping format. For `smberr.h`, it tracks the current error class from comments such as generated `ERRDOS`/`ERRSRV` class markers, matches annotated `ERR*`/`Err*` defines with POSIX errno comments, and rejects malformed annotated lines. It dies if no entries are found, sorts numerically, writes an autogenerated banner, and emits the selected C initializer format. Equal NT status values are merged into one output row with `"name or synonym"` text.

State and persistence behavior: all state is transient during code generation. Persistent output is the generated C table fragment consumed by the SMB1 error translation build. The output depends on header comments as an input contract, not just macro values.

Dependencies and integration points: depends on Perl, annotated `nterr.h`/`smberr.h`, and the build rules that call it for SMB1 mapping tables. Generated files integrate with CIFS/SMB error conversion paths that translate protocol status into DOS class/code or Linux errno.

Risks: strict comment parsing means harmless-looking header comment edits can break the build. Numeric parsing supports hex, decimal SMB errors, and simple OR expressions for NT status values but not arbitrary C expressions. Synonym merging depends on sorted numeric values. The class for SMB1 DOS/SRV entries is inferred from surrounding comments, so misplaced markers can route entries to the wrong generated table.

Test signals: run against current `nterr.h` and `smberr.h`; add duplicate/synonym NT statuses and verify one merged row; malformed annotated comments should fail; no-entry inputs should fail; DOS and SRV outputs should filter by class; and generated C should compile with the SMB1 mapping consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/gen_smb1_mapping -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/gen_smb2_mapping -->
## sources/distributed-fs/ceph-client/fs/smb/client/gen_smb2_mapping

Purpose: Perl build helper that generates an SMB2/SMB3 NT status to POSIX errno mapping table from annotated NT status header definitions, sorted by numeric status code.

Important APIs and functions: the script interface is `gen_smb2_mapping <in-h-file> <out-c-file>`. It uses `%statuses` to detect duplicate status macro names and `@list` to hold parsed records containing macro name, hex code string, numeric code, and errno text.

Control flow: argument validation requires two parameters. The input loop reads lines, matches defines of the form `#define STATUS_NAME cpu_to_le32(0x...) // -ERRNO`, skips severity helper macros, rejects duplicate status names, and stores parsed entries. After sorting by numeric code, it writes C initializer lines, skips zero status, and merges adjacent synonyms with the same numeric code into a single descriptive string joined with `or`. A padding calculation is retained but the final print emits a compact `{ code, error, "names" },` row.

State and persistence behavior: runtime state is temporary. The persistent artifact is the generated mapping table used by SMB2/SMB3 error handling to report Linux errors from protocol NTSTATUS responses. Like the SMB1 generator, the script treats structured comments as part of the source contract.

Dependencies and integration points: depends on Perl and a header that expresses statuses as `cpu_to_le32(hex)` with trailing POSIX errno comments. The generated output is consumed by SMB2 status/error mapping code in the CIFS client.

Risks: only one exact macro/comment style is recognized, so formatting changes in the input header can silently omit entries unless tests compare expected counts. Duplicate numeric values are intentionally merged, but duplicate macro names are fatal. Status code zero is skipped, so callers must handle success outside the generated error table. The script does not validate that errno names are real Linux errno constants.

Test signals: run generation against the current SMB2 status header; verify sorted numeric output and skipped zero status; introduce synonym status codes and confirm merged names; duplicate macro names should fail; malformed annotations should be detected by output count or build checks; and generated mappings should compile and translate representative SMB2/SMB3 errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/gen_smb2_mapping -->
