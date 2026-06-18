# sources/distributed-fs/ceph-client/scripts/git-resolve.sh

## Purpose
Resolves abbreviated commit IDs, optionally paired with commit subjects, into full SHA-1 hashes for fixing or validating commit references in messages.

## APIs, Control Flow, and State
The shell script exposes `git_resolve_commit [--force] <id> [subject]`, `convert_to_grep_pattern()`, `run_selftest()`, and CLI dispatch. Normal resolution uses `git rev-parse --disambiguate`. If exactly one match exists, it prints it. If multiple matches exist and a subject is present, it converts the subject into a Perl-regex anchored grep pattern, supporting escaped ellipsis as a wildcard, and checks candidate commit subjects. In `--force` mode, if no ID matches, it searches recent git log subjects directly.

## Dependencies and Integration
It depends on bash, git, sed, grep with `-P`, and repository history containing expected commits. It has no persistent state; self-tests hard-code representative commit references.

## Risks and Test Signals
Risks include regex escaping gaps, subject ambiguity, limited `git log -10` search in force mode, unquoted expansion in self-tests by design, and SHA-1-specific assumptions. Test signals are `--selftest`, exact single-match resolution, failure on wrong subject, wildcard subject matching, and force-mode fallback.
