# subset-b-009942

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_open.c -->
# sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_open.c

Purpose: `pvfs_open.c` is the POSIX NTVFS backend's open, close, delete-on-close, sharing, and open-database coordination layer. It maps generic SMB open/close requests into POSIX file descriptors or directory handles while preserving Windows share-mode, oplock, byte-range-lock, stream, EA, ACL, notification, and delete-on-close semantics.

Important APIs, types, and functions: Public entry points include `pvfs_find_fd`, `pvfs_locking_key`, `pvfs_odb_retry_setup`, `pvfs_open`, `pvfs_close`, `pvfs_logoff`, `pvfs_exit`, `pvfs_set_delete_on_close`, `pvfs_can_delete`, `pvfs_can_rename`, `pvfs_can_update_file_size`, `pvfs_can_stat`, and `pvfs_delete_on_close_set`. Important local helpers include `pvfs_open_directory`, `pvfs_create_file`, `pvfs_open_deny_dos`, `pvfs_open_setup_retry`, `pvfs_handle_destructor`, and `pvfs_brl_locking_handle`. The state model is built around `struct pvfs_file`, `struct pvfs_file_handle`, `struct pvfs_filename`, `struct odb_lock`, and `struct brl_handle`.

Control flow: `pvfs_open` normalizes legacy open levels through `ntvfs_map_open`, validates share/access/create options, handles root FIDs, resolves paths with stream support, dispatches directory opens to `pvfs_open_directory`, and dispatches absent base-file creation to `pvfs_create_file`. Existing file opens allocate an `ntvfs_handle`, build open-db and byte-range-lock keys from dev/inode plus optional stream name, lock the open database, check share access through `odb_can_open`, optionally install an async retry, open the POSIX file with `pvfs_sys_open`, register the open with `odb_open_file`, set up oplocks, create or truncate streams, refresh stat/DOS metadata, then publish backend handle data. `pvfs_close` optionally returns SMB2 close information and frees the `pvfs_file`, which triggers destructors.

State and persistence behavior: Persistent share/open state lives in the Samba open database; the locking key is a zeroed `{dev_t, ino_t}` blob. Stream byte-range locks append the stream name to that key. Per-connection live files are linked in `pvfs->files.list`; handle lifetime is talloc-driven. Close destructors close fds, remove open-db records, apply delayed write times through `odb_set_write_time` and `utimes`, honor delete-on-close, remove filesystem/EADB xattrs with `pvfs_xattr_unlink_hook`, and send notify events. File creation stores DOS attributes, initial EAs, streams, and ACLs through xattr/ACL helpers.

Dependencies and integration points: The file integrates with name resolution, ACL checks, byte-range locking, open-db share modes, oplocks, notify, xattrs/EADB, stream helpers, POSIX syscall wrappers, ntvfs handle storage, async wait messages, and generic SMB open/close mapping. It is the main caller of many helpers in this subset.

Risks: This is race-sensitive code. Correctness depends on re-resolving after creation, preserving dev/inode identity, keeping open-db locks alive only where needed for retry, and not leaking half-created files. DENY_DOS semantics intentionally create shared low-level handles. Delete-on-close differs for SMB1 and SMB2. Stream IDs are hash-based and therefore probabilistic. Error mapping and async retry timing affect Windows compatibility.

Test signals: Strong coverage should include Samba torture cases for create dispositions, share violations, async retry, DENY_DOS/FCB, delete-on-close, oplock grant/break, SMB2 close info, root FID opens, stream create/open/truncate/delete, EA/ACL initialization, and concurrent create/open races. Existing comments reference gentest, ifstest, and BASE-DENYDOS behavior as compatibility signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_open.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_oplock.c -->
# sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_oplock.c

Purpose: `pvfs_oplock.c` handles opportunistic-lock state for open PVFS files. It registers local recipients for open-db oplock break messages, forwards breaks to SMB clients, updates the open database when clients release or downgrade oplocks, and asks the open database to break level-II oplocks before writes.

Important APIs, types, and functions: The central local type is `struct pvfs_oplock`, which tracks the owning `pvfs_file_handle`, the `pvfs_file` needed for client callbacks, the current oplock level, first-break timestamps, and the messaging context. Public functions are `pvfs_setup_oplock`, `pvfs_oplock_release`, and `pvfs_break_level2_oplocks`. Key helpers are `pvfs_oplock_release_internal`, `pvfs_oplock_break`, `pvfs_oplock_break_dispatch`, and the destructor that deregisters `MSG_NTVFS_OPLOCK_BREAK`.

Control flow: `pvfs_setup_oplock` translates open-db return values into internal levels, allocates an oplock object under the file handle, and registers an imessaging callback. When a break message arrives, `pvfs_oplock_break_dispatch` validates payload length, ignores messages for other file handles, and calls `pvfs_oplock_break`. The break handler sends `ntvfs_send_oplock_break` once per target level, suppresses duplicate sends until the configured timeout, then auto-releases through `pvfs_oplock_release_internal`. Client lock requests call `pvfs_oplock_release`, extract the break level from the lock mode, and update open-db state.

State and persistence behavior: Runtime oplock state is attached to `h->oplock`; durable/interprocess visibility is in the open database via `odb_update_oplock` and `odb_break_oplocks`. If a break reaches none, the local oplock object is freed. Break timestamps prevent repeated client notifications before timeout.

Dependencies and integration points: This file depends on the open database, imessaging, ntvfs oplock-break delivery, tevent time helpers, and `pvfs_open.c` handle state. `pvfs_write.c`, `pvfs_setfileinfo.c`, and open handling call into it before operations that invalidate level-II caching.

Risks: Pointer identity in the message payload is process-local coordination and must match the open-db sender's assumptions. Failure paths return `NT_STATUS_FOOBAR` in several internal-error cases, which is imprecise. Auto-release after timeout trades client correctness for server progress. Message registration lifetime must match handle lifetime.

Test signals: Exercise exclusive, batch, and level-II grants; break-to-level-II and break-to-none; duplicate break suppression; timeout auto-release; client release via LOCKX; write-triggered level-II breaks; and cleanup on handle close.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_oplock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_qfileinfo.c -->
# sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_qfileinfo.c

Purpose: `pvfs_qfileinfo.c` implements path and handle metadata queries for the POSIX NTVFS backend. It maps `struct pvfs_filename` stat/DOS/xattr/ACL/stream state into the many SMB1, trans2, NT, and SMB2 file-information levels.

Important APIs, types, and functions: Public functions are `pvfs_query_ea_list`, `pvfs_qpathinfo`, and `pvfs_qfileinfo`. Important helpers are `pvfs_fileinfo_access`, `pvfs_query_all_eas`, and `pvfs_map_fileinfo`. It fills `union smb_fileinfo`, `struct smb_ea_list`, `struct stream_information`, and security descriptor query structures.

Control flow: `pvfs_qpathinfo` resolves the input path with stream support, verifies the stream exists, checks open-db stat permission through `pvfs_can_stat`, enforces the access bits required by the information level, then calls `pvfs_map_fileinfo`. `pvfs_qfileinfo` finds the open handle, checks the handle's granted access mask, refreshes the handle name and DOS metadata through `pvfs_resolve_name_handle`, maps common fields, then patches handle-only fields such as delete-pending, current position, access mask, and mode.

State and persistence behavior: This file does not mutate filesystem data. It reads current POSIX stat data, DOS metadata stored in xattrs/EADB, stream indexes, EA lists, ACL xattrs, open-db delete-on-close/write-time state, and handle-local position/mode fields. For SMB2 all-information, it synthesizes a share-prefixed path rather than exposing the real server path.

Dependencies and integration points: It depends on `pvfs_resolve.c`, access checks, `pvfs_open.c` share/stat helpers, xattr EA loaders, stream information helpers, ACL query hooks, short-name mangling, and protocol version checks.

Risks: Each information level has slightly different access and field semantics; regressions here are often wire-compatibility regressions. `name_info` is deliberately unsupported for SMB2 in one level. Delete-pending decrements link count in handle queries only. EA queries omit zero-length EAs and SMB2 all-EAs maps no EAs to `NT_STATUS_NO_EAS_ON_FILE`.

Test signals: Cover every `RAW_FILEINFO_*` level, especially SMB2 all information, stream info, all-EAs/no-EAs behavior, security descriptors with SACL flags, delete-on-close visibility, handle position/mode reporting, and path queries blocked by share-mode or ACL rules.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_qfileinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_read.c -->
# sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_read.c

Purpose: `pvfs_read.c` implements file reads for the POSIX NTVFS backend, primarily the generic `RAW_READ_READX` path after older SMB read levels have been mapped by common ntvfs code.

Important APIs, types, and functions: The single exported function is `pvfs_read`. It works with `union smb_read`, `struct pvfs_file`, `struct pvfs_file_handle`, byte-range lock checks, and either POSIX `pread` or `pvfs_stream_read`.

Control flow: Non-READX levels are delegated to `ntvfs_map_read`. READX finds the backend handle with `pvfs_find_fd`, rejects directories or invalid devices where `fd == -1`, builds the required access mask from `SEC_FILE_READ_DATA` and optional execute-read semantics, validates the handle grant, rejects overly large SMB1 read counts, checks byte-range locks with `pvfs_check_lock`, then reads from an alternate stream or POSIX fd. SMB2 honors `mincnt`: short reads below `mincnt`, or EOF with a nonzero request length, return `NT_STATUS_END_OF_FILE`. Successful reads update both `position` and `seek_offset` to offset plus bytes read.

State and persistence behavior: Reads do not persist metadata. They mutate only handle-local current position fields. Stream reads load stream blobs from xattr/EADB state through the stream layer.

Dependencies and integration points: It depends on open handle lookup, security masks from generated security headers, strict byte-range lock enforcement, stream storage helpers, POSIX errno mapping, and protocol version from the request context.

Risks: SMB1 and SMB2 size/minimum-count behavior differs. Stream reads materialize blob data rather than using a native file descriptor, so large streams depend on xattr/EADB limits and memory behavior. Correct lock range checking is critical to Windows semantics.

Test signals: Exercise SMB1 and SMB2 reads, read-for-execute access, denied read masks, directory-handle reads, locked ranges, max-count validation for SMB1, EOF/mincnt handling, and alternate data stream reads.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_read.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_rename.c -->
# sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_rename.c

Purpose: `pvfs_rename.c` implements legacy SMB rename, NT rename, hard-link, copy, stream rename, wildcard rename, open-db path updates, and notify generation for the POSIX backend.

Important APIs, types, and functions: Public functions are `pvfs_do_rename` and `pvfs_rename`. Local helpers include wildcard expansion (`pvfs_resolve_wildcard_component`, `pvfs_resolve_wildcard`), async retry (`pvfs_retry_rename`, `pvfs_rename_setup_retry`), `pvfs_rename_one`, `pvfs_rename_wildcard`, `pvfs_rename_mv`, `pvfs_rename_stream`, and `pvfs_rename_nt`.

Control flow: `pvfs_rename` dispatches by raw rename level. SMBmv-style rename resolves both patterns with wildcard support; wildcard renames list matching source entries and rename each within the same directory. Non-wildcard renames check source existence, destination absence, attribute filters, parent add-file access, and `pvfs_can_rename`, then call `pvfs_do_rename`. NT rename accepts rename, hard-link, copy, and move-cluster flags, rejecting unsupported flags and wildcard NT renames. Stream renames require a colon-prefixed target and delegate to `pvfs_stream_rename`. Sharing/oplock conflicts can install async retries through the shared ODB retry machinery.

State and persistence behavior: `pvfs_do_rename` calls `pvfs_sys_rename`, updates the open database with `odb_rename`, and emits remove/add or old-name/new-name notifications depending on whether the parent directory changed. Hard links use POSIX `link`; copy uses `pvfs_copy_file`, preserving DOS metadata through xattrs. Stream renames update stream xattr records rather than POSIX directory entries.

Dependencies and integration points: It integrates with path resolution, directory listing, access checks, open-db share checks, syscall wrappers, notify, stream helpers, file-copy utilities, and async wait callbacks.

Risks: Wildcard pattern rules are old-SMB-specific and easy to break. `pvfs_rename_one` does not preserve the lock pointer after freeing its talloc context, so lock lifetime is tied to careful flow. Cross-directory notify semantics differ from same-directory rename semantics. Hard link and copy paths do not update open-db path state in the same way as rename.

Test signals: Cover SMBmv wildcards, NT rename flags, hard-link and copy behavior, stream rename overwrite/no-overwrite, same-name no-op, destination collision, parent ACL denial, sharing violation retry, oplock-not-granted retry, and notify event ordering.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_rename.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_resolve.c -->
# sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_resolve.c

Purpose: `pvfs_resolve.c` converts client CIFS paths into validated POSIX paths and populated `struct pvfs_filename` objects. It centralizes path syntax checks, case-insensitive lookup, short-name lookup, stream parsing, wildcard handling, stat refresh, open-handle path refresh after rename, and parent resolution.

Important APIs, types, and functions: Public functions are `pvfs_resolve_name`, `pvfs_resolve_partial`, `pvfs_resolve_name_fd`, `pvfs_resolve_name_handle`, and `pvfs_resolve_parent`. Helpers include `component_compare`, `pvfs_case_search`, `parse_stream_name`, `pvfs_unix_path`, and `pvfs_reduce_name`.

Control flow: `pvfs_resolve_name` allocates `pvfs_filename`, strips stream support if the filesystem lacks named streams, rejects leading slash under SMB2, runs `pvfs_unix_path`, optionally reduces repeated separators or dot-dot syntax, and then either validates wildcard parent existence or stats/case-searches the final path. `pvfs_case_search` breaks the path into components beneath the share root, rejects reserved DOS names, consults the mangled-name cache, tries exact stat first, then scans directories case-insensitively. `pvfs_resolve_name_fd` refreshes stat data from fd or path and rejects dev/inode changes. `pvfs_resolve_name_handle` also consults the open database for renamed open files.

State and persistence behavior: Resolution itself is transient, but it reads persisted DOS metadata through `pvfs_fill_dos_info`, stream indexes through that path, and open-db path/write-time state for open handles. `allow_override` defaults false and follows the resolved name.

Dependencies and integration points: It depends on short-name mangling, stream metadata, `pvfs_fill_dos_info`, POSIX `stat`/directory scanning, protocol version, filesystem capability flags, and open-db path lookup. Nearly every other PVFS operation consumes its `pvfs_filename` output.

Risks: Path parsing is security-critical. Incorrect dot-dot reduction, separator handling, stream colon parsing, case-insensitive search, or dev/inode identity checks can cause path traversal or race issues. Stream IDs are hashes. SMB2 path syntax differs from SMB1.

Test signals: Cover illegal characters, control characters, repeated separators, dot and dot-dot components, leading SMB2 slashes, wildcards only in final component, reserved names, mangled short-name lookup, case-insensitive filesystems, stream names with `:$DATA`, and fd identity races.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_resolve.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_search.c -->
# sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_search.c

Purpose: `pvfs_search.c` implements directory enumeration for old SMB search, TRANS2 find-first/find-next, SMB2 find, and find-close operations. It converts directory entries into requested wire information levels while tracking resumable search state.

Important APIs, types, and functions: Public functions are `pvfs_search_first`, `pvfs_search_next`, and `pvfs_search_close`. Local helpers include `pvfs_search_destructor`, timer setup/cleanup functions, `fill_search_info`, `pvfs_search_fill`, old search handlers, trans2 handlers, and SMB2 handlers. State is `struct pvfs_search_state` plus `pvfs->search.idtree` and per-directory-handle `f->search` for SMB2.

Control flow: Search-first resolves a wildcard path, checks parent traverse/list access, starts a `pvfs_dir` listing, allocates a search state, and fills up to the requested count with `pvfs_search_fill`. Each entry is resolved with `pvfs_resolve_partial`, filtered by attributes, and mapped according to `enum smb_search_data_level`. Old SMB searches allocate small numeric handles in an idtree and age out forgotten entries. TRANS2 searches support resume keys, last-name seeks, close flags, and EA-name lists. SMB2 searches require an open directory handle, validate pattern syntax, restart or single-entry flags, and store state on the directory `pvfs_file`.

State and persistence behavior: Search state is in memory only. Old and TRANS2 searches are stored in `pvfs->search.list`/idtree and guarded by inactivity timers; SMB2 state is owned by the directory handle. Directory entry metadata is read from POSIX stat and xattr/EADB DOS metadata at fill time.

Dependencies and integration points: It depends on name resolution, directory listing helpers, access checks, EA queries, short-name mangling, idtree, tevent timers, and ntvfs search callbacks that serialize results.

Risks: Resume offsets are truncated to 32 bits in result fields and rely on `pvfs_list_seek_ofs` to cope. Old clients often forget close requests, so cleanup policy matters. Returning zero results maps to different status values by protocol. SMB2 searches destroy previous handle search state on new search-first.

Test signals: Cover old SMB search handles/cookies, TRANS2 resume by name/key, close-if-end flags, SMB2 restart/single flags, attribute and must-attribute filters, EA-list levels, short-name fields, no-match statuses, and timer cleanup of leaked searches.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_search.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_seek.c -->
# sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_seek.c

Purpose: `pvfs_seek.c` implements SMB seek semantics for open PVFS file handles. It updates the handle's logical seek offset and returns the resulting value.

Important APIs, types, and functions: The only exported function is `pvfs_seek`. It uses `union smb_seek`, `struct pvfs_file`, and `struct pvfs_file_handle`, with `SEEK_MODE_START`, `SEEK_MODE_CURRENT`, and `SEEK_MODE_END`.

Control flow: `pvfs_seek` finds the backend handle through `pvfs_find_fd` and returns `NT_STATUS_INVALID_HANDLE` if absent. For start-relative seeks it assigns the requested offset. For current-relative seeks it adds the requested offset to `h->seek_offset`. For end-relative seeks it refreshes metadata with `pvfs_resolve_name_fd(..., PVFS_RESOLVE_NO_OPENDB)` and sets the offset to current file size plus the requested offset. The resulting offset is returned in `io->lseek.out.offset`.

State and persistence behavior: The function mutates only `h->seek_offset`; it does not call POSIX `lseek` and does not affect durable file contents or xattrs. End-relative seeks refresh the handle's `pvfs_filename` stat/DOS state.

Dependencies and integration points: It depends on open handle lookup and `pvfs_resolve_name_fd`. Read and write paths independently update `position` and `seek_offset`; this function is part of that handle-local position model.

Risks: The code does not reject unknown seek modes explicitly, leaving the default `NT_STATUS_OK` and previous offset unchanged. It does not validate overflow or negative results after unsigned arithmetic. End-relative seek on a directory fd of `-1` still uses path stat through `pvfs_resolve_name_fd`.

Test signals: Cover invalid handles, all three modes, end-relative seek after external size changes, unknown mode behavior, large offset arithmetic, and interaction with subsequent read/write position reporting.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_seek.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_setfileinfo.c -->
# sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_setfileinfo.c

Purpose: `pvfs_setfileinfo.c` implements metadata updates by open handle and by pathname. It handles timestamps, DOS attributes, EAs, delete-on-close, allocation and EOF size changes, position/mode, stream and file renames, and security descriptor writes.

Important APIs, types, and functions: Public functions are `pvfs_setfileinfo_ea_set`, `pvfs_setfileinfo`, and `pvfs_setpathinfo`. Key helpers are `pvfs_setfileinfo_access`, `pvfs_setfileinfo_rename_stream`, `pvfs_setfileinfo_rename`, `pvfs_retry_setpathinfo`, and `pvfs_setpathinfo_setup_retry`.

Control flow: Both set-by-handle and set-by-path compute required access from the information level, refresh or resolve current file state, copy current `pvfs_filename` data into `newstats`, and update fields according to the level. EA levels update xattr-backed DOS EAs immediately. Delete disposition delegates to `pvfs_set_delete_on_close`. Allocation/EOF changes break level-II oplocks and truncate POSIX files or stream blobs. Rename levels delegate to the shared rename helper and update open-db path state. Security descriptor updates notify and call the ACL backend. After field changes, the code applies size changes, `utimes`, open-db write-time updates, chmod/fchmod for DOS attributes, notify events, and `pvfs_dosattrib_save`.

State and persistence behavior: It persists DOS attributes, EA size, create/change times, allocation size, and stream metadata in xattrs/EADB; POSIX size changes use `truncate`/`ftruncate`; timestamps use `utimes`; mode changes use PVFS syscall wrappers. Open-handle write-time timers are canceled or forced when an explicit write time is set.

Dependencies and integration points: It integrates with access checks, path resolution, open-db share/oplock checks, async retry, stream helpers, xattr DOS EA storage, ACL backends, notify, chmod wrappers, and `pvfs_open.c` delete-on-close logic.

Risks: Setpathinfo and setfileinfo differ subtly for access, open-db checks, ignored levels, and allocation-size increase handling. Size updates must coordinate with oplocks and share modes. A missing `talloc_free(lck)` in some error paths would be easy to introduce around retries. Rename semantics differ by SMB1 and SMB2.

Test signals: Cover every set info level, explicit and delayed write times, allocation versus EOF truncation, path-level sharing retry, stream truncation, EA add/update/delete via zero-length values, delete-on-close rules, SMB2 rename paths, ACL writes, and notify masks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_setfileinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_shortname.c -->
# sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_shortname.c

Purpose: `pvfs_shortname.c` implements 8.3 short-name generation, mangled-name detection, reverse lookup through a prefix cache, and DOS reserved-name checks for the POSIX backend.

Important APIs, types, and functions: Public functions are `pvfs_mangle_init`, `pvfs_short_name_component`, `pvfs_short_name`, `pvfs_mangled_lookup`, `pvfs_is_reserved_name`, and `pvfs_is_mangled_component`. The main state type is `struct pvfs_mangle_context`, containing character flags, mangle prefix/modulus, direct-mapped prefix cache, and base-36 reverse table. Important helpers are `mangle_hash`, `is_mangled_component`, `is_8_3`, `check_cache`, `is_reserved_name`, `is_legal_name`, `name_map`, and `init_tables`.

Control flow: Initialization reads `mangle:cachesize` and `mangle:prefix`, allocates the prefix cache, validates prefix length, and builds character classification tables. `name_map` returns no conversion for valid 8.3 names or legal long names when 8.3 is not required; otherwise it builds a `PREFIX~HASH.EXT` name using uppercase ASCII lead characters, a base-36 FNV-derived hash, and up to three ASCII extension characters. Reverse lookup recognizes mangled syntax, decodes the hash, and returns the cached original prefix plus extension.

State and persistence behavior: The cache is in-memory and direct-mapped, so reverse lookup is opportunistic and can miss after eviction or restart. Short names are not persisted. Reserved-name and legality decisions are deterministic from tables.

Dependencies and integration points: It depends on `pvfs_name_hash`, Samba charset/codepoint helpers for long-name legality, loadparm for mangle settings, and path resolution/search/query code that exposes short names or resolves mangled components.

Risks: The file intentionally uses byte-oriented string routines in many places; replacing them with multibyte helpers can break the algorithm. Hash collisions and direct-map cache eviction mean reverse lookup is not authoritative. Only restricted ASCII is allowed for generated 8.3 names.

Test signals: Cover valid 8.3 pass-through, long-name mangling, reserved DOS names, non-ASCII leading characters, extension handling, wildcard legality, cache lookup/eviction, configurable prefix lengths, and case-insensitive matching of mangled names.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_shortname.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_streams.c -->
# sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_streams.c

Purpose: `pvfs_streams.c` implements Windows alternate data streams on top of xattrs or the PVFS EADB backend. It maintains stream indexes, exposes stream information, and provides read/write/truncate/create/delete/rename behavior for stream data.

Important APIs, types, and functions: Public functions include `pvfs_stream_information`, `pvfs_stream_info`, `pvfs_stream_rename`, `pvfs_stream_create`, `pvfs_stream_delete`, `pvfs_stream_read`, `pvfs_stream_write`, and `pvfs_stream_truncate`. Helpers include `stream_name_normalise`, `stream_name_cmp`, `pvfs_stream_update_size`, and `pvfs_stream_load`.

Control flow: Stream names are normalized by dropping `:$DATA` suffixes. Querying stream information returns the default `::$DATA` stream plus xattr-indexed streams. `pvfs_stream_info` marks the default stream as always existing and searches the stream index for named streams. Create creates the per-stream xattr and adds a zero-size index entry. Reads load the stream blob, clamp to available bytes, and copy data. Writes load or create a blob, extend with zero fill as needed, save it, then update the stream index. Truncate resizes a blob and updates the index. Rename updates index names and handles overwrite rules; delete removes both the data xattr and index entry.

State and persistence behavior: Stream payloads are individual xattrs with `XATTR_DOSSTREAM_PREFIX`; stream metadata lives in the `XATTR_DOSSTREAMS_NAME` NDR xattr. Data can also be stored in the TDB EADB. Size and allocation values are persisted in the stream index and rounded through PVFS allocation rounding.

Dependencies and integration points: It uses xattr wrappers, NDR-generated xattr structures, allocation rounding, and is called by open, read, write, setfileinfo, qfileinfo, rename, unlink, and resolve paths.

Risks: Stream I/O loads whole blobs into memory. Filesystem xattr stream size limits differ from EADB limits. Case-insensitive stream lookup can require a second index scan. The default stream cannot be renamed over. Metadata and payload xattrs must remain consistent across failures.

Test signals: Cover stream create/open/read/write/sparse extension/truncate/delete, case-insensitive stream names, `:$DATA` normalization, stream information listing, overwrite rename, size-limit failures with and without EADB, and cleanup on delete-on-close.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_streams.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_sys.c -->
# sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_sys.c

Purpose: `pvfs_sys.c` wraps POSIX filesystem syscalls so PVFS can optionally override `EACCES` after ACL checks while reducing symlink-attack risk. It is the low-level bridge for open, unlink, rename, mkdir, rmdir, chmod, and fchmod operations.

Important APIs, types, and functions: Public wrappers are `pvfs_sys_open`, `pvfs_sys_unlink`, `pvfs_sys_rename`, `pvfs_sys_mkdir`, `pvfs_sys_rmdir`, `pvfs_sys_fchmod`, and `pvfs_sys_chmod`. Local state is `struct pvfs_sys_ctx`, which holds root-privilege state, original working directory, and original cwd stat. Helpers include `pvfs_sys_pushdir_destructor`, `pvfs_sys_chdir_nosymlink`, `pvfs_sys_pushdir`, `pvfs_sys_fchown`, `pvfs_sys_chown`, and `contains_symlink`.

Control flow: Each wrapper first attempts the normal syscall. If it succeeds, override is disabled, or failure is not `EACCES`, the result is returned. Otherwise `pvfs_sys_pushdir` gains root privileges, records cwd, safely changes to the path's parent while checking intermediate symlinks, rewrites the operand to a basename, and retries. Creation paths chown newly created files/directories back to the original uid. Rename additionally checks the destination for symlink behavior before and after the privileged rename.

State and persistence behavior: Wrappers mutate filesystem objects and ownership/modes but do not store Samba metadata. Temporary privilege and cwd state is talloc-scoped and restored by destructor; restoration panics if the cwd identity changed unexpectedly.

Dependencies and integration points: It depends on Samba `root_privileges`, POSIX open/unlink/rename/mkdir/rmdir/chmod APIs, `O_NOFOLLOW`/`O_DIRECTORY` where available, and the `allow_override` flag computed by higher-level PVFS access logic.

Risks: Process-wide `chdir` during privileged operations is inherently delicate in evented servers. Systems without `O_NOFOLLOW` or `O_DIRECTORY` are less protected. Symlink detection is platform-specific and maps several OS-specific errno values. Incorrect caller use before ACL checks would be a privilege bug.

Test signals: Cover normal and override paths for each wrapper, ownership after privileged create/mkdir, symlink-in-parent rejection, destination symlink rejection on rename, cwd restoration, disabled override, and behavior on platforms lacking no-follow flags.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_sys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_unlink.c -->
# sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_unlink.c

Purpose: `pvfs_unlink.c` implements file and stream deletion for the POSIX backend, including wildcard deletes, attribute filtering, share-mode checks, async retry on sharing/oplock conflicts, xattr cleanup, and notify events.

Important APIs, types, and functions: The public entry point is `pvfs_unlink`. Local helpers are `pvfs_retry_unlink`, `pvfs_unlink_setup_retry`, `pvfs_unlink_file`, and `pvfs_unlink_one`.

Control flow: `pvfs_unlink` resolves the requested pattern with wildcard, stream, and no-open-db flags. It rejects absent non-wildcard names and directory targets, then either deletes one resolved object or starts a directory listing for wildcard deletes. Wildcard deletes disable async retry until properly tested, iterate matching entries, reject dot entries when directory attributes are involved, resolve each entry partially, and call `pvfs_unlink_one`. `pvfs_unlink_one` enforces attribute filters, calls `pvfs_can_delete` to check open-db share and delete rights, optionally installs async retry, then deletes a stream through `pvfs_stream_delete` or a normal file through `pvfs_unlink_file`.

State and persistence behavior: Normal file deletion removes EADB/system xattrs through `pvfs_xattr_unlink_hook` when the file has a single link, calls `pvfs_sys_unlink`, and emits file-name removal notifications. Stream deletion updates stream xattrs and the stream index. Open-db state is consulted, not directly mutated except through retry registration.

Dependencies and integration points: It depends on name resolution, directory listing, attribute matching, delete/share checks in `pvfs_open.c`, async wait/retry infrastructure, stream deletion, xattr cleanup, syscall wrappers, and notify.

Risks: Wildcard deletion deliberately disables async behavior, so sharing conflicts in a batch may produce partial progress. Xattr cleanup only runs at link count one, which is correct for hard links but important to preserve. Directory deletion is not handled here. Error status after wildcard operations is the last failure unless at least one delete succeeds.

Test signals: Cover single file delete, stream delete, wildcard delete with partial failures, hidden/system/directory attribute filters, dot entry rejection, sharing violation retry, oplock-not-granted retry, hard-link xattr retention, notify emission, and permission override behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_unlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_util.c -->
# sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_util.c

Purpose: `pvfs_util.c` provides small shared helpers for wildcard detection, errno mapping, attribute matching/normalization, file copy, name hashing, and allocation-size rounding.

Important APIs, types, and functions: Public functions are `pvfs_has_wildcard`, `pvfs_map_errno`, `pvfs_match_attrib`, `pvfs_attrib_normalise`, `pvfs_copy_file`, `pvfs_name_hash`, and `pvfs_round_alloc_size`.

Control flow: `pvfs_has_wildcard` checks for SMB wildcard characters. `pvfs_map_errno` uses Samba common Unix-to-NTSTATUS mapping and logs at debug level 10. `pvfs_match_attrib` enforces search/delete attribute inclusion rules for directories, hidden/system files, and must-have attributes. `pvfs_attrib_normalise` removes `FILE_ATTRIBUTE_NORMAL` when other bits are present and synchronizes the directory bit with POSIX mode. `pvfs_copy_file` opens source and destination through PVFS syscall wrappers, copies in 64 KiB chunks, cleans up incomplete destinations, applies mode derived from source DOS attributes, copies DOS metadata, and saves DOS attributes. `pvfs_name_hash` implements case-folded FNV1 over codepoints. `pvfs_round_alloc_size` rounds up to the configured allocation unit.

State and persistence behavior: Most helpers are stateless. `pvfs_copy_file` creates a persistent destination file and xattr-backed DOS metadata, deleting the destination on failure. Hash output feeds stream IDs and short-name mangling.

Dependencies and integration points: Used by rename copy, short-name hashing, stream IDs, metadata save/load, search/unlink/rename filters, and file size reporting. It depends on talloc, POSIX read/write, PVFS syscall wrappers, and xattr DOS attribute saves.

Risks: `pvfs_copy_file` does not copy alternate data streams or ACLs here; it copies DOS attributes only. The write loop retries on EINTR/EAGAIN but does not handle partial positive writes by continuing the remainder. Hash-based stream IDs can collide.

Test signals: Cover wildcard detection, attribute filters, normal attribute normalization for dirs/files, copy cleanup on read/write/chmod/xattr failure, readonly/system/hidden copy metadata, hash case folding, and allocation rounding boundaries.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_wait.c -->
# sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_wait.c

Purpose: `pvfs_wait.c` provides the asynchronous wait abstraction used when open, rename, unlink, or setpathinfo must pause for share-mode or oplock-break resolution. It bridges imessaging events, tevent timeouts, ntvfs async setup, and SMB cancel behavior.

Important APIs, types, and functions: Public functions are `pvfs_async_setup`, `pvfs_wait_message`, and `pvfs_cancel`. The local state type is `struct pvfs_wait`, holding list links, the PVFS state, handler, private data, message type, messaging/event contexts, request reference, and completion reason. Local helpers are `pvfs_wait_dispatch`, `pvfs_wait_timeout`, and `pvfs_wait_destructor`.

Control flow: `pvfs_wait_message` allocates a wait object, references the request, optionally registers a message callback for a message type, optionally installs a timeout timer, marks the request async, links the wait into `pvfs->wait_list`, and returns a talloc handle. Incoming messages are filtered by private-data pointer payload, set reason to `PVFS_WAIT_EVENT`, and invoke `ntvfs_async_setup` with a temporary request reference. Timeouts similarly set `PVFS_WAIT_TIMEOUT`. `pvfs_async_setup` then runs the caller-provided handler in the correct ntvfs chain context. `pvfs_cancel` scans waits for the request and triggers `PVFS_WAIT_CANCEL`.

State and persistence behavior: All state is transient. Waits are linked in memory and deregister messaging callbacks on talloc destruction. There is no durable storage.

Dependencies and integration points: It depends on tevent, imessaging/IRPC, ntvfs async state, dlinklist, and retry code in open/rename/unlink/setfileinfo. ODB retry setup owns higher-level pending open-db registration.

Risks: Message filtering uses pointer identity in payloads. Cancellation support depends on callers implementing cancel handling; several retry handlers still have TODO comments. Request lifetime relies on talloc references around async callbacks. Forgetting to free wait handles leaks async capacity and message registrations.

Test signals: Cover event completion, timeout completion, cancel completion, deregistration on free, pointer mismatch ignored, no-fd message validation, and integration with open/unlink/rename retry handlers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_wait.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_write.c -->
# sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_write.c

Purpose: `pvfs_write.c` implements SMB write handling for PVFS files and streams, including access checks, byte-range-lock checks, level-II oplock breaks, delayed write-time updates, and POSIX or stream writes.

Important APIs, types, and functions: The exported function is `pvfs_write`. Local helpers are `pvfs_write_time_update_handler` and `pvfs_trigger_write_time_update`. It uses `union smb_write`, `struct pvfs_file`, `struct pvfs_file_handle`, open-db locks, tevent timers, and either POSIX `pwrite` or `pvfs_stream_write`.

Control flow: Non-WRITEX levels are delegated to `ntvfs_map_write`. WRITEX finds the open handle, rejects directory handles, verifies write or append access, checks byte-range locks, breaks level-II oplocks, schedules a delayed open-db write-time update if not already triggered, then writes to the stream blob or POSIX fd. `EFBIG` maps to `NT_STATUS_INVALID_PARAMETER`; other errors use PVFS errno mapping. Successful writes update `seek_offset` and return the written byte count.

State and persistence behavior: Data is persisted through POSIX file contents or stream xattr/EADB blobs. Write-time state is persisted first in the open database by a delayed timer, then potentially to filesystem timestamps on close. The timer sets `update_triggered` and `update_on_close`, and the handler calls `odb_set_write_time` with the timer time.

Dependencies and integration points: It depends on open handle lookup, byte-range lock enforcement, oplock breaking, open-db write-time fields, stream storage, POSIX pwrite, and tevent.

Risks: Delayed write-time updates rely on timer delivery and close-path fallback. Stream writes load and rewrite blobs, so large writes are memory- and xattr-limit-sensitive. Append access is accepted but the code writes at the supplied offset, so append semantics depend on earlier generic mapping or clients.

Test signals: Cover write access denial, append-only handles, locked ranges, level-II oplock break failures, delayed write-time update and close fallback, stream writes including sparse extension, EFBIG mapping, and short writes/errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_write.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_xattr.c -->
# sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_xattr.c

Purpose: `pvfs_xattr.c` is the persistence layer for PVFS DOS metadata, EAs, streams, and NT ACLs. It abstracts system xattrs and the optional TDB-backed EADB, and serializes Samba xattr structures with NDR.

Important APIs, types, and functions: Public functions include `pvfs_xattr_unlink_hook`, `pvfs_xattr_ndr_load`, `pvfs_xattr_ndr_save`, `pvfs_dosattrib_load/save`, `pvfs_doseas_load/save`, `pvfs_streams_load/save`, `pvfs_acl_load/save`, `pvfs_xattr_create/delete/load/save`, and `pvfs_xattr_probe`. Internal helpers are `pull_xattr_blob`, `push_xattr_blob`, and `delete_xattr`.

Control flow: Blob operations dispatch to EADB helpers when `pvfs->ea_db` is configured, otherwise to system xattr helpers. Unsupported system xattrs clear `PVFS_FLAG_XATTR_ENABLE` and are treated as not found. NDR load/save wrappers pull or push blobs around generated xattr structures. DOS attribute load initializes stream existence, reads versioned `xattr_DosAttrib`, normalizes attributes, restores EA size/allocation/create/change fields, then refreshes stream info. Save writes version 1. EA, stream-index, and ACL load/save functions map missing xattrs to empty state where appropriate. ACL save temporarily gains root privileges for the system namespace. Probe attempts user and security namespace reads to disable unsupported xattrs early.

State and persistence behavior: This file is responsible for durable metadata outside normal POSIX stat data. It stores DOS attributes, DOS EAs, stream indexes, stream payload xattrs via generic helpers, and NT ACL descriptors either in filesystem xattrs or a TDB EADB. Unlink hooks remove backend metadata.

Dependencies and integration points: It depends on NDR-generated xattr types, posix_eadb backend functions, system xattr backend functions, root privilege helpers, allocation/attribute normalization, and is used by open, resolve, query/set info, streams, unlink, and ACL code.

Risks: Disabling xattrs after one unsupported error changes later metadata behavior for the share. Versioned DOS attribute parsing must remain backward-compatible. System ACL xattrs require privilege handling. EADB and system xattr backends must remain behaviorally equivalent. Missing stream indexes can orphan stream payload xattrs.

Test signals: Cover xattr unsupported fallback, EADB and system backends, DOS attribute version 1 and old version 2 loads, DOS EA empty/missing behavior, stream index persistence, ACL save/load with privileges, unlink cleanup, and probe behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_xattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/posix/python/pyposix_eadb.c -->
# sources/user-network-fs/samba/source4/ntvfs/posix/python/pyposix_eadb.c

Purpose: `pyposix_eadb.c` exposes a small Python module, `posix_eadb`, for manipulating PVFS TDB-backed extended attributes from Python tests or tooling.

Important APIs, types, and functions: The module exports `wrap_getxattr`, `wrap_setxattr`, and `is_xattr_supported`. Local functions are `py_is_xattr_supported`, `py_wrap_setxattr`, `py_wrap_getxattr`, and `MODULE_INIT_FUNC(posix_eadb)`. It uses `DATA_BLOB`, `struct tdb_wrap`, Python bytes parsing/building macros, `PyErr_SetNTSTATUS`, and `py_default_loadparm_context`.

Control flow: `is_xattr_supported` always returns true for this wrapper. `wrap_setxattr` parses TDB path, filename, attribute name, and bytes payload; opens or creates the TDB with loadparm-derived flags; calls `push_xattr_blob_tdb_raw`; maps open failures to `IOError` and NTSTATUS failures to Python exceptions; then returns `None`. `wrap_getxattr` parses TDB path, filename, and attribute name; opens or creates the TDB; calls `pull_xattr_blob_tdb_raw` with an estimated size; builds a Python bytes object from the returned blob; and frees the talloc context.

State and persistence behavior: Attribute data is persisted in the named TDB file using raw posix_eadb helpers. Each operation creates a temporary talloc context and opens the TDB independently. There is no module-global cache.

Dependencies and integration points: It depends on Samba Python compatibility headers, TDB wrap, NDR/data blob utilities, posix_eadb raw helpers, loadparm Python context, and Python NTSTATUS error helpers. It likely supports tests that need to inspect or seed the EADB backend without mounting through SMB.

Risks: The function docstrings omit the TDB-name argument even though parsing requires it. The module reports xattr support unconditionally because it targets EADB, not the host filesystem xattr API. The get wrapper uses a fixed estimated size of 100, relying on the backend to grow if needed.

Test signals: Cover set/get round trips with binary bytes, missing attribute errors, TDB open failure, NTSTATUS-to-Python exception mapping, repeated opens, and argument validation under Python 3 bytes handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/posix/python/pyposix_eadb.c -->
