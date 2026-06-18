# subset-b-009110 research

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/git.py -->
# sources/sync-backup/bup/lib/bup/git.py

## Purpose
This is bup's primary Git storage integration layer. It treats a bup repository as a Git bare repository, provides object hashing/tree encoding helpers, reads `.idx` and `.midx` pack indexes with mmap, writes new pack/index pairs, manages refs and repository initialization, and exposes a cached `git cat-file` pipe for object reads.

## Important APIs, Types, And Functions
Key public surfaces include `repo()`, `init_repo()`, `establish_default_repo()`, `git_config_get()`, `calc_hash()`, `tree_encode()`, `tree_iter()`, `find_tree_entry()`, `PackIdxV1`, `PackIdxV2`, `PackIdxList`, `LocalPackStore`, `PackWriter`, `PackIdxV2Writer`, `list_refs()`, `read_ref()`, `update_ref()`, `rev_list()`, `rev_parse()`, `CatPipe`, `catpipe()`, `walk_object()`, and `MissingObject`. Name mangling helpers (`mangle_name`, `demangle_name`) encode bup's segmented-file convention with `.bup`, `.bupl`, and `.bupm` names.

## Control Flow
Repository functions first resolve `repodir` or explicit `repo_dir`, then call Git CLI commands with `GIT_DIR` in `_gitenv()`. Index lookup flows through `PackIdxList.exists()`: optional bloom rejection, `.midx` lookup, direct `.idx` lookup, recency reordering, and offset fallback for midx hits. Pack writing flows from `PackWriter.maybe_write()` to `_encode_packobj()`, `LocalPackStore.write()`, `finish_pack()`, `.idx` creation, atomic rename into `objects/pack`, fsync, optional callback, and `auto_midx()`. `CatPipe.get()` serializes requests to a long-lived `git cat-file --batch-command` or legacy batch pair and returns an iterator that must be consumed before another request.

## State And Persistence Behavior
Global state includes `repodir`, `verbose`, `_catpipe_for`, `_git_great`, and pack-index search counters. Persistent state is Git repository data: `config`, `HEAD`, `objects/pack/pack-*.pack`, `.idx`, `.midx`, `bup.bloom`, refs, and reflogs. Temporary pack files are staged below `objects/pack-tmp-*` and renamed only after full pack checksum/index generation. Open mmaps and cat-file subprocesses are explicitly close-checked through `__del__` assertions.

## Dependencies And Integration Points
This module depends on Git CLI, zlib, mmap helpers, `_helpers.write_idx`, bloom/midx support, commit serialization, `hashsplit` modes, config parsing, and `bup.path.exe()` for invoking `bup midx`/`bup bloom`. It is the storage backend for `repo/local.py`, VFS traversal, save/get transfer code, server protocol object receipt, and tests around pack/index handling.

## Risks And Edge Cases
Resource lifecycle is important: `PackIdxList` asserts only one instance, mmaps must close, and `CatPipe` forbids overlapping reads. A partially consumed cat-file iterator can block future reads. `PackIdxList.refresh()` deletes redundant or broken midx files, so stale open maps must be closed before `auto_midx()`. Git CLI failures are converted to `GitError`, but some commands intentionally treat empty results as nonfatal. Hash/tree parsing assumes well-formed Git object data and uses assertions heavily. Repository initialization mutates global `repodir`.

## Test Signals
Relevant signals are in `test/int/test_git.py`, `test/int/test_midx.py`, `test/ext/test-cat-file`, `test/ext/test-init`, `test/ext/test-walk-object-order`, `test/ext/test-list-idx`, `test/ext/test-packsizelimit`, and repository transfer tests. Good coverage should exercise pack v1/v2 parsing, midx refresh/removal, cat-file missing objects, config parsing, ref updates, repo detection, and `walk_object()` post-order traversal.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/git.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/hashsplit.py -->
# sources/sync-backup/bup/lib/bup/hashsplit.py

## Purpose
This module wraps the C-backed rolling hash splitter and turns byte streams into Git blobs or hierarchical Git trees. It centralizes bup's content-defined chunking defaults and the repository configuration that affects split compatibility.

## Important APIs, Types, And Functions
Constants include `BUP_BLOBBITS`, `BUP_TREE_BLOBBITS`, `MAX_PER_TREE`, `fanout`, and Git mode constants. `HashSplitter` is imported from `_helpers`. Public helpers are `splitter()`, `configuration()`, `from_config()`, `split_to_blobs()`, `split_to_shalist()`, and `split_to_blob_or_tree()`.

## Control Flow
`configuration(config_get)` reads `bup.split.trees` and optional `bup.split.files`, validating only `legacy:13` through `legacy:21`. `from_config()` filters that map to splitter kwargs. `split_to_blobs()` iterates `(blob, level)` from `HashSplitter`, writes each blob through `makeblob`, and tracks `total_split`. `split_to_shalist()` uses level-triggered `_squish()` to roll lower-level blob entries into intermediate trees, and `split_to_blob_or_tree()` returns either a single blob mode/id or a tree mode/id.

## State And Persistence Behavior
The only module state is configuration defaults and `total_split`. Persistence is indirect: caller-provided `makeblob` and `maketree` write Git objects, usually through `RepoProtocol`/`PackWriter`. The generated tree names are hex offsets padded to total size width.

## Dependencies And Integration Points
It depends on `_helpers.HashSplitter`, `ConfigError`, and `helpers.dict_subset`. It integrates with `cmd/save.py` for file storage, `cmd/get.py` for rewrite compatibility checks, and `git.py`/repo writers for actual object persistence.

## Risks And Edge Cases
`fanout` is mutable global test/config state; invalid or zero values can break assumptions even though an unreachable branch checks zero. Split compatibility depends on exact `blobbits` and tree behavior, so config drift can make rewrite necessary. `_make_shalist()` loads its input list and computes total size, so very large tree levels need memory proportional to entries at that level.

## Test Signals
`test/int/test_hashsplit.py`, `test/int/test_treesplit.py`, `test/ext/test-split-files-config`, `test/ext/test_split_trees.py`, `test/ext/test-treesplit`, and comparative split/join tests validate chunk boundaries, fanout, short reads, file configuration, and tree reconstruction.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/hashsplit.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/helpers.py -->
# sources/sync-backup/bup/lib/bup/helpers.py

## Purpose
This is the general-purpose support module for bup. It provides exit constants, process cleanup, atomic file replacement, fsync portability, mmap wrappers, protocol connection primitives, stream utilities, quoting, path reduction/grafting, exclusion parsing, error aggregation, and small formatting/parsing helpers.

## Important APIs, Types, And Functions
Important surfaces include `EXIT_*`, `notimplemented`, `finalized`, `temp_dir`, `stopped`, `fsync`/`fdatasync`, `merge_iter`, `atomically_replaced_file`, `BaseConn`, `Conn`, `DemuxConn`, `mux`, `chunkyreader`, `linereader`, `mmap_read*`, `parse_timestamp`, `parse_num`, `add_error`, `die_if_errors`, `parse_excludes`, `parse_rx_excludes`, `path_components`, `stripped_path_components`, `grafted_path_components`, `valid_save_name`, `period_as_secs`, and `make_repo_id`. `ObjectLocation`/`OBJECT_EXISTS` are used by storage lookups.

## Control Flow
Context managers dominate lifecycle: `stopped` terminates child processes on exit, `finalized` wraps arbitrary cleanup, and `atomically_replaced_file` opens a same-directory temp file then renames it on clean exit and fsyncs the parent. `BaseConn.check_ok()` and `DemuxConn` implement bup's simple command response protocol, while `mux()` packages stdout/stderr packets for remote command transport. Path reducers resolve symlinks in parents, sort prefixes, and remove redundant descendants.

## State And Persistence Behavior
Module state includes `saved_errors`, cached hostname, one reusable `nullctx`, platform fsync strategy, and constants such as `sc_arg_max`. Atomic replacement creates temporary directories beside targets and persists replacements with fsync when requested. Error aggregation persists only in memory until `die_if_errors()` exits.

## Dependencies And Integration Points
It depends on `_helpers`, `bup.io`, option terminal width, and standard OS/process/mmap APIs. It is imported by most storage, metadata, index, protocol, and command modules. `BaseConn` and `DemuxConn` are protocol foundations for local/remote repo communication.

## Risks And Edge Cases
Several functions assume byte paths and POSIX behavior. `atomically_replaced_file` relies on directory file descriptors and same-directory rename semantics. `grafted_path_components()` notes possible filesystem-resolution hazards. `parse_num()` accepts floats and truncates to int. `DemuxConn` must see `BUPMUX` initialization and can raise on oversized packets. `saved_errors` is global and can leak state between operations if not cleared.

## Test Signals
`test/int/test_helpers.py`, `test/int/test_shquote.py`, `test/int/test_io.py`, `test/ext/test-get-excludes`, `test/ext/test-save-strip-graft`, `test/ext/test-main`, and many command integration tests exercise quoting, path transforms, numeric parsing, exclusion files, mux/demux behavior, and error handling.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/helpers.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/hlinkdb.py -->
# sources/sync-backup/bup/lib/bup/hlinkdb.py

## Purpose
This module stores the filesystem hard-link database used by saves to remember which archive paths correspond to the same `(dev, ino)` node.

## Important APIs, Types, And Functions
The public pieces are `pickle_load()`, `Error`, and `HLinkDB`. `HLinkDB` exposes `prepare_save()`, `commit_save()`, `abort_save()`, `add_path()`, `change_path()`, `del_path()`, and `node_paths()`.

## Control Flow
Construction loads a pickle map from node key (`b"dev:ino"`) to paths and builds the reverse path-to-node index. Mutations update both maps. `prepare_save()` serializes the node map to an `atomically_replaced_file` if non-empty, or schedules removal if empty. `commit_save()` closes the pending atomic replacement; `abort_save()` cancels it.

## State And Persistence Behavior
Persistent state is a pickle file at the provided path, usually `bupindex.hlink`. In-memory state is `_node_paths`, `_path_node`, `_pending_save`, and an `ExitStack` of cleanup callbacks. The class asserts closure in `__del__`.

## Dependencies And Integration Points
It depends on `pickle`, `atomically_replaced_file`, `fsync`, and `unlink`. `cmd/save.py` uses it with index metadata to detect hardlink targets and encode `Metadata.hardlink_target`.

## Risks And Edge Cases
The pickle format is trusted input from the local repository cache, so corruption or malicious content can raise or execute pickle semantics. `node_paths()` indexes directly and raises `KeyError` for unknown nodes. There appears to be an argument-order bug in `change_path()`: it calls `self.add_path(new_dev, new_ino, path)` but `add_path()` expects `(path, dev, ino)`, which would corrupt maps if exercised. Atomic save requires `prepare_save()` before `commit_save()` when data exists.

## Test Signals
Hardlink behavior is indirectly covered by save/restore and metadata tests such as `test/ext/test-save-restore`, `test/ext/test-meta`, and paths in `cmd/save.py` that call `hlink_db.node_paths()`. Focused tests should cover add/change/delete, empty-db unlink, abort cancellation, and pickle corruption.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/hlinkdb.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/index.py -->
# sources/sync-backup/bup/lib/bup/index.py

## Purpose
This module implements bup's filesystem index format (`bupindex`) and metadata side store (`bupindex.meta`). It records stat data, metadata offsets, tree hierarchy, content hashes, and validity flags so `bup save` can avoid rehashing unchanged files.

## Important APIs, Types, And Functions
Important constants include `INDEX_HDR`, `INDEX_SIG`, `IX_EXISTS`, `IX_HASHVALID`, and `IX_SHAMISSING`. Core types are `MetaStoreReader`, `MetaStoreWriter`, `Entry`, `NewEntry`, `BlankNewEntry`, `ExistingEntry`, `Reader`, and `Writer`. Path helpers include `pathsplit()`, `unique_resolved_paths()`, `reduce_paths()`, and `merge()`.

## Control Flow
`Writer.add()` receives sorted paths, stat data, metadata offsets, and optional hash callbacks, converts paths to hierarchy elements, and uses `_golevel()`/`Level.write()` to close completed directory levels into a single mmap-friendly tree. `Reader` opens an existing index read-write, verifies the header, mmaps the file, reads the footer count, and materializes `ExistingEntry` objects on traversal. `ExistingEntry.repack()` writes modified flags back into the mmap and propagates invalidation to parents.

## State And Persistence Behavior
Index entries are binary records preceded by nul-terminated basenames and followed by a footer count. Metadata is append-only and deduplicated by encoded bytes in `MetaStoreWriter._offsets`. Index writes use `atomically_replaced_file` and fsync. Existing indexes are mutable through mmap, so flag changes can persist in place.

## Dependencies And Integration Points
It depends on `metadata.Metadata`, `xstat` nanosecond conversions, `_helpers.bytescmp`, mmap and atomic helpers. It is used by `cmd/index.py` and `cmd/save.py` to maintain scan state, by save logic to find valid hashes and metadata, and by hardlink tracking.

## Risks And Edge Cases
`Writer._add()` requires reverse-sorted path order and raises if order is wrong. `Reader` returns an empty reader for missing or invalid headers rather than always failing. Corrupt metadata can abort `MetaStoreWriter` initialization. Device checks, timestamp clamping (`tmax`), and fake entries affect stale detection. Direct mmap mutation means crashes around `save()` can leave partially updated flags.

## Test Signals
`test/int/test_index.py`, `test/ext/test-index`, `test/ext/test-index-clear`, `test/ext/test-index-save-type-change`, `test/ext/test-index-check-device`, `test/ext/test-rm-between-index-and-save`, and save/restore tests cover index construction, filtering, stale detection, metadata storage, type changes, device checks, and merge ordering.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/index.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/io.py -->
# sources/sync-backup/bup/lib/bup/io.py

## Purpose
This module centralizes low-level process I/O, terminal-aware logging/progress display, shell/path quoting for messages, SQL quoting helpers, and a close-checked mmap subclass.

## Important APIs, Types, And Functions
Important functions are `log()`, `debug1()`, `debug2()`, `progress()`, `qprogress()`, `reprogress()`, `byte_stream()`, `enc_dsq()`, `enc_dsqs()`, `enc_sh()`, `enc_shs()`, `path_msg()`, `cmd_msg()`, `walk_path_msg()`, `qsql_id()`, and `qsql_str()`. `mmap` subclasses `mmap.mmap` to assert explicit closure.

## Control Flow
The module captures `initial_umask` at import without leaving it changed. `log()` flushes stdout, clears a prior progress line when needed, and writes to stderr through `_hard_write()`, which waits with `select()` and tolerates temporary `EAGAIN`. Progress functions only emit on tty-like stderr and throttle repeated updates.

## State And Persistence Behavior
State includes `initial_umask`, `buglvl` from `BUP_DEBUG`, tty flags from `BUP_FORCE_TTY`, and last progress-line tracking. It does not persist files itself, but its mmap wrapper enforces resource lifecycle for modules that map pack indexes and bup indexes.

## Dependencies And Integration Points
This module is imported by helpers, git, metadata, ls, protocol, main, and command modules for message formatting and logging. Its quoting functions are used in error messages, repair trailers, and command diagnostics.

## Risks And Edge Cases
`_hard_write()` assumes file-descriptor readiness semantics and could block indefinitely on broken descriptors. `enc_sh()` intentionally hex-escapes high-bit bytes for ASCII-compatible output, which is safe but not necessarily pretty. `walk_path_msg()` assumes VFS walk path layout with optional commit/tree prefixes. The mmap subclass asserts explicit closure in `__del__`, so leaked maps surface as assertion failures.

## Test Signals
`test/int/test_io.py`, `test/int/test_shquote.py`, CLI integration tests, and tests that intentionally leave or close mmaps validate quoting, progress/log behavior, byte/string path rendering, and close discipline.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/io.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/ls.py -->
# sources/sync-backup/bup/lib/bup/ls.py

## Purpose
This module implements shared logic for `bup ls`: resolving repository VFS paths and formatting listings in short, hash, classified, or long metadata-rich forms.

## Important APIs, Types, And Functions
Key pieces are `item_hash()`, `item_info()`, the `optspec`, `LsOpts`, `opts_from_cmdline()`, `within_repo()`, and `via_cmdline()`.

## Control Flow
`opts_from_cmdline()` parses command arguments and maps raw flags into semantic options such as classification and hidden-file mode. `via_cmdline()` opens the selected local/remote repo and calls `within_repo()`. `within_repo()` resolves each requested path via `vfs.resolve()` or `vfs.try_resolve()`, optionally lists directory contents, augments metadata when needed, filters hidden entries, formats lines, and columnates tty short output.

## State And Persistence Behavior
The module has no persistent state. It reads repository objects and metadata through the repo/VFS layers and writes formatted bytes to the provided output stream.

## Dependencies And Integration Points
It depends on `metadata.summary_bytes`, `vfs`, `xstat.classification_str`, `Options`, terminal helpers, and `repo.main_repo_location`/`repo_for_location`. It is a command-facing consumer of repo/local and repo/remote abstractions.

## Risks And Edge Cases
Long listings require metadata augmentation, which can trigger object reads and public metadata filtering. Hidden-file behavior must match common `ls -a`/`-A` expectations, including synthetic `..`. `commit_hash` implies hash display and changes what hash is printed for commit items. Errors from VFS resolution are logged and reflected in a nonzero return.

## Test Signals
`test/ext/test-ls`, `test/ext/test-ls-remote`, VFS integration tests, and metadata listing tests cover path resolution, hidden entries, classification suffixes, hash display, remote behavior, and long-format output.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/ls.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/main.py -->
# sources/sync-backup/bup/lib/bup/main.py

## Purpose
This is the top-level `bup` command dispatcher. It parses global options, adjusts environment, loads built-in command modules, falls back to `bup-*` executables, manages profiling/debug flags, and normalizes process exit behavior.

## Important APIs, Types, And Functions
Important functions are `maybe_import_early()`, `usage()`, `misuse()`, `extract_argval()`, `parse_global_opts()`, `run_subcmd()`, and `main()`.

## Control Flow
At import, it adjusts `PYTHONPATH` from `bup_main.env_pythonpath` and processes early `--import-py-module`. `main()` installs the Ctrl-C handler, parses globals, sets absolute `BUP_DIR`, imports `bup.cmd.<subcmd>`, or locates an external `bup-<subcmd>` executable. `run_subcmd()` updates `BUP_FORCE_TTY`, invokes module `main(args)` or `os.execvp()`, clears progress output, and closes cached catpipes.

## State And Persistence Behavior
It mutates process environment (`PYTHONPATH`, `BUP_DEBUG`, `BUP_FORCE_TTY`, `BUP_DIR`) and uses global logging/progress state. It does not persist repository data directly; subcommands own that work.

## Dependencies And Integration Points
It integrates with `bup.cmd` modules, executable command directory from `bup.path`, `compat.get_argvb()`, `helpers.die_if_errors()`, and `git.close_catpipes()`. It is the user entry point for all bup commands.

## Risks And Edge Cases
Unknown module imports must distinguish missing command modules from import failures inside a command. `--import-py-module` is handled both early and skipped during global parsing. `os.execvp()` replaces the process for external commands, so cleanup only applies to in-process module commands. Environment changes can influence child behavior.

## Test Signals
`test/ext/test-main`, `test/ext/test-help`, `test/ext/test-versioning-and-archive`, command-specific tests, and error-path tests validate usage output, unknown commands, `--help` rewriting, debug/profile flags, and environment propagation.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/main.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/metadata.py -->
# sources/sync-backup/bup/lib/bup/metadata.py

## Purpose
This module captures, serializes, displays, creates, and restores filesystem metadata for bup archives. It handles common stat fields, ownership, timestamps, paths, symlink targets, hardlink targets, POSIX ACLs, Linux file attributes, and Linux xattrs.

## Important APIs, Types, And Functions
Core APIs include `Metadata`, `ApplyError`, `empty_metadata`, `from_path()`, `save_tree()`, `summary_bytes()`, `detailed_bytes()`, `display_archive()`, `start_extract()`, `finish_extract()`, and `extract()`. Internal record handlers encode/load/apply tagged fields such as common records, path, symlink target, hardlink target, POSIX1e ACL, Linux attr, and Linux xattr.

## Control Flow
`from_path()` lstat's a path, optionally calls a race-test hook, collects common fields and optional platform metadata, then freezes the object. `Metadata.encode()` emits a sequence of vint-tagged records ending with tag 0; `Metadata.read()` dispatches tags, supports legacy common/ACL formats, skips unknown bvec records, and returns `empty_metadata` for empty entries. Extraction creates paths first, then applies metadata, deferring directories until longest-path-first order to preserve directory permissions and times.

## State And Persistence Behavior
Persistent metadata lives in `.bupm` streams and `bupindex.meta`. Record tags are private and explicitly stable. Module state includes optional xattr/ACL/Linux attr backends, warning suppression flags, `verbose`, and `empty_metadata`. Restore mutates the filesystem: creates/unlinks paths, changes ownership/mode/times, sets ACLs, attrs, and xattrs when supported.

## Dependencies And Integration Points
It depends on `vint`, `xstat`, recursive directory scanning, `pwdgrp`, `_helpers` ACL/attr functions, optional xattr modules, and helpers for logging/errors. It is consumed by index metadata stores, VFS metadata augmentation, save/restore/get rewrite flows, and `ls` long output.

## Risks And Edge Cases
The file notes that metadata encoding is not stable. Restore is platform-sensitive: symlink chmod support, ACL/xattr availability, superuser ownership semantics, socket creation fallback, Linux attr API suppression on some big-endian ABIs, and unsupported filesystems all affect results. Path cleanup is security critical and rejects risky extraction paths. `finish_extract()` checks `os.path.isdir(meta.path)` rather than the cleaned path in one branch, which deserves scrutiny. Non-empty directories are not overwritten during creation.

## Test Signals
`test/int/test_metadata.py`, `test/ext/test-meta`, `test/ext/test-meta-acls`, `test/ext/test-empty-metadata`, `test/ext/test-save-restore`, `test/ext/test-restore-map-owner`, `test/ext/test-restore-single-file`, and VFS tests cover serialization, path cleanup, xattrs/ACLs, owner mapping, symlink races, empty metadata, and extraction ordering.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/metadata.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/midx.py -->
# sources/sync-backup/bup/lib/bup/midx.py

## Purpose
This module reads and validates bup multi-index (`.midx`) files, which aggregate multiple Git `.idx` files to accelerate object existence checks in repositories with many packs.

## Important APIs, Types, And Functions
Important items are `MIDX_HEADER`, `MIDX_VERSION`, `MissingIdxs`, `PackMidx`, `open_midx()`, and `clear_midxes()`. `PackMidx.exists()` supports source-index reporting but not pack offsets.

## Control Flow
`open_midx()` mmaps a candidate file, verifies header/version, handles too-old/too-new files with warnings, and constructs `PackMidx`. `PackMidx.__init__()` parses fanout bits, sha table, index selector table, and nul-separated idx names, then verifies each referenced idx exists. Lookup uses extracted leading bits to choose a fanout range and interpolated search over sorted SHA values.

## State And Persistence Behavior
The object owns an mmap and exposes iterable SHA entries. Persistent state is the `.midx` file and its referenced `.idx` files. `clear_midxes()` deletes all midx files in a directory.

## Dependencies And Integration Points
It depends on `_helpers.extract_bits`/`firstword`, mmap helpers, and logging. `git.PackIdxList` loads midx files, removes redundant or missing ones, and uses source hints from `PackMidx` when deduplicating writes.

## Risks And Edge Cases
Missing constituent idx files either raise `MissingIdxs` or cause `open_midx()` to return `None` depending on `ignore_missing`. Offset lookup is unsupported, so callers needing offsets must reopen the source idx. The interpolation formula assumes sorted hash distribution and well-formed fanout ranges. Close discipline matters because maps can keep files alive while auto-midx rewrites.

## Test Signals
`test/int/test_midx.py` and `test/int/test_git.py` cover missing idx behavior, check mode, midx close/refresh interactions, and object lookup through `PackIdxList`.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/midx.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/options.py -->
# sources/sync-backup/bup/lib/bup/options.py

## Purpose
This standalone-style module parses bup option specification strings into command usage text, getopt option sets, defaults, aliases, negated options, and an attribute-accessible option dictionary.

## Important APIs, Types, And Functions
Important pieces are `OptDict`, `Options`, `_intify()`, `_tty_width()`, `Options.parse()`, and `Options.parse_bytes()`.

## Control Flow
`Options.__init__()` stores the optspec and calls `_gen_usage()`, which parses synopsis lines until `--`, builds short/long getopt declarations, records defaults from bracket suffixes, creates aliases including `no-` forms, and formats usage. `parse()` runs the configured getopt function, loads defaults into `OptDict`, handles help/usage, converts digit aliases and integer-looking parameters, increments flag counts for repeated booleans, and returns `(opt, flags, extra)`.

## State And Persistence Behavior
Option state is per `Options`/`OptDict` instance. There is no file persistence. `OptDict` caches alias lookups and invalidates the cache on writes.

## Dependencies And Integration Points
It depends only on standard `getopt`, `textwrap`, terminal sizing, and regex. It is used by command modules such as `ls.py` and many bup commands, while `helpers.py` imports `_tty_width` for column formatting.

## Risks And Edge Cases
Specs are parsed with simple string/regex rules, so malformed specs may produce odd aliases instead of explicit failures. `--no-*` aliases are generated for all long options, including options with parameters, which command code must interpret carefully. `_intify()` converts only exact decimal strings, leaving other numeric-looking values as strings. `parse_bytes()` decodes with surrogateescape to preserve arbitrary argv bytes.

## Test Signals
`test/int/test_options.py`, command usage tests, and command-specific CLI tests validate defaults, aliasing, negation, digit options, byte argv decoding, help output, and fatal error behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/options.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/path.py -->
# sources/sync-backup/bup/lib/bup/path.py

## Purpose
This module computes bup runtime paths: executable directory, library/resource directory, default repository, cache locations, and default filesystem index paths.

## Important APIs, Types, And Functions
Public APIs include `exe()`, `exedir()`, `cmddir`, `libdir()`, `resource_path()`, `defaultrepo()`, `xdg_cache()`, `index_cache()`, `FSIndexPaths`, `flat_fsindex()`, and `default_fsindex()`.

## Control Flow
Import-time constants derive from `__file__`: `_libdir`, `_resdir`, `_exedir`, and `_exe`. `defaultrepo()` returns `BUP_DIR` or `~/.bup`. `index_cache(identifier)` prefers an existing XDG cache path, falls back to an existing legacy repo cache, and otherwise returns the XDG target.

## State And Persistence Behavior
The module stores computed path constants and reads environment variables (`BUP_DIR`, `XDG_CACHE_HOME`). It does not create directories itself. `FSIndexPaths` packages the stat, metadata, and hardlink index paths used by index/save flows.

## Dependencies And Integration Points
It is used by `git.auto_midx()` to find the bup executable, by `main.py` to find command executables, by repo selection for default repository paths, and by index/save commands for cache locations.

## Risks And Edge Cases
Path computation assumes the command directory is adjacent to the library as `../cmd`; packaging changes could break this. The file imports `environ` from both `os.environb` and `bup.compat`, relying on the latter final binding. `index_cache()` only checks existence before choosing legacy cache, so migration behavior depends on prior filesystem state.

## Test Signals
Repo/default-path behavior appears in `test/int/test_repo.py`, `test/int/test_git.py`, `test/ext/test-init`, command startup tests, and index tests that use `default_fsindex()`.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/path.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/protocol.py -->
# sources/sync-backup/bup/lib/bup/protocol.py

## Purpose
This module defines bup's client/server wire protocol helpers and server command dispatcher for remote repository operations. It serializes VFS items, resolutions, IOErrors, refs, indexes, object batches, config values, and repository reads/writes over a `BaseConn`-style stream.

## Important APIs, Types, And Functions
Important helpers include `read_item()`, `write_item()`, `write_resolution()`, `read_resolution()`, `write_ioerror()`, `read_ioerror()`, `_command`, `CommandDenied`, and `Server`. Server commands include `help`, `init-dir`, `set-dir`, `list-indexes`, `send-index`, `receive-objects-v2`, `read-ref`, `update-ref`, `join`/`cat`, `cat-batch`, `refs`, `rev-list`, `resolve`, and `config-get`.

## Control Flow
Serialization tags item class names and a `has_meta` flag, then writes either `Metadata` records or integer modes. `Server.handle()` reads command lines, validates against enabled commands, maps hyphenated command names to methods, and invokes decorated handlers. `receive_objects_v2()` loops length-prefixed objects, handles zero length as finish, `0xffffffff` as suspend, optionally suggests existing indexes for deduplication, writes raw object bytes to the repo packwriter store, and validates CRCs.

## State And Persistence Behavior
`Server` tracks the connection, backend factory, active repo, suspended write state, deduplication mode, command allowlist, and vet callbacks. Persistence is delegated to the backend repo: init creates repos, receive writes pack files, update-ref mutates refs. Suspended sessions finish writing on context exit.

## Dependencies And Integration Points
It depends on `git`, `vfs`, `vint`, `Metadata`, `helpers` connection utilities, and repo backends. It is used by remote clients/servers (`repo.remote`, `client`) and bridges local storage operations to remote command calls.

## Risks And Edge Cases
The protocol is line-oriented and comments acknowledge it is not future-proof. A malformed or unauthorized command aborts handling. `receive_objects_v2()` reaches into repo internals (`_packwriter` and store), which couples it to `LocalRepo`. `cat_batch()` reads all requested refs before responding to avoid deadlock. `read_resolution()` uses `ord(port.read(1))`; unexpected EOF as empty bytes can raise before the explicit EOF check. Config exposure is allowlisted.

## Test Signals
`test/int/test_protocol.py`, remote repository tests, `test/ext/test-on`, `test/ext/test-ls-remote`, get/save remote flows, and server command tests should cover item roundtrips, resolution/error serialization, object receipt, suspended writes, ref updates, and config-get allowlisting.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/protocol.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/pwdgrp.py -->
# sources/sync-backup/bup/lib/bup/pwdgrp.py

## Purpose
This module wraps password and group database lookups so bup can work consistently with bytes rather than locale-decoded strings, and caches lookups for metadata capture/restore.

## Important APIs, Types, And Functions
Core types are `Passwd` and `Group`. Lookup APIs are `getpwuid()`, `getpwnam()`, `getgrgid()`, `getgrnam()`, `pwd_from_uid()`, `pwd_from_name()`, `grp_from_gid()`, `grp_from_name()`, `username()`, and `userfullname()`.

## Control Flow
Raw `_helpers` lookups return tuples, which are wrapped into slot-based bytes objects. Cache helpers use `helpers.cache_key_value()` to memoize both hits and misses, and successful lookups populate reverse caches. `username()` and `userfullname()` lazily derive current-user names from uid and GECOS fields.

## State And Persistence Behavior
Persistent state is none. In-memory state includes uid/name and gid/name caches plus current-user cached values.

## Dependencies And Integration Points
It depends on `_helpers` platform lookup functions and `helpers.cache_key_value()`. `metadata.py` uses it to record user/group names and to map restored names back to ids.

## Risks And Edge Cases
Lookups can return `None`; callers must handle missing users/groups. `username()` assumes `pwd_from_uid(uid)` is not `None` before accessing `.pw_name`, so unusual systems without a passwd entry for the current uid could fail. Group password may be `None` on Android and is explicitly tolerated.

## Test Signals
Metadata tests, owner mapping restore tests, and platform integration tests cover most behavior indirectly. Focused tests should verify cache hit/miss behavior, byte enforcement, absent users/groups, and fallback current-user strings.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/pwdgrp.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/repair.py -->
# sources/sync-backup/bup/lib/bup/repair.py

## Purpose
This module records repair actions performed during `bup get --repair` or related rewrite flows and renders those actions as commit trailers.

## Important APIs, Types, And Functions
The public pieces are `valid_repair_id()` and `Repairs`. `Repairs` exposes `repair_count()`, `note_incidental_repair()`, `meta_replaced()`, `path_replaced()`, `link_blob_restored()`, `link_blob_fixed()`, and `repair_trailers()`.

## Control Flow
Each repair-recording method logs the repair id on the first repair, remembers the affected save via `_remember_save()`, and appends path/object details to a category list. `repair_trailers()` emits `Bup-Repair-ID`, repaired save refs, replaced file metadata, restored/fixed symlink blob notes, and lost metadata notes.

## State And Persistence Behavior
State is held in one `Repairs` instance: id, destructive flag, incidental count, ordered repaired-save map, and repair detail lists. Persistence happens only when callers append generated trailers to new commits.

## Dependencies And Integration Points
It depends on `vfs.Commit`, `vfs.RevList`, `render_path()`, hex encoding, shell byte quoting, and logging. `cmd/get.py` uses `valid_repair_id()` for CLI validation and repair tracking during rewrite/repair transfers.

## Risks And Edge Cases
`valid_repair_id()` allows any printable ASCII byte including spaces; trailer consumers must parse accordingly. `_remember_save()` assumes a specific VFS path shape with revlist and commit at positions 1 and 2. The `destructive` flag is stored here but not interpreted by this module.

## Test Signals
`test/ext/test-get-repair-bupm`, `test/ext/test-get-repair-symlinks`, `test/ext/test-get-rewrite-missing`, `test/ext/test-get-missing`, and get command unit/integration tests cover repair trailer generation and CLI validation paths.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/repair.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/repo/__init__.py -->
# sources/sync-backup/bup/lib/bup/repo/__init__.py

## Purpose
This module selects repository locations and constructs local or remote repository objects from command-line options, environment state, URLs, and client configs.

## Important APIs, Types, And Functions
Important APIs are `public_schemes`, `repo_location_url()`, `main_repo_location()`, `repo_for_url()`, `repo_for_location()`, and `parse_repo_url_arg()`.

## Control Flow
`main_repo_location()` prefers reverse-server mode from `BUP_SERVER_REVERSE`, rejects explicit `-r` in that mode, otherwise returns a default file URL or a `client.Config` built from the remote option. `repo_for_url()` dispatches `file` to `LocalRepo` and `ssh`/`bup`/`bup-rev` to `RemoteRepo`. `parse_repo_url_arg()` parses a bytes URL/path, rejects invalid schemes or malformed file authorities, and calls command misuse handlers on error.

## State And Persistence Behavior
The module does not maintain mutable state. It reads environment and may create a local repository when `repo_for_url(..., create=True)` is requested.

## Dependencies And Integration Points
It depends on `client.Config`, config URL parsing, `URL`, `LocalRepo`, `RemoteRepo`, and `path.defaultrepo()`. Command modules use it to resolve source/destination repositories for save, get, ls, and remote operations.

## Risks And Edge Cases
Reverse mode and explicit remote are mutually exclusive. `repo_location_url()` only accepts `URL` and `client.Config`. File URLs with authority are rejected to avoid ambiguity with extra slashes. Public scheme validation prevents accidental internal schemes from user-facing CLI arguments.

## Test Signals
`test/int/test_repo.py`, remote command tests, `test/ext/test-on`, `test/ext/test-ls-remote`, and get/save CLI tests cover remote option parsing, reverse mode, URL validation, and local/remote construction.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/repo/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/repo/base.py -->
# sources/sync-backup/bup/lib/bup/repo/base.py

## Purpose
This module defines shared repository configuration derivation and the abstract protocol expected of local and remote repository backends.

## Important APIs, Types, And Functions
Important pieces are `_make_base()` and `RepoProtocol`. `_make_base()` returns a frozen dataclass with compression level, max pack size, and max pack objects. `RepoProtocol` lists methods for reading, resolving, writing, refs, indexes, config, and object existence.

## Control Flow
`_make_base()` consults repository config for `pack.compression`, then `core.compression`, then `pack.packSizeLimit` when explicit values are absent. `RepoProtocol` methods are decorated with `helpers.notimplemented`, making accidental use of the base class fail clearly with the class and method name.

## State And Persistence Behavior
There is no persistent state. The generated base config object is immutable and stored by concrete repos such as `LocalRepo`.

## Dependencies And Integration Points
It depends on `compat.dataclass` and `helpers.notimplemented`. `repo/local.py` and remote repository implementations use the protocol to present a common interface to VFS, protocol server, save, get, and ls code.

## Risks And Edge Cases
This is an informal protocol rather than a strict typing interface, so compatibility depends on concrete classes matching semantics, especially iterator consumption requirements for `cat()` and write lifecycle for `finish_writing()`/`abort_writing()`. Config key spelling must match Git config access (`pack.packSizeLimit`).

## Test Signals
Repository behavior is tested through `test/int/test_repo.py`, VFS tests, protocol tests, local/remote command integration, and save/get flows that exercise the shared interface.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/repo/base.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/repo/local.py -->
# sources/sync-backup/bup/lib/bup/repo/local.py

## Purpose
This module implements the local repository backend for `RepoProtocol`, adapting `git.py` pack/ref/config/object helpers and `vfs` operations into the common repo interface.

## Important APIs, Types, And Functions
The central type is `LocalRepo`. Important methods include `create()`, `config_get()`, `list_indexes()`, `read_ref()`, `update_ref()`, `cat()`, `join()`, `resolve()`, `refs()`, `send_index()`, `rev_list_raw()`, `write_commit()`, `write_tree()`, `write_data()`, `just_write()`, `exists()`, `finish_writing()`, and `abort_writing()`.

## Control Flow
Construction resolves the repo path, builds base pack settings from config, creates a cached `CatPipe`, binds `rev_list`, and determines deduplication/run-midx behavior based on server mode, explicit `allow_duplicates`, `run_midx`, `bup.server.deduplicate-writes`, and `bup-dumb-server`. Writes lazily create a `PackWriter` over a `LocalPackStore`. Ref updates first finish pending writes. `send_index()` opens a requested idx and streams its mmap. `rev_list_raw()` runs Git and yields stdout chunks.

## State And Persistence Behavior
Instance state includes `repo_dir`, `_base`, `_packwriter`, `_cp`, `run_midx`, `_deduplicate_writes`, and close status. Persistent mutations are delegated to `git.init_repo()`, pack writer close/abort, and `git.update_ref()`. `close()` finishes pending writes, while `abort_writing()` aborts and removes tentative pack data.

## Dependencies And Integration Points
It depends on `git`, `vfs`, `LocalPackStore`, `PackWriter`, config errors, and process cleanup. It is the local backend used by `repo.__init__`, protocol server, VFS, save/get/ls commands, and tests.

## Risks And Edge Cases
Server deduplication config can conflict with constructor `allow_duplicates` and raises `ValueError`. Presence of `bup-dumb-server` forces deduplication off unless config disagrees, which raises `ConfigError`. `cat()` uses a shared `CatPipe`, so callers must consume data iterators before other repo operations. `abort_writing()` does not set `_packwriter` to `None` after abort, so callers should avoid reuse patterns that assume it does.

## Test Signals
`test/int/test_repo.py`, `test/int/test_vfs.py`, `test/int/test_git.py`, protocol tests, `test/ext/test-ls-remote`, `test/ext/test-on`, save/get tests, and pack-size/compression tests exercise local repo creation, config, object writing, refs, cat/join, VFS resolution, and server behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/repo/local.py -->
