# Research Report: subset-b-009202

This grouped report covers Syncthing versioner helpers/tests, filesystem watch aggregation, metadata/protocol maintenance files, release and translation scripts, and integration fixtures/tests. Each section is bounded for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/versioner/trashcan_test.go -->
## sources/sync-backup/syncthing/lib/versioner/trashcan_test.go

Purpose: exercises trashcan versioning behavior where archived files keep their original names instead of timestamp-tagged names. It validates restore-over-existing-file handling, restore of deleted files, and age-based cleanup of `.stversions`.

Important APIs and helpers: `TestTrashcanArchiveRestoreSwitcharoo`, `TestTrashcanRestoreDeletedFile`, `TestTrashcanCleanOut`, plus local `readFile`/`writeFile` wrappers over `fs.Filesystem`. The tests build `config.FolderConfiguration` values with basic folder and versioning filesystems, then instantiate `newTrashcan`.

Control flow: files are written to the folder filesystem, archived into the version filesystem, and restored through `Versioner.Restore`. The switcharoo test confirms an existing live file is archived before the requested version is moved back. The cleanout test creates old and fresh files under `.stversions`, runs `Clean`, then checks both file removal and empty directory pruning.

State and persistence: all state is filesystem-backed under temporary directories. Version times for trashcan files are represented by mtime because filenames are untagged.

Dependencies and integration: depends on `lib/config`, `lib/fs`, and the trashcan implementation in this package. Test signals cover mtime truncation, version inventory, restore collision safety, and cleanup directory retention. Risks are mostly time granularity and untagged-name collision behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/versioner/trashcan_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/versioner/util.go -->
## sources/sync-backup/syncthing/lib/versioner/util.go

Purpose: contains shared versioner mechanics: filename tagging, version discovery, archival, restoration, version filesystem resolution, and cleanup support.

Important APIs/types/functions: exported `ErrDirectory`, `DefaultPath`, `TagFilename`, `UntagFilename`; package helpers `retrieveVersions`, `archiveFile`, `dupDirTree`, `restoreFile`, `versionerFsFromFolderCfg`, `findAllVersions`, `clean`, and `cleanVersions`. `fileTagger` abstracts tagged versus untagged version naming.

Control flow: `archiveFile` checks source existence, rejects symlinks by panic, ensures destination root, duplicates directory tree permissions, then `RenameOrCopy`s a source file to the version filesystem and fixes mtime. `restoreFile` archives or removes anything currently at the restore path, locates either tagged or untagged source versions, then moves it back. `clean` walks version storage, groups tagged versions by original filename, applies a retention callback, and removes empty directories via `emptyDirTracker`.

State and persistence: all persistent state is version files and mtimes. Version identity uses `TimeFormat` tags for most versioners and mtime for trashcan-style untagged files.

Dependencies and integration: uses Syncthing filesystem abstractions, `osutil.RenameOrCopy`, path normalization, config filesystem types, and structured logging. Risks include local timezone parsing, second-level time truncation, symlink assumptions, and permission propagation across different filesystem backends. Tests in adjacent versioner packages and trashcan tests exercise restore and cleanup paths.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/versioner/util.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/versioner/versioner.go -->
## sources/sync-backup/syncthing/lib/versioner/versioner.go

Purpose: defines the common file versioning interface and factory registry used by concrete Syncthing versioners.

Important APIs/types/functions: `Versioner` exposes `Archive`, `GetVersions`, `Restore`, and `Clean`; `FileVersion` is the JSON-facing version metadata tuple of `VersionTime`, `ModTime`, and `Size`; `New` looks up `factories[cfg.Versioning.Type]`; `ErrRestorationNotSupported`, `TimeFormat`, and `timeGlob` standardize error and timestamp handling.

Control flow: concrete versioner packages register a `factory` in the package-level `factories` map. `New` fails for unknown type, otherwise wraps the concrete implementation in `versionerWithErrorContext`. The wrapper preserves behavior but annotates operation failures with versioner type and operation name.

State and persistence: this file owns no persistent state. The registry is in-process package state, while concrete implementations own filesystem persistence.

Dependencies and integration: integrates with `config.FolderConfiguration` and downstream versioner implementations. Risks are global registry mutation order and error wrapping expectations in callers. Test signals come from concrete versioner tests that call `New` and assert archive/restore semantics.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/versioner/versioner.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/watchaggregator/aggregator.go -->
## sources/sync-backup/syncthing/lib/watchaggregator/aggregator.go

Purpose: coalesces raw filesystem watcher events into bounded scan path batches, delaying noisy changes and ordering removes after non-removes when useful.

Important APIs/types/functions: public `Aggregate`; internal `aggregator`, `eventDir`, `aggregatedEvent`, `eventCounter`, `newAggregator`, `mainLoop`, `newEvent`, `aggregateEvent`, `actOnTimer`, `notify`, `popOldEventsTo`, `isOld`, `CommitConfiguration`, and `notifyTimeout`. Tunables `maxFiles` and `maxFilesPerDir` cap event fan-out.

Control flow: `mainLoop` listens to fs events, config updates, in-progress item events, timer firings, and context cancellation. `aggregateEvent` stores paths in a tree, collapses overfull directories to parent paths, and collapses global overflow or `"."` to a full-folder scan. Timer handling pops old events, optionally releases remaining remove events early when only removes remain, and sends batches asynchronously in NonRemove, Mixed, Remove order.

State and persistence: all state is in-memory: event tree, counters, timers, in-progress path set, and folder config. No disk persistence.

Dependencies and integration: connects `lib/fs.Event`, `lib/config.Wrapper` subscriptions, `lib/events` item lifecycle events, and model scan scheduling via the output channel. Risks include timing flakiness, channel backpressure, stale in-progress tracking, and path normalization across platforms. Unit tests cover aggregation caps, delays, remove ordering, and in-progress filtering.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/watchaggregator/aggregator.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/watchaggregator/aggregator_test.go -->
## sources/sync-backup/syncthing/lib/watchaggregator/aggregator_test.go

Purpose: verifies the watch aggregator's coalescing, timing, batching, and in-progress suppression behavior.

Important APIs/functions: `TestMain` lowers `maxFiles` and `maxFilesPerDir`; `TestAggregate` validates path tree collapse; `TestInProgress` validates event suppression for Syncthing-owned writes; `TestDelay` and `TestNoDelay` validate timeout and remove batching; helpers include `testScenario`, `testAggregatorOutput`, `compareBatchToExpected`, and `getEventPaths`.

Control flow: tests create a mock aggregator with a basic folder config and feed events through either direct `newEvent` calls or the real `mainLoop`. Expected batches include path groups and timing windows. `testAggregatorOutput` consumes scan batches until all expectations are met or a ten-second timeout fires.

State and persistence: state is in-memory and time-driven. Tests mutate package-level caps and restore them after `m.Run`.

Dependencies and integration: uses `config.Wrapper`, `events.Logger`, `fs.Event`, and `protocol.LocalDeviceID`. Test signals are strong for logical batching but inherently time-sensitive; Darwin bypasses strict timing checks to avoid platform flakiness.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/watchaggregator/aggregator_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/watchaggregator/debug.go -->
## sources/sync-backup/syncthing/lib/watchaggregator/debug.go

Purpose: provides the package logger used by the watch aggregator.

Important APIs/types/functions: package variable `l` is initialized via `slogutil.NewAdapter("Filesystem event watcher")`.

Control flow: there is no runtime control flow beyond package initialization. Other files call `l.Debugln` and `l.Debugf` for aggregation, timer, and lifecycle trace messages.

State and persistence: the only state is the logger adapter. It does not persist aggregator state.

Dependencies and integration: depends on `internal/slogutil` and integrates with Syncthing's debug/logging facilities. Risk is minimal; incorrect adapter naming would affect log filtering and diagnostics rather than behavior. Test signal is indirect through any test that exercises debug calls.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/watchaggregator/debug.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/man/refresh.sh -->
## sources/sync-backup/syncthing/man/refresh.sh

Purpose: refreshes checked-in manual pages from `https://docs.syncthing.net/man/`.

Important APIs/functions: Bash array `pages` lists all manual page filenames; the loop runs `curl -sLO "$base$page"` for each page.

Control flow: sequentially downloads each configured manpage into the current working directory. There is no validation, checksum, retry, or temporary-file staging.

State and persistence: overwrites or creates local files named by the `pages` array. Network state comes from the public docs site.

Dependencies and integration: depends on Bash and `curl`. It integrates with release/documentation maintenance, not runtime Syncthing. Risks include silent partial downloads due to `-s`, accidental execution from the wrong directory, and lack of failure aggregation. Test signal is manual or CI script invocation rather than a Go test.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/man/refresh.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/meta/copyright_test.go -->
## sources/sync-backup/syncthing/meta/copyright_test.go

Purpose: CI/meta test ensuring source files carry acceptable copyright or generated-code headers.

Important APIs/functions: `TestCheckCopyright` walks `copyrightCheckDirs`; `checkCopyright` filters regular `.go` and `.sql` files and scans the top five lines for `copyrightRe`.

Control flow: each configured directory is recursively walked. Files outside the extension set are ignored. Matching any configured regexp allows the file; otherwise `checkCopyright` returns an error naming the path.

State and persistence: read-only scan of repository files. No state is written.

Dependencies and integration: uses `filepath.Walk`, regexps, and OS file reads. It integrates with test/CI policy across `cmd`, `internal`, `lib`, `test`, and `script`. Risks include false negatives for generated files whose header changes, and false positives from broad `Copyright` matching. Test signal is direct via `go test ./meta`.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/meta/copyright_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/meta/forbidden_words_test.go -->
## sources/sync-backup/syncthing/meta/forbidden_words_test.go

Purpose: enforces repository-wide source hygiene by rejecting banned text in Go files.

Important APIs/functions: `TestForbiddenWords` defines checked directories and `forbiddenWords`, currently rejecting the deprecated `"io/ioutil"` import.

Control flow: recursively walks `../cmd`, `../lib`, `../test`, and `../script`; skips `.git`, non-Go files, and generated `.pb.go` files; reads each file and reports any forbidden byte sequence with `t.Errorf`.

State and persistence: read-only repository scan.

Dependencies and integration: uses `bytes.Contains`, `os.ReadFile`, and `filepath.Walk`. It is a CI policy gate. Risks include string-literal false positives and missing generated files by design. Test signal is the failing path and forbidden token.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/meta/forbidden_words_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/meta/gofmt_test.go -->
## sources/sync-backup/syncthing/meta/gofmt_test.go

Purpose: enforces canonical Go formatting and simplification.

Important APIs/functions: `TestCheckGoFmt` walks `gofmtCheckDirs` and runs `gofmt -s -d` on each non-generated Go file.

Control flow: for every eligible file, it invokes `exec.Command("gofmt", "-s", "-d", path)`. Command errors fail the walk, and non-empty diff output is reported as a formatting failure.

State and persistence: read-only check; it does not rewrite files.

Dependencies and integration: depends on a `gofmt` binary in PATH and the Go toolchain. It integrates with CI and local developer checks. Risks are environment-related failures when `gofmt` is missing and skipped `.pb.go` generated files. Test signal is the exact diff emitted by `gofmt`.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/meta/gofmt_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/proto/apiproto/tokenset.proto -->
## sources/sync-backup/syncthing/proto/apiproto/tokenset.proto

Purpose: defines API token-set persistence/serialization schema.

Important APIs/types: package `apiproto`; message `TokenSet` with `map<string, int64> tokens = 1`, documenting token to expiry time in epoch nanoseconds.

Control flow: no executable control flow; generated code will provide marshaling, unmarshaling, and map accessors.

State and persistence: represents persistent or wire-serialized API token expiry state. Field number 1 is the compatibility contract.

Dependencies and integration: uses proto3 map semantics and integrates with generated Go code for API authentication/token management. Risks are time-unit confusion and schema compatibility if field numbers or types change. Test signals are generated-code compilation and API/token tests elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/proto/apiproto/tokenset.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/proto/bep/bep.proto -->
## sources/sync-backup/syncthing/proto/bep/bep.proto

Purpose: defines the Block Exchange Protocol message schema used between Syncthing devices.

Important APIs/types: pre-auth `Hello`; message `Header`; enums for message type, compression, folder type, stop reason, file info type, response errors, and download progress updates; core messages `ClusterConfig`, `Folder`, `Device`, `Index`, `IndexUpdate`, `FileInfo`, `BlockInfo`, `Vector`, `Counter`, `PlatformData`, `Request`, `Response`, `DownloadProgress`, `Ping`, and `Close`.

Control flow: no executable flow; message flow is implicit in protocol sequencing: hello/header, cluster config, index updates, block requests/responses, progress, pings, and close.

State and persistence: `FileInfo` carries replicated file metadata, vector clocks, block hashes, platform metadata, and host-local fields with high field numbers. Reserved fields protect compatibility.

Dependencies and integration: imported by generated Go protocol code, database schemas, and network exchange logic. Risks are wire compatibility, semantic drift of host-local fields, reserved-field reuse, and enum default behavior. Test signals include protocol compatibility, generated code compilation, and integration sync tests that exchange these messages.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/proto/bep/bep.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/proto/dbproto/structs.proto -->
## sources/sync-backup/syncthing/proto/dbproto/structs.proto

Purpose: defines protobuf records persisted in Syncthing's database layer.

Important APIs/types: imports `bep/bep.proto` and `google/protobuf/timestamp.proto`; defines `FileInfoTruncated`, `FileVersion`, `VersionList`, `BlockList`, `IndirectionHashesOnly`, `Counts`, `CountsSet`, `ObservedFolder`, and `ObservedDevice`.

Control flow: schema-only. Database code serializes/deserializes these messages for file metadata, version lists, block lists, folder/device observation, and count buckets.

State and persistence: persistence is central here. `FileInfoTruncated` mirrors BEP `FileInfo` without blocks while preserving field numbers; `Counts` stores file/directory/symlink/deleted/bytes/sequence counters per folder/device or global state; observed records include timestamps and labels.

Dependencies and integration: tightly coupled to BEP schema and database migration compatibility. Risks include field-number mismatches with `bep.FileInfo`, losing host-local fields, and changing timestamp or sequence semantics. Test signals are database upgrade/load tests and generated-code compilation.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/proto/dbproto/structs.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/proto/discoproto/local.proto -->
## sources/sync-backup/syncthing/proto/discoproto/local.proto

Purpose: defines the local discovery announce payload.

Important APIs/types: package `discoproto`; message `Announce` with raw device `id`, repeated `addresses`, and `instance_id`.

Control flow: schema-only; local discovery code broadcasts or receives generated announce messages.

State and persistence: no durable persistence implied. The message carries transient discovery state: device identity, reachable addresses, and instance identity to distinguish process restarts.

Dependencies and integration: integrates with local discovery networking and generated protobuf code. Risks include malformed address lists, raw device ID length assumptions, and compatibility if field numbers change. Test signal is generated-code compilation and local discovery integration tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/proto/discoproto/local.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/proto/discosrv/discosrv.proto -->
## sources/sync-backup/syncthing/proto/discosrv/discosrv.proto

Purpose: defines discovery server database and replication records.

Important APIs/types: package `discosrv`; `DatabaseRecord`, `ReplicationRecord`, and `DatabaseAddress`. Addresses carry a string address and expiration time in Unix nanoseconds; records carry last-seen time and, for replication, the raw 32-byte device ID key.

Control flow: schema-only. Server code stores, serves, and replicates records using generated serialization.

State and persistence: explicitly persistent discovery database state and replication payloads.

Dependencies and integration: discovery server database/replication layers depend on field compatibility. Risks include time-unit mistakes, expired address retention, and raw key length assumptions. Test signal is generated-code compilation and discovery server tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/proto/discosrv/discosrv.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/script/authors.go -->
## sources/sync-backup/syncthing/script/authors.go

Purpose: maintenance generator that updates `AUTHORS` and the GUI contributor list from repository history.

Important APIs/types/functions: `author`, `authorSet`, `getAuthors`, `addAuthors`, `filteredAuthors`, `stringSet`, and regexps for nicknames, emails, and bots.

Control flow: reads existing `AUTHORS`, scans tracked source-relevant files via `git ls-tree`, runs `git log --follow` per file, records authors and co-authors while skipping known bad commits, filters bot/zero-commit entries, sorts by logarithmic commit bucket then name, rewrites `aboutModalView.html`, and rewrites `AUTHORS`.

State and persistence: writes two repository files. Commit sets are in-memory and keyed by email.

Dependencies and integration: depends on Git, AUTHORS format, and the GUI HTML marker `id="contributor-list"`. Risks include expensive per-file history scans, fragile HTML regexp replacement, email alias merging edge cases, and bot filtering misses. Test signal is mostly review of generated diffs.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/script/authors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/script/codecov-upload.sh -->
## sources/sync-backup/syncthing/script/codecov-upload.sh

Purpose: vendored Codecov Bash uploader that detects CI metadata, discovers coverage reports, builds an upload payload, and sends it to Codecov.

Important APIs/functions: command-line parser for many short options; `show_help`, `say`, `urlencode`, `swiftcov`, `parse_yaml`, `cleanup`; feature toggles for gcov, coverage.py, search, network, Xcode, S3, report fixing, HTML/YAML inclusion, and direct upload.

Control flow: initializes defaults from environment, parses flags, detects tools, detects CI provider from environment, resolves branch/commit/slug/token/url from overrides/env/yaml/VCS, optionally runs Xcode/gcov/coverage.py processing, searches for coverage reports while pruning dependency/cache paths, builds a network file list, appends reports and adjustments to a temp upload file, optionally dumps/saves it, gzips it, then uploads via Codecov v4 S3 pre-signed flow or v2 fallback.

State and persistence: creates temp upload and adjustments files, optional saved payload, optional deletion of coverage files with `-c`. Network state includes Codecov and optional AWS storage targets.

Dependencies and integration: Bash, curl, git/hg, find, awk/sed, gzip, gcov, coverage.py, xcrun/plutil for Apple coverage. Risks include shell quoting/eval complexity, credentials in query construction, many CI-provider branches, temp cleanup only on selected signals, and reliance on deprecated Codecov bash behavior. Test signal is CI coverage upload success/failure logs.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/script/codecov-upload.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/script/commit-msg.go -->
## sources/sync-backup/syncthing/script/commit-msg.go

Purpose: Git hook/helper validating Syncthing commit subject style.

Important APIs/functions: regexp `subject = ^[\w/,\. ]+: \w`; constants `exitSuccess` and `exitError`; `main` reads one filename argument and checks the first line.

Control flow: validates argument count, reads the commit message file, splits by newline, tests the subject line, prints a diagnostic with the expected pattern on failure, and exits with status 1.

State and persistence: read-only access to the commit message file.

Dependencies and integration: standard library only; intended for Git commit-msg hook use. Risks include narrow allowed tag characters, no empty-file guard before `lines[0]`, and style-only enforcement. Test signal is hook exit code.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/script/commit-msg.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/script/copyrights.go -->
## sources/sync-backup/syncthing/script/copyrights.go

Purpose: maintenance generator that updates third-party copyright notices in the GUI about modal based on modules used by `cmd/syncthing`.

Important APIs/types/functions: `CopyrightNotice`, `Type` enum, hard-coded `copyrightMap`/`urlMap`, `getModules`, `parseCopyrightNotices`, `parseGitHubURL`, `getLicenseText`, `extractCopyrights`, `defaultCopyright`, and `write`.

Control flow: parses current notices from `aboutModalView.html`, lists modules and packages via `go list`, matches existing notices to live modules, marks unused notices for removal, adds new module notices, resolves known or GitHub license copyrights for new modules, then rewrites the HTML list in sorted order while preserving JS/static notices.

State and persistence: writes `gui/default/syncthing/core/aboutModalView.html`. Network state may be read from GitHub API, optionally authenticated by `GITHUB_TOKEN`.

Dependencies and integration: Go toolchain, module graph, HTML parser, GitHub API. Risks include rate limiting, fragile matching by substring, default copyright fallback quality, and generated HTML churn. Test signal is the resulting diff and successful command execution.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/script/copyrights.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/script/docker-entrypoint.sh -->
## sources/sync-backup/syncthing/script/docker-entrypoint.sh

Purpose: container entrypoint that adjusts capabilities, ownership, umask, and user before launching Syncthing.

Important APIs/functions: shell checks for `UMASK`, root UID, `PCAP`, `PUID`, `PGID`, and `HOME`; uses `setcap`, `chown`, `su-exec`, and `exec`.

Control flow: sets umask if requested. When running as root, removes capabilities from the binary unless `PCAP` is set, otherwise applies requested capabilities, tries to chown home, then re-execs as `PUID:PGID` with HOME preserved. Non-root execution directly execs the command.

State and persistence: mutates binary capabilities and home directory ownership inside the container filesystem.

Dependencies and integration: Docker image runtime, Linux capabilities, `su-exec`. Risks include missing `PUID`/`PGID`, capability operations unavailable in restricted containers, and ignored chown failures. Test signal is container startup behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/script/docker-entrypoint.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/script/genassets.go -->
## sources/sync-backup/syncthing/script/genassets.go

Purpose: generates Go source embedding static assets into an `assets.Asset` map.

Important APIs/types/functions: template `tpl`, `asset`, `templateVars`, `walkerFor`, and `main` with `-o` output flag.

Control flow: walks the input directory, skips dotfiles, reads regular files, gzip-compresses each and keeps the gzipped payload only when smaller, records original length and slash-normalized relative name, renders a Go source template, formats it with `go/format`, and writes to stdout or output file.

State and persistence: output is generated Go code. The generated modification time is current Unix time or `SOURCE_DATE_EPOCH` for reproducible builds.

Dependencies and integration: standard library plus `lib/assets` in the generated code. Risks include embedding binary data as quoted strings, no sorting before template output, ignored walk/template write errors in some paths, and reproducibility depending on stable walk order. Test signal is generated code compilation and asset-serving behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/script/genassets.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/script/next-version.go -->
## sources/sync-backup/syncthing/script/next-version.go

Purpose: release helper that computes the next Syncthing semver tag.

Important APIs/functions: flag `-pre`, constant `suffix = "rc"`, helper `cmd`, and dependency `github.com/coreos/go-semver/semver`.

Control flow: finds latest tag and latest stable tag using `git describe`, parses both, scans commit subjects since latest stable for `feat` prefix to choose minor versus patch, handles stable release from an existing prerelease, increments prerelease counters when appropriate, or emits a new `rc.1`.

State and persistence: read-only Git history/tag inspection; output is printed tag string.

Dependencies and integration: Git tag naming convention `v[0-9].*`, semver library, release process. Risks include relying only on subject prefix for feature detection, prerelease parsing assumptions, and shallow clone tag availability. Test signal is command output under representative tag histories.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/script/next-version.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/script/prune_mocks.go -->
## sources/sync-backup/syncthing/script/prune_mocks.go

Purpose: cleanup helper for generated mocks, removing compile-time interface assertion lines and reformatting imports.

Important APIs/functions: flag `-t`, `pruneInterfaceCheck`, and `main` walking the target path.

Control flow: recursively walks target files, skips non-regular entries, rewrites each file to a temp file omitting lines whose trimmed content starts with `var _ `, replaces the original, then runs `go tool goimports -w`.

State and persistence: destructively rewrites files under the target tree.

Dependencies and integration: filesystem, `goimports` installed as a Go tool, generated mock layout. Risks include broad deletion of any `var _` line, temp file creation in current directory instead of target directory, partial rewrite if errors occur after original removal, and unchecked scanner errors. Test signal is generated mocks compiling after pruning.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/script/prune_mocks.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/script/relnotes.go -->
## sources/sync-backup/syncthing/script/relnotes.go

Purpose: release helper that combines repository-provided release note templates with GitHub-generated release notes.

Important APIs/functions: flags `--new-ver`, `--prev-ver`, `--branch`; `additionalNotes`, `generatedNotes`, and `removeHTMLComments`; env `GITHUB_TOKEN` and optional `GITHUB_REPOSITORY`.

Control flow: validates version and token, loads note templates from `relnotes/<version>.md` while progressively stripping patch/minor suffixes, executes them with the version value, POSTs to GitHub `releases/generate-notes`, strips HTML comments, and prints note blocks separated by blank lines.

State and persistence: read-only repository files; network read from GitHub API; output to stdout.

Dependencies and integration: GitHub API version header, templates, release workflow. Risks include required token, API failures, template errors, and comment stripping regex only handling single-line comments. Test signal is release-note output and API status.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/script/relnotes.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/script/transifexdl.go -->
## sources/sync-backup/syncthing/script/transifexdl.go

Purpose: legacy translation downloader for Transifex-hosted GUI translations.

Important APIs/types/functions: `stat`, `translation`, `userPass`, `req`, `loadValidLangs`, `languageName`, `saveValidLangs`, and `saveLanguageNames`.

Control flow: requires `TRANSIFEX_USER` and `TRANSIFEX_PASS`, loads current valid languages, fetches resource stats, applies completion thresholds of 75 percent for currently valid languages and 95 percent for new languages, downloads each accepted non-English translation to `lang-<code>.json`, removes low-completion language files, and rewrites `valid-langs.js` and `prettyprint.js`.

State and persistence: writes/removes translation JSON and language metadata files in the current directory.

Dependencies and integration: Transifex API v2, basic auth, JSON, language metadata endpoint. Risks include division by zero if totals are zero, no HTTP status checks, credential requirements, and regex parsing of JS language arrays. Test signal is generated translation file diff.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/script/transifexdl.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/script/translate.go -->
## sources/sync-backup/syncthing/script/translate.go

Purpose: extracts GUI translation strings from HTML/JS and merges them into an existing translation JSON.

Important APIs/functions: regexps for Angular translate attributes and `$translate.instant`, `generalNode`, `inTranslate`, `isTranslated`, `translation`, `walkerFor`, `collectThemes`, and `main`.

Control flow: reads existing translation JSON into a nested map, walks GUI files, parses HTML nodes and JS lines, records explicit translate text/ids, logs suspicious untranslated text nodes or data-content strings, adds theme names for GUI theme directories, then writes pretty JSON to stdout.

State and persistence: updates only in-memory translation map and writes JSON output; caller decides file replacement.

Dependencies and integration: `golang.org/x/net/html`, GUI template conventions, Angular translation syntax. Risks include regex-based JS extraction, deprecated `strings.Title`, nested map type assertions, and warning exceptions going stale. Test signal is output JSON diff and translation warning logs.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/script/translate.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/script/weblatedl.go -->
## sources/sync-backup/syncthing/script/weblatedl.go

Purpose: translation downloader for Weblate-hosted Syncthing GUI translations.

Important APIs/types/functions: `stat`, `translation`, `reformatLanguageCode`, `saveValidLangs`, `saveLanguageNames`, `req`, and `loadValidLangs`.

Control flow: requires `WEBLATE_TOKEN`, loads currently valid languages, fetches component statistics, normalizes language codes, applies the same 75/95 percent acceptance thresholds, downloads every non-English translation file to `lang-<code>.json`, and rewrites `valid-langs.js` plus `prettyprint.js`.

State and persistence: writes language JSON and metadata files in the current working directory.

Dependencies and integration: Weblate API token auth, hosted.weblate.org endpoints, GUI language file format. Risks include no HTTP status validation, division by zero on bad stats, downloading low-completion non-English files even when not accepted into valid list, and regex JS array parsing. Test signal is generated file diff.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/script/weblatedl.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/test/cli_test.go -->
## sources/sync-backup/syncthing/test/cli_test.go

Purpose: integration tests for Syncthing CLI startup and home/database generation/reset behavior.

Important APIs/functions: `TestCLIReset`, `TestCLIGenerate`, and `TestCLIFirstStartup`. They run `../bin/syncthing` with `--reset-database`, `--generate`, or `--home` and inspect resulting filesystem state.

Control flow: reset test creates an index directory, runs reset, then ensures it is removed. generate test removes `home.out`, invokes generation, and checks config and key/cert files. first-startup test starts Syncthing with `STNORESTART=1`, concurrently waits for required files and process exit, then kills the process after creation succeeds.

State and persistence: mutates `h1/index-v0.14.0.db`, `home.out`, generated certificates, keys, and reset backup directories.

Dependencies and integration: external built binary, OS process management, local filesystem. Risks include port/environment leakage, process timing races, and stale generated files. Test signal is file existence and process exit behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/test/cli_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/test/conflict_test.go -->
## sources/sync-backup/syncthing/test/conflict_test.go

Purpose: integration tests for conflict creation and resolution across two Syncthing peers.

Important APIs/functions: `TestConflictsDefault`, `TestConflictsInitialMerge`, `TestConflictsIndexReset`, and `TestConflictsSameContent`.

Control flow: tests clean data/index directories, create divergent file states, start h1/h2 instances, resume devices, force or delay scans, pause/resume peer links to create simultaneous edits or edit/delete conflicts, then use `rc.AwaitSync`, glob checks, content checks, and directory-content comparison.

State and persistence: uses `s1`, `s2`, and `h1/h2` index directories. Conflict artifacts are files containing `sync-conflict` in the name. Index reset test deliberately deletes `h2/index*`.

Dependencies and integration: `lib/rc` process API, local Syncthing instances, filesystem mtimes, helper functions from the integration suite. Risks include timing sensitivity, conflict filename expectations, and index-reset behavior changing with database logic. Test signals assert conflict counts, propagated contents, and same-content non-conflict handling.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/test/conflict_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/test/delay_scan_test.go -->
## sources/sync-backup/syncthing/test/delay_scan_test.go

Purpose: integration stress test for concurrent delayed rescan requests.

Important APIs/functions: `TestRescanWithDelay` and `st.RescanDelay("default", 1)` invoked from 20 goroutines.

Control flow: cleans `s1` and h1 indexes, generates 50 files, writes `.stignore`, starts instance 1, launches parallel delayed rescans, waits for all to return, sleeps briefly, and stops the instance. The stop helper checks logs for races/errors.

State and persistence: data under `s1`, `.stignore`, h1 database files.

Dependencies and integration: Syncthing REST/control API via integration helpers, concurrent Go test execution, filesystem scanning internals. Risks include data-race exposure, request coalescing regressions, and delayed scan scheduling bugs. Test signal is absence of errors/race output rather than a final directory comparison.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/test/delay_scan_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/test/filetype_test.go -->
## sources/sync-backup/syncthing/test/filetype_test.go

Purpose: verifies synchronization when filesystem object types change between file and directory under different receiver versioning modes.

Important APIs/functions: `TestFileTypeChange`, `TestFileTypeChangeSimpleVersioning`, `TestFileTypeChangeStaggeredVersioning`, and shared `testFileTypeChange`.

Control flow: each wrapper edits `h2/config.xml` to set no/simple/staggered versioning, preserving the original config. The shared test creates files and directories that are later replaced by the opposite type, syncs initial state, delays sender scans, performs replacements, rescans, awaits sync, and compares `s1`/`s2`.

State and persistence: mutates `s1`, `s2`, h1/h2 indexes, and temporarily rewrites h2 config.

Dependencies and integration: `lib/config`, `events`, `protocol`, `rc`, and versioner implementations. Risks include platform filesystem semantics, versioner interaction with replaced directories, and config restore failures. Test signal is exact directory equality after type changes.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/test/filetype_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/test/folders.sh -->
## sources/sync-backup/syncthing/test/folders.sh

Purpose: emits XML folder configuration blocks for a large number of fake folders.

Important APIs/functions: Bash C-style loop from `id=0` to `199`, with a here-document generating `<folder>` entries.

Control flow: for each numeric id, prints a sendreceive folder using fake filesystem path parameters `maxsize=1000` and `seed=<id>`, disabled watcher, two device IDs, and common folder settings.

State and persistence: no direct file writes; intended output can be redirected into a config.

Dependencies and integration: Bash and Syncthing XML config format. Risks are static device IDs and XML schema drift. Test signal is use in performance or many-folder fixture generation.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/test/folders.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/test/h1/config.xml -->
## sources/sync-backup/syncthing/test/h1/config.xml

Purpose: integration fixture for host 1 in local Syncthing test clusters.

Important configuration: version 51; folder `default` at `s1`, basic filesystem, sendreceive, watcher enabled, puller/copy settings, two devices, GUI on `127.0.0.1:8081` with basic auth and API key `abc123`, listen addresses on TCP/QUIC port 22001, local announce enabled, global announce disabled, relays disabled, and defaults for folder/device templates.

Control flow: no executable flow, but tests load and sometimes rewrite this config before starting instance 1.

State and persistence: defines persistent home configuration for `h1`, plus default folder and option state used across tests.

Dependencies and integration: consumed by config loader and integration helpers. It pairs with h2/h3/h4 configs by device IDs and local ports. Risks include hard-coded ports, plaintext fixture API key, schema migration changing serialized fields, and tests that rename/restore this file. Test signals are broad: most integration tests start h1.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/test/h1/config.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/test/h2/config.xml -->
## sources/sync-backup/syncthing/test/h2/config.xml

Purpose: integration fixture for host 2, usually syncing folder `default` with h1.

Important configuration: version 52; folder `default` at `s2`, watcher disabled, rescan interval 60 seconds, copiers 8, max concurrent writes 8, devices h1 and h2, GUI on `127.0.0.1:8082` without configured user/password, API key `abc123`, listen addresses TCP/QUIC port 22002, relay enabled, LAN bandwidth limiting enabled, and standard defaults.

Control flow: schema fixture only. Several tests temporarily rewrite folder versioning or append many devices through REST/config APIs.

State and persistence: persistent host home config and fixture defaults. Device IDs and ports coordinate with h1/h3.

Dependencies and integration: used by two-peer tests, HTTP GUI tests, conflict tests, file type/symlink/versioning tests, and many-peers configuration mutation. Risks include hard-coded ports and config version migrations. Test signal is successful startup and sync behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/test/h2/config.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/test/h3/config.xml -->
## sources/sync-backup/syncthing/test/h3/config.xml

Purpose: integration fixture for host 3 in multi-device and multi-folder cluster tests.

Important configuration: version 32; folder `default` at `s3` shared with h1/h2 and simple versioning keep=5; folder `s23` at `s23-3` shared with h2/h3; device entries for h1, h2, h3; GUI on `127.0.0.1:8083`; listen includes dynamic relay endpoint and TCP 22003; local announce and NAT disabled.

Control flow: no executable flow; consumed by integration startup helpers.

State and persistence: fixture home config for host 3, including multiple folders and simple versioning.

Dependencies and integration: used especially by `TestSyncCluster`; coordinates folder IDs including default and `s23`. Risks include older config version migrations, relay endpoint changes, and multi-folder schema drift. Test signal is three-node cluster convergence.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/test/h3/config.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/test/h4/config.xml -->
## sources/sync-backup/syncthing/test/h4/config.xml

Purpose: integration fixture for a fourth standalone host.

Important configuration: version 32; folder `default` at `s4/`, single device h4, basic filesystem, watcher disabled, auto-normalization disabled, puller pending limit 2048 KiB, GUI on `127.0.0.1:8084` with a distinct API key, listen includes dynamic relay endpoint and TCP 22004, local announce disabled, NAT disabled.

Control flow: configuration only. It is available for tests needing a separate single-device instance or normalization-specific behavior.

State and persistence: persistent fixture config under `h4`.

Dependencies and integration: config loader, integration helpers, local ports. Risks are hard-coded ports, older version migrations, and path trailing slash behavior. Test signal is indirect through any test that starts host 4.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/test/h4/config.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/test/http_test.go -->
## sources/sync-backup/syncthing/test/http_test.go

Purpose: integration tests and benchmarks for GUI/static serving, authentication, CSRF protection, and REST API performance.

Important APIs/functions: `TestHTTPGetIndex`, `TestHTTPGetIndexAuth`, `TestHTTPOptions`, `TestHTTPPOSTWithoutCSRF`, `setupAPIBench`, `benchmarkURL`, and six `BenchmarkAPI_*` functions.

Control flow: starts h1 or h2, uses raw `net/http` requests for page/auth/CSRF checks, extracts CSRF cookie and device short ID header, then tests POST success/failure. Benchmarks create a large dataset and repeatedly call REST endpoints through `rc.Process.Get`.

State and persistence: mutates `s1`, `s2`, and indexes during benchmark setup; reads GUI responses over local HTTP ports.

Dependencies and integration: `lib/protocol`, `lib/rc`, HTTP server, GUI asset serving, API key/basic auth/CSRF middleware. Risks include cookie parsing by string slicing, fixed ports, and benchmark setup cost. Test signals are status codes, response content, cookies, and benchmark throughput.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/test/http_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/test/ignore_test.go -->
## sources/sync-backup/syncthing/test/ignore_test.go

Purpose: integration test for `.stignore` pattern changes and scanner model counts.

Important APIs/functions: `TestIgnores`, `p.Rescan`, and `p.Model`.

Control flow: starts h1, creates directories and files under `s1`, scans and checks all files are visible, writes ignore patterns covering selected names and a case-insensitive txt rule, rescans and checks reduced file count, waits over one second for mtime granularity, writes a less restrictive ignore file, rescans, and checks file count increases.

State and persistence: writes files/directories and `.stignore` under `s1`; updates h1 index.

Dependencies and integration: ignore parser, scanner, model REST API. Risks include case-sensitivity differences, mtime granularity, and count expectations tied to fixture names. Test signal is `Model.LocalFiles` count after each rescan.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/test/ignore_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/test/manypeers_test.go -->
## sources/sync-backup/syncthing/test/manypeers_test.go

Purpose: integration test ensuring a folder can sync when a peer has many configured devices.

Important APIs/functions: `TestManyPeers`, REST `Get("/rest/system/config")`, `Post("/rest/system/config")`, and `rc.AwaitSync`.

Control flow: cleans two-peer state, generates files in `s1`, starts receiver h2, fetches config, appends random device IDs until there are 100 devices and corresponding folder device entries, posts modified config, starts sender h1, resumes both, awaits sync, then compares directories.

State and persistence: temporarily rewrites h2 config, mutates s1/s2 data and indexes.

Dependencies and integration: config JSON marshaling, random device ID generation, REST config replacement, folder device membership logic. Risks include config restore failure, performance regressions with large device lists, and random ID collision being theoretically possible. Test signal is sync completion and directory equality.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/test/manypeers_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/test/override_test.go -->
## sources/sync-backup/syncthing/test/override_test.go

Purpose: integration test for send-only folder override behavior.

Important APIs/functions: `TestOverride`, config mutation to `FolderTypeSendOnly`, REST POST `/rest/db/override?folder=default`, and `rc.AwaitSync`.

Control flow: rewrites h1 default folder to send-only, creates initial data, syncs to h2, edits a file on h2, rescans h2 and waits for index propagation, posts override on h1, waits for sync, then verifies h1 did not accept h2 changes and h2 was reverted. A longer ignore-related override test is present but commented out.

State and persistence: mutates `s1`, `s2`, h1/h2 indexes, and temporarily h1 config.

Dependencies and integration: config loader, REST override endpoint, send-only model logic. Risks include fixed sleep for index propagation, config restore on failure, and behavior around ignored files left untested. Test signal is file content after override.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/test/override_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/test/parallel_scan_test.go -->
## sources/sync-backup/syncthing/test/parallel_scan_test.go

Purpose: stress test for concurrent immediate rescans.

Important APIs/functions: `TestRescanInParallel`, `st.Rescan("default")`, and `sync.WaitGroup.Go`.

Control flow: cleans h1 state, generates 5000 files, writes `.stignore`, starts h1, launches 20 concurrent rescan requests, waits for all to finish, sleeps two seconds, and stops with log checking.

State and persistence: data under `s1`, h1 index, `.stignore`.

Dependencies and integration: scanner concurrency, REST rescan endpoint, test helper `checkedStop`. Risks include Go version dependency for `WaitGroup.Go`, race detector/log failure exposure, and long runtime with large file count. Test signal is no rescan errors and clean shutdown.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/test/parallel_scan_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/test/reconnect_test.go -->
## sources/sync-backup/syncthing/test/reconnect_test.go

Purpose: verifies transfers survive sender or receiver restarts during throttled synchronization.

Important APIs/functions: `TestReconnectReceiverDuringTransfer`, `TestReconnectSenderDuringTransfer`, and shared `testReconnectDuringTransfer`.

Control flow: generates files, starts h1/h2, sets receiver send/receive rate limits and LAN limiting through config API, resumes both, polls receiver model progress, restarts the selected side whenever progress crosses another 10 percent, then resets rate limits, stops both, compares directories, and verifies remote in-sync state.

State and persistence: mutates `s1`, `s2`, h1/h2 indexes and h2 runtime config.

Dependencies and integration: connection manager, block transfer resume/retry, config REST API, rate limiting. Risks include timing and progress thresholds, restart races, and failure to reset config after test failure. Test signal is final directory equality and remote in-sync checks.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/test/reconnect_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/test/reset_test.go -->
## sources/sync-backup/syncthing/test/reset_test.go

Purpose: integration test for REST-triggered database reset of one folder and all folders.

Important APIs/functions: `TestReset`, helper `createFiles`, REST POST `/rest/system/reset?folder=...` and `/rest/system/reset`.

Control flow: creates files, starts h1, confirms local model count, deletes data while preserving `.stfolder`, verifies invalid-folder reset fails, resets default folder and waits for Syncthing to exit, restarts and checks zero files, recreates files and rescans, resets all indexes, waits for exit again, restarts, and verifies file count is restored by scanning.

State and persistence: deletes/recreates `s1`, `.stfolder`, and h1 indexes; process exits are expected side effects.

Dependencies and integration: REST reset endpoint, database lifecycle, startup scanning. Risks include EOF handling during restart, timeout sensitivity, and marker preservation. Test signal is process stop and `Model.LocalFiles` counts.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/test/reset_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/test/scan_test.go -->
## sources/sync-backup/syncthing/test/scan_test.go

Purpose: integration test for targeted subdirectory/file rescans.

Important APIs/functions: `TestScanSubdir`, `sender.RescanSub`, `sender.RescanDelay`, `rc.AwaitSync`, and directory comparison helpers.

Control flow: syncs initial h1/h2 data, delays full scans, then performs seven targeted scan scenarios: new file in known directory, new file in unknown directory, new deep file, new deep directory, deleted file in known directory, scan of missing deep path, and intentionally scanning only one of two new files to confirm unscanned changes do not sync.

State and persistence: mutates `s1`, `s2`, h1/h2 indexes.

Dependencies and integration: scanner path targeting, database parent discovery, sync propagation. Risks include path normalization, delayed full scan masking targeted-scan behavior, and directory comparison expecting exact state. Test signal is equality after expected cases and deliberate inequality for the omitted file.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/test/scan_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/test/symlink_test.go -->
## sources/sync-backup/syncthing/test/symlink_test.go

Purpose: verifies symlink synchronization and symlink replacement/removal behavior under multiple receiver versioning modes.

Important APIs/functions: `TestSymlinks`, `TestSymlinksSimpleVersioning`, `TestSymlinksStaggeredVersioning`, and shared `testSymlinks`.

Control flow: skips when symlinks are unsupported, temporarily rewrites h2 versioning, creates files, directories, valid symlinks, broken symlinks, and replacement targets, syncs initial state, then removes, retargets, and replaces symlinks with files/directories and vice versa. After rescan and sync, directories are compared.

State and persistence: mutates `s1`, `s2`, h1/h2 indexes, symlink entries, and h2 config.

Dependencies and integration: OS symlink support, scanner file type detection, puller replacement logic, versioning behavior. Risks include platform-specific symlink permissions and versioner interaction with link replacement. Test signal is exact directory equality.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/test/symlink_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/test/sync_test.go -->
## sources/sync-backup/syncthing/test/sync_test.go

Purpose: broad integration coverage for multi-device/multi-folder synchronization and sparse-file transfer efficiency.

Important APIs/functions: `TestSyncCluster`, `scSyncAndCompare`, and `TestSyncSparseFile`; constant `s12Folder` intentionally uses Unicode to verify arbitrary folder IDs.

Control flow: cluster test generates initial data on h1/h2/h3 and secondary folders, starts three instances, repeatedly forces delayed rescans, awaits sync across `default`, s12, and `s23`, compares actual directory contents to expected merged state, alters source folders, and appends to a file while preserving mtime to test content-change detection. Sparse test creates a mostly-zero large file, syncs two peers, compares directories, then asserts sender transferred less than 256 KiB.

State and persistence: mutates `s1`, `s2`, `s3`, `s12-*`, `s23-*`, and h1/h2/h3 indexes.

Dependencies and integration: `lib/rc`, connection/transfer layer, scanner hashing, folder ID handling, sparse block optimization. Risks include time limits, mtime granularity, fixed random seed expectations, and bandwidth byte threshold changes. Test signal is directory equality, remote in-sync checks, and connection byte totals.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/test/sync_test.go -->
