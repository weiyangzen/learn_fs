# subset-b-009098 research

Grouped research report for Borg documentation and generated usage include files in subset B. Each file section is delimited for deterministic source-tree-aligned splitting.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/docs/misc/asciinema/install.json -->
# sources/sync-backup/borg/docs/misc/asciinema/install.json

Purpose: asciinema v2 terminal recording showing standalone Borg binary installation. The first line is the cast header with terminal dimensions, timestamp, and environment; the remaining lines are JSON event arrays with output timing and payloads.

Important APIs and control flow: consumers are asciinema-compatible players or documentation embed logic, not Borg runtime code. The event stream types out a narrative, downloads `borg-linux64` and `borg-linux64.asc` from a Borg GitHub release, verifies the detached signature with `gpg --verify`, installs to `/usr/local/bin/borg`, adjusts ownership and executable bits, and checks `borg -V`.

State and persistence: persisted state is only documentation media. The demonstrated workflow writes a binary into `/usr/local/bin`, uses local GPG keyring trust state, and depends on downloaded release artifacts.

Dependencies and integration points: integrates with Borg docs pages that embed terminal casts, GitHub release URLs, GPG signature verification, sudo, and asciinema v2 parsing.

Risks: the recording is pinned to Borg 1.2.1 while nearby docs are Borg 2-style, so version drift is likely. The JSON is newline-delimited cast data, not one JSON object. Release URLs, signer keys, and standalone binary names can become stale.

Test signals: validate with an asciinema player or line-oriented JSON parser; confirm the header parses, every event line is valid JSON, and docs render the cast without treating the file as strict single-document JSON.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/docs/misc/asciinema/install.json -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/docs/misc/logging.conf -->
# sources/sync-backup/borg/docs/misc/logging.conf

Purpose: minimal Python logging configuration example for Borg's `BORG_LOGGING_CONF` environment variable.

Important APIs and control flow: follows `logging.config.fileConfig` INI sections: root logger, one `FileHandler`, one formatter. The root logger is `NOTSET`, the handler logs `INFO` and above, and formatted records include timestamp, level name, and message.

State and persistence: writes `borg.log` in the process current working directory with mode `w`, so each run truncates previous content.

Dependencies and integration points: referenced by the environment variables documentation. It depends on Python's logging configuration grammar and Borg honoring `BORG_LOGGING_CONF`.

Risks: relative log path can write into surprising locations. Truncating mode is dangerous for long-running automation. `NOTSET` on root delegates effective filtering to the handler, which may surprise users expecting Borg's default warning threshold.

Test signals: run Borg with `BORG_LOGGING_CONF` pointing at this file and confirm `borg.log` contains INFO records with the configured format.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/docs/misc/logging.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/docs/quickstart_example.rst.inc -->
# sources/sync-backup/borg/docs/quickstart_example.rst.inc

Purpose: quickstart include that walks a user through repository creation, repeated archive creation, listing, extraction, deletion, and compaction.

Important APIs and control flow: examples use `borg -r /path/to/repo repo-create --encryption=aes-ocb`, `create`, `repo-list`, `list aid:<prefix>`, `extract aid:<prefix>`, `delete aid:<prefix>`, and `compact -v`. It illustrates Borg 2's archive-series model where duplicate archive names are normal and archive IDs disambiguate.

State and persistence: creates an encrypted repository, stores two archives sharing a name, soft-deletes one archive, and then compacts to reclaim repository space.

Dependencies and integration points: depends on the general repository, archive-ID, logging, and compaction docs. It is included by higher-level quickstart pages.

Risks: hard-coded sample fingerprints and timestamps are illustrative only. Deleting by name is risky because names can match multiple archives; the include explicitly recommends dry-run/list first.

Test signals: doctest-like smoke can verify command names and option spelling; integration tests should confirm `repo-create`, duplicate-name archive creation, ID-prefix listing/extraction, delete, and compact still match the documented flow.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/docs/quickstart_example.rst.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/docs/usage/analyze.rst.inc -->
# sources/sync-backup/borg/docs/usage/analyze.rst.inc

Purpose: generated CLI reference for `borg analyze`, used to identify high-activity directories across selected archives.

Important APIs and control flow: exposes archive filters (`--match-archives`, `--sort-by`, `--first`, `--last`, age-window options). The described command iterates matching archives, then contained files, then chunk IDs and plaintext sizes, aggregating added and removed chunk sizes by direct parent directory.

State and persistence: read-only analysis of repository metadata and archive contents. It does not mutate archives or caches beyond ordinary read-side access.

Dependencies and integration points: generated from Borg's argparse/jsonargparse help and tied to archive matching semantics documented in `borg help match-archives`. Suggested remediation integrates with future `borg create` excludes or `borg recreate`.

Risks: analysis uses plaintext chunk sizes, not compressed repository sizes, so output is a usage signal rather than exact disk-space accounting. Archive filter mistakes can hide or overstate activity.

Test signals: generated docs should match parser help; command tests should verify filtered archive iteration and directory aggregation on known archive sequences.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/docs/usage/analyze.rst.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/docs/usage/benchmark_cpu.rst.inc -->
# sources/sync-backup/borg/docs/usage/benchmark_cpu.rst.inc

Purpose: generated reference for `borg benchmark cpu`, a CPU-bound throughput benchmark for Borg internals.

Important APIs and control flow: command shape is `borg [common options] benchmark cpu [options]`; the only command-specific option is `--json`. It creates input data in memory, runs miscellaneous Borg operations, and reports throughput.

State and persistence: no repository data is required or persisted; benchmark data is in-memory.

Dependencies and integration points: integrates with common logging/output options and JSON output consumers. Meaningful results depend on machine load and memory availability.

Risks: benchmark variance is high if the host is busy or paging. The docs must stay aligned with actual measured operations in the benchmark implementation.

Test signals: parser help generation, successful text and JSON benchmark output, and JSON schema stability for automation using `--json`.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/docs/usage/benchmark_cpu.rst.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/docs/usage/benchmark_crud.rst.inc -->
# sources/sync-backup/borg/docs/usage/benchmark_crud.rst.inc

Purpose: generated reference for `borg benchmark crud`, which measures create, read/extract, update, and delete behavior against a repository.

Important APIs and control flow: requires a `PATH` for generated input data and an existing repository from common `--repo` handling. `--json-lines` switches output to JSON Lines. The benchmark creates artificial zero and random datasets, archives them, dry-run extracts, repeats unchanged creates to measure files-cache behavior, and deletes/compacts.

State and persistence: writes about 1 GB of benchmark input data plus repository objects and temporary benchmark archives named `borg-benchmark-crud*`.

Dependencies and integration points: depends on repository initialization, encryption passphrase automation via `BORG_PASSPHRASE`, files cache, extract dry-run, delete, and compaction paths.

Risks: consumes substantial disk space and uses artificial data, so results may not reflect real workloads. Running on a non-idle machine or network repository can skew measurements.

Test signals: verify command refuses missing repo/path, emits valid JSON Lines, cleans up benchmark archives, and measures all C/R/U/D phases.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/docs/usage/benchmark_crud.rst.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/docs/usage/borgfs.rst.inc -->
# sources/sync-backup/borg/docs/usage/borgfs.rst.inc

Purpose: generated reference for `borg borgfs`, a compatibility wrapper for mounting repositories or archives as FUSE filesystems.

Important APIs and control flow: command accepts `REPOSITORY_OR_ARCHIVE`, `MOUNTPOINT`, optional `PATH` selectors, `--foreground`, `-o` mount options, archive filters for repository mounts, exclude/pattern filters, and `--strip-components`. It delegates conceptually to `borg mount`.

State and persistence: creates a live FUSE mount and may daemonize. It does not modify archive contents, but kernel mount state persists until unmounted.

Dependencies and integration points: depends on FUSE implementation selection, fstab integration (`fuse.borgfs`), archive filtering, pattern matching, and `BORG_MOUNT_DATA_CACHE_ENTRIES` chunk cache tuning.

Risks: daemon crashes do not auto-unmount to avoid accidental data deletion by tools observing an empty mount. Damaged files return EIO unless `allow_damaged_files` is set. Versioned repository view is experimental.

Test signals: mount/unmount smoke tests for foreground and background modes, option passing through `-o`, path filtering, damaged-file behavior, and fstab wrapper compatibility.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/docs/usage/borgfs.rst.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/docs/usage/break-lock.rst.inc -->
# sources/sync-backup/borg/docs/usage/break-lock.rst.inc

Purpose: generated reference for `borg break-lock`, an emergency command for removing repository and cache locks.

Important APIs and control flow: no command-specific options beyond common options. The runtime path must reach both repository lock and cache lock handling and forcibly clear stale lock records.

State and persistence: mutates lock state in the repository and local cache. It does not inspect or change archive contents.

Dependencies and integration points: coupled to Borg's locking implementation, host identity/stale-lock behavior, cache directory, repository location, and lock wait semantics.

Risks: using it while any Borg process on any machine still accesses the repository or cache can corrupt state or break active operations. Documentation intentionally keeps the command terse and cautionary.

Test signals: unit/integration tests should cover stale lock removal while ensuring normal active lock acquisition still protects live processes.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/docs/usage/break-lock.rst.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/docs/usage/check.rst.inc -->
# sources/sync-backup/borg/docs/usage/check.rst.inc

Purpose: generated reference for `borg check`, the repository and archive consistency verifier.

Important APIs and control flow: command options select repository-only checks, archive-only checks, cryptographic data verification, repair, lost-archive search, and bounded partial checks with `--max-duration`. Repository checks validate object headers, metadata, data size, and hashes; archive checks validate manifest, archive metadata chunks, item references, and optionally file data.

State and persistence: read-only by default. Partial repository checks persist progress. `--repair` can remove corrupted objects, remove or restore archive directory entries, and replace missing file chunks with damage markers/zero runs.

Dependencies and integration points: archive filtering, remote execution split (repository checks on server, archive checks on client), encryption keys for archive checks, compact/undelete semantics, and return-code/logging behavior.

Risks: `--repair` is explicitly lossy and dangerous. `--max-duration` excludes archive checks and repair. `--find-lost-archives` is very expensive and only useful before compact removes data.

Test signals: parser conflict tests, repository corruption fixtures, missing chunk/archive metadata fixtures, partial-check resume/abort behavior, remote repo checks, and repair-mode confirmation handling.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/docs/usage/check.rst.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/docs/usage/common-options.rst.inc -->
# sources/sync-backup/borg/docs/usage/common-options.rst.inc

Purpose: shared generated snippet listing Borg common CLI options.

Important APIs and control flow: covers help, log level selectors, debug topics, progress, unit formatting, JSON logs, lock wait, version/rc display, umask, remote path, upload throttling/buffering, profiling, SSH command selection, and repository selection via `-r/--repo`.

State and persistence: affects process-level behavior: log emission, JSON log format, lock wait timing, local umask, remote invocation, profiling output file, and selected repository.

Dependencies and integration points: included by generated command help tables and tied to jsonargparse common option definitions, logging setup, remote repository transports, and config/env precedence.

Risks: option ordering matters elsewhere in Borg. Log JSON and profiling outputs are machine-facing contracts. Remote path and `--rsh` can change execution target and security posture.

Test signals: generated snippets should update when common parser options change; CLI tests should verify each common option remains accepted before subcommands and in documented positions.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/docs/usage/common-options.rst.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/docs/usage/compact.rst.inc -->
# sources/sync-backup/borg/docs/usage/compact.rst.inc

Purpose: generated reference for `borg compact`, which frees repository space by deleting unreferenced objects.

Important APIs and control flow: options are `--dry-run` and `--stats`. The command analyzes all existing archives, determines referenced repository objects, and deletes unused objects. With `--stats`, it lists all objects to compute stored sizes and builds/caches a fresh chunks index.

State and persistence: mutates repository object storage by deleting unreferenced chunks. It also affects recoverability: soft-deleted archives can no longer be undeleted afterward.

Dependencies and integration points: follows `delete`/`prune`, interrupted create cleanup, repository corruption/lost archive detection, chunks index caching, and `check --find-lost-archives`.

Risks: compact can permanently remove data for soft-deleted or lost archives. Running immediately after interrupted backups can discard data that a retry might reuse. `--stats` may be much slower for some repositories.

Test signals: dry-run non-mutation, unused object deletion, stats before/after accounting, undelete failure after compact, and behavior with lost archive fixtures.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/docs/usage/compact.rst.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/docs/usage/completion.rst.inc -->
# sources/sync-backup/borg/docs/usage/completion.rst.inc

Purpose: generated reference for `borg completion`, which prints a shell completion script.

Important APIs and control flow: command takes a required `SHELL` choice from the completion generator's supported shell set. It emits completion code to stdout.

State and persistence: no repository mutation. Users may persist output into shell-specific completion locations outside Borg.

Dependencies and integration points: generated completions may call Borg dynamically for archive IDs and repository information, so they integrate with repository location and passphrase environment variables.

Risks: the visible `%(choices)s` placeholder suggests a generation bug or unresolved argparse interpolation in this include. Dynamic completion can hang or prompt if repository/passphrase access is not non-interactive.

Test signals: generated docs should render concrete shell choices; completion scripts should parse in supported shells and avoid interactive prompts when `BORG_REPO`/passphrase variables are set.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/docs/usage/completion.rst.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/docs/usage/create.rst.inc -->
# sources/sync-backup/borg/docs/usage/create.rst.inc

Purpose: generated reference for `borg create`, Borg's primary archive creation command.

Important APIs and control flow: accepts archive `NAME` and paths; supports dry-run, stats/JSON, item listing/filtering, stdin/content command input, externally supplied path lists, include/exclude rules, filesystem metadata toggles, files cache modes, file-change detection, `--read-special`, archive comments/timestamps/chunker/compression, hostname/username, and tags. Runtime recursively walks roots, applies slashdot prefix stripping, filters paths, chunks/hashes/compresses/encrypts content, writes metadata, and stores only new chunks.

State and persistence: creates archive metadata and data chunks in the repository and updates local caches for files/chunks. It stores extensive file metadata unless disabled.

Dependencies and integration points: pattern engine, files cache, chunker, compression help, placeholder expansion, metadata readers, stdin command execution, path-list parsing, and common options.

Risks: mtime cache modes can miss malicious or accidental timestamp rollback; inode-aware modes perform poorly on unstable network filesystems. Direct stdin piping can archive truncated output if producer fails; `--content-from-command` avoids that. `--one-file-system` mountpoint detection has Linux/macOS edge cases.

Test signals: archive creation with duplicate names, all files-cache modes, stdin and command input failure behavior, pattern ordering, metadata toggles, slashdot paths, list flags, JSON stats, and unchanged-file cache hits.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/docs/usage/create.rst.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/docs/usage/delete.rst.inc -->
# sources/sync-backup/borg/docs/usage/delete.rst.inc

Purpose: generated reference for `borg delete`, which soft-deletes one or more archives.

Important APIs and control flow: accepts optional archive `NAME`, `--dry-run`, `--list`, and archive filters including `--match-archives`, sort, first/last, and age windows. Multiple archives can be selected through match patterns.

State and persistence: marks archives for deletion in the repository but does not free disk space. The data remains recoverable with `borg undelete` until compaction.

Dependencies and integration points: archive matching help, repository manifest/archive directory, undelete, compact, and safety prompts/automatic answerers.

Risks: archive names need not be unique, so deleting by name or broad filters can affect multiple archives. Users may incorrectly expect disk space to be freed before compact.

Test signals: dry-run/list output, duplicate-name behavior, filter combinations, soft-delete visibility in repo-list/undelete, and compact making deletion permanent.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/docs/usage/delete.rst.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/docs/usage/diff.rst.inc -->
# sources/sync-backup/borg/docs/usage/diff.rst.inc

Purpose: generated reference for `borg diff`, which compares two archives' file content and metadata.

Important APIs and control flow: accepts `ARCHIVE1`, `ARCHIVE2`, optional pattern-capable paths, metadata/content options, `--same-chunker-params`, custom `--format`, JSON Lines, sorting, and `--content-only`. It compares matching items, uses chunk IDs when chunker parameters match, otherwise compares content, and reports added/removed/modified paths plus metadata changes.

State and persistence: read-only repository/archive operation. It may load metadata and chunks but does not write archive state.

Dependencies and integration points: pattern matching, archive item metadata, chunker parameters, Python format-string syntax, JSON Lines output, and sorting fields.

Risks: `--same-chunker-params` can force unsafe assumptions if archives are not comparable. Custom format keys are a user-facing contract. Content comparison can be much slower when chunker parameters differ.

Test signals: fixtures for added/removed/modified files, metadata-only changes, content-only suppression, JSON Lines schema, format variables, and stable multi-field sorting.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/docs/usage/diff.rst.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/docs/usage/export-tar.rst.inc -->
# sources/sync-backup/borg/docs/usage/export-tar.rst.inc

Purpose: generated reference for `borg export-tar`, which writes an archive or selected paths as a tar stream/file.

Important APIs and control flow: accepts archive `NAME`, output `FILE` or `-`, optional path selectors, `--tar-filter`, `--list`, `--tar-format`, include/exclude patterns, and `--strip-components`. Auto filtering chooses gzip, bzip2, xz, zstd, or lz4 by filename extension.

State and persistence: read-only against Borg repository; writes tar output to a file, stdout, or filter pipeline.

Dependencies and integration points: tar writer, archive extraction selection, compression filter subprocesses, metadata serialization, pattern engine, and progress pass over metadata.

Risks: metadata preservation depends on tar format: BORG preserves all Borg-supported metadata, PAX preserves substantial POSIX/xattr data, GNU loses ACLs/xattrs/bsdflags and nanosecond precision. Sparse export is unsupported.

Test signals: tar output validity for BORG/PAX/GNU, auto filter selection, stdout mode, pattern/strip behavior, list output, and round-trip import where supported.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/docs/usage/export-tar.rst.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/docs/usage/extract.rst.inc -->
# sources/sync-backup/borg/docs/usage/extract.rst.inc

Purpose: generated reference for `borg extract`, which restores files from an archive.

Important APIs and control flow: accepts archive `NAME`, optional pattern-capable paths, list/dry-run, numeric IDs, metadata toggles, stdout, sparse output, continue mode, include/exclude patterns, and strip-components. Default path interpretation is literal path prefix (`pp:`).

State and persistence: writes restored filesystem objects into the current working directory unless `--stdout` or `--dry-run` is used. `--continue` resumes an interrupted extraction of the same archive.

Dependencies and integration points: archive item reader, decrypt/decompress/hash verification, metadata restoration, pattern engine, sparse file handling, and filesystem permissions.

Risks: extraction always targets `.` so wrong working directory can restore into unintended locations. If parent directories are not extracted, parent metadata cannot be restored. `--progress` adds an extra metadata pass.

Test signals: dry-run hash/decrypt/decompress without writes, stdout mode, metadata toggles, sparse output, interrupted continue, strip-components skipping, and selected path pattern behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/docs/usage/extract.rst.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/docs/usage/general/archive-specification.rst.inc -->
# sources/sync-backup/borg/docs/usage/general/archive-specification.rst.inc

Purpose: general documentation for specifying a single archive by ID or by name.

Important APIs and control flow: describes `aid:` prefix matching on archive fingerprints, with enough hex digits to uniquely identify one archive, and name-based lookup for old-style unique archive names.

State and persistence: read-only reference material; it documents immutable archive IDs and mutable/user-chosen names.

Dependencies and integration points: used by commands accepting archive names, especially `info`, `list`, `extract`, `delete`, and quickstart examples. Cross-links to archive matching patterns.

Risks: ambiguous names are common when users intentionally create archive series with repeated names. Too-short ID prefixes must be rejected or disambiguated by runtime code.

Test signals: parser tests for `aid:` abbreviation uniqueness, duplicate-name handling, and cross-command consistency for archive spec resolution.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/docs/usage/general/archive-specification.rst.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/docs/usage/general/config.rst.inc -->
# sources/sync-backup/borg/docs/usage/general/config.rst.inc

Purpose: documents Borg configuration precedence and YAML config-file support.

Important APIs and control flow: precedence runs from source defaults, `$BORG_CONFIG_DIR/default.yaml`, explicit `--config` files in order, full `BORG_CONFIG`, environment variables, then command-line arguments left to right. Config parsing is implemented via `jsonargparse`; `--print_config` prints merged effective YAML and exits.

State and persistence: Borg reads config files and environment; it does not write config except user-directed output redirection from `--print_config`.

Dependencies and integration points: common/subcommand options, jsonargparse naming (`-` to `_`), default config directory discovery, and command-line ordering.

Risks: left-to-right CLI precedence means config files placed late can override earlier arguments. Users may assume `--print_config` ignores arguments after it; docs specify arguments given before it.

Test signals: precedence matrix tests, multiple config file override order, nested subcommand keys, environment overrides, and `--print_config` output validity.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/docs/usage/general/config.rst.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/docs/usage/general/date-time.rst.inc -->
# sources/sync-backup/borg/docs/usage/general/date-time.rst.inc

Purpose: documents Borg date/time formatting and accepted timespan suffixes.

Important APIs and control flow: Borg displays ISO 8601-style dates and 24-hour times, stores/processes UTC internally, and generally displays local time. TIMESPAN accepts numeric years, months, weeks, days, hours, minutes, or seconds using suffixes such as `2y`, `12m`, `2w`, `7d`, `8H`, `30M`, `150S`.

State and persistence: no state; defines parsing/display contracts used by filters and timestamps.

Dependencies and integration points: archive filters (`--oldest`, `--newest`, `--older`, `--newer`), archive timestamps, output formatting, and placeholder expansion.

Risks: suffix case matters for months/minutes and hours/seconds examples. Local display versus UTC storage can confuse automation around time zones.

Test signals: parsing tests for all suffixes, timezone-aware timestamp handling, and deterministic formatting in command outputs.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/docs/usage/general/date-time.rst.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/docs/usage/general/environment.rst.inc -->
# sources/sync-backup/borg/docs/usage/general/environment.rst.inc

Purpose: central reference for Borg environment variables, automation hooks, directory locations, build variables, and jsonargparse-derived env names.

Important APIs and control flow: documents repository defaults, passphrase sources and precedence (`BORG_PASSPHRASE`, command, FD, new/display/debug passphrases), modern exit-code mode, host ID, lock wait, logging config, remote shell/path, repository permissions, cache suffix/TTL, chunks archive usage, system info, msgpack checks, FUSE implementation order, self-tests, workarounds, output formats, automatic prompt answerers, platform-specific directory discovery through `platformdirs`, key file override, temp directories, and build prefixes.

State and persistence: environment controls repository selection, credentials, cache/config/data/runtime/security/key directories, temporary files, and runtime behavior. Some values can expose secrets or bypass safety prompts.

Dependencies and integration points: config precedence, logging.conf example, platformdirs, XDG/macOS/Windows paths, jsonargparse `default_env=True`, remote transports, locking, FUSE, cache, and setup/build scripts.

Risks: passphrases in environment can leak to other processes; automatic yes-sayers can bypass critical safety prompts; workarounds are emergency-only; disabling msgpack checks or selftests can mask corruption/compatibility problems.

Test signals: env precedence tests, secret-source priority, platform directory resolution, auto-answer validation, generated `BORG_<SUBCOMMAND>__<OPTION>` mappings, and build env handling.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/docs/usage/general/environment.rst.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/docs/usage/general/file-metadata.rst.inc -->
# sources/sync-backup/borg/docs/usage/general/file-metadata.rst.inc

Purpose: documents the filesystem metadata Borg can preserve and platform support limitations.

Important APIs and control flow: covers symlinks, device/FIFO metadata, optional special-file contents via `--read-special`, hard links within an archive, nanosecond timestamps, birthtime where available, owner/group IDs and names, Unix permissions, ACLs, extended attributes, and BSD/Linux flags.

State and persistence: these metadata fields are stored in archive item metadata and restored during extraction unless disabled.

Dependencies and integration points: create/extract metadata readers and writers, platform-specific ACL/xattr/flag APIs, `--numeric-ids`, `--noacls`, `--noxattrs`, `--noflags`, and `--read-special`.

Risks: platform and filesystem support differ substantially. Cross-platform restores can lose or map metadata imperfectly; Linux supports only selected flags; Cygwin ACL mapping is limited.

Test signals: platform matrix tests for ACL/xattr/flags, hardlink restoration, special-file metadata versus contents, timestamp precision, and metadata-disable options.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/docs/usage/general/file-metadata.rst.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/docs/usage/general/file-systems.rst.inc -->
# sources/sync-backup/borg/docs/usage/general/file-systems.rst.inc

Purpose: documents repository filesystem recommendations and the Borg 2 storage model based on `borgstore`.

Important APIs and control flow: recommends reliable journaling filesystems and explains that Borg uses `borgstore` as a key/value repository store, currently via `file:` posixfs locally or over SSH through `borg serve`, storing each chunk as a separate filesystem file in a nested layout.

State and persistence: repository data is persisted as many filesystem objects instead of Borg 1.x segment files.

Dependencies and integration points: borgstore backends, `file:`, SSH/remote `borg serve`, future `sftp:`/`rclone:` style backend possibilities, compact behavior, locking, and repository index behavior.

Risks: many files increase filesystem overhead and can reduce performance on filesystems with poor small-file/random-I/O behavior. Space overhead depends on allocation block strategy.

Test signals: repository creation/access on supported filesystems, high-object-count scalability, compact deleting individual chunks, remote borgstore access, and backend conformance tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/docs/usage/general/file-systems.rst.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/docs/usage/general/logging.rst.inc -->
# sources/sync-backup/borg/docs/usage/general/logging.rst.inc

Purpose: general logging reference for Borg's stderr behavior, log levels, and custom logging configuration.

Important APIs and control flow: Borg writes logs to stderr by default, with WARNING as the built-in default level. `--debug`, `--info`/`-v`/`--verbose`, `--warning`, `--error`, and `--critical` set thresholds. `BORG_LOGGING_CONF` can load a Python logging config, and shell redirection captures stderr to a file.

State and persistence: default behavior writes no log files; user redirection or custom config can persist logs.

Dependencies and integration points: common options, return codes, JSON logging, logging.conf example, and Python logging.

Risks: stderr does not imply failure; automation must check log levels and return codes. `--error`/`--critical` may hide important warnings.

Test signals: log-level filtering tests, stderr output behavior, JSON log compatibility, and custom logging config loading.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/docs/usage/general/logging.rst.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/docs/usage/general/positional-arguments.rst.inc -->
# sources/sync-backup/borg/docs/usage/general/positional-arguments.rst.inc

Purpose: documents Borg's option ordering constraints around positional arguments.

Important APIs and control flow: due to argparse limitations, Borg supports options entirely before or after positional arguments, and some mixed placements, but not options interleaved between archive/path positionals in all cases.

State and persistence: no state; defines command-line parser behavior.

Dependencies and integration points: Python argparse issue 15112, command parser wrappers, and every command with positional arguments.

Risks: users and generated scripts can fail if options are inserted between positionals, especially around archive names and paths. Documentation labels such forms as bad even if adjacent variants work.

Test signals: parser acceptance/rejection tests for options before, after, and between positional arguments across representative commands.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/docs/usage/general/positional-arguments.rst.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/docs/usage/general/repository-locations.rst.inc -->
# sources/sync-backup/borg/docs/usage/general/repository-locations.rst.inc

Purpose: documents how commands receive repository locations and archive names.

Important APIs and control flow: repository location comes from `-r/--repo` or `BORG_REPO`. Commands needing one or two archive names take them as positionals; commands operating over many archives usually accept `-a`.

State and persistence: no direct state; repository selection determines all subsequent repository reads/writes.

Dependencies and integration points: common `--repo`, environment configuration, archive filters, `borg mount` directory naming, and shell quoting.

Risks: archive names cannot contain `/` and should avoid shell- or filesystem-special characters. Ambiguous or awkward names complicate mount paths and scripts.

Test signals: repository env fallback, explicit repo override, archive-name validation, and command-specific positional/archive-filter parsing.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/docs/usage/general/repository-locations.rst.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/docs/usage/general/repository-urls.rst.inc -->
# sources/sync-backup/borg/docs/usage/general/repository-urls.rst.inc

Purpose: documents accepted repository URL/path forms.

Important APIs and control flow: supports local paths and `file://`; SSH REST-over-stdio `rest://`; legacy Borg RPC `ssh://`; `sftp://`; `rclone:remote:path`; and `(s3|b2):.../bucket/path` object storage URLs. Double slash after host denotes absolute remote path; single slash denotes relative path.

State and persistence: URL choice controls where repository objects and locks live and which credentials/transports are used.

Dependencies and integration points: transport layers, `borg serve`, borgstore backends, rclone, boto3/S3/B2 credentials, SSH user/port parsing, and `BORG_REPO`.

Risks: absolute versus relative remote URL syntax is easy to misread. Some S3-compatible services require `b2:` due to known compatibility issues. Credentials embedded in URLs can leak.

Test signals: parser tests for every URL family, absolute/relative remote path behavior, optional user/port parsing, BORG_REPO defaulting, and backend-specific smoke tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/docs/usage/general/repository-urls.rst.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/docs/usage/general/resources.rst.inc -->
# sources/sync-backup/borg/docs/usage/general/resources.rst.inc

Purpose: explains CPU, memory, disk, temporary-file, and network resource use for Borg operations.

Important APIs and control flow: splits client/server resource responsibilities. Create is CPU-heavy for chunking, hashing, compression, and encryption; extract/check read/decrypt/decompress; caches and repository indexes scale with chunk/file counts; remote use adds SSH transport CPU and network traffic.

State and persistence: local cache files store chunks and files indexes plus per-archive indexes; temporary directories can hold large FUSE/cache or remote data; repository indexes live server-side.

Dependencies and integration points: files cache, chunks index, repository index, compression levels, chunker parameters, FUSE mount cache, SSH transport, TMPDIR/TEMP/TMP, and server environment setup.

Risks: large repositories can exhaust RAM, cache disk, or remote `/tmp`; high compression can waste CPU/RAM; single-threaded Borg operations do not exceed one core except transport helpers.

Test signals: performance tests for cache/index scaling, remote TMPDIR behavior, compression memory profiles, and network throughput under client/server mode.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/docs/usage/general/resources.rst.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/docs/usage/general/return-codes.rst.inc -->
# sources/sync-backup/borg/docs/usage/general/return-codes.rst.inc

Purpose: documents Borg process return-code semantics.

Important APIs and control flow: rc `0` means success, `1` generic warning, `2` generic error, `3..99` specific errors, `100..127` specific warnings, and `128+N` signal termination. Specific codes require modern exit-code mode; `--show-rc` logs the return code as the last log entry.

State and persistence: no persistent state; process exit status and optional final log line are automation contracts.

Dependencies and integration points: `BORG_EXIT_CODES`, logging levels, message IDs, shell/systemd automation, and monitoring.

Risks: legacy mode collapses all warnings/errors to 1/2, so scripts expecting specific codes must ensure modern mode. Warnings may still complete the operation.

Test signals: command fixtures producing success, warning, generic error, specific errors/warnings, signal termination mapping, and `--show-rc` final log emission.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/docs/usage/general/return-codes.rst.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/docs/usage/general/units.rst.inc -->
# sources/sync-backup/borg/docs/usage/general/units.rst.inc

Purpose: documents Borg's quantity display conventions.

Important APIs and control flow: disk sizes use decimal SI powers (`kB` = 1000 bytes), while memory usage uses IEC binary prefixes (`KiB` = 1024 bytes).

State and persistence: no state; display-format contract for user output, logs, and docs.

Dependencies and integration points: stats output, progress displays, resource docs, benchmark output, and unit formatting controlled by common options such as `--iec`.

Risks: scripts parsing human output can misinterpret decimal versus binary units. Users may compare repository disk size and memory use using different scales.

Test signals: formatter tests for decimal and IEC units, `--iec` behavior where applicable, and stable output examples in generated docs.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/docs/usage/general/units.rst.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/docs/usage/help.rst.inc -->
# sources/sync-backup/borg/docs/usage/help.rst.inc

Purpose: generated help-topic include covering patterns, archive matching, placeholders, and compression.

Important APIs and control flow: pattern help defines `fm:`, `sh:`, `re:`, `pp:`, and `pf:` styles; include/exclude pattern file prefixes `R`, `P`, `-`, `!`, and `+`; first-match ordering; and command-line/file precedence. Archive matching supports name/id shell/regex/exact, `aid:`, user, host, and tags. Placeholders include hostname, fqdn, reverse-fqdn, now/utcnow with strftime, user, pid, and Borg version parts. Compression specs include none, lz4, zstd, zlib, lzma, auto, and obfuscate padding.

State and persistence: no direct state, but these topics define how archives are selected, files are included/excluded, archive names/comments are generated, and chunks are compressed.

Dependencies and integration points: Python fnmatch/re/string/datetime formatting, pattern engine hashtable path-full matching, create/extract/export/diff filters, archive filters, systemd escaping, compression libraries, encryption for obfuscation, and chunk size limits.

Risks: untrusted regex/shell/fnmatch patterns can cause expensive matching. `pf:` ignores context/order due to O(1) lookup. Placeholder percent escaping is tricky in systemd units. Compression obfuscation increases repository size and only makes sense with encryption.

Test signals: pattern precedence fixtures, Windows path conversion/reserved-character behavior, archive matching by every selector, placeholder expansion/escaping, compression spec parsing, and generated examples remaining runnable.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/docs/usage/help.rst.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/docs/usage/import-tar.rst.inc -->
# sources/sync-backup/borg/docs/usage/import-tar.rst.inc

Purpose: generated reference for `borg import-tar`, which creates a Borg archive from a tar stream/file.

Important APIs and control flow: accepts archive `NAME`, `TARFILE` or `-`, `--tar-filter`, stats/list/filter/JSON, `--ignore-zeros`, and archive options for comment, timestamp, chunker, and compression. Auto filtering detects compressed tar input by extension and runs the matching decompressor.

State and persistence: writes a new archive and chunks to the repository. It reads tar metadata and content from file, stdin, or a filter pipeline.

Dependencies and integration points: tar readers for BORG/PAX/GNU/ustar/V7/SunOS xattr formats, compression filter subprocesses, create-like archive options, repository encryption/passphrase flow, and stats/JSON output.

Risks: unlike `create`, this command does not support excluding files. Sparse import is unsupported. Concatenated tarballs require `--ignore-zeros` to skip end markers.

Test signals: imports from each supported tar format, stdin mode, auto and explicit filter modes, concatenated tar with ignore-zeros, JSON stats, metadata conservation compared with export-tar.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/docs/usage/import-tar.rst.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/docs/usage/info.rst.inc -->
# sources/sync-backup/borg/docs/usage/info.rst.inc

Purpose: generated reference for `borg info`, which displays detailed archive information.

Important APIs and control flow: accepts optional archive `NAME`, `--json`, and archive filters. It can target a single archive or filtered archive set depending on command implementation and filter use.

State and persistence: read-only metadata query. It reads repository/archive metadata and emits human or JSON output.

Dependencies and integration points: archive specification and matching, stats accounting, JSON output, common repository options, and deduplication/chunk index concepts.

Risks: deduplicated size for an individual archive means chunks unique to that archive, while all-archives deduplicated size means all chunks in the repository; adding per-archive numbers is wrong.

Test signals: human and JSON output schema, duplicate archive names with `aid:` selection, filtered archive info, and size accounting fixtures with shared chunks.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/docs/usage/info.rst.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/docs/usage/key_add.rst.inc -->
# sources/sync-backup/borg/docs/usage/key_add.rst.inc

Purpose: generated reference for `borg key add`, which adds another Borg key/passphrase wrapper to a repository.

Important APIs and control flow: command-specific option is `--label LABEL`, which must be unique. The command creates an additional Borg key containing the same secret key material as existing keys, protected by an independent passphrase read from `BORG_NEW_PASSPHRASE` or interactively.

State and persistence: mutates repository key metadata by adding a new labeled key. It does not re-encrypt repository data and does not alter existing keys.

Dependencies and integration points: repository encryption/key management, passphrase prompting/env handling, key labels, admin key protections, and future key deletion/unlock flows.

Risks: label collisions must be rejected. The initial `admin` label is reserved and protected from deletion. New key compromise exposes the same repository data because secret key material is shared.

Test signals: adding a key with a unique label, rejecting duplicate/reserved labels, unlocking repository with either old or new passphrase, ensuring no data rewrite occurs, and non-interactive `BORG_NEW_PASSPHRASE` handling.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/docs/usage/key_add.rst.inc -->
