# subset-b-009102 Research

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/archiver/serve_cmd.py -->
## sources/sync-backup/borg/src/borg/archiver/serve_cmd.py

Purpose: defines `ServeMixIn`, the CLI implementation for `borg serve`. It supports two transport/server modes: legacy Borg 1.x RPC serving through `RepositoryServer(...).serve()`, and current repository serving through `borgstore.server.rest.serve(..., stdio=True)` for `rest://` repositories.

Important APIs: `do_serve(args)` dispatches on `args.rest`; `do_serve_rest(args)` validates `--backend`, resolves permission mode from `--permissions` or `BORG_REPO_PERMISSIONS`, converts it through `repository.borg_permissions`, and launches the REST server; `check_rest_restrictions(backend, restrict_to_paths, restrict_to_repositories)` enforces path allowlists for `FILE:` backends; `build_parser_serve(...)` installs the subcommand and options.

Control flow and state: the legacy branch intentionally does not forward `args.permissions`, because Borg 1.x repositories have no permission system. REST mode requires a `FILE:<path>` backend and runs over stdio; it does not persist state itself, but it gates access before repository/server code takes over.

Dependencies and integration: integrates with `legacy.remote.RepositoryServer`, `borgstore.server.rest`, repository permission parsing, `PathNotAllowed`, and Borg's custom `ArgumentParser`. The restriction logic normalizes paths with `expanduser` and `realpath`, then compares trailing-slash-normalized prefixes or exact repository paths.

Risks: the restriction check only applies to `FILE:` backends; non-file backends with restrictions are rejected. Prefix comparison is deliberately strict for `--restrict-to-repository` and broad for `--restrict-to-path`; regressions here could create repository escape or over-blocking bugs. Permissions default to `"all"`, so deployments relying on environment configuration should verify `BORG_REPO_PERMISSIONS`.

Test signals: useful tests should cover REST without `--backend`, restriction pass/fail for subdirectories and exact repository paths, non-`FILE:` backend rejection, permission source precedence, and legacy mode not receiving REST-only permissions.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/archiver/serve_cmd.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/archiver/tag_cmd.py -->
## sources/sync-backup/borg/src/borg/archiver/tag_cmd.py

Purpose: implements `borg tag`, a write operation that edits archive tag metadata for one named archive or for archives selected by filter arguments.

Important APIs: `TagMixIn.do_tag(args, repository, manifest, cache)` is wrapped with `with_repository(cache=True, compatibility=(Manifest.Operation.WRITE,))`. It selects archive infos from `args.name` or `manifest.archives.list_considering(args)`, opens each `Archive`, applies `--set`, `--add`, and `--remove`, writes metadata through `archive.set_meta("tags", sorted_tags)`, updates the manifest archive index if the archive ID changed, and prints old/new short IDs. `build_parser_tag(...)` defines validators for archive names and tags plus common archive filters.

Control flow and state: tag mutation changes archive metadata, which changes the archive ID. The code deletes the old manifest archive entry when `old_id != archive.id`. `--set` has protective handling for special tags beginning with `@`: existing special tags are retained unless the user includes them in the `--set` list, preventing accidental removal of tags such as `@PROT`.

Dependencies and integration: uses `Archive`, `Manifest`, archive filter helpers, `bin_to_hex`, `archivename_validator`, and `tag_validator`. The command participates in repository compatibility checks through the decorator.

Risks: the `--set` special-tag guard silently skips assignment when it would clobber existing special tags, then still applies add/remove operations. Tests and UI should make this behavior clear. Because tags live in archive metadata, interrupted writes need manifest/archive persistence code to remain atomic.

Test signals: cover setting regular tags, adding/removing tags, preserving `@` tags on unsafe `--set`, allowing `--set` when existing special tags are included, filter-selected multi-archive tagging, and manifest deletion of old archive IDs after metadata rewrite.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/archiver/tag_cmd.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/archiver/tar_cmds.py -->
## sources/sync-backup/borg/src/borg/archiver/tar_cmds.py

Purpose: provides `borg export-tar` and `borg import-tar`, streaming conversion between Borg archives and tar streams, including external compression filters and Borg/PAX/GNU metadata variants.

Important APIs: `get_tar_filter(fname, decompress)` maps tar filename suffixes to compressor/decompressor commands. `TarMixIn.do_export_tar(...)` opens the output, chooses an external filter, and calls `_export_tar`. `_export_tar(...)` builds match/filter functions, streams archive items into `tarfile.open(..., mode="w|")`, tracks hard links with `HardLinkManager`, emits progress, converts Borg items to `TarInfo`, and writes PAX headers for timestamps, xattrs, ACLs, and optional `BORG.item.meta`. `do_import_tar(...)` and `_import_tar(...)` create a new archive from `tarfile.open(..., mode="r|")`, dispatch each member to `TarfileObjectProcessors`, update stats, and save the archive.

Control flow and state: export iterates archive metadata and fetches file content chunks lazily through `archive.pipeline.fetch_many(..., ro_type=ROBJ_FILE_STREAM)` wrapped by `ChunkIteratorFileWrapper`. Progress mode first sums item sizes, creating a second metadata pass. Import creates an `Archive(create=True)` and `ChunksProcessor`; every tar member becomes a Borg item or warning, then `archive.save(comment, timestamp)` persists the archive and manifest side effects via normal archive code.

Dependencies and integration: depends on Python `tarfile`, Borg archive/chunk processors, pattern matching, `create_filter_process`, `dash_open`, msgpack, JSON/stat logging helpers, and constants such as `SCHILY_XATTR` and `ROBJ_FILE_STREAM`. It sets `tarfile.TarFile.extraction_filter` to `fully_trusted_filter` on Python versions that warn when the filter is unset.

Risks: export mutates `item.path` after `strip_components`, so code must avoid reusing the same item object with the original path. `BORG.item.meta` serializes all item metadata into PAX headers and may expose Borg-specific metadata. External filters are shell-command-like strings handled by helper code, so validation and error propagation live outside this file. Import trusts tar metadata and intentionally lacks exclude handling; hostile tar streams depend on `TarfileObjectProcessors` and tarfile streaming behavior for safety.

Test signals: cover suffix auto-filter choices, stdout/stdin `-`, export of regular files, dirs, symlinks, hard links, devices/FIFOs, unsupported file types, PAX/BORG metadata preservation, `--strip-components`, unmatched include warnings, import of concatenated tar with `--ignore-zeros`, stats/JSON output, and external filter failure behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/archiver/tar_cmds.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/archiver/transfer_cmd.py -->
## sources/sync-backup/borg/src/borg/archiver/transfer_cmd.py

Purpose: implements archive transfer from another repository into the current repository, optionally upgrading Borg 1.x data, recompressing file chunks, or rechunking with new chunker parameters.

Important APIs: `transfer_chunks(...)` copies or rechunks chunk lists and returns `(chunks, transfer_size, present_size)`. Direct mode checks the destination cache, fetches missing chunks from the source, handles missing source chunks by preserving `ChunkListEntry`, and either preserves compressed payloads (`recompress="never"`) or parses/recompresses (`"always"`). Rechunk mode streams source chunks through `DownloadPipeline`, wraps them in `ChunkIteratorFileWrapper`, chunks via `get_chunker`, hashes with `cached_hash`, and writes new chunks through `cache.add_chunk`. `TransferMixIn.do_transfer(...)` validates key/chunker compatibility, selects archives, validates names/comments, selects an upgrader, skips already-present archives, transfers each item, upgrades metadata, and saves the new archive.

Control flow and state: the command is decorated with `with_other_repository(...READ...)` and `with_repository(...WRITE..., cache=True)`. It writes destination chunks through cache/repository APIs, updates archive stats, creates destination archives only when not in dry-run mode, and uses name/timestamp or name/id checks to avoid duplicate transfers. Borg 1.x checkpoint part files are skipped.

Dependencies and integration: integrates source and destination manifests, `Archive`, `DownloadPipeline`, cache chunk index behavior, `crypto.key.uses_same_id_hash`, `uses_same_chunker_secret`, legacy repository exceptions, upgrade modules, validators, and archive filter definitions.

Risks: without rechunking, the source and destination must use compatible ID hashing and the same chunker secret; the command raises early because otherwise deduplication or chunk IDs would be invalid. Missing chunks in the source are intentionally represented rather than replaced with zero data, which preserves metadata but leaves later reads dependent on repair/reappearance behavior. The dry-run rechunk path estimates size without populating chunk entries, so it should not be treated as a full validation of write behavior.

Test signals: exercise same-key transfers, incompatible key errors, rechunk transfers across ID-hash changes, recompress never/always, Borg 1.x upgrader requirements, invalid archive names/comments, duplicate archive skipping, missing source chunk preservation, dry-run output, and filtering subsets of archives.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/archiver/transfer_cmd.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/archiver/undelete_cmd.py -->
## sources/sync-backup/borg/src/borg/archiver/undelete_cmd.py

Purpose: implements `borg undelete`, restoring soft-deleted archive entries in the manifest before compaction permanently frees their objects.

Important APIs: `UnDeleteMixIn.do_undelete(args, repository)` loads the manifest with delete compatibility, selects one deleted archive by name or a filtered list of deleted archives, requires an explicit archive match when undeleting all, calls `manifest.archives.undelete_by_id(id)`, optionally logs each archive, writes the manifest if anything changed, and reports done/aborted/dry-run. `build_parser_undelete(...)` adds `--dry-run`, `--list`, archive filters, and optional archive name.

Control flow and state: the command uses `with_repository(manifest=False)` so it can explicitly call `Manifest.load(repository, (Manifest.Operation.DELETE,))`. In non-dry-run mode, successful undeletes are persisted by `manifest.write()`. It changes manifest archive deletion state only; chunk/object reclamation is governed by compaction elsewhere.

Dependencies and integration: uses archive formatting, `CommandError`, deleted-aware manifest archive selection, logging category `borg.output.list`, and common archive filter parser helpers.

Risks: accidentally undeleting every deleted archive is guarded by requiring `-a 'sh:*'` or another selector when no name/range/filter is given. If compaction has already removed data, undelete cannot reconstruct it; this file only exposes the manifest operation.

Test signals: cover name-based undelete, filter-based undelete, dry-run not writing, list messages, explicit-all safety error, missing archive warning path, and no-op behavior when no deleted archives match.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/archiver/undelete_cmd.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/archiver/version_cmd.py -->
## sources/sync-backup/borg/src/borg/archiver/version_cmd.py

Purpose: implements `borg version`, printing client and server versions in Borg's simplified negotiated version format.

Important APIs: `VersionMixIn.do_version(args)` parses `borg.__version__`, then either uses the client version as the server version for current repository access or opens `LegacyRemoteRepository(..., lock=False)` when `args.location.proto == "ssh"` and `--from-borg1` is active. It prints `client / server` through `format_version`. `build_parser_version(...)` defines the subcommand and explanatory epilog.

Control flow and state: this command is read-only and normally performs no repository I/O for current repositories. The only remote query path is legacy SSH Borg 1.x, where a remote repository object exposes `server_version`.

Dependencies and integration: integrates with `borg.version.parse_version`, `format_version`, `legacy.remote.LegacyRemoteRepository`, the shared parser, and the location/v1 flags supplied by top-level argument parsing.

Risks: output intentionally loses precision because it uses the version tuple format, while `borg --version` can show more detail. Legacy remote behavior depends on `--from-borg1`; without it, the command reports the local client version for both sides.

Test signals: verify local/current output, legacy SSH remote server query, no lock acquisition for version, and formatting behavior for prerelease/local version strings.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/archiver/version_cmd.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/cache.py -->
## sources/sync-backup/borg/src/borg/cache.py

Purpose: implements Borg's client-side cache facade, combining a files cache for unchanged-file detection with repository-stored chunk index cache fragments for deduplication and efficient object lookup.

Important APIs and types: `files_cache_name()` hashes archive/series names or honors `BORG_FILES_CACHE_SUFFIX`; `CacheConfig` loads/saves cache config and integrity metadata; `Cache.__new__` returns `AdHocWithFilesCache`; `FilesCacheMixin` reads/builds/writes file metadata entries, compresses entries by replacing chunk IDs with `ChunkIndex` indexes, checks `file_known_and_unchanged`, and memorizes files; chunk-index helpers list/delete/read/write/build `cache/chunks.<hash>` objects; `ChunksMixin` exposes `chunks`, `seen_chunk`, `reuse_chunk`, `add_chunk`, lock refresh, and periodic chunk-index cache writes; `AdHocWithFilesCache` ties manifest, repository, key, security manager, config, and mixins together.

Control flow and state: cache state lives in the local cache directory (`config`, `README`, files cache) and in repository cache objects (`cache/chunks.*`). Files cache load first tries local `IntegrityCheckedFile`, then can rebuild from the newest archive in the same series unless disabled or denied. Writes discard entries that are too new relative to backup start/newest ctime/mtime to avoid races, and age out entries by `BORG_FILES_CACHE_TTL`. Chunk cache writes content-hashed serialized `ChunkIndex` fragments and clears `F_NEW` flags only after repository storage succeeds.

Dependencies and integration: depends on `ChunkIndex`, `ChunkIndexEntry`, `ChunkListEntry`, `IntegrityCheckedFile`, `SecurityManager`, `Manifest`, `Repository`, `repo_lister`, `SaveFile`, borgstore permission errors, msgpack timestamp helpers, and repository lock refresh via `repository.info()`.

Risks: cold chunk-index rebuild has an explicit N=1 storage assumption; for multi-object packs it needs cached pack location data or range loads may be wrong. File-cache correctness depends on chosen cache mode (`d`, `c`, `m`, `s`, `i`, `r`) and timestamp granularity handling. Integrity data can be invalidated by older Borg versions, causing cache rebuild. `Cache.destroy` removes cache directories after deleting config first and must not run on arbitrary paths.

Test signals: cover cache config create/load/save/version errors, integrity metadata mismatch, files cache read corruption fallback, rebuild from previous archive, race and TTL discard, cache-mode comparisons, missing chunks referenced by files cache, chunk cache hash validation, incremental chunk-cache writes, delete cache invalidation, lock refresh during unchanged-file reuse, and compatibility feature wipe behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/cache.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/chunkers/__init__.py -->
## sources/sync-backup/borg/src/borg/chunkers/__init__.py

Purpose: exposes chunker implementations and centralizes chunker factory selection for Borg content chunking.

Important APIs: `get_chunker(algo, *params, **kw)` accepts algorithm name, algorithm parameters, optional `key`, and `sparse`. It derives a 32-bit seed from `key.chunk_seed` for `buzhash`, derives a 32-byte `buzhash64` key from `key.derive_key(..., from_id_key=True)`, instantiates `Chunker`, `ChunkerBuzHash64`, `ChunkerFixed`, or `ChunkerFailing`, and raises `TypeError` for unsupported algorithms.

Control flow and state: no persistent state. The factory translates key material into deterministic chunker seeds so related repositories can preserve chunk boundaries and deduplication behavior.

Dependencies and integration: re-exports reader symbols, imports C/extension-backed buzhash chunkers plus Python fixed/failing chunkers, and depends on key objects implementing `chunk_seed` and `derive_key`.

Risks: changing derivation domains, seed behavior, or default sparse propagation would alter chunk boundaries and deduplication. Unsupported algorithm errors surface wherever `ChunkerParams` values reach this factory.

Test signals: instantiate every algorithm, verify keyless defaults, verify keyed `buzhash64` derivation is called with the documented domain, pass sparse to supported chunkers, and assert unsupported algorithms fail clearly.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/chunkers/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/chunkers/failing.py -->
## sources/sync-backup/borg/src/borg/chunkers/failing.py

Purpose: provides `ChunkerFailing`, a deterministic test chunker that can simulate read successes and I/O errors by block position.

Important APIs: `ChunkerFailing(block_size, map)` validates a map of `R`/`E` behavior characters, tracks block count, and exposes `chunking_time` for caller compatibility. `chunkify(fd=None, fh=-1)` reads from an OS file handle or Python file object, emits `Chunk(data, size=got, allocation=CH_DATA)` for `R`, raises `OSError(errno.EIO, "simulated I/O error", fname)` for `E`, and repeats the last map behavior beyond map length.

Control flow and state: state is per chunker instance through `self.count`. It stops when a read returns fewer bytes than `block_size`, treating that as EOF after yielding any final successful partial chunk.

Dependencies and integration: imports `Chunk` from `.reader` and `CH_DATA` from constants. Used by `get_chunker("fail", ...)`, mainly for tests of error handling in archive creation/chunk processing paths.

Risks: because the final map character repeats indefinitely, short maps can simulate persistent failures or successes. It does not update timing, hash, or sparse metadata beyond `CH_DATA`, so it should not be used as production logic.

Test signals: validate map parsing, file object and file descriptor paths, partial final reads, repeated final behavior, emitted chunk metadata, and exception filename inclusion for file-object reads.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/chunkers/failing.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/chunkers/fixed.py -->
## sources/sync-backup/borg/src/borg/chunkers/fixed.py

Purpose: implements `ChunkerFixed`, a fixed-size chunker for data with stable offsets such as disk images, block devices, or simple record-oriented database files.

Important APIs: `ChunkerFixed(block_size, header_size=0, sparse=False)` configures block size, optional first header chunk size, sparse/file-map reading, and `chunking_time`. `chunkify(fd=None, fh=-1, fmap=None)` creates a `FileReader`, optionally yields a header chunk read with `header_size`, then repeatedly reads up to `block_size` and yields chunks until a zero-size chunk indicates EOF.

Control flow and state: the chunker stores its `FileReader` on `self.reader` and accumulates monotonic-time spent in reads. It asserts each yielded non-header chunk is no larger than `block_size`; the last chunk in a data or hole range may be smaller.

Dependencies and integration: depends on `.reader.FileReader` for sparse and file-map behavior. Constructed by `get_chunker("fixed", ...)` and used anywhere fixed chunker params are selected, including transfer rechunking or create paths.

Risks: correctness rests on `FileReader` returning chunks with `meta["size"]`; a malformed reader result can trip assertions. Fixed chunking intentionally gives no content-defined boundary shifts, so insertions near the beginning can reduce deduplication versus buzhash.

Test signals: cover no-header and header modes, file descriptor/file object inputs, sparse and fmap reads, empty files, partial final chunks, timing accumulation, and assertion behavior for overlarge reader chunks.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/chunkers/fixed.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/cockpit/__init__.py -->
## sources/sync-backup/borg/src/borg/cockpit/__init__.py

Purpose: marks the `borg.cockpit` package and documents that it contains the Borg Cockpit Textual terminal UI.

Important APIs: no runtime APIs, imports, exports, or state are defined. The module docstring describes the package-level role.

Control flow and state: no control flow or persistence. Importing the package only executes the docstring.

Dependencies and integration: package siblings (`app.py`, `runner.py`, `theme.py`, `translator.py`, `widgets.py`) provide the actual UI. This file enables normal package import semantics.

Risks: minimal. If public exports are later expected from `borg.cockpit`, they are currently absent.

Test signals: import smoke tests are sufficient; functional coverage belongs to the app, runner, and widgets modules.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/cockpit/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/cockpit/app.py -->
## sources/sync-backup/borg/src/borg/cockpit/app.py

Purpose: defines the main Textual application for Borg Cockpit, a TUI that runs a Borg command and displays live output/status.

Important APIs: `BorgCockpitApp(App)` sets `TITLE`, `CSS_PATH`, and key bindings; `compose()` builds Header, LogoPanel, StatusPanel, StandardLog, and Footer; `get_theme_variable_defaults()` supplies theme variables; `on_load()` registers/selects the Borg theme; `on_mount()` animates logo/slogan and schedules `start_runner`; `start_runner()` initializes counters/timers and starts `BorgRunner`; `compute_speed()` updates line-rate and elapsed time; `on_unmount()` and `action_quit()` stop resources; `action_toggle_translator()` toggles translations and refreshes labels; `handle_log_event()` routes runner events into widgets.

Control flow and state: app state includes `total_lines_processed`, `last_lines_processed`, `speed_timer`, `start_time`, `process_running`, `runner`, and `runner_task`. The runner command comes from `self.borg_args` or defaults to `["--version"]`. Process completion sets status `rc`; quitting waits for runner shutdown and fades UI elements before exiting.

Dependencies and integration: depends on Textual `App`, widgets, containers, theme, local widgets, `BorgRunner`, and global translator state. It executes Borg indirectly through `runner.py`.

Risks: `action_quit` awaits `runner_task`; if stream processing hangs, exit can hang. `handle_log_event` assumes widgets are mounted and queryable. Speed is based on log lines rather than files, so the unit label is approximate. The app passes arbitrary `borg_args` into the runner, so caller-side argument construction matters.

Test signals: Textual app tests should cover composition IDs, theme registration, runner startup default/custom args, stream-line event handling, process-finished status updates, translator toggle refresh, timer updates, and graceful stop on unmount/quit.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/cockpit/app.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/cockpit/runner.py -->
## sources/sync-backup/borg/src/borg/cockpit/runner.py

Purpose: wraps asynchronous execution of a Borg subprocess and reports decoded stdout/stderr lines plus final return code to a callback.

Important APIs: `BorgRunner(command, log_callback)` stores the command list and callback. `start()` prevents double starts, builds either `[sys.executable] + command` for frozen binaries or `[sys.executable, "-m", "borg"] + command` for source execution, sets `PYTHONUNBUFFERED=1`, starts the subprocess with stdout/stderr pipes, reads both streams concurrently, emits `{"type": "stream_line", "stream": ..., "line": ...}`, waits for the process, then emits `{"type": "process_finished", "rc": rc}`. Exceptions produce `rc=-1`. `stop()` terminates a running process and waits.

Control flow and state: `self.process` is non-`None` while active and reset in `finally`. The nested `read_stream` coroutine runs until EOF. `stop()` only terminates processes with no return code.

Dependencies and integration: uses `asyncio.create_subprocess_exec`, Python runtime path, environment copy, and a UI callback supplied by `BorgCockpitApp`.

Risks: subprocess termination has no timeout or kill escalation after `terminate()`. Very long lines are read as complete lines, so memory use depends on subprocess output behavior. All stderr/stdout lines are treated equally by the app except for the `stream` field.

Test signals: cover source and frozen command construction, callback events for stdout/stderr and return code, exception path with `rc=-1`, double-start warning/no-op, and stop behavior for live and already-dead processes.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/cockpit/runner.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/cockpit/theme.py -->
## sources/sync-backup/borg/src/borg/cockpit/theme.py

Purpose: defines the Textual theme object used by Borg Cockpit.

Important APIs: module-level `theme = Theme(...)` names the theme `"borg"` and sets primary, secondary, error, warning, success, accent, foreground, background, surface, panel, dark mode, and custom variables for cursor, selection, starfield, pulsar, and logo colors.

Control flow and state: static module-level object creation only. No persistence.

Dependencies and integration: consumed by `BorgCockpitApp.on_load`, widgets that read `theme.variables`, and Textual's theme system.

Risks: color variables are referenced by string keys in widgets; renaming/removing variables can break rendering. The high-contrast green-on-black palette is deliberate but may need accessibility review for broader use.

Test signals: import smoke test, app theme registration, and widget rendering tests for required variable keys.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/cockpit/theme.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/cockpit/translator.py -->
## sources/sync-backup/borg/src/borg/cockpit/translator.py

Purpose: provides a small mutable translation layer that can replace selected English UI/log strings with Borg-themed wording.

Important APIs: `BORG_DICTIONARY` maps exact or substring English text to replacement text. `UniversalTranslator(enabled=True)` stores a boolean flag, `toggle()` flips it, and `translate(message)` returns the original message when disabled, exact dictionary match when present, otherwise first substring replacement. Module globals `TRANSLATOR = UniversalTranslator(enabled=False)` and `T = TRANSLATOR.translate` are imported by widgets.

Control flow and state: translation state is global and mutable through `TRANSLATOR.enabled`. The app toggles it and asks widgets to refresh displayed labels.

Dependencies and integration: used by `widgets.py` for labels/log titles and by `app.py` for toggle behavior. No external dependencies.

Risks: substring replacement order follows dictionary insertion order and can change output when keys overlap. `T` is a bound method to the global instance; replacing `TRANSLATOR` would not update existing `T` imports. Translation is not localization-grade and only handles known strings.

Test signals: cover disabled passthrough, exact replacement, substring replacement, toggle behavior, global `T`, and label refresh behavior in widgets after toggle.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/cockpit/translator.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/cockpit/widgets.py -->
## sources/sync-backup/borg/src/borg/cockpit/widgets.py

Purpose: defines Textual widgets for Borg Cockpit: status counters, live log display, logo/starfield visual panel, pulsar/slogan/logo art, and speed sparkline.

Important APIs: `StatusPanel` uses reactive counters for elapsed time, file status counts, and return code; watcher methods update child labels and classes. `StandardLog.add_line(line)` escapes Rich markup, parses Borg list-status prefixes, updates `StatusPanel` counters, and colorizes output. `Starfield`, `Pulsar`, `Slogan`, and `Logo` render decorative UI. `LogoPanel` composes and positions those elements on resize while avoiding overlap. `SpeedSparkline` keeps fixed history and renders a four-line character chart.

Control flow and state: `StatusPanel` holds `speed_history`; watchers react to state changes. `StandardLog` mutates the app-level status panel based on stream lines. `Starfield` and `LogoPanel` use per-instance random seeds for stable-but-random placement. `Pulsar` and `Slogan` use intervals to toggle CSS classes. `SpeedSparkline.refresh_chart()` normalizes visible history to 0..32 levels.

Dependencies and integration: depends on Textual widgets/containers/reactive fields, Rich `escape`, Borg `classify_ec`, the cockpit theme variables, and global translator state. It expects parent app queries for `#status` and `#standard-log-content`.

Risks: parsing status from log lines is heuristic and marked TODO; output format changes can miscount files. `random.seed(...)` changes global RNG state during rendering/resize, which could affect other UI code. Non-ASCII art/block characters are intentional but may render poorly in some terminals. `max_lines=None` may grow memory for long-running commands.

Test signals: cover each reactive watcher, return-code class mapping, elapsed formatting and translated stardate mode, log parsing for all status prefixes, Rich markup escaping, title/slogan translation refresh, resize positioning without overlap on typical sizes, and sparkline output for empty/constant/high variance data.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/cockpit/widgets.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/conftest.py -->
## sources/sync-backup/borg/src/borg/conftest.py

Purpose: configures Borg's pytest environment, isolates test state, cleans stale FUSE mountpoints, reports platform capability headers, and provides reusable archiver fixtures.

Important APIs: `pytest_sessionstart`/`pytest_sessionfinish` sweep stale `mountpoint` directories under pytest temp roots. `clean_env` autouse fixture removes most `BORG_*` environment variables, sets isolated `BORG_BASE_DIR`, weakens KDF for tests, and configures flat storage. `set_env_variables` sets confirmation/passphrase/selftest values. `backup_files` creates a small fixture tree. `ArchiverSetup` records paths and execution kind. `archiver`, `remote_archiver`, and `binary_archiver` fixtures create local/rest/binary test setups with keys/cache/input/output paths.

Control flow and state: test sessions perform best-effort FUSE cleanup before and after runs in the main process only. Each test gets a temporary base directory and archiver workspace, with environment variables pointing to isolated keys/cache directories. Cleanup handles BSD flags when removing temp trees.

Dependencies and integration: imports Borg logging setup early, `Archiver`, testsuite capability probes, `BORG_EXES`, platform fakeroot detection, and `helpers.umount`. Pytest assertion rewrite is registered for `borg.testsuite`.

Risks: autouse environment wiping can hide bugs dependent on user environment but is necessary for reproducibility. FUSE cleanup walks temp directories and best-effort unmounts paths named `mountpoint`; incorrect detection could miss or attempt stale resources. `BORG_TESTONLY_WEAKEN_KDF=1` must never leak into production contexts.

Test signals: this file is test infrastructure; validate by running representative local, remote, and binary archiver tests, plus interrupted FUSE cleanup scenarios and xdist session behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/conftest.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/constants.py -->
## sources/sync-backup/borg/src/borg/constants.py

Purpose: centralizes Borg protocol, repository, archive, chunking, cache, tar, tag, exit-code, and crypto constants used across the codebase.

Important APIs/types: defines item/archive key allowlists (`ITEM_KEYS`, `ARCHIVE_KEYS`) and required keys, repository object type labels (`ROBJ_*`), size and segment limits, listing limits, chunker names and default params, sparse chunk allocation codes, files-cache modes and timestamp tolerances, tar PAX header names, special tags, exit code bands, timestamp formats, KDF parameters (`PBKDF2_ITERATIONS`, `ARGON2_ARGS`, `ARGON2_SALT_BYTES`), key algorithms, `KeyBlobStorage`, `KeyType`, cache/repository tag names, and README content strings.

Control flow and state: no runtime control flow beyond class/constant definition. These values shape serialization, compatibility, CLI defaults, and security behavior elsewhere.

Dependencies and integration: imported broadly, often with `from ..constants import *`. `KeyBlobStorage` and `KeyType` are used by crypto key selection/storage; chunk constants feed arg parsing and chunker factories; `ROBJ_*` labels are used by repo object formatting/parsing; tar constants are consumed by tar export/import.

Risks: many values are part of on-disk or wire compatibility. Changes to object type labels, key type bytes, item/archive key sets, chunker defaults, or size limits can make repositories unreadable or alter deduplication. The comment on `ITEM_KEYS` and `ARCHIVE_KEYS` warns robust unpacking/rebuild logic requires completeness.

Test signals: broad regression suite should cover manifest/archive unpacking, repository object parsing, chunker default behavior, modern/legacy exit-code classification, key type dispatch, tar metadata, and cache behavior when constants are changed.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/constants.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/crypto/__init__.py -->
## sources/sync-backup/borg/src/borg/crypto/__init__.py

Purpose: empty package initializer for `borg.crypto`.

Important APIs: no symbols, imports, side effects, or state are defined in this file.

Control flow and state: none. Importing `borg.crypto` only initializes the package namespace.

Dependencies and integration: crypto functionality is implemented in sibling modules such as `key.py`, `keymanager.py`, `file_integrity.py`, and low-level crypto modules.

Risks: minimal. If consumers expect package-level re-exports, they are not provided here.

Test signals: import smoke coverage is sufficient; substantive crypto tests target sibling modules.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/crypto/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/crypto/file_integrity.py -->
## sources/sync-backup/borg/src/borg/crypto/file_integrity.py

Purpose: provides wrappers that hash file contents and contextual part names while reading/writing, enabling integrity checks for local cache/index-like files and detached `.integrity` sidecars.

Important APIs: `FileLikeWrapper` delegates file operations. `FileHashingWrapper` updates a hash during `read`/`write`, hashes file length on clean exit unless `pure_hash`, and exposes `hexdigest`, `update`, and `hash_length`. `SHA256FileHashingWrapper` selects SHA-256. `IntegrityCheckedFile` wraps a path or override fd, loads optional integrity JSON, hashes the basename as context, verifies or stores digests for named parts, and exposes `integrity_data` after writes. `DetachedIntegrityCheckedFile` reads/writes `<path>.integrity` files.

Control flow and state: reads parse integrity data when supplied, then each `hash_part(partname, is_final)` includes part name and current length in the digest. On clean context exit, the `"final"` part is checked/stored. Write mode records digests in memory and serializes JSON; read mode raises `FileIntegrityError` on parse or digest mismatch.

Dependencies and integration: used by cache code for files-cache integrity. Depends on `hashlib`, JSON, `hmac.compare_digest`, `Path`, Borg `IntegrityError`, and logging.

Risks: seeking/skipping data is explicitly unsafe because skipped bytes are not hashed. Integrity context includes basename but not directory, allowing supported moves while detecting filename-context changes. Unknown algorithms warn and skip verification rather than failing; malformed integrity data raises.

Test signals: cover read/write round trips, basename hashing, final digest mismatch, part digest mismatch, malformed JSON, unknown algorithm handling, detached sidecar behavior, override fd handling, and seek-to-end length hashing.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/crypto/file_integrity.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/crypto/key.py -->
## sources/sync-backup/borg/src/borg/crypto/key.py

Purpose: implements Borg key identification, keyfile/repokey storage, passphrase-protected key blobs, plaintext/authenticated/encrypted key classes, legacy compatibility dispatch, and modern AEAD crypto suites.

Important APIs and types: keyfile helpers (`keyfile_name_for`, `is_keyfile`, `keyfile_format`, `keyfile_parse`); errors for unsupported payload/manifest/key formats; `KEY_LOCATIONS`, `key_creator`, `key_argument_names`, `identify_key`, `key_factory`, `uses_same_chunker_secret`, `uses_same_id_hash`; `KeyBase` for ID assertion, metadata packing/unpacking, and derivation; `PlaintextKey`; `AESKeyBase` for legacy AES-CTR style payloads; `FlexiKey` for passphrase prompting, key discovery, multiple-key iteration, argon2/chacha key-blob encryption, save/remove/list/add/remove-key operations; `AuthenticatedKeyBase`; modern `AEADKeyBase` and concrete AES-OCB/ChaCha20-Poly1305/BLAKE3 variants; `AVAILABLE_KEY_TYPES`.

Control flow and state: manifest data's first byte identifies the crypto suite, not key storage for modern flexible keys. FlexiKey first searches `BORG_KEY_FILE`, keys directory, then repository key blobs, and tries a passphrase against all candidates. Key blobs are msgpacked `Key` objects encrypted in an `EncryptedKey` envelope using Argon2id-derived ChaCha20-Poly1305. Repositories may have multiple Borg keys with labels; `admin` is reserved/protected. AEAD encryption creates a fresh session ID per process/session and includes chunk ID as AAD while still asserting `id_hash(data)` after decrypt.

Dependencies and integration: depends on constants (`KeyType`, `KeyBlobStorage`, Argon2 params), low-level ciphers, blake3, argon2, passphrase helpers, secure erase, msgpack limited unpackers, repository key load/store/delete APIs, legacy key classes, `RepoObj`, `Manifest`, and item key structures.

Risks: this file is security-critical. Empty passphrases make repokey repositories logically unencrypted. `BORG_TESTONLY_WEAKEN_KDF` intentionally weakens Argon2 for tests and must remain test-only. Multiple key storage is per-key, so operations must target the loaded/victim key storage correctly. AEAD IV overflow is guarded; session key derivation domains and header layout are compatibility-sensitive. `AUTHENTICATED_NO_KEY` is an explicit workaround for lost authenticated-mode keys.

Test signals: cover keyfile parsing/mismatch, key detection by type byte, plaintext/authenticated/encrypted encrypt/decrypt, ID hash compatibility predicates, passphrase retry/env behavior, keyfile and repokey save/load/remove, multiple-key list/add/remove selectors and admin protection, key location changes, argon2 envelope corruption, AEAD AAD/id verification, legacy type dispatch, and KDF weakening only under test env.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/crypto/key.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/crypto/keymanager.py -->
## sources/sync-backup/borg/src/borg/crypto/keymanager.py

Purpose: implements high-level key export/import workflows, including normal keyfiles, QR HTML export, paper key export, and interactive paper key import.

Important APIs: `sha256_truncated(data, num)` makes short checksums. `KeyManager(repository)` identifies the repository key class from the manifest and rejects unencrypted repositories. `_list_borg_keys()` enumerates key blobs and labels without decrypting. `load_keyblob(label=None, key_id=None)` selects exactly one key for export. `store_keyblob(args)` writes imported key data to keyfile or repo storage according to `--key-location` or default. `get_keyfile_data`, `store_keyfile`, `export`, `export_qr`, `export_paperkey`, `import_keyfile`, and `import_paperkey` implement the concrete formats.

Control flow and state: `self.keyblob` holds base64 key payload text selected or imported. Export formats wrap it with `BORG_KEY <repoid>` as needed. Paper export decodes base64 to binary, emits an ID line with line count/repo ID/checksum, then numbered 18-byte hex lines with per-line checksums. Paper import loops until checksums and repo ID match, then stores the reconstructed base64 blob.

Dependencies and integration: uses `RepoObj.extract_crypted_data` and `identify_key` to determine crypto/key storage support; reuses keyfile helpers from `crypto.key`; accesses repository key APIs; uses `dash_open`, `yes`, keys dir helpers, `paperkey.html` package data, and `KEY_LOCATIONS`.

Risks: importing a valid key into the wrong repository is guarded by repo ID checks. Multiple-key repositories require an unambiguous selector for export. `store_keyblob` uses `CHPOKey` only to reuse target lookup for keyfile storage, which is a coupling to FlexiKey behavior. Paper import is interactive and must handle aborts without partial state.

Test signals: cover unencrypted repo rejection, single and multi-key selection by label/key prefix, ambiguous selector errors, keyfile export/import repo mismatch, QR export insertion, paper export checksums, paper import retry/abort paths, key-location storage choices, and corrupted key envelope visibility.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/crypto/keymanager.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/fslocking.py -->
## sources/sync-backup/borg/src/borg/fslocking.py

Purpose: implements filesystem-based locking primitives used to coordinate shared and exclusive access across Borg processes and machines.

Important APIs and types: constants `ADD`, `REMOVE`, `REMOVE2`, `SHARED`, `EXCLUSIVE`; `TimeoutTimer` handles timeout/sleep loops; lock error classes expose specific exit codes; `ExclusiveLock` uses atomic directory replacement to acquire a lock and stores ownership as a file named from platform process identity; `LockRoster` stores shared/exclusive owners in JSON and removes stale owners; `Lock` composes an exclusive filesystem lock and roster to provide shared/exclusive resource locking, upgrade/downgrade, break, and ownership migration.

Control flow and state: `ExclusiveLock.acquire()` creates a temp dir and unique owner file, attempts to replace the target lock dir, kills stale locks when possible, and loops until success or timeout. `release()` verifies ownership and removes owner/dir. `Lock.acquire(exclusive=True)` waits for all shared readers to leave while holding the exclusive lock; shared acquire updates the roster under the exclusive lock. Roster state is persisted in `<path>.roster`, while the mutex directory is `<path>.exclusive`.

Dependencies and integration: uses `platform.get_process_id()` and `platform.process_alive()` for owner identity/staleness, Borg `Error` classes, JSON, temp dirs, `Path`, errno, and logging. Intended for repository/cache/resource locking layers.

Risks: lock correctness depends on filesystem atomic rename/replace semantics and reliable process liveness across hosts. Multiple shared lockers attempting `upgrade()` can deadlock, explicitly warned in code. `break_lock()` forcibly removes roster/lock files and must be administrative. Corrupt roster JSON is treated as empty, which favors recovery but can lose lock visibility.

Test signals: cover exclusive acquire/release/reentrant by-me behavior, timeout, stale lock killing and disabled stale killing, malformed lock names, shared lock coexistence, exclusive waiting for readers, upgrade/downgrade, roster corruption handling, ownership migration, break_lock, and cross-platform Windows permission retry behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/fslocking.py -->
