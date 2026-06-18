<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-local-pull-depth.sh -->
# sources/cloud-native/ostree/tests/test-local-pull-depth.sh

## Purpose
`test-local-pull-depth.sh` verifies `ostree pull-local --depth` semantics when copying commits from a local repository.

## Important APIs, Types, And Functions
The script uses `setup_test_repository "archive"`, `ostree_repo_init`, `ostree pull-local --depth=N`, `rev-parse`, object glob counts for `*.commit`, partial commit markers, direct deletion of refs/commit objects, and `fsck`.

## Control Flow
It initializes a second archive repo, pulls different depths from the source repo, and asserts the number of full and partial commits after each pull. It clears refs and commit objects between scenarios, checks depth-zero and depth-one behavior, and finally removes source commit objects to ensure an infinite-depth pull fails when required history is missing.

## State And Persistence
State is stored in `repo2` refs, commit objects, and `.commitpartial` markers. The test intentionally deletes refs and commit objects to reset or corrupt scenarios.

## Dependencies And Integration Points
It covers local pull traversal, parent-depth selection, partial commit marker management, and fsck compatibility for copied commits.

## Risks And Test Signals
Object-count assertions depend on the fixture history depth. Passing signals include expected full/partial commit counts at each depth and a failure when unlimited local history cannot be read from the source.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-local-pull-depth.sh -->
