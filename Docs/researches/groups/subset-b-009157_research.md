# Research Report: subset-b-009157

Work item `subset-b-009157` covers restic command integration tests, lock and main entrypoint code, documentation/build helpers, completion scripts, Docker packaging, release tooling, release verification, and the core archiver snapshot pipeline.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/integration_test.go -->
# sources/sync-backup/restic/cmd/restic/integration_test.go

## Purpose

This file contains integration-style tests for restic command behavior around repository locking, backend list semantics, backend reader capabilities, and transient repository config access failures. The tests are written in package `main`, so they exercise the command-layer helpers and options directly rather than only testing exported internal packages.

## Important APIs, Types, and Functions

- `TestCheckRestoreNoLock` builds a readonly repository fixture, sets `env.gopts.NoLock = true`, then runs check, snapshot listing, and restore. It validates that read-oriented commands still work when locking is deliberately disabled and the repository storage cannot be written.
- `listOnceBackend` embeds `backend.Backend` and tracks file types listed through `List`. It rejects a second listing of any non-lock `restic.FileType`. With `strictOrder`, it also rejects listing snapshots after indexes, catching workflows that would break on eventually consistent backends.
- `newListOnceBackend` and `newOrderedListOnceBackend` are small wrappers used as backend test hooks.
- `TestListOnce` installs `newOrderedListOnceBackend`, creates a prunable repository, runs prune, check with read-data and unused checks, and rebuild-index with and without reading all packs. The test asserts these commands do not rely on repeated listing and preserve the expected index/snapshot listing order.
- `writeToOnly` implements `io.Reader` and `io.WriterTo`, but its `Read` method fails. It catches code paths that accidentally drop the `WriterTo` optimization/capability.
- `onlyLoadWithWriteToBackend` wraps `Load` so every load callback receives a `writeToOnly` reader.
- `TestBackendLoadWriteTo` installs that wrapper as `BackendInnerTestHook`, disables cache during a backup to force backend reads later, then re-enables cache and lists snapshots. Success means layered backend/load code preserves `WriteTo`.
- `failConfigOnceBackend` embeds `backend.Backend` and fails exactly once for config `Load` or `Stat`, depending on which method is used first.
- `TestBackendRetryConfig` installs `failConfigOnceBackend`, initializes test data, then runs another backup. It asserts config loading retries both during init/open and later command execution.
- External helpers used heavily here include `withTestEnvironment`, `testSetupBackupData`, `testRunBackup`, `testRunCheck`, `testRunRestore`, `testListSnapshots`, `testRunPrune`, `runCheck`, `runRebuildIndex`, `openWithReadLock`, and `FindFilteredSnapshots`.

## Control Flow

Each test creates a temporary restic test environment, injects optional backend wrappers through `global.Options` hooks, runs command-level helpers, and fails via `internal/test` assertions. Backend wrappers intercept `List`, `Load`, or `Stat` at the backend boundary. The `ListOnce` tests force prune/check/rebuild-index/find flows through a backend that can tolerate only one list pass per type. `TestFindListOnce` backs up three snapshots, combines explicit full ID, short ID, and `"latest"` selectors, and confirms the resulting ID set equals the known three snapshots without requiring another backend listing.

## State and Persistence Behavior

The tests create real repository fixtures under temporary directories and mutate repository contents through backup/prune/check/rebuild/restore commands. `TestCheckRestoreNoLock` changes filesystem permissions under `env.repo` to remove write bits and then verifies no-lock read operations avoid lock writes. The backend wrappers maintain in-memory state (`listedFileType`, `failedOnce`) only for a single test run. The tests also exercise cache behavior by toggling `env.gopts.NoCache`.

## Dependencies and Integration Points

The file depends on restic internals: `internal/backend`, `internal/data`, `internal/errors`, `internal/global`, `internal/restic`, `internal/test`, and `internal/ui/progress`. Its main integration point is `global.Options` backend hook support, which allows tests to wrap configured backends without changing production command code. It also directly exercises command package functions such as `runCheck`, `runRebuildIndex`, `openWithReadLock`, and snapshot filtering.

## Risks and Edge Cases

- The list-once wrappers intentionally exempt lock files; commands may list locks multiple times during locking/unlocking without failing these tests.
- `strictOrder` specifically guards against listing snapshots after indexes, a subtle risk for eventually consistent object stores.
- `writeToOnly.Read` panics through an error rather than returning EOF, making capability loss obvious.
- `failConfigOnceBackend` fails either `Load` or `Stat`, depending on access path. Tests therefore cover retry behavior without depending on one exact config access method.
- Permission changes in `TestCheckRestoreNoLock` rely on the test fixture and host filesystem honoring chmod semantics.

## Test Signals

This file is itself a test signal for backend abstractions and command integration. Passing tests indicate read operations can run with `--no-lock`, backup/check/rebuild/find avoid unsafe repeated listings, backend `Load` preserves `io.WriterTo`, and transient config access errors are retried.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/integration_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/lock.go -->
# sources/sync-backup/restic/cmd/restic/lock.go

## Purpose

This file centralizes command-layer repository opening with optional locking. It provides small helpers for read, append, and exclusive command modes and delegates actual repository opening and lock acquisition to internal global/repository packages.

## Important APIs, Types, and Functions

- `internalOpenWithLocked(ctx, gopts, dryRun, exclusive, printer)` opens the repository via `global.OpenRepository`. If `dryRun` is false, it acquires a repository lock with `repository.LockRepo`; if `dryRun` is true, it marks the repository as dry-run with `repo.SetDryRun()` and skips locking.
- `openWithReadLock(ctx, gopts, noLock, printer)` calls `internalOpenWithLocked` with `exclusive=false` and maps its `noLock` argument to `dryRun`.
- `openWithAppendLock(ctx, gopts, dryRun, printer)` opens a non-exclusive lock unless dry-run is requested.
- `openWithExclusiveLock(ctx, gopts, dryRun, printer)` opens an exclusive lock unless dry-run is requested.

All helpers return the possibly updated context, the opened `*repository.Repository`, an `unlock` callback, and an error.

## Control Flow

The common helper first opens the repository. It initializes `unlock` to a no-op so callers can defer it safely only after checking errors. For non-dry-run operations it calls `repository.LockRepo(ctx, repo, exclusive, gopts.RetryLock, statusCallback, printer.E)`. The status callback prints retry/lock messages through `printer.P` unless JSON output is enabled. On success, the lock's `Unlock` method becomes the returned cleanup function. For dry-run/no-lock operations it marks the repository dry-run and returns without lock acquisition.

## State and Persistence Behavior

The main persistent side effect is creation/removal of repository lock files through `repository.LockRepo` and the returned `Unlock` function. Dry-run/no-lock mode avoids lock file writes and changes in-memory repository state via `SetDryRun`. The helper does not itself persist data beyond lock behavior.

## Dependencies and Integration Points

The file depends on `internal/global` for repository construction, `internal/repository` for locking, and `internal/ui/progress` for output. It is used by many command implementations that need consistent lock policy. It also interacts with `global.Options.RetryLock`, `global.Options.JSON`, and the terminal printer interface.

## Risks and Edge Cases

- `openWithReadLock` currently treats `noLock` as `dryRun`; the TODO notes that stronger read-only enforcement is still pending until locking moves deeper into the repository layer.
- If `repository.LockRepo` fails after opening a repository, the returned repo is discarded and no unlock function is returned. Callers must handle the error path.
- JSON mode suppresses human lock retry messages to avoid corrupting structured output.
- The dry-run path avoids locks, so commands using it must ensure they do not persist unintended repository changes.

## Test Signals

`integration_test.go` covers no-lock behavior with a readonly repository. Broader command tests that run append/exclusive operations indirectly cover successful locking and unlock cleanup.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/lock.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/main.go -->
# sources/sync-backup/restic/cmd/restic/main.go

## Purpose

This file is the restic CLI entrypoint. It configures process-level runtime behavior, constructs the Cobra root command, registers all subcommands and global flags, applies feature flags, wires terminal status handling, normalizes command errors into user-facing messages, and maps errors to stable exit codes.

## Important APIs, Types, and Functions

- `init` calls `maxprocs.Set()` from `go.uber.org/automaxprocs/maxprocs` to honor container CPU limits while suppressing log output.
- `ErrOK` is a sentinel error used by commands to indicate a successful early exit that should override context cancellation.
- `cmdGroupDefault` and `cmdGroupAdvanced` identify Cobra command groups.
- `newRootCommand(globalOptions *global.Options)` constructs the root `*cobra.Command`, installs `PersistentPreRunE`, registers command groups, adds persistent global flags, disables Cobra's default completion command, registers every restic subcommand, and adds optional debug/mount/self-update/profiling hooks.
- `needsPassword(cmd string)` returns false for commands that should not invoke password retrieval (`cache`, `generate`, `help`, `options`, `self-update`, `version`, and Cobra completion commands).
- `tweakGoGC()` lowers default `GOGC` from 100 to 50 only when the user has not set a different value.
- `printExitError(globalOptions, code, message)` writes either a JSON `exit_error` object to stderr or a plain text message.
- `main()` performs runtime setup, command execution, error formatting, exit-code selection, and final `Exit(exitCode)`.

## Control Flow

Startup first adjusts garbage collection, redirects the standard logger to an in-memory buffer, and applies feature flags from `RESTIC_FEATURES`. It logs debug process/build information, constructs `global.Options` with all registered backends, then sets up terminal status around command execution. `newRootCommand(...).ExecuteContext(ctx)` runs Cobra. If the command returns nil, `main` checks the global context error; if it returns `ErrOK`, the error is cleared.

After command execution, `main` converts known error classes into messages: already locked errors include an unlock hint, invalid source data becomes a warning, fatal errors and missing keys receive special wording, and generic errors are formatted with stack/detail via `%+v`. If any library messages were captured in the log buffer, they are appended to the generic error message. A second switch maps errors to exit codes: success `0`, invalid source or failed snapshot removal `3`, no repository `10`, already locked `11`, no key `12`, context canceled `130`, and generic failure `1`.

## State and Persistence Behavior

The file affects process-wide state: Go GC percentage, logger output destination, enabled feature flags, terminal status setup, profiling registration, and process exit. It does not directly write repository data, but all command execution flows pass through the root command and `global.Options`. The in-memory log buffer is intentionally transient and only emitted on errors.

## Dependencies and Integration Points

Core dependencies are Cobra, automaxprocs, restic backend registry `internal/backend/all`, debug/logging, feature flags, global options, repository error predicates, and terminal status handling. It integrates every command constructor: backup, cache, cat, check, copy, diff, dump, features, find, forget, generate, init, key, list, ls, migrate, options, prune, rebuild-index, recover, repair, restore, rewrite, snapshots, stats, tag, unlock, and version. Optional debug, mount, self-update, and profiling registration are also attached here.

## Risks and Edge Cases

- Commands that do not need a password must be kept in sync with `needsPassword`; otherwise password commands may run unnecessarily or needed credentials may be skipped.
- Error-to-exit-code mapping is part of the CLI contract and affects scripts.
- Appending captured library logs to user-facing errors can expose noisy dependency logs, but only on generic errors.
- JSON output mode must encode errors cleanly; if JSON encoding itself fails, the code falls back to a plain diagnostic and debug log.
- Lowering GC can trade CPU for memory and is intentionally skipped if the user has set another `GOGC`.

## Test Signals

Command integration tests throughout `cmd/restic` exercise root command execution, pre-run behavior, lock errors, JSON output, and exit mappings indirectly. `integration_test.go` in this subset reaches `global.Options` command flows, repository opening, and error handling around backend behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/doc.go -->
# sources/sync-backup/restic/doc.go

## Purpose

This package documentation file describes the intended source layout of restic. It declares package `restic` and explains that the repository is primarily a command-line program rather than an importable library.

## Important APIs, Types, and Functions

There are no runtime APIs or functions. The file contains package-level Go documentation for `package restic`.

## Control Flow

There is no executable control flow.

## State and Persistence Behavior

There is no state or persistence behavior.

## Dependencies and Integration Points

The file has no imports. Its integration point is Go documentation tooling: `go doc` and package documentation generated from comments. It establishes architectural context for `cmd/` as the main binary package and `internal/` as the location of almost all library-form implementation.

## Risks and Edge Cases

The key maintenance risk is documentation drift if restic's architecture changes or if internal packages become supported library APIs. The comment explicitly says the non-library decision may be revisited later.

## Test Signals

There are no direct tests. Documentation consistency is indirectly checked by normal Go package parsing and documentation generation.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/doc/Makefile -->
# sources/sync-backup/restic/doc/Makefile

## Purpose

This Makefile is a minimal Sphinx documentation build wrapper. It exposes the standard Sphinx "make mode" targets and an `autobuild` helper for live HTML documentation development.

## Important APIs, Types, and Functions

- Variables: `SPHINXOPTS`, `SPHINXBUILD`, `SPHINXPROJ`, `SOURCEDIR`, and `BUILDDIR`.
- `help` target runs `sphinx-build -M help`.
- Pattern target `%: Makefile` forwards arbitrary make targets to `sphinx-build -M <target>`.
- `autobuild` runs `sphinx-autobuild -b html -i '.doctrees/*' . _build`.

## Control Flow

`make` defaults to `help` because the `help` target appears first. Any unknown target, such as `html`, `dirhtml`, or `linkcheck`, is routed to Sphinx's make-mode builder with source directory `.` and build directory `_build`. `O` can pass extra options to Sphinx as a shortcut for `SPHINXOPTS`.

## State and Persistence Behavior

Build outputs are written below `_build`. `autobuild` watches the documentation tree and refreshes generated HTML while ignoring `.doctrees` output. The Makefile itself does not delete outputs.

## Dependencies and Integration Points

It depends on `sphinx-build` and optionally `sphinx-autobuild`. It is configured by `doc/conf.py` and the `.rst` documentation tree in the same directory. It integrates with local developer workflows and CI/documentation builds that call `make -C doc html` or similar.

## Risks and Edge Cases

- Missing Sphinx or theme dependencies cause targets to fail.
- The catch-all target will forward typos to Sphinx, so user feedback depends on Sphinx's target handling.
- `autobuild` assumes `sphinx-autobuild` is installed locally.

## Test Signals

Successful `make html` or `make linkcheck` in `doc/` validates the Makefile, Sphinx config, and documentation source compatibility.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/doc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/doc/bash-completion.sh -->
# sources/sync-backup/restic/doc/bash-completion.sh

## Purpose

This generated Bash completion script wires restic command, flag, and dynamic completion behavior into Bash's `complete` system. It combines static Cobra-generated command/flag tables with runtime calls to `restic __completeNoDesc` for commands that expose Go-side completion functions.

## Important APIs, Types, and Functions

- `__restic_debug` appends debug messages to `BASH_COMP_DEBUG_FILE` when set.
- `__restic_init_completion` provides a minimal fallback for systems without Bash completion's `_init_completion`.
- `__restic_index_of_word` and `__restic_contains_word` are utility search helpers for arrays.
- `__restic_handle_go_custom_completion` invokes `RESTIC_ACTIVE_HELP=0 <cmd> __completeNoDesc ...`, parses Cobra shell completion directives, and populates `COMPREPLY`.
- `__restic_handle_reply` decides whether to complete flags, flag values, subcommands, nouns, dynamic Go completions, or fallback custom functions.
- `__restic_handle_filename_extension_flag`, `__restic_handle_subdirs_in_dir_flag`, `__restic_handle_flag`, `__restic_handle_noun`, `__restic_handle_command`, and `__restic_handle_word` implement the parser/walker for the current command line.
- `_restic_<command>` functions, such as `_restic_backup`, `_restic_forget`, `_restic_generate`, `_restic_restore`, and many others, populate command-local arrays: `commands`, `flags`, `two_word_flags`, `local_nonpersistent_flags`, `flags_with_completion`, `flags_completion`, `must_have_one_flag`, `must_have_one_noun`, and aliases.
- `_restic_root_command` declares top-level subcommands and global persistent flags.
- `__start_restic` initializes parser state and calls `__restic_handle_word`.
- Final registration calls `complete -o default -F __start_restic restic` or adds `-o nospace` when `compopt` is unavailable.

## Control Flow

When Bash requests completion for `restic`, `__start_restic` obtains `cur`, `prev`, `words`, and `cword`, initializes state arrays, and recursively processes each word. Command words dispatch to `_restic_root_command` or a command-specific `_restic_*` function. Flags update required flag/noun state, may consume the following value for two-word flags, and suppress subcommands when a local nonpersistent flag has been seen. Once the parser reaches the current word, `__restic_handle_reply` builds completion candidates.

For dynamic completions, the script calls the running restic binary's hidden Cobra completion endpoint. It parses the trailing directive bitmask for error, no-space, no-file-completion, file-extension filtering, and directory filtering. It then either uses `_filedir`, directory-only completion, or `compgen` to populate `COMPREPLY`.

## State and Persistence Behavior

The script stores only shell-local and completion-session state. It may temporarily set associative arrays `flaghash` and `aliashash` when supported by Bash. It does not persist files except optional debug logging to the user-selected `BASH_COMP_DEBUG_FILE`.

## Dependencies and Integration Points

It depends on Bash completion primitives (`complete`, `compopt`, `_get_comp_words_by_ref`, `_filedir`) with fallbacks for older macOS/Homebrew environments. Its runtime integration depends on the installed `restic` executable supporting Cobra hidden completion commands. The static command/flag tables must be regenerated when CLI commands or flags change, normally via restic's `generate` command and release tooling.

## Risks and Edge Cases

- Generated static flag tables can drift from command code if not regenerated.
- Dynamic completion uses `eval` to run the constructed completion command, matching Cobra's generated pattern but requiring careful quoting of command words.
- Bash 3 lacks associative arrays; the script degrades alias/flag hash behavior for compatibility.
- Active Help is disabled for Bash completion v1.
- Completion directive parsing assumes the final colon-suffixed directive format emitted by Cobra.
- Missing `_filedir` or `_get_comp_words_by_ref` on nonstandard environments can reduce completion quality.

## Test Signals

Manual shell completion, generated completion comparison, and release `generateFiles` flows are the primary signals. The script should also be indirectly checked by invoking `restic generate --bash-completion` and comparing the committed output.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/doc/bash-completion.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/doc/conf.py -->
# sources/sync-backup/restic/doc/conf.py

## Purpose

This is the Sphinx configuration for restic's documentation. It sets project metadata, extensions, source conventions, theme settings, GitHub integration metadata, static assets, exclusions, and external issue links.

## Important APIs, Types, and Functions

- `extensions` enables `sphinx.ext.extlinks` and `sphinx_rtd_theme`.
- `templates_path`, `source_suffix`, and `master_doc` configure source layout.
- `project`, `copyright`, and `author` provide metadata.
- `version` is read from `../VERSION`; `release` mirrors it.
- `exclude_patterns` skips build/system files and several documents included via `100_references.rst` to avoid duplicate labels.
- `html_theme`, `html_css_files`, `html_logo`, `html_favicon`, `html_show_version`, and `html_static_path` control HTML rendering.
- `html_context` enables GitHub edit/source links for the `restic/restic` repository and `master/doc/`.
- `extlinks` defines `:issue:` links to GitHub issues.

## Control Flow

Sphinx imports this file during builds. The only dynamic action is reading the first line of `../VERSION` to set `version` and `release`. Everything else is declarative module-level configuration.

## State and Persistence Behavior

The config reads the repository `VERSION` file. It does not write state. Generated documentation output is controlled by Sphinx and the Makefile, typically under `doc/_build`.

## Dependencies and Integration Points

It depends on Sphinx, `sphinx_rtd_theme`, static files in `_static`, custom CSS at `css/restic.css`, logo assets, and the documentation `.rst` tree. It integrates with Read the Docs-style theming and GitHub issue references.

## Risks and Edge Cases

- Opening `../VERSION` depends on Sphinx's working directory/import context being `doc/`, which is the normal Sphinx behavior.
- The copyright year is static and can drift.
- Excluded documents are still included indirectly; changing documentation references can reintroduce duplicate labels or hide pages unexpectedly.
- Theme/static asset paths must remain valid.

## Test Signals

Successful Sphinx builds through `doc/Makefile` validate this file. Link/reference checks can catch broken `extlinks`, duplicate labels, and missing excluded-document references.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/doc/conf.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/doc/fish-completion.fish -->
# sources/sync-backup/restic/doc/fish-completion.fish

## Purpose

This generated Fish shell completion script integrates restic with Fish's `complete` system. It delegates actual command-specific completion generation to restic's Cobra completion endpoint and adapts Cobra directives to Fish behavior.

## Important APIs, Types, and Functions

- `__restic_debug` writes debug output to `BASH_COMP_DEBUG_FILE` when set.
- `__restic_perform_completion` reads the current Fish commandline, disables Active Help with `RESTIC_ACTIVE_HELP=0`, calls `<program> __complete`, strips trailing empty lines, applies flag `--x=` prefixes, prints completions, and prints the directive line.
- `__restic_perform_completion_once` caches the completion result in the global variable `__restic_perform_completion_once_result` so multiple Fish `complete` invocations in one completion cycle do not rerun restic.
- `__restic_clear_perform_completion_once_result` clears that cache after completion.
- `__restic_requires_order_preservation` checks the Cobra `KeepOrder` directive bit and controls whether Fish's `-k` option is used.
- `__restic_prepare_completions` parses directive bits, stores candidate completions in `__restic_comp_results`, handles no-space/no-file-completion semantics as far as Fish allows, and decides whether to fall back to file completion.
- Final `complete` calls clear old completions, install cache clearing, and register ordered or normal completion candidates for `restic`.

## Control Flow

When completion is requested, Fish evaluates the registered conditions. The script calls `__restic_perform_completion_once`, which invokes restic at most once for the current completion attempt. `__restic_prepare_completions` parses the last line directive, filters completions by the current token prefix when needed, handles unsupported file-extension/directory filters by requesting normal file completion, and stores candidates for the `complete -a` argument. `__restic_requires_order_preservation` may run against the same cached result to decide whether to use `complete -k`.

## State and Persistence Behavior

The script uses global Fish variables as short-lived completion caches and erases them after use. It has no persistent state except optional debug logging. It proactively triggers existing completions with `complete --do-complete "restic "` when `restic` is on PATH, then erases pre-existing restic completions to ensure this script owns completion behavior.

## Dependencies and Integration Points

It depends on Fish builtins (`commandline`, `string`, `math`, `complete`, `type`) and the installed `restic` command's `__complete` endpoint. It integrates with Cobra's shell completion directive protocol. Active Help is disabled because this script does not support it for Fish.

## Risks and Edge Cases

- File extension and directory filtering directives are explicitly not supported; the script falls back to general file completion.
- The completion command is built as a string and executed with `eval`, so escaping from `commandline` is important.
- Fish's no-space behavior differs from Bash/Zsh; the script uses a two-completion trick for a single no-space match when needed.
- Cache globals must be cleared reliably or stale completions could leak between attempts.

## Test Signals

Manual Fish completion tests and regenerated completion comparisons are the main signals. Commands using dynamic completion should be tested for prefix filtering, flag-with-equals completion, no-file-completion, and keep-order behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/doc/fish-completion.fish -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/doc/zsh-completion.zsh -->
# sources/sync-backup/restic/doc/zsh-completion.zsh

## Purpose

This generated Zsh completion script integrates restic with Zsh's completion system. It delegates to restic's Cobra `__complete` endpoint, interprets completion directives, supports Active Help, and maps candidates into Zsh `_describe`, `_files`, and `_arguments` calls.

## Important APIs, Types, and Functions

- `#compdef restic` and `compdef _restic restic` register the completion function.
- `__restic_debug` writes diagnostics to `BASH_COMP_DEBUG_FILE` when set.
- `_restic` is the main completion function. It defines Cobra directive constants, truncates `words` to the cursor position, detects flag-with-equals prefixes, constructs and evaluates the `__complete` request, parses the trailing directive line, separates Active Help lines, builds `completions`, and dispatches to the right Zsh completion primitive.
- Directive handling covers error, no-space, no-file-completion, file-extension filtering, directory filtering, and keep-order.
- The final guard runs `_restic` only when the function is invoked by Zsh completion rather than merely sourced/evaluated.

## Control Flow

On completion, `_restic` trims the command word list to `CURRENT`, inspects the current/last parameter, and appends an empty argument if the cursor follows a space. It calls the active restic binary with `__complete`, then reads the last output line to find a colon-prefixed directive. It loops over completion lines, handling `_activeHelp_ ` entries separately through `compadd -x`, converts tab-separated descriptions to the colon format expected by `_describe`, and escapes colons in completion values.

If the directive requests extension filtering, it builds an `_files -g` command. If it requests directory filtering, it optionally `pushd`s into the specified subdirectory and uses `_files -/`. Otherwise it calls `_describe`, optionally with `-S ''` for no-space and `-V` for keep-order. If `_describe` finds nothing and file completion is allowed, it falls back to `_files`.

## State and Persistence Behavior

All state is local to a Zsh completion invocation. It does not persist files except optional debug logging. It may temporarily change directories for directory-filtered completion and restores the prior directory with `popd`.

## Dependencies and Integration Points

It depends on Zsh completion functions (`compdef`, `compadd`, `_describe`, `_arguments`, `_files`) and the installed restic binary's Cobra completion endpoint. It supports Cobra Active Help markers, unlike the Bash/Fish scripts in this subset.

## Risks and Edge Cases

- The script uses `eval` for the request command and for `_describe` invocation with dynamically assembled options.
- Correct colon escaping and tab-to-colon conversion are required for Zsh descriptions.
- Directory filtering temporarily changes directories and must always restore state when a subdir was used.
- Docker/package installs must place this file in a location loaded by Zsh's completion path.

## Test Signals

Manual Zsh completion tests should cover descriptions, Active Help display, `--flag=` prefixes, extension filtering, directory-only filtering, no-space, no-file-completion, and keep-order candidates. Regeneration by `restic generate --zsh-completion` should match committed output.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/doc/zsh-completion.zsh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/docker/Dockerfile -->
# sources/sync-backup/restic/docker/Dockerfile

## Purpose

This Dockerfile builds a restic container image. It uses a Go Alpine builder stage to compile restic from source and a minimal Alpine runtime stage with restic plus operational dependencies.

## Important APIs, Types, and Functions

- Builder stage: `FROM golang:1.26-alpine AS builder`, working directory `/go/src/github.com/restic/restic`, dependency cache via `COPY go.mod go.sum ./` and `go mod download`, source copy, and `go run build.go`.
- Runtime stage: `FROM alpine:latest AS restic`, installs `ca-certificates`, `fuse`, `openssh-client`, `tzdata`, and `jq`.
- Copies `/go/src/github.com/restic/restic/restic` to `/usr/bin`.
- Copies `docker/entrypoint.sh` to `/entrypoint.sh`.
- Defines `IONICE_CLASS`, `IONICE_PRIORITY`, and `NICE` environment defaults.
- Sets `ENTRYPOINT ["/entrypoint.sh"]`.

## Control Flow

Docker builds the binary in the first stage after downloading modules, then starts a fresh Alpine runtime image and copies only the resulting binary and entrypoint script. At container runtime, execution is delegated to `entrypoint.sh`, which wraps restic with optional `ionice` and `nice`.

## State and Persistence Behavior

Build cache state is managed by Docker layers, especially the separate module-download layer. The image itself contains the compiled restic binary and runtime packages. Runtime repository/cache persistence depends on user-mounted volumes and restic options, not the Dockerfile.

## Dependencies and Integration Points

It depends on Go, Alpine package repositories, `build.go`, module files, and `docker/entrypoint.sh`. Runtime packages support TLS certificates, FUSE-based mount usage, SSH backends, timezone handling, and JSON processing via `jq`. `docker/build.sh` is the local wrapper for building this Dockerfile.

## Risks and Edge Cases

- `golang:1.26-alpine` and `alpine:latest` are moving tags; reproducibility and compatibility depend on current image contents.
- `COPY . .` invalidates the build layer when any source changes.
- Runtime `fuse` support also requires container privileges/devices from the user.
- Entry point defaults intentionally avoid `ionice -c0 -n...` because BusyBox rejects that combination.

## Test Signals

Successful `docker/build.sh` or `docker build -f docker/Dockerfile` validates the build. Runtime smoke tests should run `restic version`, backend operations with mounted volumes, and optional `IONICE_CLASS`/`NICE` behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/docker/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/docker/build.sh -->
# sources/sync-backup/restic/docker/build.sh

## Purpose

This shell script builds the local Docker image `restic/restic:latest` using the repository's Dockerfile and root as build context.

## Important APIs, Types, and Functions

- Resolves `root` from the script path using `readlink -f "$0"` and two `dirname` calls.
- Uses `set -e` to stop on failures.
- Exports `DOCKER_BUILDKIT=${DOCKER_BUILDKIT-1}` to enable BuildKit by default unless already set.
- Runs `docker build --rm --pull --file "$root"/docker/Dockerfile --tag restic/restic:latest "$root" "$@"`.

## Control Flow

The script determines the repository root independent of caller working directory, enables BuildKit by default, prints a build message, and delegates to `docker build`. Additional user-provided arguments are appended after the build context.

## State and Persistence Behavior

It creates or updates the local Docker image tag `restic/restic:latest` and may update local Docker build cache/layers. It does not write repository files.

## Dependencies and Integration Points

It depends on POSIX `sh`, `readlink`, `dirname`, and Docker. It integrates with `docker/Dockerfile` and is likely used by developers or packaging automation for local image builds.

## Risks and Edge Cases

- `readlink -f` is not portable to all macOS environments without GNU coreutils.
- Appending `"$@"` after the context is unusual for some Docker CLI options; many options must appear before the context to be accepted.
- `--pull` can change base image versions and reduce reproducibility.

## Test Signals

Running `docker/build.sh` successfully and then `docker run --rm restic/restic:latest version` provides a basic validation signal.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/docker/build.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/docker/entrypoint.sh -->
# sources/sync-backup/restic/docker/entrypoint.sh

## Purpose

This entrypoint script runs restic inside the container, optionally wrapping it with `ionice` and always wrapping it with `nice`. It handles BusyBox `ionice` quirks by only invoking `ionice` when a non-empty class is provided.

## Important APIs, Types, and Functions

- Shebang `#!/bin/sh -e` exits on command failures.
- `set -- /usr/bin/restic "$@"` makes restic plus user arguments the command.
- If `IONICE_CLASS` is non-empty, the command becomes `ionice -c "$IONICE_CLASS" -n "${IONICE_PRIORITY:-4}" ...`.
- Final `exec nice -n "${NICE:-0}" "$@"` replaces the shell with the adjusted command.

## Control Flow

At container start, the script constructs an argument vector. It conditionally prepends `ionice`, then executes `nice`, which in turn executes either restic directly or ionice/restic depending on configuration.

## State and Persistence Behavior

The script does not write state. It affects process scheduling priority and optional I/O scheduling for the restic process.

## Dependencies and Integration Points

It depends on BusyBox/Alpine `sh`, `nice`, optionally `ionice`, and `/usr/bin/restic`. It is the entrypoint declared by `docker/Dockerfile` and is controlled by image environment variables `IONICE_CLASS`, `IONICE_PRIORITY`, and `NICE`.

## Risks and Edge Cases

- Invalid `IONICE_CLASS`, `IONICE_PRIORITY`, or `NICE` values cause startup failure.
- `ionice` is skipped by default because class `0` with a priority is rejected by BusyBox.
- Since `exec` is used, signal handling is correctly transferred to the final process.

## Test Signals

Container smoke tests should run with default environment and with explicit `IONICE_CLASS`/`IONICE_PRIORITY` values. `ps` or process inspection can confirm the shell is replaced and signals reach restic.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/docker/entrypoint.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/helpers/build-release-binaries/main.go -->
# sources/sync-backup/restic/helpers/build-release-binaries/main.go

## Purpose

This Go helper builds restic release binaries for a matrix of target operating systems and architectures. It is intended to run in the release builder environment, producing named binaries or compressed archives under an output directory.

## Important APIs, Types, and Functions

- `opts` stores flags: verbose, source/output directories, extra build tags, platform subset, single platform, skip compression, and version.
- `init` registers pflag options.
- `die`, `msg`, and `verbose` print colored messages and handle fatal errors.
- Filesystem helpers: `rm`, `mkdir`, `abs`, `modTime`, `touch`, and `chmod`.
- `build(sourceDir, outputDir, goos, goarch)` invokes `go build` for `./cmd/restic` with `CGO_ENABLED=0`, `GOOS`, `GOARCH`, `-ldflags "-s -w"`, and tags `selfupdate,disable_grpc_modules` plus optional user tags. ARM builds set `GOARM=6`.
- `compress(goos, inputDir, filename)` creates `.zip` archives for Windows and `.bz2` for other platforms, then removes the uncompressed binary.
- `buildForTarget` builds, sets timestamps to the `VERSION` file modtime, chmods executable mode, and optionally compresses.
- `buildTargets` runs builds concurrently through an `errgroup` and job channel. Worker count is `GOMAXPROCS/4`, minimum one.
- `defaultBuildTargets` defines the release platform matrix.
- `downloadModules` runs `go mod download`.
- `selectSubset` splits the sorted platform list into deterministic `n/t` shards.
- `buildPlatformList` converts `os/arch` strings into the target map.
- `main` validates arguments, selects targets, prepares directories, downloads modules, and builds.

## Control Flow

The program parses flags at init. `main` rejects positional arguments, chooses the target matrix from defaults, `--platform-subset`, or `--platform`, resolves absolute source/output paths, creates the output directory, downloads modules, and starts concurrent builds. Each job builds a binary, normalizes its timestamp and executable mode, compresses it unless disabled, and logs duration.

## State and Persistence Behavior

Outputs are written to `opts.OutputDir`, default `/output`. Existing compressed output files for a target are removed before compression. Uncompressed binaries are removed after compression unless `--skip-compress` is set. Timestamps are set to match the source `VERSION` file to improve reproducibility. The helper also uses the Go module cache and reads source from `opts.SourceDir`.

## Dependencies and Integration Points

It depends on `go`, `zip`, `bzip2`, Go modules, pflag, and `golang.org/x/sync/errgroup`. It is called by `helpers/prepare-release/main.go` inside the `restic/builder` Docker container and by `helpers/verify-release-binaries.sh` to reproduce binaries. The build tag `disable_grpc_modules` is used to reduce binary size after Google Cloud Storage dependency changes.

## Risks and Edge Cases

- `errgroup.Wait()` result is ignored in `buildTargets`, but worker errors call `die` and exit the process, so normal errors do not propagate as Go errors.
- Map iteration order is nondeterministic for job scheduling, but `selectSubset` sorts platforms before slicing for deterministic sharding.
- Cross-platform reproducibility depends on builder image, Go version, module versions, compression tools, timestamps, and environment.
- `platform-subset` validation allows `total == 0` through until division would be unsafe; callers should pass valid `t/n` with `n > 0`.
- Windows ZIP uses `zip -q -X` to reduce metadata, while non-Windows uses bzip2.

## Test Signals

Release verification rebuilds with this helper and checks `SHA256SUMS`. A narrow smoke test is `go run helpers/build-release-binaries/main.go --platform linux/amd64 --output <dir> --source <repo>`.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/helpers/build-release-binaries/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/helpers/prepare-release/main.go -->
# sources/sync-backup/restic/helpers/prepare-release/main.go

## Purpose

This Go helper orchestrates restic's release preparation. It validates release preconditions, updates generated docs/completions and version files, creates signed tags and source tarballs, builds release binaries in Docker, writes checksums/signatures, prepares Docker publish commands, and prints final push/cleanup instructions.

## Important APIs, Types, and Functions

- `opts` captures release version and ignore flags for branch, uncommitted changes, changelog checks, Docker builder Go version, plus output directory.
- `versionRegex` requires semantic `x.y.z` versions.
- Utility functions `die`, `msg`, `run`, `replace`, `rm`, `rmdir`, `mkdir`, `getwd`, `readdir`, and `tempdir` handle process execution and filesystem work.
- Git/release prechecks: `uncommittedChanges`, `getBranchName`, `preCheckBranchMaster`, `preCheckUncommittedChanges`, `preCheckVersionExists`.
- Changelog functions: `preCheckChangelogCurrent`, `preCheckChangelogRelease`, `createChangelogRelease`, and `preCheckChangelogVersion`.
- `preCheckDockerBuilderGoVersion` compares local `go version` with the `restic/builder` container's Go version.
- `generateFiles` builds a temporary restic binary and regenerates man pages plus bash, fish, PowerShell, and zsh completions under `doc/`, committing changes when present.
- `updateVersion` writes `VERSION`, updates `internal/global/global.go`, and commits if changed.
- `updateVersionDev` resets files to the next dev version and commits.
- `addTag` creates a signed annotated `v<version>` tag.
- `exportTar` creates a gzip-normalized git archive.
- `extractTar` unpacks the source archive into a build source directory.
- `runBuild` runs `helpers/build-release-binaries/main.go` inside `restic/builder`.
- `sha256sums` writes checksums for all files in the output directory.
- `signFiles` creates detached armored GPG signatures.
- `updateDocker` creates a Docker buildx builder, validates release Dockerfile build, and returns commands to push `latest` and version tags.

## Control Flow

`main` requires a version argument, validates its format, runs branch/uncommitted/tag/builder/changelog prechecks, creates a changelog release directory if needed, and ensures `CHANGELOG.md` contains the version. It creates output/source temp dirs as needed, regenerates generated docs/completions, commits release version changes, creates a signed tag, commits the post-release development version, exports a source tarball from the tag, extracts it, builds release binaries in Docker, writes `SHA256SUMS`, signs checksums and tarball, builds Docker images without pushing, and prints the exact `git push --tags` and `docker buildx` publish commands to run.

## State and Persistence Behavior

This helper intentionally mutates the working tree and git repository: it can move changelog files, regenerate `doc/`, write `VERSION`, modify `internal/global/global.go`, create commits, and create a signed tag. It writes release artifacts to `opts.OutputDir`, temporary source/build directories under the current working directory, `SHA256SUMS`, `.asc` signatures, and returns Docker builder cleanup commands. It also pulls and builds Docker images.

## Dependencies and Integration Points

It depends on Git, GPG, Docker/buildx, the `restic/builder` image, local Go, `calens`, tar/gzip, sha256sum, pflag, generated documentation commands, and `helpers/build-release-binaries`. It integrates with restic release conventions: changelog directories, `CHANGELOG.md`, `VERSION`, `internal/global/global.go`, generated `doc` assets, signed tags, GitHub release artifacts, and Docker image publishing.

## Risks and Edge Cases

- This is a high-impact mutating release script; running it in the wrong branch or dirty tree is guarded unless ignore flags are used.
- `preCheckChangelogCurrent` may create a commit automatically after regenerating `CHANGELOG.md`.
- `createChangelogRelease` moves all unreleased changelog files except `.gitignore`.
- GPG signing and Docker buildx state must be configured correctly.
- `updateDocker` creates a randomly named builder and prints cleanup, but if the process fails before the printed cleanup command, builders may remain.
- Release reproducibility depends on builder image Go version matching local Go and on deterministic tar/compression settings.

## Test Signals

Dry-run style testing is limited because the script commits/tags by design. Validation signals include running with ignore flags in a disposable clone, successful generated doc diffs, signed tag creation, successful builder container comparison, successful binary builds, valid `SHA256SUMS`, and subsequent `verify-release-binaries.sh` reproduction.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/helpers/prepare-release/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/helpers/verify-release-binaries.sh -->
# sources/sync-backup/restic/helpers/verify-release-binaries.sh

## Purpose

This Bash script verifies a restic release by checking published checksums/signatures, comparing the source tarball to the tagged repository, rebuilding release binaries in a regenerated builder container, and verifying that published Docker images contain the same binaries as the release artifacts.

## Important APIs, Types, and Functions

- Requires arguments: `restic_version` and `go_version`.
- Uses strict mode `set -euo pipefail`.
- `set_invalid` records warnings and flips `is_valid` to `0` without immediately aborting all checks.
- `highlight` prints section headers.
- Downloads release tarball signature, `SHA256SUMS`, and its signature from GitHub.
- Imports `https://restic.net/gpg-key-alex.asc` into a temporary `GNUPGHOME` and verifies signatures.
- Downloads every file listed in `SHA256SUMS` and verifies checksums.
- Extracts the source tarball, clones the matching tag, removes `.git`, and diffs source trees.
- Clones `restic/builder`, rebuilds `restic/builder:tmp` with `GO_VERSION`, and reruns `helpers/build-release-binaries/main.go`.
- `extract_docker(image, docker_platform, restic_platform)` pulls a platform-specific Docker image, saves it, extracts `usr/bin/restic` from layers, bzip2-compresses it, and checks it against release checksums.
- Loops over `restic/restic` and `ghcr.io/restic/restic` images for arm/v7, arm64, 386, and amd64.

## Control Flow

The script creates a temporary directory under the current directory, enters it, and performs verification in sections. Some mismatches call `set_invalid` so later checks still run. Fatal command failures still stop due to `set -e`. If any soft validation failed, it prints a failure header and exits `1`. If all validations pass, it removes the temporary directory and exits successfully.

## State and Persistence Behavior

It creates a temporary workspace, a temporary GPG home, cloned repositories, downloaded release artifacts, rebuilt output, Docker image tar exports, and extracted Docker binary directories. On success it removes the workspace. On validation failure it leaves the workspace for inspection.

## Dependencies and Integration Points

It depends on Bash, curl, gpg, shasum, git, diff, Docker 25+ for platform image pulls/saves, tar, bzip2, and a working network. It integrates with GitHub Releases, the restic Git tag, `restic/builder`, Docker Hub `restic/restic`, GHCR `ghcr.io/restic/restic`, and `helpers/build-release-binaries/main.go`.

## Risks and Edge Cases

- `mkdir -p 700 $GNUPGHOME` appears intended to set permissions but actually creates directories named `700` and `$GNUPGHOME`; it does not chmod the GPG home. GPG may warn or fail depending on environment.
- Parsing `SHA256SUMS` with `cut -d " " -f 3` assumes the checksum file spacing/format.
- Docker layer extraction scans all layer blobs and expects exactly one `usr/bin/restic`; multiple matches are flagged.
- The script requires substantial disk/network resources and Docker privileges.
- A hard failure before the final cleanup leaves temporary files by design for debugging.

## Test Signals

The script is itself an end-to-end release verification signal. A successful run means release artifacts match checksums/signatures, source tarball matches the tag, binaries are reproducible with the specified Go version, and Docker images embed release-equivalent binaries.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/helpers/verify-release-binaries.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/archiver/archiver.go -->
# sources/sync-backup/restic/internal/archiver/archiver.go

## Purpose

This file implements the core archiver orchestration that turns filesystem targets into restic snapshots. It resolves backup targets, walks directory trees, applies selection filters, compares files and directories to a parent snapshot, reuses unchanged blobs when safe, delegates file and tree saving to worker pools, tracks progress/statistics, and persists a final snapshot object.

## Important APIs, Types, and Functions

- Selection/error callback types:
  - `SelectByNameFunc(item string) bool` filters by path before stat/open work.
  - `SelectFunc(item string, fi *fs.ExtendedFileInfo, fs fs.FS) bool` filters with metadata.
  - `ErrorFunc(file string, err error) error` can suppress or transform archive errors.
- Statistics:
  - `ItemStats` tracks data/tree blob counts, logical sizes, and packed repository sizes.
  - `ChangeStats` tracks new/changed/unchanged counts.
  - `Summary` records backup times, file/dir change stats, processed bytes, and aggregate item stats.
  - `(*ItemStats).Add` aggregates per-item stats.
- Interfaces:
  - `toNoder` converts filesystem metadata to `*data.Node`.
  - `archiverRepo` requires loader, async blob uploader, unpacked saver, and config access.
- `Archiver` holds repository/filesystem references, filters, options, worker savers, summary mutex/state, callbacks (`Error`, `CompleteItem`, `StartFile`, `CompleteBlob`), atime and change-detection settings.
- `Options` and `applyDefaults` set read concurrency and tree-save concurrency.
- `New` constructs an archiver with permissive default selectors and no-op callbacks.
- `error` calls the configured error handler except for context cancellation and ensures filepath context is present.
- `trackItem` invokes `CompleteItem` and updates summary counters under lock.
- `nodeFromFileInfo` converts metadata to a restic node, normalizes atime/name/device ID, and handles partial metadata errors.
- `loadSubtree` and `wrapLoadTreeError` load parent tree nodes and produce repair-oriented diagnostics.
- `saveDir`, `dirToNodeAndEntries`, `save`, `saveTree`, and `dirPathToNode` are the main recursive archive functions.
- `futureNode` and `futureNodeResult` represent asynchronous file/tree save results.
- `fileChanged` implements metadata-based change detection with optional ctime/inode ignores.
- `resolveRelativeTargets` expands targets such as `.` into their directory entries and marks explicit vs implicit targets.
- `SnapshotOptions` describes snapshot metadata and parent/skip behavior.
- `loadParentTree`, `runWorkers`, `stopWorkers`, and `Snapshot` orchestrate the complete backup.

## Control Flow

`Snapshot` initializes a summary, resolves relative targets, builds an in-memory target tree, and enters `Repo.WithBlobUploader`. Inside an errgroup worker, it starts file/tree savers, calls `saveTree` for the synthetic root with the parent tree iterator, waits for the root `futureNode`, rejects empty snapshots, records the root tree ID, and stops workers. After the uploader completes, it optionally skips snapshot creation when `SkipIfUnchanged` is set and the root tree matches the parent.

`saveTree` walks the prepared target tree in deterministic name order. Leaf nodes call `save`; interior nodes load matching parent subtrees and recurse. It passes child `futureNode`s to `treeSaver.Save`, which persists tree blobs once children resolve. `saveDir` is similar for directories discovered while walking the filesystem: read directory metadata, sorted names, use a `TreeFinder` over the previous tree, call `save` for each child, and save the resulting tree.

`save` handles one filesystem item. It resolves an absolute path, applies path-only selection before opening, opens metadata without following symlinks, stats it, applies metadata-aware selection, then branches by type. Regular files are compared with the previous node using `fileChanged`. If unchanged and all previous blobs are present in the index, it reuses previous content IDs and returns an immediate future node after refreshing metadata. If content appears missing, it warns through the error handler and stores the file again. Changed regular files are made readable, re-statted to avoid race/type-swap attacks, then handed to `fileSaver.Save`. Directories load their old subtree and call `saveDir`. Sockets are ignored. Other file types are converted to metadata-only nodes and returned immediately.

## State and Persistence Behavior

Persistent repository writes happen through `fileSaver`, `treeSaver`, the async blob uploader, and `data.SaveSnapshot`. The archiver persists data blobs for changed files, tree blobs for directory structures, and finally a snapshot file containing targets, tags, hostname, time, parent ID, root tree ID, excludes, program version, and summary. In-memory state includes worker pools, futures, parent tree iterators, callback invocations, and protected summary counters. The filesystem is read through `fs.FS`; the archiver does not intentionally mutate source files, though reading may affect atime unless disabled or filesystem behavior prevents it.

## Dependencies and Integration Points

The file integrates with many restic internals: `internal/data` for nodes/trees/snapshots, `internal/fs` for portable filesystem metadata, `internal/restic` for blob IDs/load/save/uploader interfaces, `internal/feature` for `DeviceIDForHardlinks`, `internal/debug`, and `internal/errors`. It relies on sibling archiver components such as `fileSaver`, `treeSaver`, `tree`, `backupTarget`, `pathComponents`, and `fileCompleteFunc`. Command-layer backup code configures selectors, callbacks, options, parent snapshots, and snapshot metadata.

## Risks and Edge Cases

- Race hardening is important: files are opened with `O_NOFOLLOW`, then re-statted after `MakeReadable`; if a regular file changes type, archiving is refused.
- Error handling is callback-driven. A handler can suppress errors by returning nil, which lets backup continue and may exclude problematic items.
- Unchanged-file reuse depends on both metadata comparison and index presence of all content blobs. Missing index entries force re-storage and warn that repair may be needed.
- Device ID normalization for hardlinks is gated by a feature flag to avoid unnecessary tree churn on subvolumes/snapshots.
- Relative targets with no path components are expanded to directory entries, changing explicitness and filter behavior.
- `CompleteItem` may be called from multiple goroutines; callers must be concurrency-safe.
- Empty snapshots are rejected unless the skip-if-unchanged path returns earlier.
- Parent tree load failures are reported as possible repository damage but do not always abort parent use at top level; `loadParentTree` returns nil after reporting via the error handler.

## Test Signals

Useful tests include backup/restore integration tests, parent snapshot reuse tests, changed-file detection tests with ctime/inode ignore flags, hardlink/device ID feature tests, disappearing file and type-swap race tests, exclude/filter tests, unreadable directory/file tests with error suppression, and snapshot summary assertions. Existing command integration tests in this subset exercise backup creation, no-lock restore/check, and backend load/list behavior that the archiver participates in.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/archiver/archiver.go -->
