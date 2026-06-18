<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-prune.sh -->
# sources/cloud-native/ostree/tests/test-prune.sh

## Purpose
`test-prune.sh` is broad regression coverage for `ostree prune`, including dry-run output, depth pruning, tombstone commits, static deltas, partial repos, parent repos, date retention, branch-specific depth, commit-only pruning, and concurrent commit/prune behavior.

## Important APIs, Types, And Functions
Helpers include `assert_repo_has_n_commits`, `assert_repo_has_n_non_commit_objects`, `assert_has_n_objects`, `reinitialize_datesnap_repo`, and `reinitialize_commit_only_test_repo`. The script uses `ostree prune`, `--delete-commit`, `--refs-only`, `--static-deltas-only`, `--keep-younger-than`, `--retain-branch-depth`, `--only-branch`, `--depth`, `--commit-only`, `static-delta generate`, and TAP helpers.

## Control Flow
It builds fixture histories, verifies dry-run leaves object counts unchanged, prunes depths with and without tombstones, generates and prunes static deltas, checks partial repo handling, validates parent repo object retention, constructs dated branch histories for retention rules, exercises invalid depth/ref errors, and then tests commit-only pruning against multiple branch/delete combinations. A final loop commits and prunes repeatedly to catch race regressions.

## State And Persistence
Temporary repos hold object stores, refs, tombstone commits, static delta directories, parent links, date-stamped commits, and branch histories. Several scenarios reset repos from snapshot repos.

## Dependencies And Integration Points
This test integrates prune reachability, ref traversal, commit metadata timestamps, static delta storage, parent repository lookup, tombstone configuration, and object deletion accounting.

## Risks And Test Signals
Object-count tests are fixture-sensitive but catch real reachability regressions. Passing signals include expected commit/non-commit counts after each prune mode, correct error messages for invalid combinations, static delta counts, and stable behavior under repeated commit/prune operations.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-prune.sh -->
