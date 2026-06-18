# subset-b-009103 Research

Grouped research for the Borg source files assigned to subset-b-009103. Each section preserves the source path in its title and is bounded by reconciliation markers for deterministic splitting into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/fuse.py -->
# sources/sync-backup/borg/src/borg/fuse.py

## Purpose
Implements the low-level `borg mount` FUSE filesystem for llfuse or pyfuse3. It exposes one or more Borg archives as a read-only virtual filesystem, supports lazy archive expansion, optional versions mode, hard-link reconstruction, xattrs, symlink targets, damaged-file zero filling, and chunk-backed reads.

## Important APIs, Types, And Functions
`fuse_main()` dispatches to pyfuse3 under Trio or llfuse with `workers=1`. `async_wrapper()` presents synchronous methods as pyfuse3 coroutines when needed. `ItemCache` maps generated inode numbers to archive `Item` metadata using a dense bytearray plus a temporary file for metadata records that span chunks. `FuseBackend` constructs and resolves the virtual tree, with `_create_filesystem`, `_process_archive`, `_process_leaf`, `_process_inner`, `get_item`, and `check_pending_archive`. `FuseOperations` is the llfuse/pyfuse3 operation provider, implementing `mount`, `statfs`, `getattr`, `listxattr`, `getxattr`, `lookup`, `open`, `opendir`, `read`, `readdir`, and `readlink`.

## Control Flow
Mount setup parses mount options, validates forced uid/gid names, creates a default directory `Item`, builds the root, calls `llfuse.init`, optionally daemonizes, then runs the FUSE main loop under SIGUSR1/SIGINFO diagnostics. Without versions mode, archives are represented as placeholder directories and expanded on first lookup/opendir. `_process_archive` loads archive metadata chunks, filters by matcher and strip-components, creates implicit directories, installs leaves, and resolves hard links. File reads optimize linear access by remembering the last chunk position per file handle and caching partially read chunks.

## State And Persistence
State is in-memory except for `ItemCache.fd`, a process-local temporary file storing direct msgpack item records. Persistent repository data is read through `Repository.get_many`, `Repository.get`, and `manifest.repo_objs.parse`. `contents`, `parent`, `_items`, `pending_archives`, `versions_index`, inode caches, and data caches are rebuilt per mount. `mount()` migrates the repository lock when daemonizing.

## Dependencies And Integration Points
Depends on `Archive`, `Item`, `FuseVersionsIndex`, `HardLinkManager`, `LRUCache`, msgpack wrappers, repository object parsing, matcher/filter construction, platform uid/gid lookup, `daemonizing`, and FUSE bindings selected by `fuse_impl.py`. Kernel permission behavior is affected by `default_permissions`, `allow_other`, uid/gid/umask options, and Darwin `volname`.

## Risks And Edge Cases
The module explicitly assumes single-threaded synchronous access; pyfuse3 async reentrancy would be risky if true awaits are introduced. `ItemCache` has implicit inode offset/bytearray assumptions and can grow large for metadata-heavy archives. Lazy expansion can surprise memory use on directory traversal. Broken hard links are skipped with warnings. Missing repository chunks raise EIO unless `allow_damaged_files` is enabled, then reads return zero bytes. Symlinks may point outside the mount tree. Mount option parsing mutates a list and rejects unsupported typed values.

## Test Signals
Exercise through mount-focused integration tests where available: archive listing, lazy archive expansion, versions mode naming, duplicate archive name disambiguation, xattr lookup, symlink readlink, damaged chunk handling, hard-link nlink updates, uid/gid/umask mount options, pyfuse3/llfuse selection, and linear versus random read offsets.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/fuse.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/fuse_impl.py -->
# sources/sync-backup/borg/src/borg/fuse_impl.py

## Purpose
Selects the runtime FUSE binding used by Borg. It tries implementations listed in `BORG_FUSE_IMPL`, defaulting to `mfusepy,pyfuse3,llfuse`, and exposes shared module variables consumed by `fuse.py`, `hlfuse.py`, and diagnostics.

## Important APIs, Types, And Functions
Exports `BORG_FUSE_IMPL`, `hlfuse`, `llfuse`, `has_llfuse`, `has_pyfuse3`, `has_mfusepy`, `has_any_fuse`, and imports platform `ENOATTR`. There are no functions; import-time selection is the API.

## Control Flow
At import time, the comma-separated implementation preference list is normalized and processed in order. `pyfuse3` populates `llfuse` with the pyfuse3 module and marks `has_pyfuse3`; `llfuse` imports the low-level module; `mfusepy` populates `hlfuse`. The first successful import breaks the loop. `none` is accepted as a non-importing option, and unknown names raise `RuntimeError`.

## State And Persistence
All state is module-global and process-local. It does not persist anything, but import order matters because consumers branch on these booleans at import time.

## Dependencies And Integration Points
Integrated by low-level `fuse.py`, high-level `hlfuse.py`, and `helpers.misc.sysinfo`. It depends on optional third-party modules `mfusepy`, `pyfuse3`, and `llfuse`, plus Borg platform errno constants.

## Risks And Edge Cases
Because selection happens at import time, changing `BORG_FUSE_IMPL` later has no effect. A typo in the environment variable raises immediately. If all configured modules are unavailable, callers must tolerate `has_any_fuse=False`. The pyfuse3 branch deliberately assigns the module to `llfuse` for compatibility, so downstream code must always check the feature booleans.

## Test Signals
Mock or subprocess tests should cover preference ordering, `none`, unknown implementation names, absent optional imports, and `sysinfo` reporting.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/fuse_impl.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/helpers/__init__.py -->
# sources/sync-backup/borg/src/borg/helpers/__init__.py

## Purpose
Compatibility façade for Borg helper utilities that were split out of a historical monolithic `helpers.py`. It re-exports common helpers and owns process-wide warning and exit-code aggregation.

## Important APIs, Types, And Functions
Re-exports data structures, error classes, filesystem helpers, parsing/formatting helpers, process helpers, progress indicators, time helpers, yes/no utilities, and msgpack helpers. Defines `workarounds`, `warning_info`, `_warnings_list`, `_exit_code`, `add_warning`, `classify_ec`, `max_ec`, `set_ec`, `init_ec_warnings`, `get_ec`, `get_reset_ec`, and `do_show_rc`.

## Control Flow
Importing this module imports many helper submodules and constants, so it is a high-fanout dependency. Warning collection appends typed tuples. Exit code handling classifies return codes into success, warning, error, or signal; `set_ec` keeps the more severe value; `get_ec` returns explicit error/signal/warning codes first, otherwise derives a warning code from collected warnings.

## State And Persistence
State is process-global: `_warnings_list`, `_exit_code`, and `workarounds` from `BORG_WORKAROUNDS`. `init_ec_warnings` resets mutable globals and can accept an existing warning list, which makes test isolation important. Nothing is persisted to disk.

## Dependencies And Integration Points
Almost every Borg command path imports from this package. `helpers.process` also imports back from `..helpers`, creating import-order sensitivity. `do_show_rc` uses the `borg.output.show-rc` logger and must never interfere with program exit.

## Risks And Edge Cases
The compatibility import surface can hide circular dependencies and slows import. Global exit/warning state must be reset between tests and top-level invocations. `classify_ec` rejects unknown codes, so additions to constants must keep ranges coherent. Multiple warning codes collapse to generic `EXIT_WARNING`.

## Test Signals
Existing helper package tests should cover warning aggregation, modern versus legacy exit code mode, `get_reset_ec`, `do_show_rc` logging resilience, and import compatibility for names historically exported from `borg.helpers`.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/helpers/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/helpers/argparsing.py -->
# sources/sync-backup/borg/src/borg/helpers/argparsing.py

## Purpose
Centralizes Borg's use of `jsonargparse` and flattens nested command namespaces into the single-level namespace expected by command dispatch.

## Important APIs, Types, And Functions
Re-exports `Action`, `ArgumentError`, `ArgumentTypeError`, `RawDescriptionHelpFormatter`, `Namespace`, `ActionSubCommands`, `SUPPRESS`, `REMAINDER`, `register_type`, and `PositiveInt`. `ArgumentParser` subclasses jsonargparse's parser to enforce Borg defaults. `flatten_namespace(ns)` converts nested subcommand namespaces to one `Namespace`.

## Control Flow
The parser hierarchy allows common options at top-level, group-command level, and leaf-command level. `flatten_namespace` walks `subcommand` attributes to build a joined subcommand path, then uses `Namespace.as_flat()` and sorts dotted keys by depth descending so innermost options win. For list values, it merges shallower and deeper lists so append-style options accumulate.

## State And Persistence
No persistent state. The returned `Namespace` is a new object derived from parser output. Parser registrations imported from jsonargparse affect config serialization/deserialization elsewhere.

## Dependencies And Integration Points
Used by archiver parser construction, helper validators, and config-file/environment support from jsonargparse. It is intentionally the only import point for argparse/jsonargparse classes used by Borg.

## Risks And Edge Cases
Precedence depends on dotted-key depth, so unexpected nested keys could collapse to the same destination. List merging assumes outer values should precede inner values. `existing is None` is used as the absence test, so a legitimate `None` from an inner scope does not block outer defaults.

## Test Signals
Tests should include top-level versus subcommand option precedence, two-level subcommands, `SUPPRESS` default behavior, append-list merging, empty subcommand paths, and config/environment values from jsonargparse.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/helpers/argparsing.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/helpers/datastruct.py -->
# sources/sync-backup/borg/src/borg/helpers/datastruct.py

## Purpose
Provides small reusable data structures: deterministic dict iteration, managed buffers with limits, and a chunked FIFO queue.

## Important APIs, Types, And Functions
`StableDict.items()` returns sorted items for stable serialization. `Buffer` manages an allocator-backed buffer with `resize` and `get`; `Buffer.MemoryLimitExceeded` is both `Error` and `OSError`. `EfficientCollectionQueue` maintains FIFO data split across member-type chunks; it provides `peek_front`, `pop_front`, `push_back`, `__len__`, and `__bool__`, plus `SizeUnderflow`.

## Control Flow
`Buffer.get` optionally resizes before returning the current buffer; normal growth only reallocates when the requested size exceeds the current buffer, while `init=True` permits shrinking/reinitialization. `EfficientCollectionQueue.push_back` appends into the last chunk until `split_size`, then creates new member collections. `pop_front` removes across chunks and deletes exhausted buffers.

## State And Persistence
All state is in-memory. `Buffer` stores `allocator`, `limit`, and `buffer`. `EfficientCollectionQueue` tracks `buffers`, total `size`, `split_size`, and `member_type`.

## Dependencies And Integration Points
`StableDict` is used by msgpack limited unpackers and legacy manifest output for deterministic ordering. `Buffer` is useful for low-level IO and crypto/compression paths. `EfficientCollectionQueue` has dedicated tests and supports stream assembly behavior.

## Risks And Edge Cases
`Buffer.__init__` asserts initial size does not exceed limit; assertions may be optimized out under `-O`. `push_back` relies on `member_type` supporting empty construction, slicing, concatenation, and length. `pop_front` raises for underflow before mutating, which is important for callers.

## Test Signals
Existing tests should cover stable ordering, allocator call counts, limit exceptions, shrink behavior with `init=True`, queue chunk boundaries, peeking empty/non-empty queues, multi-buffer pops, and underflow.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/helpers/datastruct.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/helpers/errors.py -->
# sources/sync-backup/borg/src/borg/helpers/errors.py

## Purpose
Defines Borg's structured error and warning classes with modern/legacy exit-code behavior and backup-specific wrappers.

## Important APIs, Types, And Functions
`ErrorBase`, `Error`, `ErrorWithTraceback`, `IntegrityError`, `DecompressionError`, `CancelledByUser`, `RTError`, `CommandError`, and `PathNotAllowed` are raised errors. `BorgWarning`, `FileChangedWarning`, `IncludePatternNeverMatchedWarning`, `BackupWarning`, `BackupError`, `BackupRaceConditionError`, `BackupOSError`, `BackupPermissionError`, `BackupIOError`, `BackupFileNotFoundError`, and `BackupItemExcluded` model warnings, backup access failures, and internal skipping.

## Control Flow
Message text is taken from class docstrings and formatted with constructor args. `exit_code` properties return class-specific modern codes when `BORG_EXIT_CODES=modern` at import time, otherwise generic legacy warning/error codes. `BackupWarning.exit_code` delegates to the wrapped `BackupError` in modern mode.

## State And Persistence
The only module state is `modern_ec`, derived once from the environment at import. Error instances retain args and, for `BackupOSError`, selected `OSError` fields.

## Dependencies And Integration Points
Uses constants for exit-code ranges and low-level crypto `IntegrityError` as a base for integrity failures. These classes are consumed by archiver top-level exception handling, backup traversal, repository integrity checks, and helpers warning aggregation.

## Risks And Edge Cases
Docstring formatting means constructor arg counts must match class docs. `modern_ec` does not react to environment changes after import. `BackupWarning` asserts its second arg is a `BackupError`, which can fail loudly if misused. `BackupItemExcluded` is intentionally not an `ErrorBase`.

## Test Signals
Tests should cover formatted messages, modern/legacy exit code switching in isolated processes or module reloads, traceback flags, `BackupOSError` field copying, and `BackupWarning` exit code delegation.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/helpers/errors.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/helpers/fs.py -->
# sources/sync-backup/borg/src/borg/helpers/fs.py

## Purpose
Collects filesystem, path-safety, Borg directory-location, hard-link, deletion, open/stat, unmount, and temp-file helpers.

## Important APIs, Types, And Functions
Directory helpers include `ensure_dir`, `get_base_dir`, `join_base_dir`, `get_keys_dir`, `get_security_dir`, `get_data_dir`, `get_runtime_dir`, `get_cache_dir`, and `get_config_dir`. Path/tag helpers include `dir_is_cachedir`, `dir_is_tagged`, `make_path_safe`, `slashify`, `map_chars`, `get_strip_prefix`, `remove_dotdot_prefixes`, `assert_sanitized_path`, and `to_sanitized_path`. IO helpers include `scandir_inorder`, `secure_erase`, `safe_unlink`, `dash_open`, `O_`, flag constants, `os_open`, `os_stat`, `umount`, and `mkstemp_mode`. `HardLinkManager` stores typed hard-link identity mappings.

## Control Flow
Borg directory resolution combines environment overrides with legacy and non-legacy XDG/platformdirs behavior, creating directories and cache tags when requested. Path sanitization normalizes separators, handles Windows drive letters/reserved characters, rejects `..`, and normalizes to relative paths. `os_open` supports openat-style parent fd/name, optional `O_NOATIME` fallback, and WSL read-only retry workaround. `safe_unlink` tries unlink, handles ENOSPC by truncating only single-link files, then retries.

## State And Persistence
Most helpers are stateless, but directory helpers create directories and cache tag files. `HardLinkManager` stores an in-memory map. `secure_erase`, `safe_unlink`, `umount`, and `mkstemp_mode` modify filesystem or mount state.

## Dependencies And Integration Points
Integrates with platform flags, constants, `platformdirs`, `SaveFile`, process environment sanitation for unmount subprocesses, archive creation/extraction hard-link handling, pattern/path safety, and tests under `helpers/fs_test.py`.

## Risks And Edge Cases
Environment-derived directory paths must avoid root HOME confusion under mount helpers. `make_path_safe` is security-sensitive for legacy archive reads. Secure erase can damage other links unless `avoid_collateral_damage` is true. Windows behavior differs for directories, drive letters, and reserved chars. `safe_unlink` must not truncate multi-link files.

## Test Signals
Tests should cover env precedence, legacy versus non-legacy dirs, cache tag creation, path sanitization and rejection, Windows mapping via monkeypatch, hard-link manager type assertions, `O_NOATIME` fallback paths, ENOSPC unlink recovery, and temp-file mode creation.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/helpers/fs.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/helpers/lrucache.py -->
# sources/sync-backup/borg/src/borg/helpers/lrucache.py

## Purpose
Provides a small mutable mapping with least-recently-used eviction and disposal callbacks, used by FUSE metadata/data caches and other bounded caches.

## Important APIs, Types, And Functions
`LRUCache[K, V]` implements `MutableMapping` methods `__setitem__`, `__getitem__`, `__delitem__`, `__contains__`, `__len__`, `__iter__`, plus `replace`, `clear`, `keys`, `values`, and `items`.

## Control Flow
The internal `OrderedDict` tracks recency. `__getitem__` moves a key to the end before returning. `__setitem__` asserts the key is new, evicts from the front while at capacity, calls `dispose` for each evicted value, then appends. `replace` updates an existing key without disposal and without changing the assertion model. `clear` disposes all values.

## State And Persistence
State is in-memory: `_cache`, `_capacity`, and `_dispose`. It does not persist anything.

## Dependencies And Integration Points
Used by `fuse.py` and `hlfuse.py` for open-file item/chunk caches. The disposal hook allows callers to close resources or release external state when entries are removed.

## Risks And Edge Cases
Capacity zero would make `__setitem__` loop attempt to pop from an empty dict. Replacement must use `replace` or delete first; otherwise assertions fire. `replace` does not move entries to most-recent. `items()` returns the live view, so iteration while mutating has normal mapping risks.

## Test Signals
Existing tests should verify eviction order, disposal on eviction/delete/clear, `__getitem__` recency updates, assertions for duplicate set and missing replace, and behavior of mapping views.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/helpers/lrucache.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/helpers/misc.py -->
# sources/sync-backup/borg/src/borg/helpers/misc.py

## Purpose
Miscellaneous runtime helpers for system diagnostics, multi-line logging, chunk iterator file wrappers, iterator consumption, tolerant broken-pipe text IO, and separated stream iteration.

## Important APIs, Types, And Functions
`sysinfo`, `log_multi`, `ChunkIteratorFileWrapper`, `open_item`, `chunkit`, `consume`, `ErrorIgnoringTextIOWrapper`, and `iter_separated`.

## Control Flow
`sysinfo` returns platform, Borg, Python, msgpack, FUSE, PID, CWD, argv, and SSH command information unless `BORG_SHOW_SYSINFO=no`. `ChunkIteratorFileWrapper.read` refills from a bytes iterator and assembles exactly up to requested bytes, invoking an optional progress callback on each read fragment. `open_item` wraps archive pipeline chunk fetching. `iter_separated` incrementally splits file reads by separator while preserving partial records across buffer boundaries.

## State And Persistence
`ChunkIteratorFileWrapper` stores the current memoryview, offset, exhaustion flag, iterator, and callback. `ErrorIgnoringTextIOWrapper` closes itself after broken pipes. `sysinfo` only reads environment/process state.

## Dependencies And Integration Points
Depends on Borg logger, msgpack wrapper, FUSE selection, archive pipeline `fetch_many`, and repository object type constants. It supports command diagnostics and streaming file contents from archives.

## Risks And Edge Cases
`sysinfo` imports FUSE selection and may reflect optional dependency availability. `ChunkIteratorFileWrapper.read` does not implement all file-like methods and can return memoryview slices joined as bytes. Broken-pipe wrapper intentionally hides write/read failures after closure. `iter_separated` does not trim separators and must handle both str and bytes streams consistently.

## Test Signals
Tests should cover sysinfo environment suppression, multi-line logging levels, chunk reads across boundaries, read callbacks, `chunkit` partial final chunks, `consume`, broken pipe suppression, and separator iteration with trailing separators.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/helpers/misc.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/helpers/msgpack.py -->
# sources/sync-backup/borg/src/borg/helpers/msgpack.py

## Purpose
Wraps `msgpack` so Borg consistently uses binary/string settings, surrogateescape handling, bounded unpackers for untrusted data, and Borg-specific exception types.

## Important APIs, Types, And Functions
Constants `USE_BIN_TYPE=True`, `RAW=False`, `UNICODE_ERRORS="surrogateescape"`. Exceptions `PackException` and `UnpackException`. Wrappers `Packer`, `packb`, `pack`, `Unpacker`, `unpackb`, `unpack`. Utility exports include `is_slow_msgpack`, `is_supported_msgpack`, `get_limited_unpacker`, `int_to_timestamp`, `timestamp_to_int`, plus re-exported `ExtType`, `Timestamp`, and `OutOfData`.

## Control Flow
Pack wrappers assert Borg's unicode-error policy and translate any packing exception. Unpack wrappers preserve `OutOfData` for streaming callers but wrap other exceptions. `get_limited_unpacker` selects use-list and max-buffer policies by data kind: remote client/server get maximum buffers for large store operations, while manifest/archive/key get `StableDict` hooks and list behavior.

## State And Persistence
No persistent state. `is_supported_msgpack` reads `BORG_MSGPACK_VERSION_CHECK` each call. `Unpacker` instances hold stream buffers internally.

## Dependencies And Integration Points
Used by archive metadata, item serialization, key files, repository RPC, FUSE metadata, and JSON dump preparation. It depends on Borg constants and `StableDict` to preserve deterministic map ordering for selected unpacking paths.

## Risks And Edge Cases
Changing raw/bin defaults can break repository compatibility. `get_limited_unpacker("server"|"client")` intentionally disables max buffer limits for specific large operations, so callers must use the correct kind. Environment override can bypass version checks. Wrapping exceptions may hide original exception types unless callers inspect `args`.

## Test Signals
Existing msgpack tests should cover str/bytes round-trips with surrogateescape, streaming `OutOfData`, wrapped exceptions, supported-version environment override, limited unpacker settings, timestamp conversion, and legacy data compatibility.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/helpers/msgpack.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/helpers/nanorst.py -->
# sources/sync-backup/borg/src/borg/helpers/nanorst.py

## Purpose
Converts the limited reStructuredText used in Borg help text into plain or terminal-styled text without pulling in a full rST renderer.

## Important APIs, Types, And Functions
`TextPecker` is a small reader with `read`, `peek`, `peekline`, and `readline`. `process_directive` handles directives. `rst_to_text` performs conversion. `RstToTextLazy` delays conversion and proxies string behavior. `ansi_escapes` emits terminal escape transitions. `rst_to_terminal` chooses ANSI output based on `is_terminal`.

## Control Flow
`rst_to_text` scans character-by-character with states for plain text, inline emphasis/code markers, strong markers, literal code blocks, directives, and references. It supports custom `nanorst` inline fill/replace directives, directive rendering, reference substitution through a caller-provided map, escaped inline markers, and code-block exit on blank-line indentation rules.

## State And Persistence
All conversion state is local to the scanner. `RstToTextLazy` caches the converted string after first access. No persistent state.

## Dependencies And Integration Points
Used by CLI help formatting and terminal output. It depends on `helpers.is_terminal` imported through the package façade and standard streams.

## Risks And Edge Cases
This is intentionally loose parsing, not full rST. Unmatched inline states assert at the end. Missing references raise `ValueError` with a maintenance instruction. The parser relies on indexing semantics in `TextPecker.peek`, making off-by-one behavior important. ANSI styling must reset on state transitions.

## Test Signals
Existing nanorst tests should cover inline emphasis/code, bold, escaped markers, code blocks, directives, reference substitution and missing references, lazy conversion, terminal/non-terminal rendering, and invalid final states.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/helpers/nanorst.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/helpers/parseformat.py -->
# sources/sync-backup/borg/src/borg/helpers/parseformat.py

## Purpose
Large helper module for parsing CLI values and repository locations, formatting archive/item/diff output, JSON serialization, placeholder replacement, text validation, path safety actions, and display utilities.

## Important APIs, Types, And Functions
Primitive helpers include `octal_int`, `bin_to_hex`, `hex_to_bin`, `safe_decode`, `safe_encode`, `remove_surrogates`, `binary_to_json`, `text_to_json`, `join_cmd`, `eval_escapes`, `decode_dict`, and `interval`. CLI parsers include `CompressionSpec`, `ChunkerParams`, `FilesCacheMode`, `PathSpec`, `FilesystemPathSpec`, `SortBySpec`, size parsers/formatters, relative time and text validators, tag/archive/comment validators, `Highlander`, and `MakePathSafeAction`. Formatting types include `DatetimeWrapper`, `PlaceholderReplacer`, `Location`, `BaseFormatter`, `ArchiveFormatter`, `ItemFormatter`, `DiffFormatter`, `BorgJsonEncoder`, and JSON/dump helpers.

## Control Flow
Validators convert strings to typed values or raise `ArgumentTypeError`/`ArgumentError`. `CompressionSpec` parses nested compression forms and lazily builds compressor objects. `ChunkerParams` accepts fixed, fail, default, buzhash64, and legacy buzhash forms with bounds checks. `Location` replaces placeholders, then parses legacy ssh/rest/file forms, borgstore-handled schemes, or local paths; canonical paths redact credentials for external schemes. Formatters precompute requested keys from format strings and lazily load archive metadata or file content hashes only when requested.

## State And Persistence
`replace_placeholders` is a module-level `PlaceholderReplacer` with mutable overrides. YAML representers and jsonargparse type registrations are global side effects at import. Formatter instances cache archive objects, requested keys, and condition hashes. JSON helpers do not persist directly but serialize repository/cache/archive state for command output.

## Dependencies And Integration Points
Tightly integrated with constants, argument parsing, msgpack timestamps, time helpers, filesystem path safety, platform display width, archive/repository/cache classes, borgstore URL handoff, manifest sorting keys, compression registry, and command output modes.

## Risks And Edge Cases
This module is security-sensitive around path sanitization, URL credential redaction, JSON-safe surrogate handling, and shell command display. `Location` treats several schemes as pass-through, so canonicalization differs by proto. Formatter hash keys can trigger expensive archive reads. Text validators must reject surrogate escapes for user-visible metadata. Placeholder replacement can inject current time/user/uuid and must validate unknown placeholders.

## Test Signals
Existing parseformat tests should cover compression grammar, chunker bounds, file-size parsing/formatting, location variants and credential redaction, placeholder validation, validators, JSON encoding of bytes/surrogates/timestamps, formatter key help and lazy calls, hash/fingerprint calculations, display-width truncation, and action classes.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/helpers/parseformat.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/helpers/passphrase.py -->
# sources/sync-backup/borg/src/borg/helpers/passphrase.py

## Purpose
Acquires, validates, and displays encryption passphrases from environment variables, commands, file descriptors, and interactive prompts while hiding values in repr output.

## Important APIs, Types, And Functions
Error classes: `NoPassphraseFailure`, `PasscommandFailure`, `PassphraseWrong`, and `PasswordRetriesExceeded`. `Passphrase` subclasses `str` and provides `_check_ambiguity`, `_env_passphrase`, `env_passphrase`, `env_passcommand`, `fd_passphrase`, `env_new_passphrase`, `getpass`, `verification`, `display_debug_info`, `new`, and redacted `__repr__`.

## Control Flow
`env_passphrase` rejects ambiguous simultaneous sources, then tries direct env var, passcommand, and fd in order. `env_passcommand` runs a shell-split command with sanitized system environment and strips one trailing newline. `fd_passphrase` reads all text from a numeric fd. `new` prefers new-passphrase env, then existing passphrase sources, then prompts up to ten times with confirmation and optional display verification.

## State And Persistence
Passphrases are plain Python strings in memory. The module reads environment variables and may consume/close the fd named by `BORG_PASSPHRASE_FD`. It does not persist secrets, but debug/verification paths can print them intentionally.

## Dependencies And Integration Points
Depends on `yes`, `prepare_subprocess_env`, Borg error classes, hex formatting, logger, `getpass`, `subprocess`, and command-line encryption/key handling. Supports primary and `other` repository passphrase namespaces.

## Risks And Edge Cases
Environment ambiguity is fatal. `BORG_DEBUG_PASSPHRASE=YES` and verification can reveal secrets on stderr by design. `shlex.split` means passcommands are not shell-expanded. FD reads close the descriptor. Interactive failure reports which passphrase env vars are set. Empty passphrases are rejected by `new` unless allowed.

## Test Signals
Existing passphrase tests should cover source precedence, ambiguity, passcommand success/failure, fd reading, EOF handling, retry exhaustion, empty-passphrase policy, debug output gating, verification prompt env override, and redacted repr.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/helpers/passphrase.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/helpers/process.py -->
# sources/sync-backup/borg/src/borg/helpers/process.py

## Purpose
Process, daemonization, signal, subprocess, filter-pipeline, and recurring-thread utilities used by Borg commands and mount operations.

## Important APIs, Types, And Functions
Daemon helpers `_daemonize`, `daemonize`, and `daemonizing`; signal helpers `_ExitCodeException`, `SignalException`, `SigHup`, `SigTerm`, `signal_handler`, `raising_signal_handler`, `SigIntManager`, global `sig_int`, and `ignore_sigint`; subprocess helpers `popen_with_error_handling`, `is_terminal`, `prepare_subprocess_env`, and `create_filter_process`; background utility `ThreadRunner`.

## Control Flow
`_daemonize` double-forks, detaches, redirects stdio, and yields old/new process IDs. `daemonizing` keeps a foreground process alive until the background signals success/failure or times out, optionally logging return code. Signal contexts install and restore handlers. `SigIntManager` debounces first Ctrl-C for graceful cancellation and lets later interrupts raise. `create_filter_process` inserts one-way filter subprocesses for inbound or outbound streams and kills/waits/raises depending on Borg and filter success.

## State And Persistence
Process state changes are real: forks, session creation, cwd `/`, stdio fd changes, signal handlers, subprocesses, and thread lifecycle. `sig_int` holds global cancellation state. `prepare_subprocess_env` copies and sanitizes environment, removing `BORG_PASSPHRASE` and setting `BORG_VERSION`.

## Dependencies And Integration Points
Used by FUSE background mounts, remote/filter commands, archive import/export, top-level signal handling, and terminal-dependent output. Integrates with platform flags and helper exit codes.

## Risks And Edge Cases
Fork/daemon logic is POSIX-specific. Foreground/background signaling uses SIGHUP/SIGTERM and must not leave locks stale. Signal handlers raising exceptions can happen at arbitrary bytecode locations. `popen_with_error_handling` forbids shell mode and returns `None` on common creation failures. Filter subprocess deadlock avoidance assumes one-way communication.

## Test Signals
Existing process tests should cover environment sanitization, command splitting failures, missing executable/permission errors, signal context restoration, SIGINT debounce, filter process success/failure, terminal detection, `ThreadRunner` termination, and daemon behavior with careful subprocess isolation.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/helpers/process.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/helpers/progress.py -->
# sources/sync-backup/borg/src/borg/helpers/progress.py

## Purpose
Emits machine-readable progress messages and percentage updates through the Borg progress logger.

## Important APIs, Types, And Functions
`ProgressIndicatorBase` provides logger setup, unique `operation_id`, `make_json`, and `finish`. `ProgressIndicatorMessage.output` emits arbitrary progress messages. `ProgressIndicatorPercent` tracks total, counter, percentage step, formatting message, `progress`, `show`, and `output`.

## Control Flow
Each instance receives a monotonically increasing operation id. `make_json` adds operation id, message id, JSON type, finished flag, and current wall time. Percent progress computes `counter * 100 / total`, increments the counter, and emits only when the threshold `trigger_at` is reached, then advances the threshold.

## State And Persistence
State is in-memory per indicator plus class-level `operation_id_counter`. Output is logged to `borg.output.progress` as JSON lines; no files are written here.

## Dependencies And Integration Points
Used by commands that need structured progress output and by frontends consuming Borg logs. Depends on standard logging/json/time and Borg logger setup.

## Risks And Edge Cases
`ProgressIndicatorPercent` divides by `total`, so callers must avoid zero totals when showing progress. Class-level operation ids are process-local and not reset except by test manipulation. JSON messages include wall-clock time, making exact-output assertions brittle.

## Test Signals
Existing progress tests should cover message JSON shape, finish events, percent thresholds, counter increments, info payload formatting, operation id increments, and logger integration.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/helpers/progress.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/helpers/shellpattern.py -->
# sources/sync-backup/borg/src/borg/helpers/shellpattern.py

## Purpose
Translates Borg shell-style path patterns, including directory wildcards and brace alternatives, into regular expressions.

## Important APIs, Types, And Functions
`translate(pat, match_end=r"\Z")` is the public converter. `_parse_braces` identifies matching unescaped brace pairs. `_translate_alternatives` rewrites shell brace alternatives into regex groups.

## Control Flow
Brace alternatives are translated first, converting unescaped commas inside matched brace pairs to `|` and only changing braces to parentheses when alternatives exist. `translate` then scans the pattern: `**/` matches zero or more directory levels, `*` and `?` do not cross the platform separator, bracket classes are preserved with negation handling, unescaped regex group characters from alternatives are allowed, and everything else is escaped.

## State And Persistence
No persistent state. Uses local scan state and a `LifoQueue` for brace matching.

## Dependencies And Integration Points
Used by Borg pattern matching and archive filtering. Depends on `os.path.sep` and `re`. Results are consumed as regex strings with `(?ms)` flags and caller-provided ending behavior.

## Risks And Edge Cases
Nested and adjacent brace groups are subtle. Escaped braces, commas, and pipes must remain literal. `**/` behavior depends on the platform path separator, while Borg archive paths often use `/`; callers must normalize consistently. Bracket parsing must avoid invalid regex for unterminated classes.

## Test Signals
Existing shellpattern tests should cover `*`, `?`, bracket classes, `**/`, custom `match_end`, escaped metacharacters, adjacent/nested brace alternatives, alternatives without commas, and platform separator assumptions.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/helpers/shellpattern.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/helpers/time.py -->
# sources/sync-backup/borg/src/borg/helpers/time.py

## Purpose
Parses, clamps, formats, and computes timestamps for archive metadata, CLI arguments, JSON output, and relative time filters.

## Important APIs, Types, And Functions
`parse_timestamp`, `parse_local_timestamp`, `utcfromtimestampns`, `timestamp`, `safe_s`, `safe_ns`, `safe_timestamp`, `format_time`, `format_timedelta`, `calculate_relative_offset`, `offset_n_months`, `OutputTimestamp`, and `archive_ts_now`. Constants include `SUPPORT_32BIT_PLATFORMS`, `MAX_NS`, and `MAX_S`.

## Control Flow
Timestamp parsing assumes UTC for naive ISO strings in `parse_timestamp`, but local time for CLI `timestamp` parsing if stat fails. Nanosecond timestamps are converted from a UTC epoch without float math. Unsafe negative or too-large timestamps are clamped. Relative offsets parse units `y`, `m`, `w`, `d`, `H`, `M`, and `S`; month offsets preserve day where possible by clamping to the target month length.

## State And Persistence
No mutable state. Constants are computed at import based on 32-bit support policy. `OutputTimestamp` wraps a datetime and serializes in local timezone.

## Dependencies And Integration Points
Used by archive creation/listing, filters, formatters, msgpack timestamp conversion, and JSON output. Depends on filesystem `stat` for file timestamp CLI values.

## Risks And Edge Cases
Local versus UTC assumptions differ by function and must match caller semantics. Year offsets can fail for leap-day or out-of-range dates. Month arithmetic must handle varying month lengths. Clamping future timestamps can hide invalid filesystem metadata but prevents overflow.

## Test Signals
Existing time tests should cover aware/naive parsing, file path timestamp arguments, ns conversion without float precision loss, clamping, output timezone formatting, relative offsets by each unit, month end behavior, and timedelta formatting.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/helpers/time.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/helpers/yes_no.py -->
# sources/sync-backup/borg/src/borg/helpers/yes_no.py

## Purpose
Implements reusable yes/no/default prompting with environment overrides, retry behavior, JSON logging mode, and robust EOF/Unicode handling.

## Important APIs, Types, And Functions
Constants `FALSISH`, `TRUISH`, `DEFAULTISH`, and sentinel `ERROR`. Public function `yes(...)` supports prompt messages, accepted-answer messages, default behavior, retry control, environment override, custom output stream, injected input function, prompt suppression, and message id.

## Control Flow
`yes` prints an initial prompt if provided, then loops. If an env override is set, that value is used once and optionally reported. Otherwise it reads input unless prompting is disabled. EOF maps to the default answer; `UnicodeDecodeError` maps to an invalid sentinel. Answers are classified against defaultish/truish/falsish. Invalid answers optionally log an invalid message; retry false returns the default, retry true emits retry prompt and repeats, clearing a bad env override.

## State And Persistence
No module mutable state. It reads environment and writes to stderr or the provided stream. In JSON logger mode it prints structured question events to stderr.

## Dependencies And Integration Points
Used by passphrase verification and other interactive confirmations. Depends on the `borg` logger's `json` attribute convention.

## Risks And Edge Cases
Output mode changes with logger configuration. Empty string is defaultish by default. Environment overrides can bypass interactivity but are cleared after invalid input. Custom accepted-answer lists must not include the `ERROR` sentinel. Prompting with `prompt=False` returns default without reading.

## Test Signals
Existing yes/no tests should cover true/false/default answers, EOF, Unicode decode errors, retry/no-retry, env overrides, JSON output, prompt suppression, custom streams, and invalid defaults.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/helpers/yes_no.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/hlfuse.py -->
# sources/sync-backup/borg/src/borg/hlfuse.py

## Purpose
Implements an alternate high-level FUSE backend using `mfusepy`. It exposes Borg archives as a read-only path-based filesystem with lazy archive expansion, versions mode, hard-link handling, xattrs, symlinks, and chunk-backed reads.

## Important APIs, Types, And Functions
`DirEntry` stores inode, parent, and lazily allocated children. `FuseBackend` manages tree construction and item packing with `_create_node`, `get_inode`, `set_inode`, `_create_filesystem`, `check_pending_archive`, `_iter_archive_items`, `_process_archive`, `_process_leaf_versioned`, `_file_version`, `_make_versioned_name`, `_find_node_from_root`, `_find_node`, handle helpers, and `_make_stat_dict`. `borgfs` implements `mount`, `statfs`, `getattr`, `listxattr`, `getxattr`, `open`, `release`, `create`, `read`, `readdir`, and `readlink`.

## Control Flow
Mount option parsing mirrors `fuse.py`. The filesystem tree uses path lookups instead of low-level inode callbacks. Archive directories are placeholders until accessed; `_find_node` expands pending archives along traversal. Items are msgpacked per inode to reduce Python object memory. Reads use file handles, last-position optimization, data chunk LRU cache, repository object parsing, and optional zero-fill for missing chunks.

## State And Persistence
State is in-memory: `DirEntry` tree, packed `inodes`, pending archive map, handles, LRU caches, version index, and mount option flags. Debug logging can append to `DEBUG_LOG` if configured. Daemonizing migrates the repository lock. No archive data is persisted by this module.

## Dependencies And Integration Points
Depends on `fuse_impl.hlfuse`, archive/matcher/filter helpers, `HardLinkManager`, msgpack, repository object parsing, uid/gid lookup, platform flags, and `daemonizing`. It is selected when `mfusepy` is preferred/available.

## Risks And Edge Cases
Path-based FUSE semantics differ from low-level APIs; offset handling in `readdir` currently yields repeated zero offsets, which may be sensitive to mfusepy expectations. Inode reuse for hard links mutates `DirEntry.ino`. Packed items save memory but require repeated msgpack unpacking. Versions mode uses SHA-256 truncated hashes, unlike `fuse.py`'s blake2b_128. `create` explicitly rejects writes with EROFS.

## Test Signals
Test through mfusepy-capable mount integration or backend unit tests for lazy expansion, path lookup, hard links, versions naming, xattrs, damaged chunks, handle release cache cleanup, readonly create, duplicate archive names, uid/gid/umask options, and debug logging.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/hlfuse.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/legacy/__init__.py -->
# sources/sync-backup/borg/src/borg/legacy/__init__.py

## Purpose
Documents the legacy package as Borg's Borg 1.x compatibility layer for `borg transfer --from-borg1` and serving v1 clients.

## Important APIs, Types, And Functions
This package initializer exports no runtime API. Its module docstring explains the package boundary and planned removability when Borg 1.x support is dropped.

## Control Flow
No executable control flow beyond module import.

## State And Persistence
No state and no persistence.

## Dependencies And Integration Points
The package contains legacy archive, crypto, hashindex, repository, remote, repo object, helper, and upgrade code. Importers use submodules directly.

## Risks And Edge Cases
Because it is documentation-only, risk is low. The main maintenance risk is stale package-level documentation if legacy support scope changes.

## Test Signals
Coverage comes from submodule tests such as legacy archive/helper/upgrade/repository tests rather than this initializer.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/legacy/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/legacy/archives.py -->
# sources/sync-backup/borg/src/borg/legacy/archives.py

## Purpose
Manages Borg 1.x archive registries embedded in legacy manifest blobs. It adapts old `{name: {"id": bytes, "time": str}}` storage to the modern archive listing interface used during transfer and compatibility operations.

## Important APIs, Types, And Functions
`LegacyArchives` provides `prepare`, `finish`, `ids`, `_get_archive_meta`, `_infos`, `_info_tuples`, `_matching_info_tuples`, `count`, `names`, `exists`, `get`, `get_by_id`, `create`, `list`, `list_considering`, `get_one`, `_set_raw_dict`, and `_get_raw_dict`. Several soft-delete methods intentionally raise `NotImplementedError`.

## Control Flow
`prepare` loads the raw manifest archive dict; `finish` returns a `StableDict` for deterministic manifest serialization. Listing converts raw entries to `ArchiveInfo`, optionally loads archive metadata from the repository, filters by archive id prefix, tags, user, host, or name pattern, applies date filters, sorts by requested keys, slices first/last, and reverses if requested.

## State And Persistence
`_archives` is an in-memory dict mirroring legacy manifest state. `finish` hands it back for manifest persistence. `_get_archive_meta` reads archive metadata objects from the legacy repository and reports a placeholder for missing objects.

## Dependencies And Integration Points
Used by manifest initialization for `LegacyRepository`. Depends on legacy repository object retrieval, manifest repo object parser, key unpacking, `ArchiveItem`, pattern translation, date filtering from modern manifest code, and parse/time helpers.

## Risks And Edge Cases
Some modern archive APIs are unsupported for Borg 1.x repositories. Archive ID matching must match exactly one archive. Missing archive metadata is represented as a fake non-existing archive. Sorting keys must exist on `ArchiveInfo`. `list_considering` rejects combining a specific name with list filters.

## Test Signals
Existing legacy archive tests should cover raw dict round-trip, create overwrite behavior, get by name/id, match filters, id prefix ambiguity, tags/user/host/name filtering, date filtering, sorting/slicing/reverse, missing archive object placeholder, and unsupported delete APIs.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/legacy/archives.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/legacy/crypto/__init__.py -->
# sources/sync-backup/borg/src/borg/legacy/crypto/__init__.py

## Purpose
Marks the legacy crypto package namespace.

## Important APIs, Types, And Functions
This file is empty and exports no direct API.

## Control Flow
No executable control flow.

## State And Persistence
No state and no persistence.

## Dependencies And Integration Points
Submodules such as `legacy.crypto.key` and `legacy.crypto.low_level` provide Borg 1.x key/cipher compatibility.

## Risks And Edge Cases
No runtime risk in the file itself; package import behavior relies on Python's package machinery.

## Test Signals
Coverage is provided by tests for legacy crypto key handling rather than this empty initializer.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/legacy/crypto/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/legacy/crypto/key.py -->
# sources/sync-backup/borg/src/borg/legacy/crypto/key.py

## Purpose
Provides Borg 1.x key compatibility classes and PBKDF2/AES-CTR key-file encryption/decryption for reading legacy repositories.

## Important APIs, Types, And Functions
`Pbkdf2FileMixin` implements `pbkdf2`, `decrypt_key_file`, `encrypt_key_file`, `decrypt_key_file_pbkdf2`, and `encrypt_key_file_pbkdf2`. `random_blake2b_256_key` creates padded BLAKE2b keys. `ID_BLAKE2b_256` supplies BLAKE2b id hashing and random initialization. Key classes are `Blake2AuthenticatedKey`, `AESCTRKey`, and `Blake2AESCTRKey`. `LEGACY_KEY_TYPES` aggregates accepted legacy key types.

## Control Flow
PBKDF2 key-file decrypt unpacks an `EncryptedKey`, checks version, stores algorithm, and for `"sha256"` derives a key, AES-decrypts data, and validates HMAC. Unsupported or non-PBKDF2 algorithms defer to superclass behavior. Encrypt mirrors this with random salt, configured iterations, HMAC, AES encryption, and msgpack packing. Key classes define accepted type bytes and cipher suites for read-only Borg 1.x compatibility.

## State And Persistence
Key instances store cryptographic key material inherited from modern key bases. PBKDF2 encryption persists encrypted key blobs. `BORG_TESTONLY_WEAKEN_KDF=1` reduces iterations for tests only.

## Dependencies And Integration Points
Depends on modern crypto key bases, low-level cipher/HMAC/BLAKE2b functions, legacy AES implementation, constants, msgpack helpers, and `EncryptedKey` items. Used by legacy repository transfer and key loading.

## Risks And Edge Cases
This is cryptography-sensitive compatibility code. Weakening KDF must remain test-only. Decrypt returns `None` on HMAC mismatch, so callers must distinguish wrong passphrase from unsupported format. Legacy key classes are read-only/not creatable despite having TYPE defaults. Random BLAKE2b keys are padded to match low-level assumptions.

## Test Signals
Legacy key tests should cover PBKDF2 encrypt/decrypt round-trip, wrong passphrase/HMAC failure, unsupported version/algorithm fallback, weak-KDF environment behavior, id hashing, random initialization lengths, and accepted type sets.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/legacy/crypto/key.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/legacy/hashindex.py -->
# sources/sync-backup/borg/src/borg/legacy/hashindex.py

## Purpose
Implements reading and writing Borg 1.x repository index files that map 256-bit keys to 32-bit segment/offset pairs.

## Important APIs, Types, And Functions
Named tuples `NSIndex1Entry`, `NSIndex1EntryFormatT`, and `NSIndex1EntryFormat`. Class `NSIndex1` implements `MutableMapping` through `HTProxyMixin` and provides `iteritems`, `read`, `size`, `write`, `_read`, `_write_fd`, and `_read_fd`.

## Control Flow
Construction creates a `borghash.HashTableNT` with key size 32 and value size 8, optionally reading from a path. Writing emits a legacy header with magic, used entry count as entries/buckets, key size, and value size, then writes each key and raw value. Reading validates header length, magic, key/value sizes, expected file size, then scans bucket records, skipping empty and tombstone sentinel values before installing raw hash table entries.

## State And Persistence
The in-memory state is the `HashTableNT`. Persistent state is the binary legacy index format with magic `BORG_IDX`. Optional file wrappers can receive `hash_part("HashHeader")` callbacks.

## Dependencies And Integration Points
Used by legacy repository code. Depends on `borghash.HashTableNT` and modern `HTProxyMixin`.

## Risks And Edge Cases
Header validation is strict but key/value size checks are assertions. `size()` reports hash table memory sizing, not necessarily on-disk format size. `iteritems(marker)` starts yielding at the marker including it; callers must understand marker semantics. Empty/tombstone sentinels are detected by value prefixes.

## Test Signals
Legacy repository/hashindex tests should cover binary round-trip, invalid short file, bad magic, size mismatch, empty/tombstone buckets, marker iteration, non-string file objects, and hash header callbacks.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/legacy/hashindex.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/legacy/helpers.py -->
# sources/sync-backup/borg/src/borg/legacy/helpers.py

## Purpose
Provides Borg 1.x hard-link classification helpers for legacy item conversion.

## Important APIs, Types, And Functions
`borg1_hardlinkable(mode)` returns true for regular files, block devices, character devices, and FIFOs. `borg1_hardlink_master(item)` detects old-style hard-link masters. `borg1_hardlink_slave(item)` detects old-style hard-link slaves with a `source`.

## Control Flow
The helpers inspect `stat` file type bits and selected item fields. Masters require `hardlink_master` truthy, no `source`, and a hardlinkable mode. Slaves require `source` and hardlinkable mode.

## State And Persistence
No state and no persistence.

## Dependencies And Integration Points
Used by Borg 1.x archive transfer/upgrade code to map old hard-link representation to newer hard-link identities and chunk reuse. Depends only on `stat` and item dict-like access.

## Risks And Edge Cases
Only selected file types are hardlinkable; directories and symlinks are excluded. Item field presence controls classification, so malformed legacy items can be misclassified or ignored.

## Test Signals
Existing legacy helper tests should cover each supported file type, unsupported types, master/slave field combinations, absent `hardlink_master`, and `source` interactions.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/legacy/helpers.py -->
