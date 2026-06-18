# subset-b-009126 research

Grouped research report for Git LFS build orchestration and command-layer source files. Each section preserves the exact source path and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/Makefile -->
# sources/sync-backup/git-lfs/Makefile

Purpose: top-level build, test, localization, documentation, and release orchestration for the Git LFS Go project. It defines how binaries, generated command manpage content, translation bundles, release archives, vendor archives, Windows/macOS signing assets, Go tests, integration tests, formatting, linting, and manpage outputs are produced.

Important APIs/types/functions: Make variables `GIT_LFS_SHA`, `VERSION`, `PREFIX`, `GO`, `GOTOOLCHAIN`, `LD_FLAGS`, `GC_FLAGS`, `BUILD`, `BUILD_TARGETS`, `RELEASE_TARGETS`, `MAN_ROFF_TARGETS`, `MAN_HTML_TARGETS`, and tools such as `go generate`, `go build`, `go test`, `goimports`, `asciidoctor`, `msgfmt`, `xgotext`, `tar`, `bsdtar`, `codesign`, and `signtool`. Key targets include `mangen`, `trgen`, `all`, `build`, platform-specific `bin/git-lfs-*`, `resource.syso`, `release`, `release-linux`, Windows staged release targets, `release-darwin`, certificate helpers, `test`, `integration`, `vendor`, `fmt`, `lint`, and `man`.

Control flow: source and version variables feed a reusable `BUILD` macro; generated manpage and translation Go files are prerequisites of binary targets; platform targets set `GOOS` and `GOARCH`; release archive targets wrap built binaries with README, changelog, manpages, and install scripts; Windows and Darwin release paths add platform-specific signing/notarization stages; `test` first builds/formats, creates an isolated temporary HOME and Git config environment, then runs package tests; `man` uses Asciidoctor to convert each `.adoc` page to roff and HTML.

State and persistence behavior: outputs are written under `bin/`, `bin/releases/`, `commands/mancontent_gen.go`, `tr/tr_gen.go`, `po/build`, `resource.syso`, `tmp/stage*`, `vendor/`, `man/`, and `go.sum`. Release targets package repository state at `$(VERSION)`, and code-signing/notarization targets depend on external keychain or certificate state.

Dependencies/integration points: integrates Go modules, vendoring, gettext catalogs, Asciidoctor extensions, Docker packaging scripts, Windows Inno Setup, macOS keychain/notarization helpers, Git archive, Git describe/rev-parse, and package lists mirrored to repository layout.

Risks and test signals: risks include stale generated mancontent/translations, missing optional local tools causing skipped localization or formatting, fragile tar transform differences between GNU and BSD tar, platform-only signing assumptions, duplicated `git` package in `PKGS`, and release artifact naming coupled to `VERSION`. Test signals are successful default `make`, `make test`, package-scoped `PKGS=... test`, generated manpages, release archive contents with correct prefixes, and Windows/Darwin release dry-runs in the intended host environments.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_checkout.go -->
# sources/sync-backup/git-lfs/commands/command_checkout.go

Purpose: implements `git lfs checkout`, replacing LFS pointer files in the working tree with locally cached media files, and supports extracting a specific conflict stage to a chosen path.

Important APIs/types/functions: globals `checkoutTo`, `checkoutBase`, `checkoutOurs`, `checkoutTheirs`; `checkoutCommand`, `checkoutConflict`, `whichCheckout`, and `rootedPathPatterns`. It uses `setupRepository`, `git.CurrentRef`, `git.ResolveRef` stage syntax, `lfs.NewGitScanner`, `newSingleCheckout`, `filepathfilter.New`, `lfs.NewCurrentToRepoPatternConverter`, `lfs.NewCurrentToRepoPathConverter`, `tasklog`, and `tq.Meter`.

Control flow: the command validates repository/worktree state, parses mutually exclusive conflict stage flags, then either performs conflict checkout via `checkoutConflict` or scans LFS files at the current ref filtered by rooted path patterns. It records pointer sizes in a checkout meter, then runs single checkout for each pointer. Conflict checkout converts paths to repository-relative names, resolves `:<stage>:<file>`, decodes the pointer object, and writes the matching media to `--to`.

State and persistence behavior: normal checkout mutates working-tree files by linking/copying from `.git/lfs/objects`; conflict checkout creates parent directories for the `--to` path and writes a standalone output file. No remote download is attempted, so missing local media remains a checkout failure or skip through `singleCheckout`.

Dependencies/integration points: depends on index stage semantics, Git object scanning, LFS pointer decoding, tasklog progress, path conversion from current directory to repository root, and the `singleCheckout` implementation outside this subset.

Risks and test signals: risks include silent return rather than nonzero exit for bare repositories, only local-cache availability, path conversion edge cases from subdirectories, and meter byte accounting being serial rather than callback-driven. Test signals include checking out all pointers, filtered paths, bare repository behavior, missing object behavior, and conflict-stage extraction for base/ours/theirs with exactly one path.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_checkout.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_clean.go -->
# sources/sync-backup/git-lfs/commands/command_clean.go

Purpose: implements the Git clean filter, converting working-tree file content into a Git LFS pointer and storing the media object in local LFS storage.

Important APIs/types/functions: `clean`, `cleanCommand`, `lfs.GitFilter.Clean`, `gf.CopyCallbackFile`, `gf.ObjectPath`, `lfs.EncodePointer`, and `errors.IsCleanPointerError`. It uses `requireStdin`, `setupRepository`, `installHooks`, `tools.CopyCallback`, and Windows large-file warning helper `possiblyMalformedObjectSize`.

Control flow: `cleanCommand` requires pipe input, initializes repository and hooks, derives an optional filename argument, and calls `clean`. `clean` optionally stats the file and creates a progress callback, delegates transformation to `GitFilter.Clean`, handles already-clean pointer errors by writing the original pointer bytes, moves the cleaned temp object into the media store if no matching object exists, validates size mismatches for non-extension objects, and writes the pointer to Git.

State and persistence behavior: stores content-addressed media files under `.git/lfs/objects`, removes ownership from temporary clean files via `Teardown`, writes pointer text to stdout, and may leave existing objects untouched. It reads current file size to improve progress and pointer metadata.

Dependencies/integration points: clean is shared by filter-process, migrate import, merge-driver output, and pointer generation behavior. It depends on configured LFS extensions, object path layout, and central command error handling.

Risks and test signals: risks include fatal exits inside a helper used by multiple commands, mismatch handling when extensions are present, rename failures across filesystems, and Windows files larger than 4 GiB warning paths. Test signals include idempotent cleaning of an existing pointer, media-object creation, duplicate object reuse, extension-enabled clean, stdin filter invocation, and size mismatch protection.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_clean.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_clone.go -->
# sources/sync-backup/git-lfs/commands/command_clone.go

Purpose: implements deprecated `git lfs clone`, wrapping `git clone` with filters disabled and then fetching/checking out LFS objects for the cloned repository.

Important APIs/types/functions: `cloneCommand`, `postCloneSubmodules`, `cloneFlags git.CloneFlags`, `cloneSkipRepoInstall`, `git.CloneWithoutFilters`, `setupRepository`, `buildFilepathFilter`, `fetchRef`, `pull`, and `installHooks`.

Control flow: validates Git version, warns on newer Git versions, passes mirrored clone flags to Git, finds the clone directory from the final argument or URL basename, changes into it, initializes the Git LFS repository context, applies `--origin`, and either fetches LFS objects for no-checkout/bare clones or runs `pull` and recursive submodule pulls. It then installs hooks unless `--skip-repo` is set.

State and persistence behavior: creates a new repository via Git, changes process cwd temporarily, downloads LFS objects into the clone's LFS store, mutates the working tree through checkout unless bare/no-checkout, and installs repository hooks.

Dependencies/integration points: depends on Git clone flag parity, Git version behavior around submodule filter propagation, `git submodule foreach`, global include/exclude flags, and the pull/fetch command helpers.

Risks and test signals: risks include deprecated flag coverage drifting from Git, clone directory inference for unusual URLs or explicit paths, submodule pull errors after successful parent pull, and cwd restoration. Test signals include normal clone, `--bare`, `--no-checkout`, `--origin`, include/exclude filters, recursive submodules on Git >=2.9, and hook install skipping.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_clone.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_dedup.go -->
# sources/sync-backup/git-lfs/commands/command_dedup.go

Purpose: implements `git lfs dedup`, replacing working-tree media files with filesystem-level clones of matching LFS object files when the platform supports clonefile/reflink-like deduplication.

Important APIs/types/functions: `dedupCommand`, `dedupTestCommand`, `dedup`, `dedupFlags.test`, `dedupStats`, `tools.CheckCloneFileSupported`, `tools.CloneFileByPath`, `git.IsWorkingCopyDirty`, and `lfs.NewGitScanner`.

Control flow: `--test` validates platform support and absence of configured LFS extensions. Normal operation verifies repository support, rejects extensions and dirty working trees, scans `HEAD` for LFS pointers, and for each pointer checks local object existence, stats the working-tree file, clone-copies the media object over it, restores mode bits, and updates aggregate stats.

State and persistence behavior: overwrites working-tree files with deduplicated clones from `.git/lfs/objects`, preserving original permissions. It does not change Git history or object storage and depends on a clean worktree to avoid data loss.

Dependencies/integration points: integrates filesystem clone capability detection, LFS object cache paths, Git scanner tree traversal, and command output localization.

Risks and test signals: risks include platform-specific clone semantics, object existence assumptions tied to prior `git status`, extensions being incompatible with raw object deduplication, and only restoring chmod metadata. Test signals include `--test`, unsupported filesystem failure, dirty worktree rejection, successful reflink/clone replacement, missing object skip, and permission preservation.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_dedup.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_env.go -->
# sources/sync-backup/git-lfs/commands/command_env.go

Purpose: implements `git lfs env`, printing version, Git version, endpoint/auth configuration, environment-derived LFS settings, and configured filter commands for diagnostics.

Important APIs/types/functions: `envCommand`, `config.ShowConfigWarnings`, `git.Version`, `config.VersionDesc`, `cfg.Remotes`, `cfg.IsDefaultRemote`, `getAPIClient().Endpoints`, `lfs.Environ`, and `getTransferManifest`.

Control flow: enables config warnings, prints Git LFS and Git version data, prints default remote endpoint with auth and SSH metadata, prints non-default remote endpoints, dumps the computed LFS environment, then prints `filter.lfs.process`, `filter.lfs.smudge`, and `filter.lfs.clean` config values.

State and persistence behavior: read-only except for lazy API client and transfer manifest creation. Output goes through the shared `Print` writer and may be captured in error buffers used for logs.

Dependencies/integration points: integrates configuration, endpoint discovery, auth access mode reporting, SSH metadata parsing, transfer adapter manifest construction, and filter install state.

Risks and test signals: risks include exposing sensitive endpoint/auth mode context, forcing lazy client creation in a diagnostic command, and config warnings changing output stability. Test signals include repositories with default and multiple remotes, SSH remotes, missing Git version, and installed/uninstalled filter config.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_env.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_ext.go -->
# sources/sync-backup/git-lfs/commands/command_ext.go

Purpose: implements `git lfs ext` and `git lfs ext list`, printing configured custom LFS extension clean/smudge commands and priorities.

Important APIs/types/functions: `extCommand`, `extListCommand`, `printAllExts`, `printExt`, `cfg.Extensions`, `cfg.SortedExtensions`, and `config.Extension`.

Control flow: the root command prints all extensions; `list` with no args does the same, while named args fetch matching entries from `cfg.Extensions()` and print them. Each extension emits name, clean command, smudge command, and priority.

State and persistence behavior: read-only; output is diagnostic. Missing named extensions resolve to zero-value `config.Extension` and are still printed.

Dependencies/integration points: depends on Git LFS extension configuration and command registration. Extensions affect clean/smudge/migrate/pointer behavior elsewhere.

Risks and test signals: risks include poor error reporting for unknown extension keys and direct stdout printing for sort errors. Test signals include no extensions, multiple sorted extensions, named extension lookup, and invalid extension config from `SortedExtensions`.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_ext.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_fetch.go -->
# sources/sync-backup/git-lfs/commands/command_fetch.go

Purpose: implements `git lfs fetch`, scanning refs/history for LFS pointers and downloading missing media objects, with options for all refs, recent refs/commits, pruning, dry-run/refetch, JSON output, and refs from stdin.

Important APIs/types/functions: `fetchWatcher`, `fetchCommand`, `pointersToFetchForRef`, `fetchRef`, `pointersToFetchForRefs`, `fetchRefs`, `fetchPreviousVersions`, `fetchRecent`, `fetchAll`, `scanAll`, `fetch`, `pointersToFetch`, and `getIncludeExcludeArgs`. It uses `lfs.GitScanner`, `tq.TransferQueue`, `tasklog`, `lfs.FetchPruneConfig`, and `newDownloadQueue`.

Control flow: parses remote and refs, supports stdin ref resolution, defaults to current ref unless `--all`, rejects incompatible flag combinations, builds path filters, scans requested refs or all history, optionally scans recent branches and previous versions, then downloads via a transfer queue. The watcher records transfers for JSON/dry-run and avoids duplicate observed OIDs under dry-run/refetch. `--prune` invokes shared prune after fetch.

State and persistence behavior: writes objects into local LFS storage, may link/copy from reference repositories before deciding a download is needed, and may prune local objects when requested. JSON output buffers observed transfers until the end; progress writes to stderr/stdout tasklog.

Dependencies/integration points: integrates Git ref resolution, recent branch discovery, commit summaries, filepath filters, transfer adapter manifests, API endpoints, prune configuration, and shared download queue construction.

Risks and test signals: risks include complex flag interactions, dry-run/refetch watcher state controlling duplicate suppression, `--all` ignoring configured filters, scanner multi-error accumulation, and prune after partial fetch. Test signals include stdin refs, explicit refs, current ref, `--all`, `--recent`, include/exclude, dry-run JSON, refetch existing objects, missing objects causing final failure, and fetch-prune behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_fetch.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_filter_process.go -->
# sources/sync-backup/git-lfs/commands/command_filter_process.go

Purpose: implements Git's long-running `filter-process` protocol for clean, smudge, delayed smudge, and `list_available_blobs` interactions.

Important APIs/types/functions: constants `cleanFilterBufferCapacity`, `smudgeFilterBufferCapacity`; global `filterSmudgeSkip`; `filterCommand`, `infiniteTransferBuffer`, `incomingOrCached`, `readAvailable`, `pathnames`, `statusFromErr`, and `delayedStatusFromErr`. It uses `git.FilterProcessScanner`, `pktline.PktlineWriter`, `lfs.GitFilter`, `tq.TransferQueue`, and shared `clean`/`smudge` helpers.

Control flow: requires stdin, sets up repo/hooks, negotiates capabilities, detects `delay`, builds skip/filter state, then loops over Git filter requests. `clean` writes pointer output; `smudge` either initializes a delayed download queue and queues missing objects when `can-delay=1`, or smudges immediately using cached pointer fallback; `list_available_blobs` starts queue drain and returns ready pathnames until completion. Malformed pointer and Windows large-file warnings are accumulated and printed after the scan.

State and persistence behavior: long-lived process holds a transfer queue, delayed pathname-to-pointer map, malformed path lists, and channel buffer goroutine. It downloads into the LFS object store, writes blobs/pointers over pktline stdout, and installs hooks opportunistically.

Dependencies/integration points: tightly integrates with Git filter protocol capabilities, pkt-line framing, transfer queue batch behavior, auto remote detection from treeish, include/exclude filters, and shared clean/smudge semantics.

Risks and test signals: risks include nil `closeOnce` if `list_available_blobs` arrives without delayed smudge setup, protocol status ordering, channel close/race behavior in delayed queue buffering, path cache for `can-delay=0` follow-up requests, and large warning behavior. Test signals include Git checkout with filter-process, clean requests, immediate smudge, delayed smudge with repeated list calls, skip smudge, malformed pointers, and queue errors mapped to protocol statuses.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_filter_process.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_fsck.go -->
# sources/sync-backup/git-lfs/commands/command_fsck.go

Purpose: implements `git lfs fsck`, validating local LFS object contents and pointer canonicality for selected refs/ranges/index state, and quarantining corrupt media objects unless dry-run is set.

Important APIs/types/functions: globals `fsckDryRun`, `fsckObjects`, `fsckPointers`; `corruptPointer`; `fsckCommand`, `doFsckObjects`, `doFsckPointers`, and `fsckPointer`. It uses `lfs.GitScanner`, `filepathfilter`, `sha256`, `cfg.Filesystem().ObjectPathname`, and pointer scan errors.

Control flow: installs hooks, resolves current ref or a single ref/range argument, defaults to both object and pointer checks, scans pointer references for media objects and hashes local files, scans by tree for noncanonical or unexpected Git objects, prints OK or errors, and moves corrupt object files into `.git/lfs/bad` unless dry-run or only pointer corruption occurred.

State and persistence behavior: read-mostly validation, but non-dry corrupt object repair creates the bad directory and renames corrupt media files into it. Zero-size missing objects are accepted.

Dependencies/integration points: integrates ref resolution, index scanning, fetch-exclude filters to avoid expected missing subsets, LFS object storage layout, and pointer scanner canonicality metadata.

Risks and test signals: risks include limited argument parsing, only one ref/range supported, hashing large files without progress, dry-run exit semantics, and object quarantine rename failures. Test signals include valid repo OK, corrupt media hash detection, missing nonzero object, zero-size pointer, noncanonical pointer, unexpected Git object, index scanning with no args, and dry-run no quarantine.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_fsck.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_install.go -->
# sources/sync-backup/git-lfs/commands/command_install.go

Purpose: implements `git lfs install` and `git lfs install hooks`, installing Git LFS filter configuration and repository hooks.

Important APIs/types/functions: globals `fileInstall`, `forceInstall`, `localInstall`, `worktreeInstall`, `manualInstall`, `systemInstall`, `skipSmudgeInstall`, `skipRepoInstall`; `installCommand`, `cmdInstallOptions`, and `installHooksCommand`; `lfs.FilterOptions`.

Control flow: `cmdInstallOptions` validates Git version, optionally sets up repository for local/worktree, enforces mutually exclusive install scopes, warns for non-root system install, and builds filter options. `installCommand` installs filter config, optionally delegates to hook installation, and prints initialization status. `installHooksCommand` maps install flags onto update globals and calls `updateCommand`.

State and persistence behavior: writes Git configuration in global/local/worktree/system/file scope and installs or prints hook content depending on flags. It can skip smudge filters and skip repository hook setup.

Dependencies/integration points: depends on Git version for worktree support, `lfs.FilterOptions`, `updateCommand`, `installHooks`, and shared command configuration state reused by uninstall.

Risks and test signals: risks include shared global flag state between install/update/uninstall, system install privilege warning being advisory, and `install hooks` going through update behavior. Test signals include each scope, mutually exclusive scope rejection, skip-smudge config, manual hook instructions, force overwrite, and repository hook install failure guidance.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_install.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_lock.go -->
# sources/sync-backup/git-lfs/commands/command_lock.go

Purpose: implements `git lfs lock`, creating server-side locks for repository-relative file paths and optionally emitting JSON.

Important APIs/types/functions: global `lockRemote`; `lockCommand`, `lockData`, `computeLockData`, and `lockPath`; `newLockClient`, `locking.Client.LockFile`, `git.NewRefUpdate`, and shared `locksCmdFlags.JSON`.

Control flow: optional `--remote` updates fetch and push remote config, computes cwd/root data, creates a lock client with remote ref, normalizes each provided path, rejects directories/outside-root paths, locks each file, collects successes for JSON, and exits with code 2 if any item failed.

State and persistence behavior: creates remote locks and updates local lock cache through the lock client. It reads filesystem state to reject directories and canonicalize paths.

Dependencies/integration points: integrates lock API client, push remote selection, current ref remote ref metadata, local working directory/cwd canonicalization, and JSON output shared with locks/unlock.

Risks and test signals: risks include partial success semantics, force of both remote settings, path handling for nonexistent files, and use of `cfg.CurrentRef()` for remote ref creation. Test signals include relative/absolute paths, path outside repo, directory rejection, remote override, JSON output, multi-path partial failure, and server lock errors.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_lock.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_locks.go -->
# sources/sync-backup/git-lfs/commands/command_locks.go

Purpose: implements `git lfs locks`, listing local, cached, remote, filtered, or verification-classified locks in text or JSON form.

Important APIs/types/functions: global `locksCmdFlags`; `locksCommand`; `locksFlags` with `Filters`; `locking.Client.SearchLocks`, `SearchLocksVerifiable`, `EncodeLocks`, and `EncodeLocksVerifiable`.

Control flow: computes lock path filters, applies optional remote override, builds lock client with current remote ref, validates incompatible `--cached` and `--verify` combinations, queries locks or verifiable own/their lock sets, writes JSON if requested, otherwise sorts by path and prints padded rows with optional ownership marker. Retrieval errors are reported after printing any partial results.

State and persistence behavior: may read/write local lock cache depending on client query mode; remote queries contact locking API. Text formatting is derived from returned lock owner fields.

Dependencies/integration points: shares path normalization with `lock`, JSON flag state with lock/unlock, and remote/ref setup with lock client. Verification mode supports pre-push lock semantics.

Risks and test signals: risks include using `locking.Lock` as a map key, partial output before final error, incompatible flag matrix, and cached/local semantics diverging from remote truth. Test signals include path/id filters, limits, local-only, cached-only, verify mode, JSON encoders, sorting/padding, and server errors with partial data.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_locks.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_logs.go -->
# sources/sync-backup/git-lfs/commands/command_logs.go

Purpose: implements `git lfs logs` subcommands for listing, showing, clearing, and generating sample panic logs.

Important APIs/types/functions: `logsCommand`, `logsLastCommand`, `logsShowCommand`, `logsClearCommand`, `logsBoomtownCommand`, and `sortedLogs`; `cfg.LocalLogDir`, `os.ReadDir`, `os.ReadFile`, `os.RemoveAll`, and shared `Panic`.

Control flow: root lists filenames in the log directory; `last` selects the last filename from `sortedLogs`; `show` reads a named log file and writes it to stdout; `clear` removes the log directory; `boomtown` writes a sample trace and panics with a wrapped sample error.

State and persistence behavior: reads and deletes files in `.git/lfs/logs` or configured local log directory. `boomtown` creates a new log through normal panic logging.

Dependencies/integration points: integrates with `LoggedError`/`Panic` output from `commands.go` and tracerx logs.

Risks and test signals: risks include `sortedLogs` not actually sorting beyond filesystem order, path joining allowing only names relative to log dir but no explicit traversal defense, and clear deleting the whole log directory. Test signals include no logs, showing a named log, last log selection, clear behavior, and boomtown sample generation.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_logs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_ls_files.go -->
# sources/sync-backup/git-lfs/commands/command_ls_files.go

Purpose: implements `git lfs ls-files`, listing LFS pointer files from the index, current tree, specified refs/ranges, all history, or deleted entries, with text, debug, or JSON output.

Important APIs/types/functions: globals `longOIDs`, `lsFilesScanAll`, `lsFilesScanDeleted`, `lsFilesShowSize`, `lsFilesShowNameOnly`, `lsFilesJSON`, `debug`; `lsFilesObject`, `lsFilesCommand`, `fileExistsOfSize`, and `lsFilesMarker`; `lfs.GitScanner`.

Control flow: resolves optional ref/range or current ref/empty tree, sets OID display length, scans index when no args, then scans all history, deleted tree entries, range, or tree. Callback skips zero-size objects, de-duplicates by name for non-range/non-all scans, emits debug, JSON, or text output with checkout/download markers and optional size.

State and persistence behavior: read-only; checks working-tree file size and local LFS object existence for status markers. JSON output accumulates entries until scan completion.

Dependencies/integration points: integrates Git ref resolution, pointer scanning, filepath include/exclude filters, local filesystem decoding, and humanized sizes.

Risks and test signals: risks include `--all` argument ambiguity, name-based de-duplication hiding multiple historical OIDs, file-size-only checkout marker, and scan mode flag incompatibilities. Test signals include no-arg index+tree, explicit ref, range, all, deleted, JSON/debug/name-only/size/long output, include/exclude filters, and files absent from working tree.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_ls_files.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_merge_driver.go -->
# sources/sync-backup/git-lfs/commands/command_merge_driver.go

Purpose: implements a custom merge driver that smudges LFS pointer inputs to real file contents, runs a merge program, then cleans the merged output back into an LFS pointer.

Important APIs/types/functions: globals for `mergeDriverAncestor`, `mergeDriverCurrent`, `mergeDriverOther`, `mergeDriverOutput`, `mergeDriverProgram`, `mergeDriverMarkerSize`; `mergeDriverCommand`, `processFiles`, `mergeCleanup`, and `mergeProcessInput`.

Control flow: validates mandatory file arguments, creates temp files for ancestor/current/other/output, converts input pointers to content via `GitFilter.Smudge` or copies non-pointer content, formats a merge command with percent substitutions, runs it through `sh -c`, captures conflict exit status, opens the temporary merged file, cleans it into the requested output pointer file, removes temps, and exits with the merge status.

State and persistence behavior: creates temporary files, downloads LFS objects if needed for smudging, writes the final cleaned pointer to `--output`, and stores merged media in the local LFS object cache through `clean`.

Dependencies/integration points: integrates Git merge-driver configuration, `git merge-file` default program, subprocess percent substitution, LFS pointer decoding, transfer manifest downloads, and clean filter storage.

Risks and test signals: risks include shell command injection if configured program is unsafe, temp cleanup only for expected specifier keys, missing error check after smudge in `mergeProcessInput`, and output mode fixed at 0600. Test signals include pointer-pointer merge, non-pointer input fallback, custom merge program, conflict exit propagation, missing pointer download, and cleanup after failures.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_merge_driver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_migrate.go -->
# sources/sync-backup/git-lfs/commands/command_migrate.go

Purpose: shared implementation and command registration for `git lfs migrate` subcommands, especially ref selection, working-copy safety, history rewriter setup, and global migrate flags.

Important APIs/types/functions: globals `migrateIncludeRefs`, `migrateExcludeRefs`, `migrateYes`, `migrateSkipFetch`, `migrateImportAboveFmt`, `migrateEverything`, `migrateVerbose`, `objectMapFilePath`, `migrateNoRewrite`, `migrateCommitMessage`, `exportRemote`, `migrateFixup`; functions `migrate`, `getObjectDatabase`, `rewriteOptions`, `isSpecialGitRef`, `includeExcludeRefs`, `getRemoteRefs`, `fetchRemoteRefs`, `formatRefName`, `currentRefToMigrate`, `getHistoryRewriter`, and `ensureWorkingCopyClean`.

Control flow: command registration wires `info`, `import`, and `export` subcommands. `migrate` sets up the repository, computes rewrite options from args and flags, and calls `githistory.Rewriter.Rewrite`. Ref selection defaults to current local ref, supports explicit args and include/exclude refs, excludes remote refs in non-bare default mode, and with `--everything` includes local branches/tags, remote branches, and non-special other refs while excluding stash/notes/bisect/replace. Dirty worktrees prompt unless `--yes`.

State and persistence behavior: opens the Git object database rooted at common dir and uses temp storage. It may fetch remote refs unless `--skip-fetch`, prompts on stdin/stdout, and later subcommands rewrite refs through provided options.

Dependencies/integration points: central integration with `git/githistory`, `gitobj`, Git remote/ref APIs, filepath filters in Git attributes mode, tasklog, and migrate subcommand-specific blob/tree callbacks.

Risks and test signals: risks include a likely bug in `strings.HasPrefix("^", name)` instead of checking the name for `^`, destructive dirty-worktree override after prompt, ref namespace edge cases, and remote fetch dependence. Test signals include default current branch migration, `--everything`, include/exclude refs, special ref exclusion, dirty prompt yes/no/EOF, skip-fetch using cached refs, and non-local current ref rejection.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_migrate.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_migrate_export.go -->
# sources/sync-backup/git-lfs/commands/command_migrate_export.go

Purpose: implements `git lfs migrate export`, rewriting history to replace LFS pointer blobs with real Git blobs and updating `.gitattributes` to untrack included paths.

Important APIs/types/functions: `migrateExportCommand`, `performForceCheckout`, and `trackedFromExportFilter`; `getHistoryRewriter`, `trackedFromAttrs`, `trackedToBlob`, `lfs.DecodePointer`, `gitobj.NewBlobFromFile`, `newDownloadQueue`, and `prune`.

Control flow: ensures the working copy is clean, opens object database and rewriter, requires at least one include filter, defines a blob callback that ignores `.gitattributes`, decodes LFS pointers, and replaces them with local media blobs. A root-tree callback merges adjusted `.gitattributes` lines. Before rewriting, it resolves the export remote and pre-downloads needed included objects if a download endpoint exists. After rewrite it force-checks out non-bare repos and prunes cache with recent-ref retention disabled.

State and persistence behavior: rewrites Git history and refs, downloads missing media into LFS storage, updates `.gitattributes` blobs in rewritten root trees, checks out the working tree, and prunes local LFS cache.

Dependencies/integration points: integrates migrate ref-selection/options, LFS transfer queue, object database blob/tree writing, attributes helpers from import, and shared prune logic.

Risks and test signals: risks include destructive history rewrite, needing all pointer objects locally or downloadable, `.gitattributes` union semantics preserving old lines, remote endpoint validation only when explicitly changed, and prune after rewrite. Test signals include export included patterns, excluded patterns retaining LFS attributes, missing object predownload, invalid remote, bare/non-bare checkout behavior, and object map generation.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_migrate_export.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_migrate_import.go -->
# sources/sync-backup/git-lfs/commands/command_migrate_import.go

Purpose: implements `git lfs migrate import`, rewriting history to replace matching Git blobs with LFS pointers, and a `--no-rewrite` mode that appends a new commit converting specified files.

Important APIs/types/functions: `migrateImportCommand`, `generateMigrateCommitMessage`, `checkoutNonBare`, `trackedFromFilter`, `trackedFromAttrs`, `trackedToBlob`, `rewriteTree`, and `findEntry`. It uses `clean`, `githistory.RewriteOptions`, `gitattr.Tree`, `gitobj`, and `humanize.ParseBytes`.

Control flow: ensures clean working copy, opens DB, installs hooks, then branches for `--no-rewrite`: validate args and attributes, load current commit tree, recursively replace specified blobs with cleaned pointer blobs, write a new commit with author/committer metadata, update the current ref, and checkout. Normal rewrite validates `--fixup`/`--above` flag combinations, builds a rewriter, cleans matching blobs into pointers, records attribute patterns from includes/excludes or file extensions, optionally consults per-tree attributes for fixup, updates root `.gitattributes` unless fixup, rewrites refs, and checks out.

State and persistence behavior: writes media files to `.git/lfs/objects`, writes new Git blobs/trees/commits, updates refs, mutates working tree on checkout, and caches `.gitattributes` parsing by blob SHA in `attrsCache`.

Dependencies/integration points: integrates clean filter semantics, object database writes, Git attributes parser, tasklog, migrate shared ref handling, current author/committer config, and LFS hook installation.

Risks and test signals: risks include destructive rewrite, global `attrsCache` lifetime, extension-derived tracking patterns that may overmatch, `--above` excluding equal-size blobs due to `< above`, recursive path rewrite assumptions, and symlink `.gitattributes` rejection. Test signals include include/exclude rewrite, no-rewrite single and nested paths, custom message, fixup using attributes, above threshold, extension pattern generation, checkout in bare repo skipped, and object map output.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_migrate_import.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_migrate_info.go -->
# sources/sync-backup/git-lfs/commands/command_migrate_info.go

Purpose: implements `git lfs migrate info`, scanning selected history and summarizing large file usage by extension or file name, with optional LFS pointer treatment modes and fixup inference.

Important APIs/types/functions: `migrateInfoPointersType`, globals `migrateInfoTopN`, `migrateInfoAboveFmt`, `migrateInfoUnitFmt`, `migrateInfoPointers`, `migrateInfoPointersMode`; `migrateInfoCommand`, `MigrateInfoEntry`, `findEntryByExtension`, `MapToEntries`, `removeEmptyEntries`, `EntriesBySize`, and `EntriesBySize.Print`.

Control flow: opens DB and history rewriter, parses byte threshold and optional unit, parses `--pointers` mode, validates `--fixup`, then uses migrate's rewrite walk with blob callbacks that optionally follow/ignore/no-follow LFS pointers, group entries by extension or basename, and count total/above-threshold bytes. Root tree pre-callback validates `.gitattributes` or loads fixup attributes. Results are sorted descending by size, truncated to `--top`, optionally append a separate LFS Objects row, and printed tabularly.

State and persistence behavior: read-only history traversal; counters are in memory. It still uses migrate's ref selection and remote fetch behavior, but no refs are updated because callbacks return original blobs/trees.

Dependencies/integration points: depends on `githistory.Rewriter` as a scanner, LFS pointer decoding, Git attributes fixup tree, humanize byte parsing/formatting, and shared migrate flags.

Risks and test signals: risks include using rewrite machinery for reporting, pointer mode defaults depending on global initialization, percentage formatting when totals are nonzero only, symlink `.gitattributes` rejection, and top truncation before adding LFS pointer summary. Test signals include thresholds, unit formatting, pointer follow/no-follow/ignore, fixup with attributes, include/exclude incompatibility, sort tie order, no matching files, and top count clamping.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_migrate_info.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_pointer.go -->
# sources/sync-backup/git-lfs/commands/command_pointer.go

Purpose: implements `git lfs pointer`, generating LFS pointer text for a file, validating pointer files, and comparing generated pointers with existing pointer input.

Important APIs/types/functions: globals `pointerFile`, `pointerCompare`, `pointerStdin`, `pointerCheck`, `pointerStrict`, `pointerNoStrict`, `pointerNoExtensions`; `pointerCommand` and `pointerReader`; `lfs.DecodePointer`, `lfs.EncodePointer`, `lfs.NewPointer`, `git.HashObject`, and `lfs.GitFilter.Clean`.

Control flow: `--check` validates exactly one input source, rejects incompatible strict flags, decodes the pointer, and exits 1 for invalid or 2 for noncanonical strict mode. Generation opens `--file`, either hashes directly for plain pointer/no repo or cleans through GitFilter to honor extensions, prints pointer to stdout and diagnostics to stderr, optionally hashes the pointer blob. Comparison reads `--pointer` or stdin, decodes and prints it, hashes it, and exits nonzero if blob OIDs differ.

State and persistence behavior: mostly read-only, but generation through `GitFilter.Clean` can invoke extension clean logic and may create temporary cleaned state depending on implementation. Output is split between stdout pointer text and stderr diagnostics.

Dependencies/integration points: integrates LFS pointer encoding/decoding, optional configured extensions, Git blob hashing, stdin validation, and repository detection.

Risks and test signals: risks include clean result teardown not explicit in this command, confusing stdout/stderr split for scripts, extension-driven pointer mismatch, and strict/no-strict flag interaction only enforced in check mode. Test signals include plain pointer generation, extension warning, invalid pointer check exit 1, noncanonical strict exit 2, file-vs-pointer comparison match/mismatch, stdin comparison, and no-op error.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_pointer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_post_checkout.go -->
# sources/sync-backup/git-lfs/commands/command_post_checkout.go

Purpose: implements the `post-checkout` hook command that enforces read-only permissions for lockable files after checkout operations.

Important APIs/types/functions: `postCheckoutCommand`, `postCheckoutRevChange`, and `postCheckoutFileChange`; `newLockClient`, `locking.Client.GetLockablePatterns`, `FixLockableFileWriteFlags`, `FixAllLockableFileWriteFlags`, and `git.GetFilesChanged`.

Control flow: validates the three Git hook args, returns if lockable read-only mode is disabled or no lockable patterns exist, then distinguishes branch/SHA checkout from file checkout. Revision changes try to diff old/new commits and fix only changed files, falling back to full scan on diff failure; file checkout performs a full lockable scan.

State and persistence behavior: mutates working-tree file permissions according to lock ownership and lockable patterns. It may query local/remote lock state through the lock client depending on client internals.

Dependencies/integration points: installed by Git LFS hooks, depends on Git hook argument contract, lock client patterns, and Git version.

Risks and test signals: risks include full-repo scan cost, fallback after diff errors, hook failures logged as warnings rather than hard stops, and zero SHA handling only for initial checkout. Test signals include branch checkout, file checkout, disabled setting, no lockable patterns, diff failure fallback, and permission changes for locked/unlocked files.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_post_checkout.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_post_commit.go -->
# sources/sync-backup/git-lfs/commands/command_post_commit.go

Purpose: implements the `post-commit` hook command that fixes read-only flags for lockable files changed in the new commit.

Important APIs/types/functions: `postCommitCommand`, `newLockClient`, `git.GetFilesChanged`, `FixLockableFileWriteFlags`, and `cfg.SetLockableFilesReadOnly`.

Control flow: returns when read-only lockable support is disabled, validates Git version, creates a lock client, skips when there are no lockable patterns, diffs `HEAD` against the working tree baseline via `git.GetFilesChanged("HEAD", "")`, and fixes write flags for those files.

State and persistence behavior: mutates working-tree file permissions after commit, mainly for newly added lockable files that might otherwise remain writable.

Dependencies/integration points: installed as a Git hook, integrates lockable attribute patterns, lock cache/client behavior, and Git changed-file detection.

Risks and test signals: risks include exiting with code 1 on changed-file diff errors, but only logging permission-fix errors; changed-file semantics around root commits may matter. Test signals include disabled setting, no patterns, added lockable files becoming read-only, locked files remaining writable, and diff failure handling.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_post_commit.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_post_merge.go -->
# sources/sync-backup/git-lfs/commands/command_post_merge.go

Purpose: implements the `post-merge` hook command that reapplies read-only permissions for all lockable files after merges.

Important APIs/types/functions: `postMergeCommand`, `newLockClient`, `FixAllLockableFileWriteFlags`, and `cfg.SetLockableFilesReadOnly`.

Control flow: validates the single Git hook squash flag argument, returns if read-only lockable behavior is disabled, validates Git version, creates a lock client, skips when no lockable patterns exist, then scans all lockable files because the hook does not report changed paths.

State and persistence behavior: mutates working-tree permissions for lockable files. It does not change repository data or refs.

Dependencies/integration points: installed as Git post-merge hook, depends on lockable patterns and lock client permission logic.

Risks and test signals: risks include full-repo scan cost after every merge, warning-only failure behavior, and no use of squash flag. Test signals include invalid arg count, disabled setting, no patterns, merge with lockable files, and permission-fix failures logged.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_post_merge.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_pre_push.go -->
# sources/sync-backup/git-lfs/commands/command_pre_push.go

Purpose: implements the Git `pre-push` hook command, uploading required LFS objects for pushed ref updates before Git completes the push.

Important APIs/types/functions: global `prePushDryRun`; `prePushCommand`, `prePushRefs`, and `decodeRefs`; `git.MapRemoteURL`, `cfg.SetValidPushRemote`, `newUploadContext`, and `uploadForRefUpdates`.

Control flow: validates hook args, respects `GIT_LFS_SKIP_PUSH`, validates Git version, maps the remote argument to a configured remote, creates upload context, parses stdin lines of `<local ref> <local sha> <remote ref> <remote sha>`, skips branch deletions with zero local SHA, creates `git.RefUpdate` values, and uploads objects for those updates.

State and persistence behavior: contacts LFS upload endpoint and may update transfer/log state; no local working-tree mutation. Dry-run avoids actual upload via upload context.

Dependencies/integration points: depends on Git pre-push stdin contract, remote URL mapping, upload context implementation, and lock verification in upload flow.

Risks and test signals: risks include scanner errors ignored in `prePushRefs`, simplistic space splitting, remote mapping edge cases, and environment skip bypassing all validation. Test signals include single/multiple updates, deleted branch skip, dry-run, invalid remote, URL-mapped remote, stdin blank lines, and upload failures.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_pre_push.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_prune.go -->
# sources/sync-backup/git-lfs/commands/command_prune.go

Purpose: implements `git lfs prune`, identifying local LFS objects not retained by refs, recent history, unpushed commits, worktrees, stash, or index state, optionally verifying remote presence before deleting them.

Important APIs/types/functions: prune flag globals; `pruneCommand`, `PruneProgressType`, `PruneProgress`, `prune`, `logVerboseOutput`, `pruneGetVerifiedPrunableObjects`, `pruneCheckErrors`, progress/error/retained collector tasks, `pruneDeleteFiles`, and scanner tasks for local objects, refs, previous versions, unpushed, worktrees, stash, index, and reachable objects.

Control flow: parses verification and force/recent flags into `FetchPruneConfig`, launches goroutines to collect local objects and retained OIDs from several Git sources, uses a semaphore to bound scanner concurrency, gathers errors, computes prunable OIDs, optionally enqueues download-check transfers to verify remote presence, filters unverified objects according to reachability and `--verify-unreachable`, reports progress/verbose output, and deletes object files unless dry-run.

State and persistence behavior: deletes media files from `.git/lfs/objects` by OID in non-dry mode, reads all local object metadata, and may query remote download endpoints in dry-run check mode. It does not update refs.

Dependencies/integration points: integrates GitScanner APIs, worktree/stash/index/ref scanning, LFS object filesystem, tasklog progress, transfer queues, config retention windows, and fetch `--prune`.

Risks and test signals: risks include concurrent use of a shared GitScanner across goroutines, semaphore acquire errors ignored, verify logic depending on remote download check semantics, force/recent retention interactions, and deleting by OID without retry. Test signals include dry-run, verbose, recent/force, verify remote reachable/unreachable, unpushed retention, worktree/index/stash retention, remote missing halt/continue, and deletion failure handling.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_prune.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_pull.go -->
# sources/sync-backup/git-lfs/commands/command_pull.go

Purpose: implements `git lfs pull`, downloading LFS objects for the current ref and checking them out into the working tree.

Important APIs/types/functions: `pullCommand`, `pull`, `pointerMap`, `newPointerMap`, `Seen`, `Add`, and `All`; `lfs.GitScanner.ScanLFSFiles`, `newSingleCheckout`, `newDownloadQueue`, and `tq.Meter`.

Control flow: validates Git version/repository, optionally sets remote, builds include/exclude filter, scans current ref for LFS pointers, immediately checks out objects already present locally, queues missing unique OIDs for download while mapping all paths to each OID, watches download completion to checkout all paths for that OID, waits for scan/queue/watch completion, reports transfer errors, and warns if checkout was skipped because LFS is not installed.

State and persistence behavior: downloads media into local LFS storage and mutates working-tree files. `pointerMap` holds in-memory OID-to-path associations and deletes them after checkout.

Dependencies/integration points: integrates current ref resolution, reference object linking, transfer queue progress, single checkout, filepath filters, remote endpoint failure reporting, and clone command reuse.

Risks and test signals: risks include callback and watcher concurrency, duplicate OID mapping correctness, checkout of already-present objects before meter start, and partial download failure after some checkouts. Test signals include current ref pull, include/exclude, duplicate OID multiple paths, existing object checkout, missing object download/checkout, transfer errors, and skip checkout when hooks/filter missing.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_pull.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_push.go -->
# sources/sync-backup/git-lfs/commands/command_push.go

Purpose: implements user-facing `git lfs push`, uploading LFS objects by ref comparison, all local refs, explicit object IDs, or stdin-provided refs/OIDs.

Important APIs/types/functions: globals `pushDryRun`, `pushObjectIDs`, `pushAll`, `useStdin`; `pushCommand`, `uploadsBetweenRefAndRemote`, `uploadsWithObjectIDs`, and `lfsPushRefs`; `newUploadContext`, `uploadForRefUpdates`, `git.LocalRefs`, and `git.NewRefUpdate`.

Control flow: requires a remote arg, validates Git version and push remote, gathers remaining args or stdin lines, then either validates and uploads explicit object IDs by statting local media files, or resolves ref updates from local refs/explicit names/all refs and delegates upload scanning. It reports invalid input with exit code 1 or fatal upload errors through shared error handling.

State and persistence behavior: uploads local media to the LFS server; reads object files and refs; no working-tree mutation. Dry-run configures upload context not to send data.

Dependencies/integration points: depends on upload context implementation, transfer queues, push remote config, local refs, object path layout, and shared `useStdin` global also used by fetch in a different file name.

Risks and test signals: risks include explicit object ID mode trusting local object size from filesystem, ref lookup only by local ref name before falling back to resolve, and `--all` with explicit refs behavior. Test signals include remote required, invalid remote, stdin refs, stdin OIDs, object-id missing file, push all, explicit branch/tag/SHA, dry-run, and upload errors.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_push.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_smudge.go -->
# sources/sync-backup/git-lfs/commands/command_smudge.go

Purpose: implements the Git smudge filter and delayed smudge helper, converting LFS pointers into media content or leaving pointers when skipped/filtered.

Important APIs/types/functions: global `smudgeSkip`; `delayedSmudge`, `smudge`, `smudgeCommand`, `smudgeFilename`, and `possiblyMalformedObjectSize`; `lfs.DecodeFrom`, `GitFilter.Smudge`, `tools.Spool`, `tq.TransferQueue`, and filepath filters.

Control flow: `smudgeCommand` requires stdin, sets up repo/hooks, honors `GIT_LFS_SKIP_SMUDGE`, builds filter, and calls `smudge`. `smudge` decodes pointer input or spools non-pointers back out, links/copies reference objects, creates a progress callback, writes pointer unchanged if skipped/excluded, otherwise downloads/smudges object and falls back to writing pointer plus logging on errors. `delayedSmudge` supports filter-process delay by queueing missing allowed objects and returning status delay, or writing content/pointer immediately.

State and persistence behavior: downloads media into local object storage, writes media or pointer bytes to stdout/pktline writer, creates temp spool files for non-pointer passthrough, and may log download errors.

Dependencies/integration points: used directly by Git smudge filter and by filter-process. Integrates transfer manifest downloads, include/exclude config, reference storage, skip-download-errors behavior, and Windows large-file warnings.

Risks and test signals: risks include writing pointer fallback after partial smudge errors, callback file close only after smudge path, delayed queue requiring caller-managed status writes, and 4 GiB Windows warning heuristic. Test signals include valid pointer download, local object smudge, skip smudge, excluded path, non-pointer passthrough, missing object with skipDownloadErrors true/false, delayed missing object, delayed present object, and large object warning.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_smudge.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_standalone_file.go -->
# sources/sync-backup/git-lfs/commands/command_standalone_file.go

Purpose: implements `git lfs standalone-file`, processing standalone transfer adapter data from stdin to stdout.

Important APIs/types/functions: `standaloneFileCommand` and `standalone.ProcessStandaloneData`.

Control flow: delegates directly to standalone file processor with current config and standard streams, exiting through shared error handling on failure.

State and persistence behavior: behavior is owned by the standalone package; this command streams data and may read/write local object data according to standalone transfer protocol.

Dependencies/integration points: integrates the `lfshttp/standalone` adapter with Cobra command registration and global config.

Risks and test signals: risks are mostly delegated: protocol framing, stdin/stdout binary safety, and config availability. Test signals include valid standalone transfer requests over stdin/stdout and propagated processing errors.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_standalone_file.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_status.go -->
# sources/sync-backup/git-lfs/commands/command_status.go

Purpose: implements `git lfs status`, reporting staged/unstaged LFS-related changes, objects to push, and porcelain/JSON scriptable status.

Important APIs/types/functions: globals `porcelain`, `statusJson`; `statusCommand`, `formatBlobInfo`, `blobInfoFrom`, `blobInfoTo`, `blobInfo`, `scanIndex`, `drainScanner`, `keyFromEntry`, `statusScanRefRange`, `JSONStatusEntry`, `JSONStatus`, `jsonStagedPointers`, `porcelainStagedPointers`, `porcelainStatusLine`, and `relativize`.

Control flow: sets up working copy, resolves current ref or empty tree, creates pointer scanner, dispatches porcelain/JSON modes early, prints branch and objects to push by scanning ref range to current remote, scans cached and uncached diff-index entries, de-duplicates entries, computes relative paths from cwd, and formats each staged/unstaged entry with source/destination blob info from LFS pointer scanner or working-tree SHA-256.

State and persistence behavior: read-only; scans Git objects/index and working-tree files. JSON output accumulates map entries in memory.

Dependencies/integration points: integrates diff-index scanner, pointer scanner, current remote ref config, Git object IDs, filesystem symlink resolution, and SHA-256 content hashing for working files.

Risks and test signals: risks include JSON mode only including entries whose source is LFS, missing scanner close in early porcelain/JSON returns, working-tree hash using SHA-256 rather than Git blob SHA, and relative path edge cases. Test signals include no commits/empty tree, staged/unstaged add/modify/delete/rename/copy, missing objects, porcelain output, JSON output, subdirectory execution, and objects-to-push scan.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_status.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_track.go -->
# sources/sync-backup/git-lfs/commands/command_track.go

Purpose: implements `git lfs track`, listing or modifying Git attributes patterns for LFS tracking and lockable behavior.

Important APIs/types/functions: blocklist `prefixBlocklist`; flags `trackLockableFlag`, `trackNotLockableFlag`, `trackVerboseLoggingFlag`, `trackDryRunFlag`, `trackNoModifyAttrsFlag`, `trackNoExcludedFlag`, `trackFilenameFlag`, `trackJSONFlag`; `trackCommand`, `PatternData`, `listPatterns`, `getAllKnownPatterns`, `getAttributeLineEnding`, `blocklistItem`, `escapeGlobCharacters`, `escapeAttrPattern`, and `unescapeAttrPattern`.

Control flow: validates Git version and working copy, optionally installs hooks, lists patterns when no args, rejects JSON with modifications, loads system/user/local attributes for macro expansion and line endings, computes cwd relative to repo root, normalizes/escapes each pattern, skips already-supported patterns, prepares changed `.gitattributes` lines, rewrites existing local `.gitattributes`, appends new patterns after checking Git-tracked matches and blocklisted `.git`/`.lfs` files, touches matching tracked files to mark them modified, then fixes lockable file write flags.

State and persistence behavior: writes `.gitattributes`, changes mtimes of matching tracked files, and mutates file permissions for lockable/not-lockable changes. Dry-run disables attributes modification and avoids touching mtimes.

Dependencies/integration points: integrates Git attributes parser/macro processor, hook installation, Git tracked-file lookup, path cleanup helpers, lock client permission fixes, config line endings, and JSON encoder.

Risks and test signals: risks include map iteration ordering for appended patterns, broad extension/glob escaping differences by platform, blocklist only checking tracked matches, `.gitattributes` truncation before full write, and global flags for lockable/not-lockable conflict not explicitly rejected. Test signals include listing text/JSON, tracking new/existing patterns, dry-run, no-modify-attrs, filename literal escaping, lockable/not-lockable permissions, subdirectory execution, line-ending preservation, and forbidden file match.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_track.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_uninstall.go -->
# sources/sync-backup/git-lfs/commands/command_uninstall.go

Purpose: implements `git lfs uninstall` and `git lfs uninstall hooks`, removing Git LFS filter configuration and repository hooks.

Important APIs/types/functions: `uninstallCommand`, `uninstallHooksCommand`, shared install-scope globals from `command_install.go`, `cmdInstallOptions().Uninstall`, and `uninstallHooks`.

Control flow: builds filter options using the same scope parsing as install, uninstalls config while warning on errors, optionally removes repository hooks when in repo or local/worktree scope and not skipped, then prints scope-specific removal messages.

State and persistence behavior: removes Git config entries from selected scope and uninstalls Git LFS hook snippets/files from the repository hook directory.

Dependencies/integration points: shares flag variables and option validation with install, depends on `lfs.FilterOptions`, Git version worktree support, and hook uninstall logic in `commands.go`.

Risks and test signals: risks include shared mutable install globals, warnings not always causing nonzero exit, and no global removal message for local/worktree scopes. Test signals include global/system/local/worktree/file uninstall, skip-repo, hooks-only uninstall, non-repo behavior, and hook removal errors.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_uninstall.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_unlock.go -->
# sources/sync-backup/git-lfs/commands/command_unlock.go

Purpose: implements `git lfs unlock`, releasing locks by path or lock ID, with force and JSON modes.

Important APIs/types/functions: `unlockFlags`, `unlockResponse`, `handleUnlockError`, `unlockCommand`, `unlockAbortIfFileModified`, and `unlockAbortIfFileModifiedById`; `locking.Client.UnlockFile`, `UnlockFileById`, and `SearchLocks`.

Control flow: requires exactly one of path args or `--id`, applies optional remote override, creates lock client with remote ref, then for paths normalizes each path, rejects modified files unless `--force`, unlocks, and records JSON/text results. For ID mode it first tries to resolve lock path from local cache then server to check modification state, unlocks by ID, and reports result. Partial failures exit code 2.

State and persistence behavior: releases remote locks and updates local lock cache through client internals. It reads working-tree modification state and may allow nonexistent forced paths.

Dependencies/integration points: shares lock path normalization and JSON flag with lock/locks, depends on Git file modification checks and lock API behavior.

Risks and test signals: risks include ID mode ignoring returned error from `unlockAbortIfFileModifiedById`, path fallback with force using unnormalized user input, partial success semantics, and stale local cache path resolution. Test signals include path unlock, ID unlock, modified file rejection, force modified/nonexistent unlock, JSON success/failure arrays, remote override, and server errors.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_unlock.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_untrack.go -->
# sources/sync-backup/git-lfs/commands/command_untrack.go

Purpose: implements `git lfs untrack`, removing matching LFS filter lines from the local `.gitattributes` file.

Important APIs/types/functions: `untrackCommand` and `removePath`; shared `escapeAttrPattern`, `unescapeAttrPattern`, `tools.TrimCurrentPrefix`, and `installHooks`.

Control flow: sets up working copy, installs hooks, prints usage with no args, reads `.gitattributes`, recreates it, scans each line, preserves non-LFS lines, removes LFS filter lines whose first field matches any requested pattern after current-directory trimming and escaping, and prints untracking messages.

State and persistence behavior: truncates and rewrites `.gitattributes`. If the file does not exist it returns silently.

Dependencies/integration points: depends on track escaping rules and hook installation. It only operates on the default local attributes file, not global/system attributes.

Risks and test signals: risks include truncating before scanner completes, losing original line endings/comments around removed lines, matching only first field and `filter=lfs` substring, and no scanner error handling. Test signals include removing one/multiple tracked patterns, preserving non-LFS and unmatched lines, missing `.gitattributes`, escaped spaces/hash patterns, and no-arg usage.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_untrack.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_update.go -->
# sources/sync-backup/git-lfs/commands/command_update.go

Purpose: implements `git lfs update`, updating repository hooks and migrating legacy/invalid `lfs.<url>.access` config values.

Important APIs/types/functions: globals `updateForce`, `updateManual`; `updateCommand`; `regexp.MustCompile` for access keys; `getHookInstallSteps`; and `installHooks`.

Control flow: validates Git version and repository, scans all Git config keys for `lfs.<...>.access`, converts `private` to `basic`, removes invalid values, rejects simultaneous `--force` and `--manual`, then either prints manual hook install instructions or installs hooks with optional overwrite and detailed remediation on failure.

State and persistence behavior: mutates local Git config access keys and hook files. Manual mode only prints hook content after config access cleanup.

Dependencies/integration points: used directly and indirectly by install hooks, depends on hook loading/installing in `commands.go`, local config APIs, and regex key parsing.

Risks and test signals: risks include rewriting local config before hook failure, only accepting `basic` and `private`, shared globals with install, and manual/force conflict. Test signals include private-to-basic migration, invalid access removal, basic preservation, manual output, force overwrite, hook collision failure, and non-repo rejection.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_update.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_version.go -->
# sources/sync-backup/git-lfs/commands/command_version.go

Purpose: implements `git lfs version`, printing the Git LFS user agent/version string.

Important APIs/types/functions: global `lovesComics`; `versionCommand`; `lfshttp.UserAgent`.

Control flow: prints the user agent, and with `--comics` prints an extra easter-egg line. The command disables the normal prereq `PreRun`.

State and persistence behavior: read-only diagnostic output.

Dependencies/integration points: depends on version/user-agent construction in `lfshttp` and Cobra command registration.

Risks and test signals: risks are minimal; output stability matters for scripts. Test signals include default version output and `--comics` extra line without repository setup.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_version.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/commands.go -->
# sources/sync-backup/git-lfs/commands/commands.go

Purpose: shared command infrastructure for Git LFS commands: transfer manifest/client construction, lock client setup, hook install/uninstall, output/error/exit handling, repository setup, environment canonicalization, panic logging, filepath filter construction, progress meter creation, and Git version requirements.

Important APIs/types/functions: globals `ErrorBuffer`, `ErrorWriter`, `OutputWriter`, `ManPages`, `tqManifest`, `cfg`, `apiClient`, `global`, `cleanupOnce`, `oldEnv`, `includeArg`, `excludeArg`; functions `getTransferManifest`, `getTransferManifestOperationRemote`, `getAPIClient`, `closeAPIClient`, `newLockClient`, `newDownloadCheckQueue`, `newDownloadQueue`, `fetchRemoteRef`, `pushRemoteRef`, `buildFilepathFilter`, `buildFilepathFilterWithPatternType`, `downloadTransfer`, `getHookInstallSteps`, `installHooks`, `uninstallHooks`, `ExitWithCode`, `Error`, `Print`, `Exit`, `ExitWithError`, `FullError`, `errorWith`, `LoggedError`, `Panic`, `Cleanup`, `doCleanup`, `requireStdin`, `requireInRepo`, `requireWorkingCopy`, `setupRepository`, `verifyRepositoryVersion`, `setupWorkingCopy`, `changeToWorkingCopy`, `canonicalizeEnvironment`, `handlePanic`, `logPanic`, `ipAddresses`, `logPanicToWriter`, `determineIncludeExcludePaths`, `determineFilepathFilterCache`, `buildProgressMeter`, and `requireGitVersion`.

Control flow: commands call setup helpers to validate repo/worktree and normalize cwd. Transfer helpers lazily create API clients and manifests under a mutex. Exit paths call cleanup once before `os.Exit`. Error paths distinguish fatal stack-trace errors from plain errors. Panic logging creates timestamped log files, writes version/command/error/context/environment/IP data, and informs the user. Filepath filters merge CLI include/exclude args with config defaults and cache config.

State and persistence behavior: owns global API client and manifest caches, log files under local log dir, temporary cleanup via config, old environment map after canonicalization, and output buffers mirrored to stdout/stderr. It may set `lfs.repositoryformatversion=0` in local config.

Dependencies/integration points: central dependency for almost every command; integrates config, Git refs/version, transfer queue, API endpoints, locking, subprocess environment, LFS hooks, filepath filters, tracer/error packages, and generated manpage content.

Risks and test signals: risks include global mutable state across commands/tests, manifest cache key collisions for empty operation/remote, panic logging exposing environment, cwd prefix checks with symlinks/case sensitivity, local config mutation during setup, and `ipAddresses` ignoring address retrieval errors. Test signals include include/exclude path tests, path filter cache config, setup in bare/non-repo/worktree, panic log creation/failure, cleanup idempotence, hook install/uninstall, and min Git version enforcement.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/commands.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/commands_test.go -->
# sources/sync-backup/git-lfs/commands/commands_test.go

Purpose: unit tests for shared command helpers, currently include/exclude path selection and special migrate ref exclusion.

Important APIs/types/functions: `testcfg`, `TestDetermineIncludeExcludePathsReturnsCleanedPaths`, `TestDetermineIncludeExcludePathsReturnsEmptyPaths`, `TestDetermineIncludeExcludePathsReturnsDefaultsWhenAbsent`, `TestDetermineIncludeExcludePathsReturnsNothingWhenAbsent`, and `TestSpecialGitRefsExclusion`.

Control flow: constructs a config with default `lfs.fetchinclude` and `lfs.fetchexclude`, calls `determineIncludeExcludePaths` with explicit, empty, nil/useFetchOptions true, and nil/useFetchOptions false cases, and asserts expected slices. Special ref tests assert stash/notes/bisect/replace are excluded and a normal-ish ref is not.

State and persistence behavior: in-memory only; no filesystem or Git state.

Dependencies/integration points: uses `config.NewFrom` and `testify/assert`. It covers behavior consumed by fetch/clone/pull/ls-files/migrate filters and migrate `--everything`.

Risks and test signals: test coverage is narrow relative to `commands.go`; it does not cover path filter cache config, setup, panic logging, hook helpers, or the apparent caret exclusion bug in migrate arg parsing. Signal is fast regression coverage for default-vs-explicit include/exclude semantics and special ref namespace filtering.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/commands_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/lockverifier.go -->
# sources/sync-backup/git-lfs/commands/lockverifier.go

Purpose: lock verification support for uploads/pre-push, detecting LFS files locked by other users across refs and honoring per-endpoint locksverify configuration.

Important APIs/types/functions: `verifyState` enum, `verifyLocksForUpdates`, `lockVerifier`, methods `Verify`, `addLocks`, `Contains`, `LockedByThem`, `LockedByUs`, `UnownedLocks`, `HasUnownedLocks`, `OwnedLocks`, `HasOwnedLocks`, `Enabled`, `newRefLocks`; constructor `newLockVerifier`; `refLock` with `Path`, `Owners`, `Add`; and `getVerifyStateFor`.

Control flow: for each remote ref update, `Verify` skips disabled/already-verified refs, queries `SearchLocksVerifiable`, disables verification on not-implemented, warns or exits for auth/API errors depending on configured state, suggests enabling/disabling config for unknown support, records our/their locks by path, and marks the ref verified. Scanner-set methods classify changed names as locked by us/them and collect matched locks for later reporting.

State and persistence behavior: in-memory maps of verified refs, our locks, their locks, owned/unowned matches, and endpoint verify state. `disableFor`/`supportsLockingAPI` are external and may update config/cache outside this file.

Dependencies/integration points: integrates transfer manifest standalone detection, lock API client, endpoint URL config via `config.NewURLConfig`, upload scanning, and Git ref update structures.

Risks and test signals: risks include panicking on nil ref, owner nil assumptions in `Owners`, duplicate owned/unowned entries on repeated classification, support auto-detection changing default enabled state, and auth errors being warning-only in unknown mode. Test signals include standalone transfer disabled, explicit true/false locksverify, unknown supported/unsupported endpoints, auth failure, not implemented disabling, multiple refs same path owners string, and scanner `Contains`/LockedByThem/LockedByUs behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/lockverifier.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/multiwriter.go -->
# sources/sync-backup/git-lfs/commands/multiwriter.go

Purpose: wraps an `io.MultiWriter` while preserving the original file descriptor, allowing command output writers to behave like files for consumers that need `Fd`.

Important APIs/types/functions: `multiWriter`, `newMultiWriter`, `Write`, and `Fd`.

Control flow: constructor prepends the provided `*os.File` to additional writers, stores the file descriptor, and `Write` delegates to the multiwriter. `Fd` returns the stored descriptor.

State and persistence behavior: writes are duplicated to the file and additional writers such as `ErrorBuffer`; the fd is captured at construction.

Dependencies/integration points: used by `ErrorWriter` and `OutputWriter` in `commands.go` to mirror stdout/stderr into panic logs while retaining file descriptor compatibility.

Risks and test signals: risks include stale fd if the underlying file is closed/replaced, partial write semantics from `io.MultiWriter`, and no synchronization. Test signals include duplicated writes to buffer and file, `Fd` matching original stdout/stderr, and error propagation from secondary writers.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/multiwriter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/path.go -->
# sources/sync-backup/git-lfs/commands/path.go

Purpose: shared line-ending helper abstraction for command code that writes files or logs with Git/OS-appropriate newlines.

Important APIs/types/functions: `gitLineEnding` and interface `env`.

Control flow: reads `core.autocrlf`; returns CRLF for true/t/1, otherwise delegates to platform-specific `osLineEnding`.

State and persistence behavior: read-only config lookup; no persistence.

Dependencies/integration points: used by panic logging and track attribute writing to choose line endings. Platform behavior is supplied by `path_nix.go` or `path_windows.go`.

Risks and test signals: risks include only handling `core.autocrlf=true`, not `input`, and relying on string normalization. Test signals include true/t/1 variants, false/unset behavior on Unix and Windows, and integration with `.gitattributes` line-ending preservation.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/path.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/path_nix.go -->
# sources/sync-backup/git-lfs/commands/path_nix.go

Purpose: non-Windows platform implementation of path root cleanup and OS line-ending helpers.

Important APIs/types/functions: `cleanRootPath` and `osLineEnding`.

Control flow: `cleanRootPath` returns its input unchanged; `osLineEnding` returns LF.

State and persistence behavior: stateless and read-only.

Dependencies/integration points: selected by build tags `!windows`; used by track path normalization and shared line-ending logic.

Risks and test signals: risks are minimal; behavior assumes Unix-like shells do not rewrite root-style paths like Git Bash on Windows. Test signals are non-Windows builds preserving patterns and defaulting to LF when `core.autocrlf` is not true.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/path_nix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/path_windows.go -->
# sources/sync-backup/git-lfs/commands/path_windows.go

Purpose: Windows implementation of path root cleanup and OS line endings, specifically compensating for Git Bash drive-prefix expansion.

Important APIs/types/functions: globals `winBashPrefix`, `winBashMu`, `winBashRe`; functions `osLineEnding`, `cleanRootPath`, and `winPathHasDrive`.

Control flow: `osLineEnding` returns CRLF. `cleanRootPath` locks, returns non-drive paths unchanged, lazily locates Git Bash root by inspecting the `pwd` executable path and deriving a forward-slash prefix, then replaces that prefix with `/`. `winPathHasDrive` lazily compiles a drive-letter regex.

State and persistence behavior: process-local cached Git Bash prefix and regex; no filesystem writes.

Dependencies/integration points: used by track path normalization for Windows/Git Bash input, depends on `subprocess.ExecCommand("pwd")` and filepath path derivation.

Risks and test signals: risks include deriving the wrong prefix from unusual `pwd` locations, replacing only first prefix occurrence, concurrency around regex initialization mostly protected by caller lock for `cleanRootPath` but not direct `winPathHasDrive`, and mixed slash cases. Test signals include `C:/Program Files/Git/foo` conversion, normal relative paths unchanged, backslash drive paths, missing `pwd`, and concurrent calls.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/path_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/pointers.go -->
# sources/sync-backup/git-lfs/commands/pointers.go

Purpose: small helper to collect all wrapped pointers from an asynchronous LFS pointer channel and return the channel's terminal error.

Important APIs/types/functions: `collectPointers` and `lfs.PointerChannelWrapper`.

Control flow: ranges over `pointerCh.Results`, appends every pointer to a slice, then returns the collected slice and `pointerCh.Wait()` error.

State and persistence behavior: in-memory slice only; no persistence.

Dependencies/integration points: helper for scanner/channel APIs elsewhere in commands or adjacent files, preserving channel completion error semantics.

Risks and test signals: risks include unbounded memory use for large pointer sets and blocking forever if producer never closes. Test signals include normal pointer collection, empty channel, and propagation of wait errors after result drain.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/pointers.go -->
