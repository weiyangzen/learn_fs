# subset-b-009104 grouped research

This grouped report covers the exact source files assigned to work item `subset-b-009104`. Each section preserves the source path in its title and is wrapped with the reconciliation markers required for splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/legacy/remote.py -->
# sources/sync-backup/borg/src/borg/legacy/remote.py

Purpose: this module implements Borg's legacy SSH remote repository protocol. In Borg 2, current repositories are served through `rest://`, while this path keeps Borg 1.x / legacy repository access working through a `borg serve` subprocess and a msgpack RPC stream.

Important APIs and types: `LegacyRemoteRepository` is the client-side proxy. Its `@api`-decorated methods (`open`, `info`, `check`, `commit`, `rollback`, `destroy`, `list`, `put`, `delete`, `save_key`, `load_key`, `break_lock`, `get_manifest`, `put_manifest`) are stubs whose decorator turns local calls into RPC requests after checking server version constraints. `RepositoryServer` is the server-side dispatcher used by `borg serve`; it owns the allowlist in `_legacy_rpc_methods`, path restriction checks, repository lifecycle, and log forwarding. `SleepingBandwidthLimiter` rate-limits writes to the subprocess stdin. Exception classes such as `ConnectionClosed`, `UnexpectedRPCDataFormatFromServer`, `InvalidRPCMethod`, and `LegacyRemoteRepository.RPCServerOutdated` normalize transport and compatibility failures.

Control flow: client construction builds a local borg command or SSH command, starts it with `Popen`, makes stdin/stdout/stderr nonblocking, negotiates protocol version, opens the remote repository with `v1_legacy=True`, then reads repository info. Calls go through `call_many`, which batches msgpack request dictionaries with message IDs, sends up to `MAX_INFLIGHT`, multiplexes stdout/stderr with `select`, routes normal responses, remote log records, async responses, and reconstructed exceptions. The server `serve` loop reads msgpack requests from stdin, validates `method in self.rpc_methods`, filters unknown kwargs against the target signature for compatibility, invokes either a server method or repository method, and writes either `{i, r}` or structured exception data.

State and persistence: the module does not persist repository data itself; it maintains transport state (`msgid`, byte counters, response maps, async response maps, buffered outgoing bytes, shutdown deadline, partial stderr line buffer). `RepositoryServer.open` creates a `LegacyRepository` with `send_log_cb` so long-running repository operations can flush queued log records through the RPC stream. `close` flushes logging before returning.

Dependencies and integration points: it integrates with `borg.legacy.repository.LegacyRepository`, modern `Repository` only for exception typing, `borg.logger.borg_serve_log_queue`, `helpers.msgpack`, limited unpackers, `fslocking` exceptions, `Location`, version parsing, and platform flags. The path restriction code enforces `--restrict-to-path` and `--restrict-to-repository` on resolved real paths.

Risks: protocol compatibility is fragile because parameters are name-based and older servers silently ignore unknown kwargs unless the `@api` restriction blocks the call. `call_many` contains complex async bookkeeping; missed `async_response()` calls can defer exceptions from `wait=False` operations. Transport failure handling depends on nonblocking IO and subprocess behavior; stderr output is only logged. The client-side code appears to feed received stdout data to the unpacker twice, which is a high-risk area to test or inspect if failures appear.

Test signals: tests should cover version negotiation, API restriction failures, remote exception reconstruction, async put/delete error collection, path restriction denial, stderr logging, and clean close flushing server logs. The `inject_exception` helper exists specifically to exercise remote exception marshalling.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/legacy/remote.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/legacy/repoobj.py -->
# sources/sync-backup/borg/src/borg/legacy/repoobj.py

Purpose: this module contains `RepoObj1`, the Borg 1.x repository object codec retained for reading and transferring legacy data. It is intentionally simpler than the Borg 2 object envelope and treats the stored blob as encrypted compressed payload with no separate object header.

Important APIs and types: `RepoObj1.extract_crypted_data(data)` returns the input unchanged for crypto type detection. `RepoObj1.id_hash(data)` delegates to the key. `format(...)` compresses plaintext with a legacy-mode compressor unless caller provides already compressed data, encrypts with `key.encrypt(id, data_compressed)`, and returns only encrypted data. `parse_meta` is unsupported and raises `NotImplementedError`; legacy objects require full decryption to inspect metadata. `parse(...)` decrypts, detects compression from the first two bytes, builds `meta_compressed` with `ctype`, `clevel`, and `csize`, optionally decompresses, and verifies chunk identity through `key.assert_id` unless the `authenticated_no_key` workaround is active.

Control flow: write flow asserts the metadata dict is empty, selects legacy lz4 by default, compresses or accepts precompressed bytes, encrypts, and returns encrypted bytes. Read flow decrypts first, detects the compressor from the compressed prefix, optionally decompresses, and returns either plaintext metadata/data or compressed metadata/data depending on `want_compressed`.

State and persistence: instances keep only `key` and the default legacy compressor. Persistent state is the encrypted legacy object bytes stored by a repository; no header, type field, or embedded metadata envelope exists in this format.

Dependencies and integration points: it depends on Borg constants for repository object types, `workarounds`, and `compress.Compressor` / `get_compressor`. It is imported by modern `borg.repoobj` for backward compatibility and is used by transfer/upgrade paths that parse Borg 1 chunks before reformatting them.

Risks: no `parse_meta` means callers cannot do cheap metadata-only reads. Assertions encode important preconditions, so optimized Python would remove some checks. The `AUTHENTICATED_NO_KEY` workaround intentionally disables ID verification and should remain narrowly scoped. `format` accepts `ro_type` but does not store it, so object type validation must happen at a higher level for legacy data.

Test signals: tests should validate legacy lz4 and legacy zlib compressed round trips, `want_compressed` combinations, ID mismatch behavior with and without the workaround, and rejection of invalid parameter combinations.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/legacy/repoobj.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/legacy/repository.py -->
# sources/sync-backup/borg/src/borg/legacy/repository.py

Purpose: this module implements the legacy filesystem-backed transactional key-value repository. It stores objects in append-only segment files under `data/`, records PUT/DELETE/COMMIT entries, maintains committed `index.N`, `hints.N`, and `integrity.N` side files, and supports repair, rollback, compaction, and Borg 1.x compatibility.

Important APIs and types: `LegacyRepository` is the high-level repository. It exposes lifecycle (`create`, `open`, `close`, `destroy`, context manager), config/key storage (`save_config`, `save_key`, `load_key`), transaction and repair (`get_transaction_id`, `check_transaction`, `prepare_txn`, `write_index`, `commit`, `rollback`, `check`, `compact_segments`, `replay_segments`), object access (`list`, `get`, `get_many`, `put`, `delete`, `get_manifest`, `put_manifest`), and lock helpers. Nested error classes provide Borg exit codes. `LoggedIO` owns segment file layout and low-level read/write operations. Constants define segment magic and entry tags (`TAG_PUT`, `TAG_DELETE`, `TAG_COMMIT`).

Control flow: opening validates the repository config, version, ID, lock, and constructs `LoggedIO`. Reads load or rebuild the committed index as needed, then fetch by `(segment, offset)`. Writes call `prepare_txn`, possibly upgrade to an exclusive lock, load index and hints, clean uncommitted segments, then append PUT/DELETE entries and update in-memory `index`, `segments`, `compact`, and `shadow_index`. `commit` checks free space, writes a COMMIT tag, optionally compacts sparse segments, writes integrity-protected hints/index/integrity files in a careful rename order, and rolls back in-memory transaction state.

State and persistence: persistent layout is `README`, `config`, `data/<segment-dir>/<segment>`, `index.N`, `hints.N`, and `integrity.N`. `index` maps object IDs to segment offsets. `hints` persists segment reference counts, compactable byte counts, and `shadow_index`. `integrity.N` stores integrity metadata for hints and index. `LoggedIO` writes segment entries with CRC32 checksums and uses `SyncFile` plus directory fsyncs to improve durability. Transaction state is committed only through a final COMMIT tag and later side-file write.

Dependencies and integration points: it uses legacy hash indexes (`NSIndex1`), platform durability helpers (`SaveFile`, `SyncFile`, `sync_dir`, `safe_fadvise`), `fslocking.Lock`, `IntegrityCheckedFile`, msgpack, progress indicators, and `Manifest.MANIFEST_ID`. It is opened directly for local legacy repositories and by `legacy.remote.RepositoryServer` for SSH serving.

Risks: compaction and crash recovery are the highest-risk areas. The `shadow_index` is essential to avoid resurrecting deleted objects when only some sparse segments are compacted. Free-space checks are conservative but still depend on filesystem behavior. Partial checks persist `last_segment_checked` in config; interrupted or concurrent operations around this state need care. CRC32 protects segment integrity but is not cryptographic. Many correctness checks are in assertions and internal invariants.

Test signals: good coverage includes create/open/config validation, transaction replay after missing side files, commit crash windows, corrupted segment recovery, compaction with superseded PUTs and DELETEs, ENOSPC rollback cleanup, partial and full `check`, index mismatch reporting, `get_manifest` mapping to `NoManifestError`, and remote-mode calls to `_send_log`.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/legacy/repository.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/legacy/upgrade.py -->
# sources/sync-backup/borg/src/borg/legacy/upgrade.py

Purpose: this module upgrades Borg 1.2-era archive items, compressed chunk metadata, and archive metadata into Borg 2.0-compatible structures during transfer or migration.

Important APIs and types: `UpgraderFrom12To20` owns upgrade context. `new_archive(archive=...)` resets per-archive hardlink tracking. `upgrade_item(item=...)` converts legacy item fields, handles hardlink masters/slaves, rewrites symlink `source` to `target`, drops obsolete or invalid fields, computes size, and enforces `REQUIRED_ITEM_KEYS`. `upgrade_compressed_chunk(meta, data)` converts legacy compressed payload format to Borg 2 metadata and data conventions, including `ObfuscateSize` handling and zlib legacy detection. `upgrade_archive_metadata(metadata=...)` preserves supported metadata, normalizes chunker params, appends UTC offsets to legacy timestamps, converts argv lists to command-line strings, and initializes tags.

Control flow: item upgrade first handles hardlink semantics through `HardLinkManager`, then builds a whitelist-only dict and returns a fresh `Item`. Chunk upgrade inspects the leading compression type, strips or translates legacy type/level prefixes, handles older obfuscation size header byte order, and updates `ctype`, `clevel`, `csize`, and optional `psize`. Metadata upgrade is mostly field-by-field conversion with special cases for rechunking and old buzhash chunker parameter tuples.

State and persistence: the upgrader itself persists no files. It mutates/translates in-memory `Item` and metadata structures that are later written by archive transfer code. It calls `cache.reuse_chunk` for hardlink slave chunks so archive stats/cache accounting stays consistent.

Dependencies and integration points: it depends on item constants, compression classes (`ZLIB`, `ZLIB_legacy`, `ObfuscateSize`), hardlink helper predicates, `HardLinkManager`, `Item`, and command-line joining helpers. It is part of the legacy transfer path that reads with `RepoObj1` and writes with modern repository/object code.

Risks: hardlink ordering matters; a slave before its master can only work if `HardLinkManager` has the needed entry. The whitelist can drop fields that older Borg wrote but newer code might still need if compatibility assumptions change. Compression conversion has byte-level assumptions about legacy prefixes and obfuscation headers. The unknown compression level marker `0xFF` must be accepted downstream.

Test signals: tests should cover master/slave hardlinks with and without content, symlink source-to-target conversion, dropping `None` user/group fields, legacy zlib and prefixed compression conversion, `ObfuscateSize` with padding, rechunked and non-rechunked archive metadata, timestamp UTC suffixing, and command-line field conversion.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/legacy/upgrade.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/logger.py -->
# sources/sync-backup/borg/src/borg/logger.py

Purpose: this module centralizes Borg logging setup for local CLI runs, remote `borg serve` runs, progress output, JSON logs, warnings redirection, and lazy module loggers.

Important APIs and types: `setup_logging(...)` installs either a user-provided logging config or Borg's fallback root/progress handlers. `create_logger(name=None)` returns `LazyLogger`, which delays resolving the real `logging.Logger` until after setup. `BorgQueueHandler` serializes log records into dictionaries for remote transfer. `StderrHandler` always writes to the current `sys.stderr`. `TextProgressFormatter` and `JSONProgressFormatter` format progress logger records, which are always emitted as JSON internally. `JsonFormatter` formats normal logs as Borg JSON log messages. `flush_logging()` flushes root and progress handlers.

Control flow: module-level `configured` starts false, so imported modules may create `LazyLogger`s but cannot emit logs until `setup_logging`. Setup optionally reads `BORG_LOGGING_CONF`; on failure it falls back to a stream handler or queue handler, sets root level, optionally adds debugging file handlers, configures `borg.output.progress` separately, redirects Python warnings through `_log_warning`, and marks logging configured. `LazyLogger` methods proxy standard logging calls and move Borg's `msgid` kwarg into `extra`.

State and persistence: global state is `configured`, optional `logging_debugging_path`, and `borg_serve_log_queue`. Normal fallback logging is process-global. Debug file handlers persist logs under `logging_debugging_path` when enabled. Remote serve logging persists only as queued records until the server sends them over RPC.

Dependencies and integration points: all Borg modules use `create_logger`. `legacy.remote.RepositoryServer` drains `borg_serve_log_queue` and sends record dictionaries to clients. Progress helpers log to `borg.output.progress`. The module also suppresses noisy urllib/OpenBSD LibreSSL warnings.

Risks: calling a lazy logger before setup raises an exception, so import-time logging is unsafe. Logging is global and must be reset carefully in tests. Queue handler records must stay compatible with `logging.LogRecord(**dict)` reconstruction on the client. Progress formatters assume `record.msg` is valid JSON with a `message` key. Fallback from invalid logging config logs only after fallback setup.

Test signals: tests should cover early logger-use failure, fallback setup with text and JSON modes, custom config failure warning, warnings redirection, progress logger formatting, serve-mode queue contents, `flush_logging`, and `msgid` propagation through `LazyLogger`.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/logger.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/manifest.py -->
# sources/sync-backup/borg/src/borg/manifest.py

Purpose: this module manages repository manifests and archive listings across modern Borg 2 repositories and legacy repositories. It defines the compatibility feature checks used when loading a manifest and abstracts archive listing/deletion behind a common interface.

Important APIs and types: `Manifest` owns manifest serialization, `MANIFEST_ID`, supported feature flags, and operation-scoped compatibility checks. `Manifest.load(...)` fetches and decrypts the manifest, instantiates a key if needed, chooses legacy or modern archive interface, populates config/timestamp/item keys, and validates mandatory features. `Manifest.write()` updates a monotonic timestamp and stores a new manifest object. `ArchivesInterface` documents the archive API. `Archives` implements modern archive directory behavior using borgstore entries under `archives/<hex-id>`. `ArchiveInfo` is the public archive summary tuple. `filter_archives_by_date` applies relative date windows.

Control flow: `Archives.ids` lists store entries, `_get_archive_meta` loads archive metadata object by ID and tolerates missing/corrupt archive item objects by returning sentinel metadata. Matching first materializes archive infos, then supports `aid:`, `tags:`, `user:`, `host:`, and name/glob/regex matches via `get_regex_from_pattern`. `list` applies match, date filters, sorting, first/last limiting, and reverse. Manifest load parses a `ManifestItem`, prepares archive interface state, merges known item keys from config and legacy fields, then checks feature requirements per requested operation.

State and persistence: modern archives are persisted as borgstore directory entries, with archive metadata stored as repository objects. The manifest object is stored at the all-zero `MANIFEST_ID` through `repository.get_manifest` / `put_manifest`. Manifest config stores `item_keys` and optional `feature_flags`. Timestamp persistence is strictly monotonic on writes by maxing current time against last timestamp plus one microsecond.

Dependencies and integration points: it uses `RepoObj`, crypto key factory, `ArchiveItem` / `ManifestItem`, borgstore `ObjectNotFound`, parse/format time helpers, patterns, and both `LegacyRepository` / `LegacyRemoteRepository` to choose `LegacyArchives`. Repository security checks consume manifest timestamp and key details.

Risks: archive listing materializes metadata and may be expensive for large repositories. Missing or corrupt archive metadata is represented as synthetic archive entries, so callers must honor the `exists` field in raw metadata paths. Feature flag keys are `Operation` enum values; serialization compatibility must keep those stable. ID-prefix matching requires exactly one result and can surprise callers if prefixes are ambiguous.

Test signals: tests should cover manifest load/write round trips, monotonic timestamp update, mandatory feature rejection per operation, modern archive create/delete/undelete/nuke/list behavior, matching modes, date filters, missing/corrupt archive metadata sentinels, legacy repository selecting `LegacyArchives`, and `NoManifestError` propagation from repositories.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/manifest.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/patterns.py -->
# sources/sync-backup/borg/src/borg/patterns.py

Purpose: this module parses and evaluates Borg include/exclude patterns from command-line options and pattern files. It supports literal paths, path prefixes, fnmatch globs, Borg shell patterns, regular expressions, root directives, and pattern-style directives.

Important APIs and types: `PatternMatcher` stores ordered pattern/command pairs and a fast full-path lookup. `PatternBase` is the superclass for `PathFullPattern`, `PathPrefixPattern`, `FnmatchPattern`, `ShellPattern`, and `RegexPattern`. `IECommand` represents root, style, include, exclude, and exclude-no-recurse commands. Parser helpers include `parse_patternfile_line`, `load_pattern_file`, `load_exclude_file`, `parse_pattern`, `parse_exclude_pattern`, `parse_inclexcl_command`, and `get_regex_from_pattern`. Argparse actions load patterns directly into parsed args.

Control flow: pattern-file lines are cleaned externally, then parsed as include/exclude/root/style commands. Style commands update the fallback parser for later lines. `PatternMatcher.match` normalizes paths, checks exact full-path patterns first, then ordered patterns, updates `recurse_dir`, and returns include/exclude/fallback. Pattern subclasses prepare their normalized pattern and compiled regex at construction. `get_regex_from_pattern` is a separate string-matching helper for archive names with `sh:`, `re:`, and default exact matching.

State and persistence: no file state is persisted. Runtime state includes pattern lists, `match_count` on non-full include patterns, `recurse_dir`, fallback behavior, and include patterns added from positional paths. On macOS, path normalization uses Unicode NFD to match HFS+ behavior.

Dependencies and integration points: it depends on Borg's `shellpattern.translate`, `clean_lines`, argparse helper classes, and Borg `Error`. Archive matching in `manifest.py` uses `get_regex_from_pattern`; archiver command parsing uses the argparse actions and matcher.

Risks: recursion semantics are subtle. `ExcludeNoRecurse` sets `recurse_dir=False`, while ordinary exclude still recurses to allow later include patterns under excluded directories. Full-path patterns bypass `match_count`, so unmatched include reporting intentionally excludes them. Root path commands warn, not fail, for relative or nonexistent roots. Regex patterns run user-provided regexes and can be expensive or invalid if not validated by callers.

Test signals: tests should cover each prefix (`pf`, `pp`, `fm`, `sh`, `re`), pattern-style switching, include/exclude/no-recurse semantics, fast full-path lookup, unmatched include reporting, macOS normalization, root path warnings, invalid command errors, and archive-name regex conversion.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/patterns.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/platform/__init__.py -->
# sources/sync-backup/borg/src/borg/platform/__init__.py

Purpose: this package initializer selects Borg's platform-specific filesystem APIs and re-exports a stable public platform surface. It hides OS-specific modules behind common names such as `listxattr`, `acl_get`, `SyncFile`, `process_alive`, and user/group lookup wrappers.

Important APIs and types: it exports `ENOATTR`, `SaveFile`, `sync_dir`, `fdatasync`, `safe_fadvise`, `get_process_id`, `fqdn`, `hostname`, `hostid`, `swidth`, xattr functions, ACL functions, flag functions, `SyncFile`, process helpers, `getosusername`, `get_birthtime_ns`, and wrappers `uid2user`, `gid2group`, `user2uid`, `group2gid`.

Control flow: import-time platform flags choose Linux, FreeBSD, NetBSD, Darwin, generic POSIX, or Windows branches. Each branch imports the best available concrete implementations and sets `platform_ug` to either `posix_ug` or `windows_ug`. `get_birthtime_ns` prefers `st_birthtime_ns`, falls back to Darwin-specific inode support, then `st_birthtime`, else `None`.

State and persistence: import-time state is the chosen function set and `platform_ug` module. No data is persisted here, but selected durability helpers strongly influence repository persistence behavior.

Dependencies and integration points: nearly all filesystem code imports from `borg.platform` rather than direct OS modules. `legacy.repository` relies on `SaveFile`, `SyncFile`, `sync_dir`, and `safe_fadvise`; archive metadata code uses ownership and xattr/ACL functions.

Risks: import-time selection means tests must monkeypatch wrapper functions or reload modules carefully. Missing platform-specific modules or wrong flags break broad filesystem behavior. Birthtime behavior differs across OSes. User/group wrappers depend on `platform_ug`, so it must be set in every branch.

Test signals: tests should cover branch-specific imports in platform CI, monkeypatchability of ownership wrappers, `get_birthtime_ns` fallbacks, Windows fallback xattr stubs, and generic POSIX behavior on less common platforms.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/platform/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/platform/base.py -->
# sources/sync-backup/borg/src/borg/platform/base.py

Purpose: this module provides base/fallback platform APIs and durable file update helpers. It supplies no-op or minimal xattr/ACL/flag implementations, directory sync, `posix_fadvise` safety, atomic file replacement, terminal string width, and host/process identity helpers.

Important APIs and types: `listxattr`, `getxattr`, `setxattr`, `acl_get`, and `acl_set` are fallbacks. `get_flags` / `set_flags` handle BSD-style flags where available. `sync_dir` fsyncs directories except on Windows. `safe_fadvise` wraps `os.posix_fadvise` and ignores noncritical failures. `SyncFile` writes new files with flush/fdatasync/fadvise/directory sync on close. `SaveFile` writes atomically via a temporary file and `os.replace`. `swidth`, `getfqdn`, and `get_process_id` support UI and locking identity.

Control flow: `SyncFile.close` syncs file contents, closes, then syncs the parent directory. `SaveFile.__enter__` creates a temp file in the target directory using Borg's mode-aware mkstemp, wraps it in platform `SyncFile`, and returns the file object. `SaveFile.__exit__` closes/syncs, unlinks temp files on errors, atomically replaces the target on success, and syncs the directory. Host identity is computed once at import using hostname/FQDN and `uuid.getnode`, overrideable by `BORG_HOST_ID`.

State and persistence: `SyncFile` and `SaveFile` directly affect on-disk durability. Temporary files are named from the target basename plus random suffix and are cleaned on normal or exceptional exits. Global `hostname`, `fqdn`, and `hostid` are fixed at import.

Dependencies and integration points: repository config/index/hints/security files use `SaveFile`; legacy segment writing uses `SyncFile`. `platform.__init__` composes OS-specific functions with these base helpers. Lock identity uses `get_process_id`.

Risks: durability guarantees vary by filesystem and hardware; comments explicitly note that fsync cannot guarantee all power-failure semantics. `SaveFile` last-writer-wins under concurrent writers. Base xattr/ACL stubs silently omit unsupported metadata except `getxattr`, which raises `ENOATTR`. Import-time FQDN resolution may perform DNS work.

Test signals: tests should cover atomic replace, cleanup on exceptions, binary/text modes, directory sync error handling for `EINVAL`, no-op xattr/ACL behavior, string width for CJK/combining characters, and `BORG_HOST_ID` override.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/platform/base.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/platform/posix_ug.py -->
# sources/sync-backup/borg/src/borg/platform/posix_ug.py

Purpose: this module provides cached POSIX user/group name and ID lookup helpers using Python's `pwd` and `grp` modules.

Important APIs and types: `_uid2user(uid, default=None)`, `_user2uid(user, default=None)`, `_gid2group(gid, default=None)`, and `_group2gid(group, default=None)` are all decorated with `functools.cache`.

Control flow: numeric-to-name helpers call `pwd.getpwuid` or `grp.getgrgid` and return `default` on `KeyError`. Name-to-numeric helpers return `default` for empty names, otherwise call `pwd.getpwnam` or `grp.getgrnam`, again returning `default` on `KeyError`.

State and persistence: lookup results are process-local cache entries. No data is persisted.

Dependencies and integration points: `platform.__init__` exposes these helpers through `uid2user`, `user2uid`, `gid2group`, and `group2gid` wrappers on POSIX platforms. Archive create/extract code uses them when storing or restoring ownership metadata.

Risks: cache entries can become stale if system user/group databases change during a Borg process. Empty names are treated as missing. The helpers intentionally swallow missing users/groups, which is appropriate for archive portability but can hide local account configuration changes.

Test signals: tests should cover successful lookups, missing IDs/names returning defaults, empty-name behavior, and cache clearing/monkeypatching when simulating user database changes.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/platform/posix_ug.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/platform/windows_ug.py -->
# sources/sync-backup/borg/src/borg/platform/windows_ug.py

Purpose: this module supplies simplified ownership mapping helpers for Windows, where Borg does not preserve POSIX uid/gid identities in the same way.

Important APIs and types: `_uid2user`, `_user2uid`, `_gid2group`, and `_group2gid` are cached functions. Numeric-to-name helpers return `"root"` as a stable placeholder. Name-to-ID helpers return `0` for nonempty values and `default` for empty values.

Control flow: there is no OS lookup. The functions are deterministic placeholder mappings designed to keep ownership fields stable enough for Borg metadata flows on Windows.

State and persistence: only process-local `functools.cache` state exists. No external state is read or written.

Dependencies and integration points: selected by `platform.__init__` on Win32 and exposed through platform ownership wrappers. Archive metadata conversion and extraction can call these wrappers without platform-specific branching.

Risks: placeholder mapping loses real Windows ACL/security identity information. Code that assumes POSIX-like ownership semantics must not use these helpers as proof of real account ownership. Returning `"root"` and `0` is compatibility behavior, not a security mapping.

Test signals: tests should cover deterministic placeholder values, default handling for empty user/group names, and wrapper selection on Windows.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/platform/windows_ug.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/platform/xattr.py -->
# sources/sync-backup/borg/src/borg/platform/xattr.py

Purpose: this module provides shared low-level helpers for platform-specific extended attribute implementations. It handles buffer sizing, errno translation, and byte-string list splitting conventions.

Important APIs and types: `split_string0(buf)` splits null-terminated byte-string lists. `split_lstring(buf)` splits length-prefixed byte-string lists. `BufferTooSmallError` is an internal retry signal. `_check(rv, path=None, detect_buffer_too_small=False)` converts negative C return values into `OSError` or `BufferTooSmallError`. `_listxattr_inner`, `_getxattr_inner`, and `_setxattr_inner` wrap platform C functions with dynamic buffers and type assertions.

Control flow: list/get helpers start with the shared `Buffer` size, call the platform function, and double size on `ERANGE` or full-buffer truncation. `_check` asks platform `get_errno`, maps invalid errno values to an empty message, formats integer paths as `<FD n>`, and raises `OSError` for regular failures. Set helper performs a single call and does not treat `ERANGE` as buffer growth because it means invalid input for set operations.

State and persistence: a process-global `Buffer(bytearray, limit=2**24)` provides reusable storage up to 16 MiB. The module does not persist data; it supports reading/writing xattrs through platform modules.

Dependencies and integration points: Linux, Darwin, FreeBSD, and NetBSD xattr modules use these helpers around their C bindings. `platform.__init__` imports this module to ensure packaging includes it.

Risks: buffer growth can reach the 16 MiB limit for pathological xattrs. `_check` relies on correct platform `get_errno`. `split_lstring` trusts length prefixes and does not explicitly validate truncated input. Full-buffer detection is intentionally conservative and may retry even when exact-size results are valid.

Test signals: tests should cover null and length-prefixed splitting, `ERANGE` retry growth, FreeBSD-style full-buffer retry, OSError path formatting for FDs, invalid errno handling, and setxattr error propagation.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/platform/xattr.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/platformflags.py -->
# sources/sync-backup/borg/src/borg/platformflags.py

Purpose: this tiny module centralizes boolean platform flags so the rest of Borg avoids scattered `sys.platform.startswith(...)` checks.

Important APIs and types: exported booleans are `is_win32`, `is_cygwin`, `is_linux`, `is_freebsd`, `is_netbsd`, `is_openbsd`, `is_darwin`, `is_haiku`, and `is_msystem`.

Control flow: flags are computed once at import from `sys.platform`, with `is_msystem` additionally requiring Win32 and an `MSYSTEM` environment variable.

State and persistence: import-time booleans only. No persistence or mutable state.

Dependencies and integration points: `platform.__init__` uses these flags for OS-specific imports. Other modules use them for small platform-specific behavior, such as skipping directory open/fsync on Windows.

Risks: import-time flags do not change if tests monkeypatch `sys.platform` after import. Prefix checks must stay aligned with Python's platform strings. `is_msystem` depends on environment at import time.

Test signals: tests should verify expected flags under monkeypatched import environments and MSYS2 detection.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/platformflags.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/repoobj.py -->
# sources/sync-backup/borg/src/borg/repoobj.py

Purpose: this module defines Borg 2 repository object framing. It wraps encrypted metadata and encrypted compressed data in a fixed header so repository objects can support metadata-only reads, type validation, and modern compression metadata.

Important APIs and types: `RepoObj` exposes `extract_crypted_data`, `id_hash`, `format`, `parse_meta`, and `parse`. Constants `OBJ_MAGIC`, `OBJ_VERSION`, and `REPOOBJ_HEADER_SIZE` define the object envelope. `ObjHeader` contains magic, version, chunk ID, encrypted metadata size, and encrypted data size. The module re-exports `RepoObj1` from `borg.legacy.repoobj` for compatibility.

Control flow: `format` asserts a real repository object type, stores it in metadata, compresses data with the default lz4 compressor unless receiving already compressed data and explicit size/ctype/clevel, encrypts data and msgpacked metadata separately, then prefixes the binary header. `parse_meta` validates header and decrypts only metadata, optionally checking `ro_type`. `parse` validates full object size, decrypts metadata/data, optionally decompresses, handles obfuscation payload size (`psize`), and verifies plaintext ID unless the authenticated-no-key workaround is active.

State and persistence: instances keep `key` and default compressor. Persistent state is the object byte layout: header, encrypted msgpack metadata, encrypted compressed data. Metadata includes type, compression details, sizes, and optional payload size.

Dependencies and integration points: repositories store these bytes in pack objects. `Manifest`, `Archives`, cache and archive code call `RepoObj` to serialize manifests, archive metadata, and chunks. `Repository.get(read_data=False)` intentionally returns enough bytes for `parse_meta`.

Risks: `format` mutates the supplied `meta` dict by adding `type` and compression fields. Assertions enforce important preconditions. Metadata/data size validation must remain exact to avoid parsing adjacent packed objects. `parse(decompress=False, want_compressed=True)` deliberately skips ID verification, so callers must use it only for safe reuse paths.

Test signals: tests should cover header validation, invalid magic/version/size errors, metadata-only reads, type mismatch rejection, compressed and precompressed formatting, obfuscation `psize`, ID verification behavior, and compatibility import of `RepoObj1`.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/repoobj.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/repository.py -->
# sources/sync-backup/borg/src/borg/repository.py

Purpose: this module implements the modern Borg repository abstraction on top of `borgstore`. It replaces legacy segment journals with namespaced store objects, repository locks, pack objects under `packs/`, config objects, key objects, archive directory entries, and cache helpers.

Important APIs and types: `Repository` exposes lifecycle (`create`, `open`, `close`, `destroy`), lock/key/config operations, chunk index management, object access (`list`, `get`, `put`, `delete`, `get_many`), checks, manifest access, and generic store wrapper methods. `PackWriter` buffers chunks into pack bytes and updates `ChunkIndex`. Helper functions include `repo_lister`, `borg_permissions`, `rest_serve_command`, and `build_rest_backend`. Error classes mirror legacy repository errors plus `PackLocationUnknown`.

Control flow: construction resolves a `Location` or local path to a store URL, defines namespace config, maps permissions from parameter or `BORG_REPO_PERMISSIONS`, and creates either a local store or REST backend. `create` initializes `config/readme`, `config/version`, `config/id`, and an empty chunk index cache. `open` validates config, acquires a store lock, creates `PackWriter`, and lazily defers chunk index building. `put` delegates to `PackWriter.add`; at current `max_count=1`, each chunk flushes to one pack. `get` resolves ID through `chunks`, rejects pending pack entries, then loads full object bytes or enough header+metadata bytes for metadata-only parsing.

State and persistence: persistent namespaces are `archives/`, `cache/`, `config/`, `keys/`, `locks/`, and `packs/`. The repository ID and manifest are stored under `config/`. Repokeys are content-addressed under `keys/<sha256>`. Pack objects are stored under `packs/<pack_id_hex>`. The in-memory chunk index is lazy and persisted incrementally to repo cache on close if loaded.

Dependencies and integration points: it integrates with `borgstore.Store`, REST backend serving through `borg serve --rest`, `storelocking.Lock`, `ChunkIndex`, `RepoObj` constants for object checking, `Manifest` errors, keyfile detection, and cache helpers. `Manifest.Archives` uses `store_list/store_store/store_move` for archive entries.

Risks: pack support is in an N=1-compatible phase; code comments document future N>1 assumptions. `delete` currently maps `pack_id = id`, which is correct only for N=1. `get(read_data=False)` must respect object boundaries when packs later contain multiple objects. If `PackWriter.store.store` fails, pending index entries must be removed to avoid silent data loss; this cleanup is present and important. Permission mapping must match repository namespace needs exactly.

Test signals: tests should cover repository creation/open validation, permission modes, REST command construction, key save/load/delete, lazy chunk index rebuild/persist behavior, PackWriter success/failure index updates, metadata-only `get`, `PackLocationUnknown`, check/repair behavior for corrupt pack headers, partial check checkpoints, store wrapper lock refresh, and N=1 pack/list/delete semantics.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/repository.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/security.py -->
# sources/sync-backup/borg/src/borg/security.py

Purpose: this module tracks repository trust state outside the repository itself to detect relocated repositories, encryption method changes, replayed manifests, and unknown unencrypted repository access.

Important APIs and types: `SecurityManager` manages a per-repository security directory with `key-type`, `location`, and `manifest-timestamp` files. Public methods include `known`, `key_matches`, `save`, `assert_location_matches`, `assert_no_manifest_replay`, `assert_key_type`, `assert_access_unknown`, `assert_secure`, and static `destroy`. `assert_secure(repository, manifest)` is the convenience wrapper. Error classes encode user-facing abort and security failures.

Control flow: construction derives the security directory from repository ID and legacy version. `assert_secure` first handles unknown unencrypted access, then checks location, key type, and manifest timestamp. Relocation prompts the user through `yes` unless overridden by `BORG_RELOCATED_REPO_ACCESS_IS_OK`, and updates the stored location if accepted. Unknown unencrypted access prompts through `BORG_UNKNOWN_UNENCRYPTED_REPO_ACCESS_IS_OK`. Manifest replay compares stored timestamp lexicographically to current manifest timestamp and raises a different error for plaintext keys versus encrypted keys.

State and persistence: security state is persisted with `SaveFile` in the external security directory, not in the repository. Files store canonical repository location, key type string, and latest manifest timestamp. `destroy` removes the directory.

Dependencies and integration points: it depends on `get_security_dir`, `SaveFile`, user prompt helper `yes`, repository `_location.canonical_path()`, manifest timestamp/key, and `PlaintextKey` for replay error classification. It is called after manifest loading to decide whether repository access is safe.

Risks: timestamp comparison assumes ISO-like manifest timestamps that sort lexicographically. OSError while reading previous state degrades to warnings and empty values, which can reduce protection. User/environment overrides are necessary for automation but can bypass safeguards. Security directory loss causes Borg to relearn repositories, with special care for unencrypted repos.

Test signals: tests should cover first-known saves, relocation prompt accept/deny and env override, key type mismatch, manifest replay for plaintext and encrypted repos, unknown unencrypted access prompt behavior, read errors, and legacy security directory selection.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/security.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/selftest.py -->
# sources/sync-backup/borg/src/borg/selftest.py

Purpose: this module runs Borg's built-in self-test suite using `unittest` only. It is intended to catch packaging, compilation, platform, or core Borg defects in a small set of fast tests.

Important APIs and types: `SELFTEST_CASES` contains crypto and chunker self-test classes. `SELFTEST_COUNT` is the expected successful test count. `SelfTestResult` records successes, formats test names, logs failures/errors/unexpected successes/skips, and reports success count. `selftest(logger)` is the public runner.

Control flow: `selftest` exits early when `BORG_SELFTEST=disabled`. Otherwise it builds a `TestSuite` from each configured test case, asserts that the corresponding modules do not import pytest, runs the suite, logs failures and skips, compares successful count against `SELFTEST_COUNT`, logs a generic failure message on any failure or count mismatch, exits with status 2, and logs elapsed time on success.

State and persistence: no persistent files are written. Runtime state is the unittest result object and elapsed timing. Failure path terminates the process with `sys.exit(2)`.

Dependencies and integration points: it imports selected test cases from Borg's test suite and is called by command startup or packaging checks with an already configured logger. It intentionally avoids pytest APIs because normal users may not have pytest installed.

Risks: `SELFTEST_COUNT` must be updated whenever test methods change; otherwise all tests can pass but selftest still fails. Importing test modules must remain lightweight and pytest-free. Because failure calls `sys.exit`, callers must treat this as a process-level health gate.

Test signals: tests should cover disabled env var behavior, successful run count, count mismatch failure, pytest import assertion, skip/failure logging, and exit code 2 on failure.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/selftest.py -->
