# subset-b-009864 research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/filename.c -->
# sources/user-network-fs/samba/source3/smbd/filename.c

## Purpose
`filename.c` is smbd's high-level SMB pathname conversion layer. It converts client paths, create options, DFS/reparse flags, snapshot tokens, case rules, mangled names, streams, fake files, and symlink policy into canonical `smb_filename` objects plus directory `files_struct` path references. It is the bridge between protocol-facing path strings and the lower `files.c` pathref/openat machinery.

## Important APIs, Types, And Functions
`ucf_flags_from_smb_request()` and `filename_create_ucf_flags()` derive unified conversion flags from SMB request state, create disposition, create options, POSIX pathname mode, DFS pathname mode, reparse/GMT pathnames, and `FILE_OPEN_REPARSE_POINT`. `canonicalize_snapshot_path()` strips valid `@GMT-YYYY-MM-DD-HH-MM-SS` path tokens and preserves the resulting time-warp read point in `smb_fname->twrp`. `get_real_filename_at()` resolves on-disk capitalization by first trying `SMB_VFS_GET_REAL_FILENAME_AT()` and then falling back to `get_real_filename_full_scan_at()` for mangled or unsupported case-insensitive lookup paths. `get_original_lcomp()` returns the normalized last component used by rename/enumeration paths.

The core conversion APIs are `filename_convert_dirfsp_nosymlink()`, `filename_convert_dirfsp_rel()`, and `filename_convert_dirfsp()`. They split a client path into parent directory and last component, validate wildcards and dot components, normalize case when share settings require it, resolve named streams, open pathrefs with `openat_pathref_fsp_nosymlink()` and `openat_pathref_fsp_lcomp()`, and either return an existing pathref-backed `smb_filename` or a create-target `smb_filename` without a backing fsp. `full_path_from_dirfsp_at_basename()` and `full_path_from_dirfsp_atname()` reconstruct share-relative full names from dirfsp-relative names. Helper logic includes `filename_split_lcomp()`, `filename_convert_normalize_new()`, `get_real_stream_name()`, and `safe_symlink_target_path()`.

## Control Flow
Path conversion starts by translating request/create state into UCF flags. `filename_convert_dirfsp()` uses the connection cwd pathref and delegates to `filename_convert_dirfsp_rel()`, which repeatedly calls the no-symlink converter until it either succeeds, fails for a non-symlink reason, or safely follows an in-share symlink. The no-symlink path first special-cases fake files, rejects invalid `.` inputs, splits parent/last component, rejects streams on non-stream shares and wildcards for non-POSIX paths, opens the parent directory pathref, validates that it is a directory, then validates the last component only after the parent path is known.

For existing normal files, the last component is opened with `openat_pathref_fsp_lcomp()`; a copied full `smb_filename` receives the embedded pathref link using `move_smb_fname_fsp_link()`. For missing names, `filename_convert_normalize_new()` applies create-time case preservation and mangled-name reverse lookup, then returns a full target path without an fsp. For named streams, the code temporarily removes the stream name, opens the base fsp, opens the stream pathref, optionally retries with the real stream capitalization on case-insensitive shares, and carefully closes the base fsp if stream creation is needed.

Symlink handling is deliberately two-stage. `filename_convert_dirfsp_nosymlink()` reports `NT_STATUS_STOPPED_ON_SYMLINK` with `reparse_data_buffer` details and adjusted unparsed-path length. `filename_convert_dirfsp_rel()` then decides whether terminal symlinks are allowed by flags, whether an MSDFS link should return `NT_STATUS_PATH_NOT_COVERED`, whether share policy allows following symlinks, and whether the target canonicalizes back under `conn->connectpath`. It caps redirects at 40.

## State And Persistence
This file does not own persistent storage. It mutates transient `smb_filename` fields such as `base_name`, `stream_name`, `st`, `twrp`, flags, and embedded `fsp` links. It consumes connection/share state including `case_sensitive`, case preservation options, filesystem capabilities, connect path, cwd fsp, and `lp_*` configuration. It also relies on mangling caches through `mangle_lookup_name_from_8_3()` and name-to-8.3 comparisons, but does not own those caches.

## Dependencies And Integration Points
The file integrates with VFS directory enumeration and real-name lookup, fake-file handling, snapshot token parsing, mangling backends, pathref creation in `files.c`, stream enumeration via `vfs_fstreaminfo()`, symlink reparse helpers from `files.c`, DFS detection through `lp_host_msdfs()` and `lp_msdfs_root()`, and share parameters from loadparm. It returns NTSTATUS values that directly drive SMB create/open error mapping and DFS referral handling.

## Risks
Security-sensitive risks are symlink traversal containment, wide-link rejection, POSIX pathname semantics, DFS link recognition, and correct unparsed-path lengths for reparse responses. Case-insensitive lookup has correctness and performance risks when VFS lookup is unsupported and full directory scans are needed. Stream handling is leak-prone because base fsps and stream fsps are linked but may need to be freed separately on some `OBJECT_NAME_NOT_FOUND` paths. Create-time normalization can accidentally change client-requested names if case-preservation and mangled-name rules are not kept aligned with SMB compatibility expectations.

## Test Signals
Tests should cover SMB1/SMB2 UCF flag derivation, POSIX pathnames, `FILE_OPEN_REPARSE_POINT`, DFS pathname flags, `@GMT` tokens, invalid `.` and `..` components, wildcard rejection, fake-file paths, case-sensitive and case-insensitive lookup, VFS unsupported real-name fallback, mangled-name lookup and directory-scan fallback, veto-file interactions, stream open/create on stream and non-stream shares, terminal versus non-terminal symlink handling, in-share and out-of-share symlink targets, redirect loop limit, MSDFS symlink paths returning `PATH_NOT_COVERED`, and create-target capitalization.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/filename.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/files.c -->
# sources/user-network-fs/samba/source3/smbd/files.c

## Purpose
`files.c` owns smbd's `files_struct` lifecycle, pathref fsp creation, embedded `smb_filename` to fsp links, fd/pathref helpers, open-file lookup, close-all operations, and stream/base fsp relationships. It is the central in-memory open-file table for a server connection and the lower implementation used by `filename.c` to walk paths safely.

## Important APIs, Types, And Functions
`fsp_new()`, `file_new()`, `create_internal_fsp()`, `create_internal_dirfsp()`, and `open_internal_dirfsp()` allocate and initialize fsps, bind SMB-visible handles through `fsp_bind_smb()`, and add fsps to `sconn->files`. `fsp_set_gen_id()` provides internal-open generation ids outside the 32-bit real-handle range. `fsp_bind_smb()` creates an `smbXsrv_open`, connects it to the request/session/tcon, sets `fnum`, and installs the request chain fsp.

The pathref family includes `openat_pathref_fsp()`, `openat_pathref_fsp_rootdir()`, `open_stream_pathref_fsp()`, `openat_pathref_fsp_nosymlink()`, `openat_pathref_fsp_lcomp()`, `openat_pathref_fsp_dot()`, `synthetic_pathref()`, and `parent_pathref()`. These functions use `SMB_VFS_OPENAT()`, `fd_openat()`, `vfs_stat_fsp()`, `SMB_VFS_FSTATAT()`, O_PATH/O_SEARCH/O_NOFOLLOW semantics, optional `openat2` `RESOLVE_NO_SYMLINKS`, and case-insensitive retry through `smb_vfs_openat_ci()`.

Ownership helpers are `fsp_attach_smb_fname()`, `fsp_set_smb_fname()`, `smb_fname_fsp_unlink()`, `move_smb_fname_fsp_link()`, and `reference_smb_fname_fsp_link()`. They maintain `struct fsp_smb_fname_link`, ensure destructors clear dangling pointers, and determine whether freeing an `smb_filename` should close an embedded fsp. Lookup and close APIs include `files_forall()`, `file_find_fd()`, `file_find_dif()`, `file_find_di_first()`, `file_find_di_next()`, `file_find_one_fsp_from_lease_key()`, `file_find_subpath()`, `file_close_conn()`, `file_close_user()`, `file_fsp_get()`, and `file_fsp_smb2()`.

## Control Flow
Allocation begins with `fsp_new()`: allocate `files_struct`, create a separate fd handle, initialize lock mode and fd, link it at the head of `sconn->files`, increment file counters, and later bind it to SMB state if the open is not internal. Pathref open flows allocate an fsp, attach a full `smb_filename`, open relative to a directory fsp, stat the resulting object, set flags and file id, and link the newly opened fsp back into the caller's `smb_filename`. Destructors ensure freeing pathref-backed filenames closes and frees the embedded fsp unless the caller explicitly unlinks or references without close ownership.

`openat_pathref_fsp_nosymlink()` is the full path walker. It splits the path into components, rejects `.`/`..` and vetoed components, optionally tries a direct no-symlink open, then walks component by component with openat. It detects symlinks with O_PATH/O_NOFOLLOW behavior, reads reparse data, tracks unparsed path length, closes intermediate dirfsps, and returns either a linked final pathref or `NT_STATUS_STOPPED_ON_SYMLINK`. `openat_pathref_fsp_lcomp()` is the optimized last-component path that can fall back to `GETREALFILENAME_CACHE` and directory real-name lookup after ENOENT on case-insensitive shares.

Close control flow walks `sconn->files` with `files_forall()`. Alternate stream fsps and base fsps can reference each other, so `close_file_in_loop()` may need two passes: first breaks base/stream links and closes stream fsps, then closes the now-normal base fsps. `fsp_unbind_smb()` removes notify registrations, SMB open compatibility links, request chain refs, and SMB2 chained fsp refs before `fsp_free()` removes the object from lists and frees handle/lease/fsp-name links.

## State And Persistence
The file manages per-process/per-connection in-memory state only: `sconn->files`, `sconn->num_files`, `conn->num_files_open`, `sconn->fsp_fi_cache`, `files_max_open_fds`, fd handle refcounts, lease refcounts, `smbXsrv_open` compatibility pointers, notify state, and base/stream links. Durable-handle state is partly represented through `fsp->op->global->durable`, which is cleared on tree disconnect. Case-insensitive last-component lookup uses the global smbd memcache `GETREALFILENAME_CACHE`, keyed by parent file id plus uppercased requested name.

## Dependencies And Integration Points
`files.c` sits under SMB1 and SMB2 open paths, `filename.c`, VFS modules, share-mode and lease code, notify code, fd-handle code, SMBXSRV open tables, security/access checks, memcache, loadparm, and reparse helpers. It calls VFS operations such as `SMB_VFS_OPENAT`, `SMB_VFS_FSTAT`, `SMB_VFS_FSTATAT`, `SMB_VFS_READLINKAT`, `SMB_VFS_PARENT_PATHNAME`, and file-id derivation. It also uses protocol structures from `globals.h` for SMB2 request lookup and chained fsp compatibility.

## Risks
The highest risks are fd leaks or double closes around embedded pathref destructors, stream/base error paths, symlink stop handling, and intermediate dirfsp cleanup. Security risks include accidentally following symlinks while path-walking, requiring read permission instead of execute/search permission when O_PATH/O_SEARCH is unavailable, stale case-insensitive cache entries, veto-file bypasses, and returning an fsp across the wrong session/tcon in SMB2 handle lookup. The open-file singleton cache must be invalidated when list order changes or fsps are freed.

## Test Signals
Tests should exercise allocation failure cleanup, internal opens, SMB-bound opens, fsp name replacement, pathref destructor ownership, move/reference fsp links, root/dot pathrefs, multi-component path walking, no-symlink openat2 fallback, O_PATH unavailable behavior, symlink metadata/unparsed lengths, case-insensitive cache hit/miss/delete paths, vetoed components, named stream opens and missing stream creation, parent pathrefs, file lookup by fd/file-id/gen-id/lease key, subpath detection, durable close on tree disconnect, two-pass stream close, SMB2 persistent/volatile id validation, and max-open-files initialization.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/files.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/globals.c -->
# sources/user-network-fs/samba/source3/smbd/globals.c

## Purpose
`globals.c` defines smbd process-global variables declared in `globals.h` and provides small initialization/accessor helpers. It centralizes state shared by many smbd modules: mangling state, memcache, security context stacks, connection context stacks, global SMBXSRV client pointer, encryption contexts, VFS backend list, reload timestamps, and request GUID derivation.

## Important APIs, Types, And Functions
Global definitions include `mangle_fns`, `chartest`, `tdb_mangled_cache`, `mangle_prefix`, `common_flags2`, `sec_ctx_stack`, `conn_ctx_stack`, `smbd_memcache_ctx`, `global_smbXsrv_client`, and related flags/counters. `smbd_memcache()` lazily allocates a process-global memcache under the NULL talloc context sized by `lp_max_stat_cache_size()*1024`; allocation failure calls `smb_panic()`. `smbd_init_globals()` zeroes the security and connection context stacks at startup. `smbd_request_guid()` builds a deterministic GUID-like value from an SMB1 request mid, SMB2 compound index or SMB1 parameter pointer, a caller-supplied index, and connection channel id.

## Control Flow
Most state is initialized by static C initialization. Runtime initialization calls `smbd_init_globals()` to clear context stacks. Callers that need memcache use `smbd_memcache()`, which creates the cache on first use and then returns the same pointer. Request GUID creation is stateless other than reading fields from `smb_request` and `xconn`.

## State And Persistence
All state is process memory. The memcache is intentionally allocated under NULL rather than autofree to avoid fork-child exit side effects. Mangling cache pointers may refer to internal TDB/memcache structures initialized elsewhere. Security and connection stacks are fixed-size arrays tied to `MAX_SEC_CTX_DEPTH`. No on-disk persistence is implemented in this file.

## Dependencies And Integration Points
This file depends on loadparm for memcache sizing, the memcache library, messages/TDB headers, SMB request structures, and protocol constants. Its globals are consumed by name mangling, path lookup caches, authentication/security context switching, VFS backend registration, trans encryption, and SMBXSRV connection/client code.

## Risks
Global mutable state creates ordering and lifetime risks, especially with forked processes and NULL-context allocations. `smbd_memcache()` panics on allocation failure rather than returning an error, so callers assume availability. `smbd_request_guid()` is a correlation identifier built from request metadata rather than a random GUID; consumers must not treat it as cryptographically unique.

## Test Signals
Tests should verify lazy memcache allocation size and reuse, panic behavior under forced allocation failure if supported, `smbd_init_globals()` clearing stack state, and `smbd_request_guid()` stability across SMB1, SMB2 compound indices, different mids, and different channel ids.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/globals.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/globals.h -->
# sources/user-network-fs/samba/source3/smbd/globals.h

## Purpose
`globals.h` is the central declaration and protocol-state header for source3 smbd. It declares process globals, shared context structures, SMB1/SMB2 request/connection structures, server-connection state, macros for SMB2 compound iovec access, and prototypes for cross-module smbd entry points.

## Important APIs, Types, And Functions
Global declarations include mangling state, security/connection context stacks, SMB encryption contexts, VFS backend list, sparse buffer, parent context, global memcache, and global SMBXSRV client. `struct fsp_singleton_cache` caches a single file-id to fsp lookup. `struct sec_ctx` and `struct conn_ctx` represent pushed security and current-user/connection contexts.

The header declares many smbd APIs: info/query/set functions, notify cancellation, SMBXSRV connection/client/tcon lifecycle functions, SMB2 request processors, deferred-open helpers, send oplock/lease breaks, SMB2 fake SMB1 request construction, credit/size verification, and request completion/error wrappers. The macros `smbd_server_connection_terminate`, `smbd_server_disconnect_client`, `smbd_smb2_request_error`, and `smbd_smb2_request_done` preserve call-site location.

The main types are `struct smbXsrv_connection`, `struct smbd_smb2_send_queue`, `struct smbd_smb2_request`, `struct smbd_server_connection`, `struct file_modified_state`, and `struct aio_extra`. `struct smbXsrv_connection` stores transport, ack, SMB1 negotiation/session/signing state, SMB2 credits, dialect/capability negotiation, preauth hash, active requests, signing/encryption state, and multi-channel bookkeeping. `struct smbd_smb2_request` stores current compound index, signing/encryption state, async subrequest pointers, session/tcon refs, input/output vectors, fake SMB1 request compatibility, and chained fsp state. `struct smbd_server_connection` stores per-process connection lists, open files, notify context, search handles, oplock counts, deferred open queue, pthread pool, and client pointer.

## Control Flow
The header itself has no control flow, but it defines the state transitions expected by implementation files: an SMBXSRV client owns one or more connections, each connection has transport and SMB dialect substate, SMB2 requests move through parser/dispatcher/processor/completion functions, and server connections own the in-memory lists used by files, notify, searches, oplocks, and deferred opens. The SMB2 iovec macros assume `current_idx` selects the active compound element and map transform/header/body/dynamic slots in fixed increments.

## State And Persistence
All declared structures are in-memory runtime state. Some fields mirror persistent or cluster-visible SMBXSRV tables managed elsewhere, such as tcon and open globals. The tmpname macros define naming conventions for temporary names (`.::TMPNAME:` and directory prefix) but do not create persistence themselves.

## Dependencies And Integration Points
`globals.h` integrates most smbd subsystems: SMB1/SMB2 protocol handlers, SMBXSRV global tables, notify, file lifecycle, searches, oplocks, DCE/RPC server context, pthread pools, authentication/security tokens, loadparm-driven features, and profiling. Changes here have broad compile and behavioral impact because implementation files include it for core structures and prototypes.

## Risks
Layout changes can break many modules and assumptions in SMB2 compound processing, async completion, and SMB1 compatibility. The iovec macros are index-sensitive and can corrupt parsing or replies if vector layout changes. Global extern declarations require single-definition discipline in `globals.c` and sibling files. State fields such as `compat_chain_fsp`, transport termination flags, credits, and signing/encryption booleans are security-sensitive.

## Test Signals
Tests should cover SMB2 compound request vector indexing, request error/done wrappers preserving location metadata, transport termination/disconnect paths, SMB2 credit accounting, fake SMB1 request construction, chained fsp removal, tcon/session lookup paths, notify cancellation declarations linking correctly, tmpname prefix predicates, and build coverage for SMB1 enabled/disabled configurations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/globals.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/mangle.c -->
# sources/user-network-fs/samba/source3/smbd/mangle.c

## Purpose
`mangle.c` is the dispatch layer for Samba's DOS 8.3 name mangling subsystem. It selects a backend based on `mangling method`, exposes wrapper APIs used by directory/path code, and provides a POSIX-mode switch that disables mangling behavior.

## Important APIs, Types, And Functions
`mangle_backends[]` maps backend names to initialization functions: `hash`, `hash2`, and `posix`. `mangle_init()` lazily chooses the configured backend and terminates the server if no backend initializes. Public wrappers are `mangle_reset_cache()`, `mangle_change_to_posix()`, `mangle_is_mangled()`, `mangle_is_8_3()`, `mangle_is_8_3_wildcards()`, `mangle_must_mangle()`, `mangle_lookup_name_from_8_3()`, and `name_to_8_3()`.

## Control Flow
Most wrappers assume `mangle_fns` is initialized by startup or by a prior reset; `mangle_reset_cache()` explicitly calls `mangle_init()` before invoking the backend reset hook. `mangle_change_to_posix()` clears the current backend, sets the loadparm mangling method to `posix`, and reinitializes. `name_to_8_3()` returns a simple truncation when mangled names are disabled for the share; otherwise it delegates to the selected backend with share default-case settings.

## State And Persistence
The selected backend is the global function table `mangle_fns`. Backend caches live in `mangle_hash.c` or `mangle_hash2.c`; this file only selects and calls them. The POSIX switch mutates runtime configuration through `lp_set_mangling_method("posix")`.

## Dependencies And Integration Points
This file integrates with loadparm (`lp_mangling_method`, `lp_mangled_names`, `lp_default_case`), global mangling state in `globals.c`, and `struct mangle_fns` from `mangle.h`. `filename.c` and directory enumeration use these wrappers for mangled-name detection, reverse lookup, and 8.3 output generation.

## Risks
Several wrappers dereference `mangle_fns` without calling `mangle_init()`, so initialization ordering matters. Runtime switching to POSIX mangling affects all later name resolution in the process. Disabling mangled names truncates rather than hashes, which can create collisions or client-visible ambiguity.

## Test Signals
Tests should cover backend selection by parameter, default fallback, failure-to-initialize exit behavior, cache reset, POSIX switch, mangled-names disabled truncation, wildcard 8.3 checks, and wrapper behavior across `hash`, `hash2`, and `posix` backends.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/mangle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/mangle_hash.c -->
# sources/user-network-fs/samba/source3/smbd/mangle_hash.c

## Purpose
`mangle_hash.c` implements Samba's legacy hash-based 8.3 name mangling backend. It validates DOS 8.3 legality using UCS2 tables, detects legacy mangled patterns, generates short names using a magic character plus checksum-derived base characters, and stores reverse mappings in an internal TDB.

## Important APIs, Types, And Functions
The backend exports `mangle_hash_init()` and a `struct mangle_fns` with reset, detect, must-mangle, 8.3 validation, reverse lookup, and forward conversion hooks. Core validation functions are `isvalid83_w()`, `has_valid_83_chars()`, `has_illegal_chars()`, `mangle_get_prefix()`, `is_valid_name()`, `is_8_3_w()`, and `is_8_3()`. Detection uses `init_chartest()` and `is_mangled()` to find the configured magic character followed by two valid basechars at component boundaries. Reverse mapping uses `cache_mangled_name()` and `lookup_name_from_8_3()` against `tdb_mangled_cache`. Forward mapping is `to_8_3()` and `hash_name_to_8_3()`. `fast_string_hash()` customizes the internal TDB hash.

## Control Flow
Initialization creates the `chartest` basechar table if needed, opens an internal TDB named `mangled_cache`, and returns the backend function table. `hash_name_to_8_3()` converts input to UCS2, returns it unchanged if it is already legal 8.3, otherwise calls `to_8_3()`, which computes a checksum, uppercases the string, extracts up to five basechars for the prefix, appends the magic character and two checksum chars, and preserves up to three extension chars. The generated mapping is cached for reverse lookup. Reverse lookup first tries the full mangled name, then tries without extension and reattaches the requested extension when a prefix mapping is found.

## State And Persistence
State is in process memory: global `chartest`, global `tdb_mangled_cache`, and the configured magic/default-case values read at call time. The TDB is opened with `TDB_INTERNAL`, so it is not a durable database. The backend reset hook is effectively a no-op and does not clear or reopen the TDB.

## Dependencies And Integration Points
The backend depends on Unicode conversion helpers (`push_ucs2_talloc`, UCS2 string functions), string case helpers, TDB utility functions, loadparm share settings, and global mangling variables. It is selected by `mangle.c` and used by path lookup when clients provide or request DOS 8.3 names.

## Risks
The legacy algorithm has a small checksum space and can collide. `cache_mangled_name()` temporarily modifies the raw-name extension through a discarded const pointer, which is carefully restored but fragile. Reverse lookup depends on cache warmness and can fail, forcing directory scans elsewhere. Validation is UCS2-table based and must match Windows compatibility expectations for reserved names, trailing dots/spaces, wildcards, and illegal characters.

## Test Signals
Tests should cover legal and illegal 8.3 names, reserved DOS device names, trailing dot/space rejection, wildcard allowance toggles, multibyte conversion failures, magic-pattern detection across path components, extension-group reverse cache behavior, checksum collisions, cache disabled/uninitialized lookup, `cache83` false behavior, default upper/lower case behavior, and internal TDB initialization failure paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/mangle_hash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/mangle_hash2.c -->
# sources/user-network-fs/samba/source3/smbd/mangle_hash2.c

## Purpose
`mangle_hash2.c` implements the newer hash2 name mangling backend. It produces names of the form `Annnn~n.AAA` using a base-36 FNV1-derived hash, fast ASCII character tables, DOS reserved-name detection, and the global smbd memcache for reverse prefix lookup. It also contains the no-op POSIX mangling backend.

## Important APIs, Types, And Functions
The backend exports `mangle_hash2_init()` and `posix_mangle_init()`. Important constants and tables are `basechars`, `reserved_names`, `char_flags`, `base_reverse`, `FNV1_PRIME`, and `FNV1_INIT`. Hashing and cache helpers are `mangle_hash()`, `cache_insert()`, and `cache_lookup()`. Detection and validation are handled by `is_mangled_component()`, `is_mangled()`, `is_8_3()`, `is_reserved_name()`, `is_legal_name()`, and `must_mangle()`. Forward conversion is `hash2_name_to_8_3()`, and reverse lookup is `lookup_name_from_8_3()`. The POSIX backend functions always report no mangling and return an empty 8.3 output buffer.

## Control Flow
`mangle_hash2_init()` clamps `mangle_prefix` from loadparm into the range 1..6, optionally initializes generated tables when dynamic mode is enabled, resets the backend, and returns the function table. `hash2_name_to_8_3()` first returns legal non-reserved 8.3 names unchanged. Otherwise it chooses an extension only when the suffix is 1..3 ASCII chars, derives leading uppercase ASCII prefix characters, hashes the prefix before the dot, emits base36 hash characters around `~`, appends an uppercased extension, and optionally stores the prefix in `MANGLE_HASH2_CACHE`. Reverse lookup validates that the name matches hash2 shape, decodes the base36 hash, reads the cached prefix from memcache, and appends any extension from the short name.

## State And Persistence
State is process-local. `mangle_prefix` is global and configured at backend initialization. Reverse lookup data is stored in `smbd_memcache()` under `MANGLE_HASH2_CACHE`, keyed by the 31-bit hash value and containing a NUL-terminated prefix. Static character tables are compiled in unless `DYNAMIC_MANGLE_TABLES` is enabled for regeneration. The POSIX backend keeps no state.

## Dependencies And Integration Points
This file depends on global memcache from `globals.c`, loadparm for `mangle prefix`, Samba string/case helpers, and the `mangle_fns` abstraction. `filename.c` relies on the reverse cache to avoid full directory scans for incoming mangled names. Directory listing code uses `name_to_8_3()` via the wrapper layer.

## Risks
Reverse lookup is cache-dependent and hash-only, so collisions can map to the most recently cached prefix. The code intentionally uses byte string operations for performance and must preserve the documented multibyte assumptions. Changes to flag tables require regeneration. Extension parsing is ASCII-only by design. `mangle_prefix` affects the hash space and collision behavior; larger visible prefixes weaken the hash.

## Test Signals
Tests should cover prefix clamping, legal-name pass-through, DOS reserved-name mangling, illegal chars, forced shortname chars, wildcard handling, multibyte names, extension selection rules, cache insertion disabled/enabled, reverse lookup success/miss/collision, exact hash2 pattern detection, path-component detection, table regeneration equivalence, and POSIX backend no-op behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/mangle_hash2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/msdfs.c -->
# sources/user-network-fs/samba/source3/smbd/msdfs.c

## Purpose
`msdfs.c` implements source3 smbd support for Microsoft DFS referrals. It parses DFS paths, builds temporary VFS connections for referral lookup, parses and emits Samba's `msdfs:` symlink format, detects MSDFS links, resolves a DFS path to referral targets, and serializes referral replies for TRANS2/FSCTL callers.

## Important APIs, Types, And Functions
`parse_dfs_path_strict()` parses `\\server\\share` and `\\server\\share\\remaining` paths, verifies the hostname belongs to this server, and returns hostname/share/remaining components. `create_conn_struct_chdir()` wraps `create_conn_struct_as_root()` and returns a `conn_wrap` whose destructor disconnects VFS state and resets cwd/chdir cache. `parse_msdfs_symlink()` parses `msdfs:server\\share,...` or slash variants into `struct referral` arrays and optional shuffled order. `is_msdfs_link()` asks the VFS to read DFS path data at a dirfsp-relative name. `get_referred_path()` is the main referral resolver. `setup_dfs_referral()` invokes VFS referral generation and NDR-marshals the response. `msdfs_link_string()` formats referrals back into a storable `msdfs:` string.

## Control Flow
Strict parsing copies the path, requires an initial backslash, splits hostname and share on backslashes, checks `is_myname_or_ipaddr()`, and leaves remaining path syntax validation to the caller. Referral lookup starts in `get_referred_path()`: parse the DFS path, reject invalid syntax, normalize the service name, verify the share is a DFS root or proxy, and handle self-referral or proxy-target referral without opening the share path. For non-root paths, it creates a temporary connection to the share as the caller session, copies remote/local addresses if missing, and calls `dfs_path_lookup()`.

`dfs_path_lookup()` converts the requested path with `filename_convert_dirfsp()`. When conversion returns `NT_STATUS_PATH_NOT_COVERED`, it strips one component and retries until a covered parent is found. It then resolves the real last component name under the parent, asks `SMB_VFS_READ_DFS_PATHAT()` for referrals, and computes how many bytes of the canonical DFS path were consumed by removing the still-unconsumed path components from the original DFS path.

## State And Persistence
This file creates transient `connection_struct` and `smbd_server_connection` objects for referral lookup. `parse_msdfs_symlink()` and `msdfs_link_string()` operate on in-memory referral structures but encode/decode the persistent Samba MSDFS symlink payload format. The temporary connection destructor calls `SMB_VFS_DISCONNECT()`, frees the connection, `chdir("/")`, and resets the chdir cache to make unmounts possible.

## Dependencies And Integration Points
`msdfs.c` depends on loadparm share settings (`msdfs root`, `msdfs proxy`, shuffle referrals, share paths), authentication/session info, VFS connect/read-dfs hooks, global messaging context, DFS NDR blobs, `filename.c` path conversion, `get_real_filename_at()` for case-correct link names, and `conn_new`/VFS initialization. It integrates with trans2/FSCTL referral reply generation through `SMB_VFS_GET_DFS_REFERRALS()` and `ndr_push_dfs_referral_resp`.

## Risks
Security-sensitive areas include hostname validation, share access checks during fake connection creation, root privilege boundaries around VFS connect, cwd changes in a server process, DFS proxy target parsing, and path-consumed length calculation. Referral resolution depends on path conversion returning `PATH_NOT_COVERED` only for DFS links; other errors abort. Component stripping has mismatch and integer-wrap checks, but malformed paths and path separator normalization remain high-value tests.

## Test Signals
Tests should cover strict DFS parsing, nonlocal host rejection, missing share rejection, invalid remaining path syntax, service alias resolution, non-DFS share rejection, DFS root self-referral, DFS proxy referral, shuffled referral order, slash and backslash symlink target canonicalization, max referral count, empty referral entries, temporary connection access denied/read-only paths, `PATH_NOT_COVERED` walkback through nested paths, consumed-count calculation, GMT token handling inside lookup, VFS read failures, NDR marshal failures, and `msdfs_link_string()` formatting/trimming.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/msdfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/notify.c -->
# sources/user-network-fs/samba/source3/smbd/notify.c

## Purpose
`notify.c` implements SMB change-notify request tracking and delivery inside smbd. It stores per-fsp notify subscriptions, queues filesystem change events, marshals `FILE_NOTIFY_INFORMATION` replies, cancels pending requests by MID/fid/request, reregisters watches after notifyd restarts, enforces optional ChangeNotify privilege visibility rules, and triggers backend notifications for changed filenames.

## Important APIs, Types, And Functions
Key local types are `notify_change_event`, `notify_change_buf`, `notify_change_request`, and `notify_mid_map`. Public APIs include `change_notify_fsp_has_changes()`, `change_notify_reply()`, `notify_callback()`, `change_notify_create()`, `change_notify_add_request()`, `remove_pending_change_notify_requests_by_mid()`, `smbd_notify_cancel_by_smbreq()`, `smbd_notify_cancel_deleted()`, `smbd_notifyd_restarted()`, `remove_pending_change_notify_requests_by_fid()`, `notify_fname()`, `notify_filter_string()`, and `sys_notify_context_create()`.

Internal helpers include `notify_marshall_changes()` for sorted/coalesced NDR encoding, `change_notify_remove_request()` for unlinking both fsp request and MID map lists, `smbd_notify_cancel_by_map()` for choosing cancellation status in SMB2 cleanup cases, `user_can_stat_name_under_fsp()` for access-filtering notification visibility, and `notify_fsp()` for queueing and replying to a notified fsp.

## Control Flow
`change_notify_create()` validates list access on the directory fsp, allocates `fsp->notify`, stores filters and maximum response size, computes the full path, and registers with notifyd when filters are nonzero. `change_notify_add_request()` moves the incoming SMB request under a new notify request object, appends it to the fsp queue, and adds a MID lookup map to `sconn->notify_mid_maps`.

Backend events enter via `notify_callback()`, which finds the target fsp in `sconn->files` and calls `notify_fsp()`. `notify_fsp()` optionally enforces ChangeNotify privilege semantics, rejects hidden events, caps queued events at 1000 or converts backend drop indications (`name == NULL`) into catch-all state, stores the event with slash-to-backslash conversion, holds `OLD_NAME` rename halves until the paired event arrives, and replies to the first waiting request when deliverable. `change_notify_reply()` clamps to the server buffer limit, marshals sorted and coalesced changes, sends an empty response if the client buffer is too small or catch-all state is present, then clears queued changes.

Cancellation flows locate a MID map or request pointer, compute `CANCELLED` versus `NOTIFY_CLEANUP` for SMB2 session/tcon cleanup, send a completion, and remove request/map state. Delete notifications and notifyd restarts are delivered through messaging callbacks that walk all fsps.

## State And Persistence
State is per-process memory: `fsp->notify` buffers, queued changes, pending request lists, and `sconn->notify_mid_maps`. Notify registrations live in `sconn->notify_ctx` and are recreated after notifyd restarts. No persistent storage is owned by this file. Event names are talloc-owned under the changes array, and the request object owns the moved `smb_request`.

## Dependencies And Integration Points
This file integrates with notifyd through `notify_add()`, `notify_init()`, `notify_trigger()`, and callback private data; with file lifecycle through `fsp_unbind_smb()` and `files_forall()`; with SMB1/SMB2 request reply functions supplied by callers; with SMB2 session/tcon cleanup state from `globals.h`; with directory lease break handling through `contend_dirleases()`; and with security/access checks through privilege tests, user switching, `synthetic_pathref()`, and `smbd_check_access_rights_fsp()`.

## Risks
Risks include request leaks in cancellation paths, missed removal from either the fsp list or MID map list, incorrect SMB2 cleanup status, event disclosure without adequate traverse/list rights, queue growth or catch-all behavior under event storms, rename old/new event pairing, buffer-size truncation semantics, and stale registrations after notifyd restart. `notify_fsp()` currently replies only to the first waiting request, so multi-request behavior must match SMB semantics.

## Test Signals
Tests should cover access denied on notify creation, duplicate notify create rejection, zero filters, recursive versus nonrecursive filters, request queue ordering, MID cancellation, SMB2 session/tcon cleanup cancellation status, delete-pending cancellation by file id, notifyd restart reregistration, marshalling order and duplicate coalescing, max buffer too small, catch-all state, more than 1000 queued events, rename old/new pairing, slash conversion, ChangeNotify privilege enabled/disabled, traverse/list failures hiding events, dirlease break actions, filter string formatting, and sys notify context allocation failure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/notify.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/notify_fam.c -->
# sources/user-network-fs/samba/source3/smbd/notify_fam.c

## Purpose
`notify_fam.c` provides optional FAM/Gamin-backed system notification integration for smbd. It opens a single process-wide FAM connection, registers directory monitors for a subset of Windows notify filters, converts FAM events into Samba `notify_event` actions, and falls back silently to other notify mechanisms when FAM is unavailable.

## Important APIs, Types, And Functions
`struct fam_watch_context` stores a FAM request, the Samba sys notify context, callback, private data, filter mask, and watched path. Static state includes the singleton `FAMConnection fam_connection`, `fam_connection_initialized`, and `fam_notify_list`. `fam_open_connection()` opens FAM with a process-name string, optionally sets Gamin-specific client options, registers the FAM fd with tevent, and returns NTSTATUS. `fam_reopen()` closes and reopens the singleton connection and reissues monitors. `fam_handler()` drains FAM events and dispatches supported event codes. `fam_watch_context_destructor()` cancels a monitor and removes it from the list. The exported `fam_watch()` installs a watch and returns a talloc handle.

## Control Flow
`fam_watch()` first intersects the requested filter with the FAM-supported mask of file and directory name changes. If none are requested, it returns success with no handle and leaves the filters for other backends. On first use it opens the singleton connection; failure also returns success so smbd can rely on non-FAM notification. A watch object is allocated, path/callback/filter fields are set, handled filter bits are removed from `*filter`, the watch is linked into `fam_notify_list`, and `FAMMonitorDirectory()` is called if the connection fd is valid. If not, `fam_reopen()` attempts to restore all watches.

When tevent signals readability, `fam_handler()` calls `FAMPending()` and `FAMNextEvent()`. A read error frees the fd event and reopens the connection. Supported codes map `FAMChanged` to modified, `FAMCreated` to added, and `FAMDeleted` to removed; other FAM events are ignored. It finds the matching watch by comparing `FAMRequest`, derives the relative path from the event filename, and calls the stored Samba callback with `UINT32_MAX` as the filter.

## State And Persistence
All state is in memory. The FAM connection is singleton per smbd process. Watch lifetimes are controlled by talloc handles returned to callers. The destructor cancels monitor state in FAM when the connection fd is valid and removes the watch from the global list. No events or watches are persisted across process restart.

## Dependencies And Integration Points
This file depends on FAM/Gamin headers and library behavior, tevent fd registration, Samba notify action constants, talloc lifetime management, and the generic sys notify callback signature from smbd. It only handles file/directory name filters and deliberately leaves other filters to notifyd or polling mechanisms by clearing only its supported bits.

## Risks
FAM implementations differ, so the code avoids non-SGI extensions except guarded Gamin calls. Connection reopen must not lose live watch registrations. The global singleton means errors affect all watches. Event path parsing only looks for backslash separators before falling back to the full filename. Returning success when FAM is unavailable is intentional but can hide lack of kernel/system notification coverage if no other backend handles the remaining filters.

## Test Signals
Tests should cover ignored filters, first-open failure fallback, successful watch registration clearing only name-change bits, destructor cancellation/list removal, FAM changed/created/deleted mappings, ignored event codes, unknown request discard, event fd read error and reopen, re-monitoring all watches after reopen, Gamin `FAMNoExists` guarded behavior, and multiple watches sharing the singleton connection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/notify_fam.c -->
