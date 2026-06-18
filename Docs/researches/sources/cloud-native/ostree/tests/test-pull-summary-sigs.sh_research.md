# sources/cloud-native/ostree/tests/test-pull-summary-sigs.sh

## Purpose
This large shell test validates pulling from summary files, signed summary verification, cache cleanup, custom cache directories, invalid summary failures, static-delta metadata display, and race recovery for mismatched summary/signature pairs.

## Important APIs, Types, And Functions
It uses `has_ostree_feature gpgme`, `setup_fake_remote_repo1`, `ostree commit`, `ostree summary -u`, `ostree pull --mirror`, `ostree remote add --set=gpg-verify-summary=true`, `ostree prune`, `ostree static-delta generate`, `ostree remote summary`, metadata key options, and `OSTREE_REPO_TEST_ERROR=invalid-cache`. Helper `repo_reinit` resets a client repo with summary verification enabled.

## Control Flow
The test first creates a multi-branch remote and checks that mirror pull from an unsigned summary retrieves all branches and passes `fsck`. If GPGME exists, it signs the summary and runs repeated scenarios: normal signed summary pull and cache refill, pruning stale summary cache entries, using `--cache-dir`, rejecting invalid `summary.sig`, rejecting malformed `summary`, pulling a static delta with signed summary, checking human and metadata-key output from `remote summary`, and simulating races between old/new summaries and signatures. The final scenarios ensure the client preserves the last valid cache on verification failure and can recover after the remote publishes a matching pair.

## State And Persistence
State is held in remote refs, `summary`, `summary.sig`, static delta metadata, client refs, object stores, and cache files under either `repo/tmp/cache/summaries` or an external `cachedir/summaries`. The script deliberately copies `summary.1`, `summary.2`, and matching signatures to model server-side race windows.

## Dependencies And Integration Points
This covers summary parsing, GPG signature verification, cache update atomicity, pull mirror semantics, static delta indexing, remote summary CLI rendering, metadata printing, and test-only invalid-cache injection in repository code. It depends on the local HTTP server and GPGME-enabled builds for most checks.

## Risks
The highest-risk behavior is replacing a valid cache with an unverified or mismatched summary/signature pair. Other risks include accepting malformed summaries, deleting valid cache entries during prune, mishandling custom cache directories, and printing stale static-delta metadata. Timestamp manipulation is used to model races and may be sensitive to filesystem granularity.

## Test Signals
The plan is one test without GPGME and ten with GPGME. Success signals include valid checkouts of all branches, preserved cache files after failed race pulls, expected `BAD signature` and invalid-cache errors, and exact metadata keys such as `ostree.summary.indexed-deltas` and `ostree.summary.mode`.
