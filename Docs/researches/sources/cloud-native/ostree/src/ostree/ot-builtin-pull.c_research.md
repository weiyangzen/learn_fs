# sources/cloud-native/ostree/src/ostree/ot-builtin-pull.c

## Purpose
Implements `ostree pull`, fetching refs, commits, objects, summaries, and optional static deltas from a configured remote or refspec into the current repository.

## Important APIs, Types, And Functions
`ostree_builtin_pull()` is the command entry. `gpg_verify_result_cb()` prints GPG verification results while temporarily unlocking the console. `dry_run_console_progress_changed()` formats static-delta dry-run size/part information. `noninteractive_console_progress_changed()` suppresses progress spam. The command builds a large `a{sv}` option dictionary for `ostree_repo_pull_with_options()`.

## Control Flow
The command opens a writable repo, requires a remote or refspec, applies fsync/cache-dir settings, builds pull flags for mirror, commit-only, trusted/untrusted HTTP, and bare-user-only files, and rejects `--dry-run` unless static deltas are required. It parses either a remote name plus optional branches, or a `REMOTE:REF` refspec. Branch arguments may include `@CHECKSUM` commit overrides, which are validated and split into parallel refs and override arrays. It then builds pull options for URL override, subpaths, flags, refs, depth, progress frequency, network retry/low-speed/concurrency settings, retry-all toggle, static delta controls, dry-run, timestamp checks, commit overrides, local cache repos, per-object fsync, binding verification, HTTP headers, and appended user agent. It installs progress callbacks, optionally connects GPG verify result output for TTYs, runs the pull, prints final noninteractive status, finishes progress, asserts dry-run progress happened, disconnects signals, and returns.

## State And Persistence
Successful pulls write objects, commit metadata, refs, summaries, and possibly static delta results to the local repository. Mirror mode writes mirror-suitable refs and fetches all refs when none are specified by the pull engine. Cache-dir and localcache repos affect object sourcing. The command itself does not explicitly abort transactions, relying on pull API behavior.

## Dependencies And Integration Points
This is the CLI front end to libostree's remote fetcher, HTTP stack, static delta engine, GPG verification signals, timestamp validation, binding verification, and progress system. It consumes remote configuration and is used by update, mirror, CI, and repository synchronization workflows.

## Risks And Edge Cases
Branch `@CHECKSUM` overrides require careful array alignment. `--disable-retry-on-network-errors` maps to an option named `retry-all-network-errors` with boolean false. HTTP headers must be `NAME=VALUE`. Dry-run depends on static delta metadata and asserts a progress callback. Trust flags can weaken integrity verification, especially `--http-trusted`. Refspec parsing distinguishes remotes by presence of `:`, which affects remote names containing colons.

## Test Signals
Tests should cover remote and refspec parsing, branch checksum overrides, mirror and commit-only flags, dry-run requiring static deltas and printing size data, timestamp checks, HTTP headers, URL override, subpath single and multiple forms, network option propagation, local cache repos, GPG verify output, and failure cleanup.
