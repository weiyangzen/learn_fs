# subset-b-009101 Research

Grouped source research for Borg archiver command mixins in `sources/sync-backup/borg/src/borg/archiver`. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/archiver/compact_cmd.py -->
# sources/sync-backup/borg/src/borg/archiver/compact_cmd.py

## Purpose

`compact_cmd.py` implements `borg compact`, Borg's repository garbage collection command. It scans repository objects, determines which objects are still referenced by live archives, deletes unused objects, cleans soft-deleted archive entries, refreshes the repository chunk index, and removes files-cache entries for archive series that no longer exist. The source was read as a complete 277-line file.

## Important APIs, Types, and Functions

`ArchiveGarbageCollector` owns compaction state: `repository`, `manifest`, `chunks`, `total_files`, `total_size`, `archives_count`, `stats`, and `iec`. `garbage_collect()` orchestrates the operation. `get_repository_chunks()` builds the object index either from `repo_lister()` with stored sizes for `--stats` or from `build_chunkindex_from_repo()` for the fast path. `analyze_archives()` walks all archive metadata and item chunks, marking referenced object IDs. `report_and_delete()` reports missing objects, purges soft-deleted archive entries via `manifest.archives.nuke_by_id()`, deletes unused repository objects, and logs statistics. `save_chunk_index()` writes the new full chunk index with `write_chunkindex_to_repo_cache()`. `cleanup_files_cache()` removes cache files whose generated archive-series suffix no longer maps to an existing series. `CompactMixIn.do_compact()` is the CLI entry point, and `build_parser_compact()` wires `--dry-run` and `--stats`.

## Control Flow

`do_compact()` opens the repository exclusively with delete compatibility and skips mutation when `--dry-run` is set. Normal compaction calls `garbage_collect()`, which first builds a chunk index for all objects, then analyzes every archive in timestamp order. For each archive it marks the archive metadata object, item pointer objects, item stream objects, and all content chunk IDs as used. It then reports missing referenced objects, removes soft-deleted archive directory entries, computes the unused ID set from unmarked chunk-index entries, deletes stale central chunk-index caches before any object deletion, deletes each unused repository object, writes a clean replacement chunk index, and cleans files-cache files.

## State and Persistence Behavior

The command mutates repository object storage by deleting unused objects and mutates the archives directory by permanently nuking soft-deleted archives. It persists an updated chunk index into the repository cache and deletes older chunk-index caches to avoid stale indexes after interrupted deletion. It also mutates the local cache directory under `get_cache_dir()/repository.id_str` by unlinking unused files-cache files. Missing referenced objects set Borg's global exit code to `EXIT_ERROR` but do not stop the deletion pass by themselves.

## Dependencies and Integration Points

This command integrates with `Archive` for archive metadata and item iteration, `Manifest` for archive listings and soft-deleted archive removal, `Repository`/`repo_lister()` for object enumeration and deletion, `ChunkIndex` for used/unused tracking, cache helpers for chunk-index and files-cache maintenance, and `ProgressIndicatorPercent` for progress output. It is coupled to the soft-delete lifecycle started by `delete_cmd.py` and `prune_cmd.py`, and to `repo_space_cmd.py` because compaction is the operation that actually frees storage after deletions.

## Risks and Edge Cases

The fast path trusts the cached chunk index enough to find repository object IDs; a stale or incomplete cache can make missing chunks appear. `--stats` is slower but builds from repository listings and knows object sizes. Interruptions during deletion are handled conservatively by deleting central chunk-index caches before object deletion, but an interrupted run still leaves partially compacted storage until the next rebuild. Files-cache cleanup assumes normal automatically generated cache suffixes and may not perfectly handle manually varied `BORG_FILES_CACHE_SUFFIX` values. Missing archive metadata or repository corruption can produce missing-object errors while compaction continues.

## Test Signals

Useful tests include compacting a repository after `delete`/`prune` and verifying unused objects disappear only after `compact`; comparing `--stats` and non-`--stats` behavior; interrupting deletion after chunk-index cache invalidation and verifying later create/check rebuilds safely; repositories with soft-deleted archives whose archive objects are already absent; missing referenced chunk fixtures that set an error exit; and files-cache directories containing both used and unused generated cache files.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/archiver/compact_cmd.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/archiver/completion_cmd.py -->
# sources/sync-backup/borg/src/borg/archiver/completion_cmd.py

## Purpose

`completion_cmd.py` implements `borg completion`, generating shell completion scripts through `shtab` and augmenting generated output with Borg-specific dynamic completions for bash and zsh. It supports completions for archive names and IDs, tags, sort keys, files-cache modes, compression specs, chunker parameters, timestamps, sizes, paths, and help topics. The source was read as a complete 763-line file.

## Important APIs, Types, and Functions

The major constants are `BASH_PREAMBLE_TMPL` and `ZSH_PREAMBLE_TMPL`, which embed shell functions such as `_borg_complete_archive`, `_borg_complete_tags`, `_borg_complete_sortby`, `_borg_complete_filescachemode`, `_borg_complete_compression_spec`, `_borg_complete_chunker_params`, `_borg_complete_relative_time`, `_borg_complete_timestamp`, `_borg_complete_file_size`, and `_borg_help_topics`. `_attach_completion()` recursively tags argparse actions whose `type` matches a target validator/type. `_attach_help_completion()` recursively tags help topic arguments. `CompletionMixIn.do_completion()` rebuilds the full parser, attaches custom completion metadata, formats shell preambles with `partial_format()`, and prints `parser.get_completion_script()`. `build_parser_completion()` wires the `completion SHELL` subcommand.

## Control Flow

At runtime, `do_completion()` calls `self.build_parser()` to obtain the complete command tree. It walks all nested subcommands and attaches shell completion hooks to specific action types: `archivename_validator`, `SortBySpec`, `FilesCacheMode`, `CompressionSpec`, `PathSpec`, `ChunkerParams`, `tag_validator`, `relative_time_marker_validator`, `timestamp`, and `parse_file_size`. It builds help choices from registered help topics and subcommand names, substitutes static choice lists into the selected shell preamble, asks `shtab` to emit the script, and prints it. Generated shell functions later run in the user's shell; dynamic archive and tag completion invoke `borg repo-list` with detected `--repo`/`-r` context.

## State and Persistence Behavior

The Python command itself only prints a completion script. The generated script has runtime side effects when used interactively: archive and tag completion spawn `borg repo-list`, read repository metadata, may require repository/passphrase environment configuration, and suppress stderr to avoid noisy completions. There is no persistent cache in this module.

## Dependencies and Integration Points

The module depends on `shtab`, Borg's custom argparse classes (`ArgumentParser`, `ActionSubCommands`), helper validator/type classes, `timestamp`, `partial_format()`, and `AI_HUMAN_SORT_KEYS`. It integrates with every command parser because it tags actions by type across the full parser tree. The shell preambles integrate with the `borg repo-list` output format contract, so changes to archive/tag formatting or command names can affect completions.

## Risks and Edge Cases

The embedded shell code must handle bash and zsh quoting, word splitting, `COMP_WORDBREAKS`, `--repo=value`, `--repo value`, `-r=value`, `-rVALUE`, and `-r VALUE` forms. Dynamic completions can be slow or fail silently for locked, encrypted, remote, or prompt-requiring repositories. Static completion lists for compression specs, chunker params, relative times, file sizes, and files-cache tokens can drift from parser validation. Recursive attachment matches by type identity, so wrapper validators or equivalent classes will not receive custom completions unless added explicitly.

## Test Signals

Tests should generate bash and zsh scripts and assert that custom functions are present, parser actions get the expected `complete` metadata, help choices include command names and help topics, sort/files-cache comma completions avoid duplicates and mutual exclusions, and archive/tag completions parse all repository option forms. Shell-level smoke tests should cover `aid:` prefixes, empty repositories, repository paths with spaces, stderr-suppressed failures, and both bash and zsh loading.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/archiver/completion_cmd.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/archiver/create_cmd.py -->
# sources/sync-backup/borg/src/borg/archiver/create_cmd.py

## Purpose

`create_cmd.py` implements `borg create`, the command that traverses filesystem inputs or command/stdin streams and writes a new archive. It handles include/exclude matching, filesystem recursion, special files, metadata collection, chunking, cache usage, progress/stat output, dry runs, and parser wiring for a large set of backup options. The source was read as a complete 1046-line file.

## Important APIs, Types, and Functions

`CreateMixIn.do_create()` is the entry point and contains `create_inner()`, which handles input modes and archive finalization. `_process_any()` dispatches a stat result to the correct `FilesystemObjectProcessors` method for regular files, directories, symlinks, FIFOs, devices, sockets, doors, and event ports, with retry logic around transient backup errors. `_rec_walk()` recursively descends directories, applies matchers, handles tagged directories and one-file-system restrictions, skips cache/repository inodes, filters dataless macOS files, opens directories safely with `OsOpen`, and records file status. `build_parser_create()` defines the command, including stdin metadata, external path sources, exclusion options, filesystem metadata toggles, cache mode, file-change detection, chunker/compression, archive tags, and path arguments.

## Control Flow

`do_create()` opens the repository for write, constructs a `PatternMatcher`, initializes output flags on `self`, records the start time, and creates a `Cache`, `Archive`, `MetadataCollector`, `ChunksProcessor`, and `FilesystemObjectProcessors` unless in dry-run mode. `create_inner()` first adds the local cache directory and local repository directory to `skip_inodes`. It then selects one of four input modes: run a content-producing command and store stdout as one file; read paths from a command, shell command, or stdin; process explicit paths including `-` as stdin; or recursively walk normal roots. After processing, non-dry-run saves the archive unless SIGINT was received, sets tags/comment/timestamp, merges stats, and emits text or JSON stats.

## State and Persistence Behavior

Successful non-dry-run execution writes a new archive into the repository, updates the manifest through `archive.save()`, writes file metadata and content chunks through the cache/chunker pipeline, and updates files-cache state according to `--files-cache`. Dry-run avoids archive/cache writes but still stats and walks inputs. External command modes spawn subprocesses; `--content-from-command` prevents archive creation if the command exits nonzero after piping, while plain stdin piping cannot observe the producer's exit status. Warnings are recorded for per-item backup errors, and file status counters update for processed items.

## Dependencies and Integration Points

The command integrates deeply with `Archive`, `Cache`, `FilesystemObjectProcessors`, `MetadataCollector`, `ChunksProcessor`, `PatternMatcher`, `backup_io`, `OsOpen`, `stat_update_check`, filesystem helpers (`os_stat`, `get_strip_prefix`, `slashify`, `dir_is_tagged`, platform flags), subprocess environment preparation, and JSON/stat formatting helpers. It also shares parser conventions with help text, completion support, and exclusion groups from `_common`.

## Risks and Edge Cases

Key risks include filesystem races between stat/open/read, files changing during backup, permission errors, recursive loops or duplicate roots avoided through `skip_inodes`, accidentally backing up the repository/cache, path normalization and slashdot prefix stripping, shell-command injection inherent to explicit `--paths-from-shell-command`, special-device reads when `--read-special` is enabled, dataless cloud files materializing unless filtered before open, and differing ctime semantics on Windows. `_process_any()` retries transient backup errors but intentionally does not retry permission errors.

## Test Signals

Tests should cover normal recursion, dry-run/list/filter output, `-` stdin, `--content-from-command` success and nonzero failure, `--paths-from-stdin` with custom delimiters, shell and non-shell path commands, slashdot stripping, exclude/include/tagged directory behavior, one-file-system recursion, skipping cache/repository inodes, symlink and `--read-special` handling, dataless file filtering, Windows `files_changed=ctime` fallback, retry paths for transient `BackupOSError`, file-changed warnings, JSON stats, and SIGINT avoiding archive save.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/archiver/create_cmd.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/archiver/debug_cmd.py -->
# sources/sync-backup/borg/src/borg/archiver/debug_cmd.py

## Purpose

`debug_cmd.py` implements the `borg debug` command group. These commands expose low-level repository, manifest, archive, object, key, and profiling internals for diagnostics and recovery work, and are explicitly not intended for normal use. The source was read as a complete 530-line file.

## Important APIs, Types, and Functions

`DebugMixIn` provides `do_debug_info()`, `do_debug_dump_archive_items()`, `do_debug_dump_archive()`, `do_debug_dump_manifest()`, `do_debug_dump_repo_objs()`, `do_debug_search_repo_objs()`, `do_debug_get_obj()`, `do_debug_id_hash()`, `do_debug_parse_obj()`, `do_debug_format_obj()`, `do_debug_put_obj()`, `do_debug_delete_obj()`, and `do_debug_convert_profile()`. `build_parser_debug()` constructs the nested `debug` subcommands and arguments. Important helpers include `RepoObj.parse()/format()`, `key_factory()`, `msgpack` unpackers, `prepare_dump_dict()`, `StableDict`, `hex_to_bin()`, `bin_to_hex()`, and `dash_open()`.

## Control Flow

The debug commands use different repository wrappers depending on risk and required state. Metadata dump commands open a manifest with no operation compatibility check, load archive or manifest objects, parse encrypted/compressed repository objects through `manifest.repo_objs`, and stream JSON or binary files. Repository-object dump/search commands open the repository without a manifest, bootstrap a key from the first listed object, and iterate `repo_lister()`. Object get/put/delete commands convert user-supplied hex IDs to 32-byte IDs, then directly call repository get/put/delete. Parse/format object commands convert between raw object files plus JSON metadata and Borg object bytes. The parser nests all of these under `borg debug`.

## State and Persistence Behavior

Many commands write files in the current working directory or to user-supplied paths. `put-obj` directly inserts arbitrary bytes at a repository object ID, and `delete-obj` deletes repository objects under an exclusive lock. `format-obj` produces object files but does not store them unless combined with `put-obj`. Dump/search/info/id-hash commands are read-only with respect to the repository. Because some commands open without normal manifest checks, they can operate on partially corrupted repositories but also bypass guardrails.

## Dependencies and Integration Points

This module integrates with archive metadata layout (`ROBJ_ARCHIVE_META`, `ROBJ_ARCHIVE_CHUNKIDS`, `ROBJ_ARCHIVE_STREAM`), manifest object layout, repository object encryption/compression through `RepoObj`, key creation from repository content, and platform process info. It is a diagnostic backdoor into the same objects manipulated by create, extract, compact, and check.

## Risks and Edge Cases

The command group can corrupt repositories if used incorrectly, especially `put-obj`, `delete-obj`, and `format-obj`. Dumping archive metadata can create many files and large JSON outputs. `do_debug_dump_repo_objs()` assumes at least one repository object exists to bootstrap the key. Search only supports `hex:` and `str:` prefixes and keeps boundary data to find cross-object matches. Hex ID validation prevents wrong-length IDs but cannot ensure semantic object type correctness when formatting/inserting. Some commands intentionally suppress normal operation compatibility checks.

## Test Signals

Tests should use disposable repositories to verify manifest/archive dumps are parseable JSON, archive item dumps match item pointer streams, object get/parse/format round-trips preserve metadata and payload, invalid IDs raise `CommandError`, search finds in-object and cross-boundary byte sequences, empty/corrupt repository bootstrap failures are understandable, delete handles missing objects, and parser coverage confirms every debug subcommand is registered with expected arguments.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/archiver/debug_cmd.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/archiver/delete_cmd.py -->
# sources/sync-backup/borg/src/borg/archiver/delete_cmd.py

## Purpose

`delete_cmd.py` implements `borg delete`, which soft-deletes one or more archives from a repository. It intentionally does not free repository object storage; users must later run `borg compact`. The source was read as a complete 94-line file.

## Important APIs, Types, and Functions

`DeleteMixIn.do_delete()` loads the manifest, resolves either a single archive name or archive-filtered list, excludes protected archives tagged `@PROT`, soft-deletes archive IDs with `manifest.archives.delete_by_id()`, optionally lists results, and writes the manifest. `build_parser_delete()` wires `--dry-run`, `--list`, archive filters, and optional `NAME`.

## Control Flow

The command opens the repository with `manifest=False`, then explicitly loads the manifest for delete compatibility. It determines the candidate archives, filters protected archives, aborts if the user selected all archives without an explicit name or match pattern, and iterates candidates. Each archive is formatted before deletion for output stability. Non-dry-run deletes by ID; dry-run only logs what would happen. If at least one archive was deleted, the manifest is written and a compact reminder is emitted.

## State and Persistence Behavior

The command mutates only manifest archive metadata by marking/removing archive entries according to Borg's soft-delete mechanism. It does not delete content chunks or free disk space. Dry-run makes no repository changes. The operation is a precursor to `compact_cmd.py`, which permanently removes soft-deleted archive entries and unreferenced objects.

## Dependencies and Integration Points

Dependencies include `Manifest`, archive filter helpers from `_common`, `format_archive()`, `archivename_validator`, and `bin_to_hex()`. It integrates with `undelete` semantics through soft deletion and with `compact` for final space reclamation.

## Risks and Edge Cases

The safety guard prevents accidental deletion of every archive unless a name or archive match is explicit. Protected archives are silently excluded from candidates. Corrupt archive metadata is handled by deleting manifest entries by ID rather than constructing full `Archive` objects. A `KeyError` during deletion produces a warning but does not abort all candidates.

## Test Signals

Tests should cover single-name deletion, filter-based deletion, dry-run/list output, all-archive safety abort, protected `@PROT` archives, already-missing archive IDs, manifest write only after actual deletion, and the compact reminder after successful mutation.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/archiver/delete_cmd.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/archiver/diff_cmd.py -->
# sources/sync-backup/borg/src/borg/archiver/diff_cmd.py

## Purpose

`diff_cmd.py` implements `borg diff`, comparing contents and metadata between two archives. It formats text or JSON Lines output, supports content-only mode, validates and applies sort specifications, and warns when chunker parameters may force slower comparison. The source was read as a complete 338-line file.

## Important APIs, Types, and Functions

`DiffMixIn.do_diff()` is the command entry point. Local helpers `actual_change()`, `print_json_output()`, `print_text_output()`, and `key_for()` filter no-op changes, serialize `ItemDiff` changes, and compute sort keys. It uses `Archive.compare_archives_iter()` for comparison and `DiffFormatter` for text formatting. `build_parser_diff()` defines flags such as `--numeric-ids`, `--same-chunker-params`, `--format`, `--json-lines`, `--sort-by`, `--content-only`, two archive names, paths, and exclusions. `diff_sort_spec_validator()` restricts accepted sort fields.

## Control Flow

The command resolves both archive names from the manifest and constructs `Archive` instances. It compares archive chunker parameters; if they differ and the user has not asserted sameness, it warns and disables chunk-ID-only comparison. It builds a matcher from patterns and path arguments, calls `Archive.compare_archives_iter()`, filters equal items, optionally materializes and stably sorts the result list from last sort key to first, then emits each diff as JSON Lines or formatted text. Finally it warns for unmatched include patterns.

## State and Persistence Behavior

The command is read-only with repository read compatibility. It may load archive metadata and content chunks depending on comparison mode and chunker compatibility, but it does not mutate repository, cache, or manifest state. Output is written to stdout and warnings to Borg's warning channel.

## Dependencies and Integration Points

The module depends on `Archive`, `ItemDiff`, `DiffFormatter`, `BaseFormatter`, `BorgJsonEncoder`, path pattern helpers from `_common`, and archive-name/path validators. Its performance depends on archive metadata including `chunker_params`, and its output contract integrates with scripts using `BORG_DIFF_FORMAT` or `--json-lines`.

## Risks and Edge Cases

When chunker params differ, modified-file change objects may not contain `added` and `removed`; `actual_change()` treats that conservatively as a real change. Sorting forces the generator into memory, which can be expensive on huge archives. `content_only` filters metadata fields by comparing change names to `DiffFormatter.METADATA`. Sort keys read private-ish fields (`_item1`, `_item2`) from `ItemDiff`, so formatter/data structure changes can break sorting.

## Test Signals

Tests should compare archives with added, removed, modified, metadata-only, and unchanged items; verify content-only filtering; assert JSON Lines schema; exercise chunker mismatch warnings and `--same-chunker-params`; cover each sort field and direction; validate bad sort specs; test custom formats and `BORG_DIFF_FORMAT`; and confirm unmatched include warnings.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/archiver/diff_cmd.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/archiver/extract_cmd.py -->
# sources/sync-backup/borg/src/borg/archiver/extract_cmd.py

## Purpose

`extract_cmd.py` implements `borg extract`, restoring archive contents into the current working directory or stdout. It handles path filtering, strip-components, dry-run, sparse extraction, hard links, progress accounting, and delayed directory permission restoration. The source was read as a complete 191-line file.

## Important APIs, Types, and Functions

`ExtractMixIn.do_extract()` is wrapped by `with_repository` and `with_archive`. It uses `build_matcher()` for path/pattern selection, `build_filter()` for progress size calculation with stripping, `HardLinkManager` for hardlink identity tracking, `ProgressIndicatorPercent` for extraction and permission progress, and `archive.extract_item()` for actual restoration. `build_parser_extract()` wires list/dry-run/numeric metadata flags, `--stdout`, `--sparse`, `--continue`, archive name, paths, and exclusion options.

## Control Flow

The command first warns if the filesystem encoding is ASCII. It builds a matcher, initializes options and a directory stack, and optionally computes total extracted size by iterating matching archive items. It then iterates all archive items in archive order. For each item it applies `strip_components`, logs list output with `+` or `-`, and if matched extracts it. Directories are extracted immediately with attributes deferred, pushed onto a stack, and finalized after children are processed. Non-directories are extracted with sparse/hardlink/progress/continue settings. At the end, remaining directories are extracted again to restore attributes, unmatched include patterns are warned, and progress output is cleared.

## State and Persistence Behavior

Non-dry-run extraction writes files, directories, links, device metadata, xattrs, ACLs, flags, and permissions into the current working directory unless `--stdout` changes data output. Dry-run still reads archive metadata/data enough to validate extraction but does not write files. `--continue` permits continuing interrupted extraction for the same archive. Directory attributes are deliberately restored last to avoid permission modes preventing child creation.

## Dependencies and Integration Points

This command depends on archive extraction behavior, platform metadata restoration options controlled by parsed args, hardlink management, matcher/filter helpers, progress display, and warning types. It integrates with `list_cmd.py` and `create_cmd.py` semantics for path matching and item status display.

## Risks and Edge Cases

Extraction always targets the current working directory, so caller cwd matters. ASCII filesystem encoding cannot represent non-ASCII archive paths. `strip_components` can skip items entirely if no path remains. Parent directories omitted by filtering cannot have metadata restored. Symlink behavior is handled by archive extraction and can affect visible paths. Errors per item are warnings, so extraction can complete partially.

## Test Signals

Tests should cover full and partial extraction, dry-run, list markers, strip-components skipping and renaming, directory attribute restoration order, hardlinks, sparse files, stdout extraction, continue mode after interruption, unmatched include warnings, ASCII encoding warnings, and per-item `BackupError` warnings without total abort.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/archiver/extract_cmd.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/archiver/help_cmd.py -->
# sources/sync-backup/borg/src/borg/archiver/help_cmd.py

## Purpose

`help_cmd.py` implements Borg's extra help system, including long-form help topics for patterns, archive matching, placeholders, and compression, plus command-help routing. The source was read as a complete 563-line file.

## Important APIs, Types, and Functions

`HelpMixIn.helptext` is a class-level dictionary populated with nanorst/reStructuredText-like text for `"patterns"`, `"match-archives"`, `"placeholders"`, and `"compression"`. `do_help()` selects between top-level parser help, topic help rendered through `rst_to_terminal()`, command parser help, command epilog-only output, command usage-only output, and an error listing known commands/topics. `do_subcommand_help()` and `do_maincommand_help` print parser help. `build_parser_help()` registers `borg help` with `--epilog-only`, `--usage-only`, and optional `TOPIC`.

## Control Flow

The help command receives the main parser and args. Without a topic it prints main parser help. If the topic is in `helptext`, it renders that topic for terminal output. If the topic matches a registered subcommand, it prints either the command epilog, usage/help with epilog suppressed, or full help. Unknown topics call `parser.error()` with suggestions. The parser builder simply adds the `help` subcommand and options.

## State and Persistence Behavior

There is no persistent state. The command mutates a command parser object transiently when `--usage-only` sets `commands[topic].epilog = None` before printing help. All output is terminal text.

## Dependencies and Integration Points

The module depends on Borg's `ArgumentParser`, shared constants, and `rst_to_terminal()` conversion. Its topic names are also consumed by `completion_cmd.py`, which completes help topics from `self.helptext.keys()`. Topic text documents parser behavior implemented across `create`, `extract`, `delete`, `prune`, and related commands.

## Risks and Edge Cases

Static help text can drift from parser defaults, validator behavior, or feature support. `--usage-only` mutates the parser's epilog field for the current process, which is normally harmless for one-shot CLI use but could affect repeated parser use in tests. Long topic strings include examples, escaping rules, and platform notes that need careful maintenance when path or pattern behavior changes.

## Test Signals

Tests should assert every expected topic renders, unknown topics include command/topic suggestions, command topics support full help, epilog-only and usage-only modes work, completion sees the same topic names, and representative text snippets for pattern/compression behavior stay in sync with parser choices.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/archiver/help_cmd.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/archiver/info_cmd.py -->
# sources/sync-backup/borg/src/borg/archiver/info_cmd.py

## Purpose

`info_cmd.py` implements `borg info`, showing detailed information for one archive or an archive-filtered set. It formats archive metadata and stats as text or JSON. The source was read as a complete 87-line file.

## Important APIs, Types, and Functions

`InfoMixIn.do_info()` opens the repository with cache and read compatibility, resolves archive candidates, constructs `Archive` objects with the shared cache, calls `archive.info()`, formats duration and tags for text output, or accumulates raw info for JSON. `build_parser_info()` registers `--json`, archive filters, and optional archive name.

## Control Flow

The command chooses either a single archive from `manifest.archives.get_one()` or a list from `manifest.archives.list_considering(args)`. It iterates each archive, fetches `archive.info()`, prints a formatted text block with name, fingerprint, comment, host/user, tags, nominal/start/end times, duration, command line, cwd, number of files, and original size, inserting blank lines between archives. In JSON mode it prints `basic_json_data()` with an `archives` array.

## State and Persistence Behavior

The command is read-only but uses the cache because archive info can depend on cached repository/chunk metadata. It writes only stdout. It does not alter manifests, archives, repository objects, or cache contents beyond normal read/cache access side effects.

## Dependencies and Integration Points

It depends on `Archive.info()`, manifest archive filtering, `format_timedelta()`, `basic_json_data()`, and `json_print()`. Its JSON output is part of Borg's machine-readable interface and should stay compatible with scripts.

## Risks and Edge Cases

Large filtered archive sets instantiate and inspect each archive. Text mode transforms `duration` from seconds to a string and joins tags, while JSON preserves raw structures, so tests need to distinguish output modes. Missing/corrupt archives are handled by lower-level manifest/archive resolution.

## Test Signals

Tests should cover single archive and filtered multi-archive info, text formatting fields, blank-line separation, JSON archive array, tag formatting, duration conversion, and cache-required archive stats.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/archiver/info_cmd.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/archiver/key_cmds.py -->
# sources/sync-backup/borg/src/borg/archiver/key_cmds.py

## Purpose

`key_cmds.py` implements `borg key`, managing repository key passphrases, additional Borg keys, key listing/removal, key storage location changes, and key export/import. It is a security-sensitive command group operating on key material and key metadata. The source was read as a complete 354-line file.

## Important APIs, Types, and Functions

`KeysMixIn` defines `do_key_change_passphrase()`, `do_key_add()`, `do_key_remove()`, `do_key_list()`, `do_key_change_location()`, `do_key_export()`, and `do_key_import()`. `build_parser_keys()` registers nested subcommands: `export`, `import`, `change-passphrase`, `add`, `remove`, `list`, and `change-location`. Important dependencies are `KEY_LOCATIONS`, `KeyManager`, `Manifest`, `PathSpec`, and `CommandError`.

## Control Flow

Passphrase/add/remove/list/change-location commands open the repository with manifest and check compatibility, then inspect whether the loaded key exposes the needed capability method (`change_passphrase`, `add_key`, `remove_key`, `list_keys`). Export/import use `KeyManager` with no repository lock, manifest, or cache. `change-location` validates configurability, constructs a new same-class key with copied key material and optional AEAD session/cipher attributes, saves it to the new target using the existing passphrase/algorithm/label, updates manifest/repo object/cache key references, and optionally removes the old key file/blob. The parser includes mutually exclusive key selectors for export/remove and import options for paper/keyfile/repokey.

## State and Persistence Behavior

These commands mutate local key files, repository key blobs, manifest key references, and cache key references depending on mode. Passphrase changes re-encrypt key material but do not change repository encryption secrets. Add/remove manage independent Borg key wrappers around the same secret material. Export writes encrypted key backups, paper keys, or QR HTML to a path/stdout. Import reads key backups or interactive paper-key data and writes key storage. `change-location` moves or copies the active key between keyfile and repokey storage without changing crypto algorithms.

## Dependencies and Integration Points

The module integrates with crypto key classes via duck-typed capability methods, `KeyManager` backup/import formats, repository/manifest/cache wrappers, and parser choices derived from key location names. It is tied to `repo_create_cmd.py` because repository creation establishes the initial key and user-facing backup guidance.

## Risks and Edge Cases

Unencrypted repositories reject key operations that require key capabilities. `change-location` must preserve all cryptographic material exactly; missing attributes are conditionally copied for non-AEAD modes. Removing the wrong key can lock users out, so remove requires exactly one selector and underlying key logic protects admin/last keys. Export path validation handles directory paths specially. Paper import cannot use a path. Environment-dependent key locations (`BORG_KEY_FILE`, `BORG_KEYS_DIR`) affect import targets.

## Test Signals

Tests should cover encrypted, authenticated, and plaintext repositories; passphrase change capability errors; add/list/remove by label, key prefix, and current passphrase; admin/last-key protection; export normal, paper, and QR formats; import from file/stdin and paper mode errors; change-location keyfile-to-repokey and reverse with `--keep`; preservation of key IDs/labels/algorithm; and cache/manifest key references after movement.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/archiver/key_cmds.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/archiver/list_cmd.py -->
# sources/sync-backup/borg/src/borg/archiver/list_cmd.py

## Purpose

`list_cmd.py` implements `borg list`, listing items contained in an archive with configurable text or JSON Lines formatting and optional path/depth filtering. The source was read as a complete 133-line file.

## Important APIs, Types, and Functions

`ListMixIn.do_list()` resolves the archive, builds a matcher, chooses a format from `--format`, `--short`, or `BORG_LIST_FORMAT`, constructs an `ItemFormatter`, and iterates archive items. `ItemFormatter.format_needs_cache()` decides whether to open `Cache`. `build_parser_list()` registers `--short`, `--format`, `--json-lines`, `--depth`, archive name, paths, and exclusions.

## Control Flow

The command builds a path/pattern matcher, selects a format string, resolves the target archive, and defines `_list_inner(cache)`. Inside it, an `Archive` is opened with optional cache and an `item_filter()` checks matcher results and maximum slash-count depth. It then writes each formatted item to stdout. Cache acquisition is deferred and avoided unless the selected format needs cache-derived fields.

## State and Persistence Behavior

The command is read-only and writes listing output to stdout. It may open the cache for read access or cache population if the formatter requires it, but no archive or manifest mutation is intended.

## Dependencies and Integration Points

Dependencies include `Archive`, `Cache`, `ItemFormatter`, `BaseFormatter` help text, matcher/exclusion helpers, and environment-variable format overrides. It shares path filtering semantics with extract/diff and formatter infrastructure with repo-list/prune.

## Risks and Edge Cases

Depth is computed by counting `/`, so root-level files have depth 0 and nested paths depend on archive path normalization. JSON Lines ignores the display form of `--format` but uses keys referenced in it, which can surprise callers. Cache opening is format-dependent, so adding formatter keys must keep `format_needs_cache()` accurate.

## Test Signals

Tests should list archives in default, short, custom format, and JSON Lines modes; verify path and exclusion filtering; verify depth boundaries; cover cache-needed and cache-free formats; validate `BORG_LIST_FORMAT`; and assert formatter help includes the advertised keys.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/archiver/list_cmd.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/archiver/lock_cmds.py -->
# sources/sync-backup/borg/src/borg/archiver/lock_cmds.py

## Purpose

`lock_cmds.py` implements repository lock utilities: `borg with-lock`, which runs a user command while holding the repository lock, and `borg break-lock`, which breaks repository and cache locks. The source was read as a complete 79-line file.

## Important APIs, Types, and Functions

`LocksMixIn.do_with_lock()` opens the repository exclusively without a manifest, starts a `ThreadRunner` that periodically calls `repository.info` to refresh the lock, runs a subprocess command, and sets Borg's exit code to the subprocess return code. `do_break_lock()` opens without taking a lock and calls `repository.break_lock()` plus `Cache.break_lock(repository)`. `build_parser_locks()` registers both commands and the `REMAINDER` argument for user command arguments.

## Control Flow

`with-lock` acquires the repository lock through the decorator, starts the refresh thread with a 60-second interval, prepares a system subprocess environment, executes `[args.command] + args.args`, records the return code, and terminates the refresh thread in `finally`. `break-lock` intentionally avoids acquiring the lock and directly removes lock state. Parser epilogs document intended cautious use.

## State and Persistence Behavior

`with-lock` creates and maintains a live repository lock while an arbitrary child process runs, then releases it through normal repository wrapper cleanup. It does not otherwise mutate the repository unless the child process does. `break-lock` mutates repository and cache lock files/state and can disrupt active Borg processes if misused.

## Dependencies and Integration Points

The module depends on repository locking from `with_repository`, cache lock handling, subprocess execution, `prepare_subprocess_env()`, `set_ec()`, `CommandError`, and `ThreadRunner`. It integrates with operational workflows such as copying repositories while locked.

## Risks and Edge Cases

The child command is arbitrary and inherits a Borg-prepared environment. If the command cannot execute, `CommandError` is raised. Lock refresh relies on `repository.info` as an indirect refresh mechanism because the repository API has no explicit refresh call. `break-lock` is dangerous on shared repositories and must only be used when no process is active.

## Test Signals

Tests should verify subprocess return code propagation, failed command errors, refresh-thread termination on success and failure, exclusive lock acquisition during command execution, and `break-lock` clearing both repository and cache lock fixtures.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/archiver/lock_cmds.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/archiver/mount_cmds.py -->
# sources/sync-backup/borg/src/borg/archiver/mount_cmds.py

## Purpose

`mount_cmds.py` implements `borg mount`, `borg umount`, and `borgfs` parser setup for exposing a repository or archive as a FUSE filesystem. It validates mount prerequisites, selects the available FUSE backend, and wires mount-specific archive/path/filter options. The source was read as a complete 196-line file.

## Important APIs, Types, and Functions

`MountMixIn.do_mount()` performs pre-repository FUSE and mountpoint checks. `_do_mount()` opens the repository for read and dispatches to either `hlfuse.borgfs` when `has_mfusepy` is true or `fuse.FuseOperations` otherwise. `do_umount()` calls the platform `umount()` helper. `build_parser_mount_umount()` registers `mount` and `umount`, `build_parser_borgfs()` configures the standalone `borgfs` entrypoint, and `_define_borg_mount()` adds shared mount arguments.

## Control Flow

`do_mount()` imports FUSE capability flags, raises `RTError` if no backend exists, checks that the mountpoint is an existing writable directory, then calls `_do_mount()`. `_do_mount()` creates backend operations with the manifest, args, and repository, logs mounting, and invokes `operations.mount()` with mountpoint, options, foreground, and show-rc settings. Runtime errors are converted into `RTError("FUSE mount failed")`. `umount` delegates to platform unmount logic.

## State and Persistence Behavior

Mounting creates a live FUSE mount and usually daemonizes unless `--foreground` is set. It does not mutate repository data. Unmounting mutates OS mount state. The mounted view loads archive directory data on demand and may consume memory cache in the FUSE layer.

## Dependencies and Integration Points

The module integrates with `fuse_impl` backend selection, `hlfuse`/`fuse` operations, manifest/archive filtering, path matching/exclusion groups, platform unmount helpers, and mount options such as `versions`, `allow_damaged_files`, `ignore_permissions`, `uid`, and `gid`. It exposes the same option set through both `borg mount` and `borgfs`.

## Risks and Edge Cases

Mount checks happen before passphrase prompts to fail fast. Missing FUSE support, nonexistent mountpoints, or insufficient permissions stop the command. Symlinks inside archives can point outside the mountpoint when followed by users. Daemon crashes do not automatically unmount, and foreground mode handles SIGINT more cleanly. Backend differences between mfusepy and llfuse/pyfuse3 can change behavior.

## Test Signals

Tests should mock no-FUSE and each backend path, validate mountpoint existence and access checks, assert mount argument propagation, cover RuntimeError translation, verify `borgfs` parser setup, and smoke-test unmount delegation. Integration tests need actual FUSE support and should cover foreground/background behavior and path-filtered archive mounts.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/archiver/mount_cmds.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/archiver/prune_cmd.py -->
# sources/sync-backup/borg/src/borg/archiver/prune_cmd.py

## Purpose

`prune_cmd.py` implements `borg prune`, applying retention rules to archive sets and soft-deleting archives that are not retained. It supports keep-within and GFS-style time bucket retention at second, minute, hour, day, week, month, quarter, and year granularities. The source was read as a complete 420-line file.

## Important APIs, Types, and Functions

Pure helper functions include `prune_within()`, `default_period_func()`, `quarterly_13weekly_period_func()`, `quarterly_3monthly_period_func()`, and `prune_split()`. `PRUNING_PATTERNS` orders retention buckets. `PruneMixIn.do_prune()` validates that at least one retention rule is set, selects archive format, builds an `ArchiveFormatter`, resolves matching archives while excluding `@PROT`, computes keep/delete sets, logs or emits JSON, deletes unkept archive IDs, writes the manifest, and handles SIGINT. `build_parser_prune()` wires retention flags, list/format/json options, archive filters, and optional name.

## Control Flow

The command first rejects invocations with no retention rule. It selects a display format, resolves a candidate archive list sorted newest-first, and filters protected archives. It creates `keep` and `kept_because`, adds all archives newer than `--keep-within`, then iterates `PRUNING_PATTERNS` in order and calls `prune_split()` for each configured count. `prune_split()` keeps the newest archive per period, avoids archives already kept by earlier rules, and keeps the oldest archive if the requested count cannot be reached. The complement is soft-deleted unless dry-run. Output can include all archives, only pruned, only kept, or JSON.

## State and Persistence Behavior

Like `delete`, prune only mutates manifest archive metadata by soft-deleting archive entries. It does not free repository object storage and prints a compact reminder after actual deletions. Dry-run computes and reports without writing. JSON output is generated before manifest write and includes kept/deleted metadata. SIGINT can break the deletion loop and then raises `Error`.

## Dependencies and Integration Points

The module depends on manifest archive listing/deletion, archive filters, `ArchiveFormatter`, `interval()` parsing, progress display, JSON helpers, and global `sig_int`. It is coupled to `compact_cmd.py` for final object cleanup and to help text documenting GFS retention semantics.

## Risks and Edge Cases

Without a name or match pattern, all non-protected archives are candidates; the epilog warns users to run one prune per series. Local timezone is used for period grouping, including ISO week semantics. Negative keep counts are accepted by argparse as ints, but `prune_split()` breaks only when `len(keep) == n`; negative values effectively have no equality target and can keep every period. Sorting and set conversion require archive info objects to be hashable and comparable by identity/value as expected.

## Test Signals

Tests should cover each retention granularity, both quarterly strategies, `--keep-within`, earlier-rule precedence, oldest-retention fallback, dry-run, protected tags, JSON output fields, list-kept/list-pruned/list behavior, no-rule rejection, name versus match filtering, negative keep semantics, SIGINT interruption, and manifest write only when archives are actually deleted.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/archiver/prune_cmd.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/archiver/recreate_cmd.py -->
# sources/sync-backup/borg/src/borg/archiver/recreate_cmd.py

## Purpose

`recreate_cmd.py` implements `borg recreate`, rebuilding existing archives with optional filtering, rechunking, recompression, comment/timestamp changes, and target archive naming. It is a potentially destructive archive transformation command. The source was read as a complete 175-line file.

## Important APIs, Types, and Functions

`RecreateMixIn.do_recreate()` builds a matcher, configures `ArchiveRecreater`, selects archive candidates, skips temporary recreate archives, chooses target/delete-original behavior, calls `recreater.recreate()`, and writes the manifest. `build_parser_recreate()` wires list/filter/dry-run/stats options, exclusion groups, archive filters, `--target`, `--comment`, `--timestamp`, `--compression`, `--chunker-params`, and path arguments.

## Control Flow

The command opens the repository with cache and check compatibility. It builds a matcher from archive-internal paths and patterns, stores list/filter output flags on `self`, and constructs an `ArchiveRecreater` with exclusion tag settings, chunker params, compression, progress, stats, file-status printer, dry-run, and timestamp. It iterates `manifest.archives.list_considering(args)`, filters protected archives, skips temporary archive names, prints the archive being processed, and recreates either in place or to `--target`. If no changes are needed, it logs a skip. Non-dry-run writes the manifest after processing.

## State and Persistence Behavior

Non-dry-run recreate writes new archive metadata and chunks, may delete or replace the original archive entry when no target is specified, and can permanently remove files from archives according to filters after compaction. Dry-run avoids repository changes. Temporary archives named by `ArchiveRecreater` exist during operation and are skipped if encountered in the candidate list.

## Dependencies and Integration Points

The module is a thin command layer over `ArchiveRecreater` from `archive`, and depends on matcher/exclusion helpers, archive filters, validators for archive names/comments/timestamps/chunker/compression, manifest writing, and status printing shared with create. It interacts with compact because replaced/deleted archive data does not free space until compaction.

## Risks and Edge Cases

Filtering semantics apply to archived paths, not local filesystem paths, so absolute patterns do not match as users may expect. Rechunking can require large temporary space and may worsen data loss if chunks are already missing. `--target` creates a new archive instead of replacing originals; without it, originals are removed only after successful recreation. Multiple input archives with a single `--target` would rely on lower-level duplicate-name handling and should be treated carefully.

## Test Signals

Tests should cover dry-run/list/filter behavior, in-place recreation, target recreation, comment/timestamp changes, recompression and rechunking, path/exclusion filtering, protected archives, temporary archive skipping, no-op skip logging, manifest write behavior, and missing-chunk/rechunk warnings through integration tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/archiver/recreate_cmd.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/archiver/rename_cmd.py -->
# sources/sync-backup/borg/src/borg/archiver/rename_cmd.py

## Purpose

`rename_cmd.py` implements `borg rename`, changing an archive's name. Renaming creates a different archive ID because archive metadata changes. The source was read as a complete 37-line file.

## Important APIs, Types, and Functions

`RenameMixIn.do_rename()` is wrapped with repository/cache/check compatibility and `with_archive`; it calls `archive.rename(args.newname)` and writes the manifest. `build_parser_rename()` registers old and new archive names using `archivename_validator`.

## Control Flow

The decorators resolve the repository, manifest, cache, and current archive from `OLDNAME`. The method delegates the actual rename to the `Archive` instance, then persists the manifest. Parser setup provides a short epilog and two required positional names.

## State and Persistence Behavior

The command mutates archive metadata and manifest state. Because the archive ID changes, downstream references by ID and cached metadata may need to observe the new ID. It does not directly delete content chunks.

## Dependencies and Integration Points

It depends on `with_archive`, `Archive.rename()`, manifest writing, and archive-name validation. It is the simplest command layer for archive metadata mutation and shares check compatibility with recreate/key operations.

## Risks and Edge Cases

Name validation happens at parse time, but duplicate names or repository-specific conflicts are handled by lower layers. Partial failure between `archive.rename()` and `manifest.write()` would be critical, so integration tests should use the real archive implementation. Users relying on old archive IDs must understand ID changes.

## Test Signals

Tests should verify successful rename changes archive name and ID, manifest persistence, missing old-name errors via `with_archive`, invalid new names rejected by parser, and duplicate/conflicting target handling from archive internals.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/archiver/rename_cmd.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/archiver/repo_create_cmd.py -->
# sources/sync-backup/borg/src/borg/archiver/repo_create_cmd.py

## Purpose

`repo_create_cmd.py` implements `borg repo-create`, creating a new empty repository, selecting encryption/key storage, optionally deriving related repository key material from another repository, initializing the manifest, and creating the initial cache. The source was read as a complete 243-line file.

## Important APIs, Types, and Functions

`RepoCreateMixIn.do_repo_create()` is wrapped with `with_repository(create=True, exclusive=True, manifest=False)` and `with_other_repository(manifest=True, compatibility=READ)`. It calls `key_creator()`, constructs `Manifest`, writes it, opens `Cache` once, and prints key backup and reserve-space guidance. `build_parser_repo_create()` registers `--other-repo`, `--from-borg1`, required `--encryption`, `--key-location`, and `--copy-crypt-key`, with encryption choices from `key_argument_names()`.

## Control Flow

The command opens/creates the target repository and optionally an already existing other repository. If an other manifest exists, its key is passed to `key_creator()` and may have `copy_crypt_key` set. On passphrase EOF or keyboard interrupt, the partially created repository is destroyed and `CancelledByUser` is raised. Otherwise it writes a new manifest with the created key, initializes the cache with `warn_if_unencrypted=False`, warns about backing up key/passphrase for non-plaintext modes, and recommends reserving emergency repository space.

## State and Persistence Behavior

This command creates persistent repository storage, key material in either repository or keyfile location, a manifest object, and local cache/security metadata. Cancellation before key creation completion destroys the target repository. Related repository creation can persist shared ID/chunker secret material, and optionally shared crypt key, enabling dedup/transfer workflows.

## Dependencies and Integration Points

It integrates with repository creation wrappers, key creation and key argument registries, `Location` validation, optional other-repository access, `Manifest`, `Cache`, and reserve-space guidance implemented by `repo_space_cmd.py`. It is the root lifecycle command for repositories later used by create, key, info, and delete commands.

## Risks and Edge Cases

Encryption mode is required and cannot be changed later; only key storage can move later. Related repositories need careful crypt-key copying decisions. Passphrase cancellation must destroy incomplete repositories to avoid unusable leftovers. Plaintext mode suppresses key backup warning but still creates a repository with different security assumptions. Remote/sftp stores can be slow because underlying borgstore pre-creates directories.

## Test Signals

Tests should cover each encryption/key-location parser choice, plaintext versus encrypted warning behavior, cancellation cleanup, initial manifest/cache creation, related repository key material reuse with and without `--copy-crypt-key`, `--from-borg1` argument propagation, required encryption validation, and reserve-space warning output.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/archiver/repo_create_cmd.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/archiver/repo_delete_cmd.py -->
# sources/sync-backup/borg/src/borg/archiver/repo_delete_cmd.py

## Purpose

`repo_delete_cmd.py` implements `borg repo-delete`, deleting an entire repository and its local cache/security metadata, or deleting only the local cache. It includes a strong confirmation path for destructive repository deletion. The source was read as a complete 133-line file.

## Important APIs, Types, and Functions

`RepoDeleteMixIn.do_repo_delete()` opens the repository exclusively without a manifest, optionally loads the manifest to count/list archives, asks for `YES` confirmation through `yes()`, calls `repository.destroy()`, optionally calls `SecurityManager.destroy(repository)`, and always destroys `Cache` unless dry-run. `build_parser_repo_delete()` registers `--dry-run`, `--list`, counted `--force`, `--cache-only`, and `--keep-security-info`.

## Control Flow

If `--cache-only` is not set and no `--force` is supplied, the command builds a confirmation message containing repository ID, location, and optionally archive listings. It handles missing manifests by warning that contents cannot be described. The user must type exact `YES`, or set `BORG_DELETE_I_KNOW_WHAT_I_AM_DOING`, otherwise `CancelledByUser` is raised. Non-dry-run destroys the repository and security info unless kept, then destroys the cache. Dry-run logs what would happen.

## State and Persistence Behavior

Non-dry-run repository deletion removes repository storage; cache deletion removes local cache state; security info deletion removes local security metadata unless `--keep-security-info` is set. `--cache-only` leaves the repository and security info alone but deletes cache. Dry-run performs no deletion.

## Dependencies and Integration Points

The module depends on repository destruction, `Cache.destroy()`, `SecurityManager.destroy()`, manifest loading/listing, archive formatting, `yes()` confirmation, and `NoManifestError`. It is the hard-delete counterpart to archive-level `delete` and `prune`.

## Risks and Edge Cases

`--force` bypasses the interactive archive listing/confirmation path. Missing or corrupt manifest means the command cannot enumerate contents but can still delete the repository. `--keep-security-info` can leave local metadata behind intentionally. Cache destruction occurs after repository deletion path and also in cache-only mode, so tests must separate those branches.

## Test Signals

Tests should cover dry-run with and without cache-only, confirmation success/failure, environment override, archive listing in confirmation, missing-manifest confirmation text, forced deletion, security-info deletion and preservation, cache-only deletion, and repository/cache destroy call ordering.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/archiver/repo_delete_cmd.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/archiver/repo_info_cmd.py -->
# sources/sync-backup/borg/src/borg/archiver/repo_info_cmd.py

## Purpose

`repo_info_cmd.py` implements `borg repo-info`, displaying repository identity, location, version, encryption/key-storage details, security directory, cache info, or equivalent JSON. The source was read as a complete 75-line file.

## Important APIs, Types, and Functions

`RepoInfoMixIn.do_repo_info()` opens the repository with cache and read compatibility, builds `basic_json_data()` with `security_dir`, formats encryption state from `manifest.key.NAME` and key storage, appends keyfile location when relevant, and prints text or JSON. `build_parser_repo_info()` registers `--json`.

## Control Flow

The command obtains the active key and base info. JSON mode prints the info directly. Text mode builds an `encryption` string distinguishing encrypted, authenticated, and plaintext modes, maps `KeyBlobStorage.KEYFILE`/`REPO` to user-facing storage labels, includes key file location for keyfile storage, formats repository ID/location/version/security directory, appends cache path when present, and prints.

## State and Persistence Behavior

The command is read-only. It may open cache/security metadata for reporting and writes only stdout. No manifest or repository mutation is intended.

## Dependencies and Integration Points

It depends on `basic_json_data()`, `bin_to_hex()`, cache security manager state, repository location/version/id, key storage constants from shared constants, and key methods like `find_key()`. It complements `key_cmds.py` and `repo_create_cmd.py` by reporting the key mode they configure.

## Risks and Edge Cases

Authenticated modes are not encrypted but still have key storage, so text must avoid saying data is encrypted. `KeyBlobStorage` constants are imported through wildcard constants, which hides the dependency. Some info cache objects may not expose `path`; the code checks with `hasattr`. Key classes without storage or `find_key()` need graceful formatting.

## Test Signals

Tests should cover plaintext, encrypted repokey, encrypted keyfile, authenticated key modes, JSON output, cache path presence/absence, security directory inclusion, and keyfile location formatting.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/archiver/repo_info_cmd.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/archiver/repo_list_cmd.py -->
# sources/sync-backup/borg/src/borg/archiver/repo_list_cmd.py

## Purpose

`repo_list_cmd.py` implements `borg repo-list`, listing archives contained in a repository in text or JSON form, with archive filtering and optional deleted archive visibility. The source was read as a complete 110-line file.

## Important APIs, Types, and Functions

`RepoListMixIn.do_repo_list()` selects a format from `--format`, `--short`, or `BORG_REPO_LIST_FORMAT`, constructs `ArchiveFormatter`, iterates `manifest.archives.list_considering(args)`, writes formatted rows or accumulates JSON data, and emits `basic_json_data()`. `build_parser_repo_list()` registers `--short`, `--from-borg1`, `--format`, `--json`, and archive filters with deleted support.

## Control Flow

The command opens a repository for read and allows Borg 1 repositories. It chooses the format, passing `deleted=args.deleted` to the formatter. It iterates archive infos selected by archive filters, writing text rows to stdout or collecting formatter item data. JSON mode prints a top-level Borg JSON structure with `archives`.

## State and Persistence Behavior

The command is read-only and writes stdout. It may read deleted archive entries when requested through filter options. It does not require cache.

## Dependencies and Integration Points

Dependencies include `ArchiveFormatter`, `BaseFormatter` help text, archive filter helper definitions, `basic_json_data()`, and environment format override support. `completion_cmd.py` shell snippets call `borg repo-list` with custom formats to complete archive names, IDs, and tags, making this output functionality an integration point for shell completions.

## Risks and Edge Cases

`--short` outputs IDs rather than archive names, which differs from some list commands. JSON ignores display formatting except for included keys as implemented by formatter. Deleted archive handling must stay consistent with soft-delete behavior from delete/prune and final removal by compact.

## Test Signals

Tests should cover default, short, custom format, environment format, JSON, archive filters, deleted archive listing, Borg 1 compatibility flag parsing, and formatter key help text. Completion integration should verify formats like `{id}{NL}`, `{archive}{NL}`, and `{tags}{NL}` remain valid.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/archiver/repo_list_cmd.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/archiver/repo_space_cmd.py -->
# sources/sync-backup/borg/src/borg/archiver/repo_space_cmd.py

## Purpose

`repo_space_cmd.py` implements `borg repo-space`, managing emergency reserved space inside a repository so users can recover from disk-full situations by freeing preallocated reserve objects. The source was read as a complete 106-line file.

## Important APIs, Types, and Functions

`RepoSpaceMixIn.do_repo_space()` opens the repository without lock or manifest, then either reserves space, frees reserve objects, or reports current reserve size. It uses 64 MiB `space-reserve.N` objects under the repository `config` namespace, `os.urandom()` to resist compression/deduplication, `repository.store_store()`, `repository.store_list()`, and `repository.store_delete()`. `build_parser_repo_space()` registers `--reserve SPACE` parsed by `parse_file_size` and `--free`.

## Control Flow

When `--reserve` is positive, the command rounds requested bytes up to 64 MiB objects, writes random data to `config/space-reserve.0`, `.1`, and so on, sums written bytes, and prints the reserved amount. When `--free` is set, it lists `config`, wraps RPC tuples as `ItemInfo`, deletes objects whose names start with `space-reserve.`, sums sizes, and prints follow-up instructions. With neither option, it lists existing reserve objects and reports total reserved space plus how to change it.

## State and Persistence Behavior

The command intentionally works without locks because lock acquisition may fail when the disk is full. Reserving writes large random config objects to persistent repository storage. Freeing deletes those config objects. Reporting is read-only. Existing reserve objects are overwritten/reused by deterministic names when reserving again without freeing first.

## Dependencies and Integration Points

It depends on borgstore `ItemInfo`, repository config store APIs, file-size parsing/formatting, and parser helper `Highlander`. It is referenced by `repo_create_cmd.py` guidance and operationally supports later `prune`, `delete`, and `compact` recovery.

## Risks and Edge Cases

Working without locks is deliberate but means concurrent reserve/free operations can race. Random reserve data consumes CPU and memory in 64 MiB chunks. Re-reserving without `--free` can overwrite or add deterministic reserve names depending on store semantics. Prefix matching deletes any config item starting `space-reserve.`, so unrelated objects should not use that prefix.

## Test Signals

Tests should cover reserve rounding, zero/default report, free deleting only matching config objects, RPC tuple conversion through `ItemInfo`, parse-file-size inputs, formatting output, no-lock repository opening, and concurrent/race behavior in integration tests where possible.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/archiver/repo_space_cmd.py -->
