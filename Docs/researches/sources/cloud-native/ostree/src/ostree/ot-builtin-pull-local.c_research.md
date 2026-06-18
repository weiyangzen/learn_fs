# sources/cloud-native/ostree/src/ostree/ot-builtin-pull-local.c

## Purpose
Implements `ostree pull-local`, copying refs and objects from a local repository path into the current repository using the same pull machinery as remote pulls with a `file://` source URI.

## Important APIs, Types, And Functions
`ostree_builtin_pull_local()` is the command entry. It builds pull flags and options for `ostree_repo_pull_with_options()`. `noninteractive_console_progress_changed()` suppresses intermediate progress but allows final status retrieval. The command uses `ostree_repo_list_refs()` to clone all refs when none are specified.

## Control Flow
The command opens a writable destination repo, requires a source repository path, converts absolute or relative paths to a `file://` URI, applies pull flags for untrusted verification, bare-user-only file checks, and commit-metadata-only mode, and disables fsync if requested. With no explicit refs, it opens the source repo and lists all normal refs; otherwise it uses the provided refs. It builds a `GVariant` pull option dictionary containing flags, refs, optional remote override, static delta settings, GPG verification toggles, binding verification toggle, depth, disabled signapi verification for local pulls, and optional per-object fsync. It runs the pull with TTY or noninteractive progress, prints final status for non-TTYs, finishes progress, and aborts any open transaction on exit.

## State And Persistence
The destination repo receives copied commits, metadata, content objects, and refs according to pull options. Source repo state is read-only. Local pulls always disable signapi verification unless users model the source as a remote with configured signature verification. Fsync options affect durability.

## Dependencies And Integration Points
This command shares the pull engine with `ostree pull`, while adding local source discovery and all-ref cloning. It integrates with GPG verification, static deltas, commit binding verification, and per-object fsync behavior.

## Risks And Edge Cases
When no refs are supplied, only normal refs are listed; a FIXME notes missing collection-ref support. Relative paths are joined with the current directory without URI escaping. Using `--remote` only overrides refspec naming; it does not configure a remote. Disabling signapi verification is a deliberate local-pull policy that can surprise users expecting signature enforcement.

## Test Signals
Tests should cover cloning all refs, pulling selected refs, relative and absolute source paths, remote override, untrusted checksum verification, static-delta require/disable options, GPG verification toggles, depth behavior, final noninteractive progress output, and transaction abort after failures.
