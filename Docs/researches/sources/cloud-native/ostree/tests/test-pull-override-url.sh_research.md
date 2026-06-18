<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-override-url.sh -->
# sources/cloud-native/ostree/tests/test-pull-override-url.sh

## Purpose
`test-pull-override-url.sh` verifies `ostree pull --url=...` can override a configured remote URL.

## Important APIs, Types, And Functions
It uses an HTTP fixture, `setup_fake_remote_repo1`, creates a mirror server tree, `ostree_repo_init`, `remote add`, `pull --depth=-1`, `pull --url=...`, `refs`, and `cmp` over commit lists.

## Control Flow
The script creates a mirror repo with the same commits as the original, starts serving it under a different URL, initializes a client repo configured for the original remote, removes the original served repo to force failure, then pulls successfully with `--url` pointing at the mirror and compares pulled commits.

## State And Persistence
State includes original and mirror served repos, commit list files, local client repo, and HTTP server directories.

## Dependencies And Integration Points
It covers command-line URL override, remote config fallback, full-depth pulling, and HTTP repository compatibility.

## Risks And Test Signals
The test ensures `--url` is used for network access without changing ref semantics. Passing signals include failure without override after original removal, success with override, and matching commit lists.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-override-url.sh -->
