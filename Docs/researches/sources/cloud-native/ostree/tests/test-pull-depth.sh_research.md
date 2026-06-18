<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-depth.sh -->
# sources/cloud-native/ostree/tests/test-pull-depth.sh

## Purpose
`test-pull-depth.sh` verifies remote `ostree pull --depth` behavior over HTTP.

## Important APIs, Types, And Functions
It uses `setup_fake_remote_repo1 "archive"`, `ostree_repo_init`, `ostree pull --depth=N origin main`, object counts for commit and partial commit markers, ref cleanup, direct deletion of remote commit objects, and expected failure checks.

## Control Flow
The script pulls increasing depths and checks how many commit objects and partial markers exist. It resets refs and commit objects between scenarios, checks depth-zero and depth-one semantics, and then removes remote commit objects before an unlimited-depth pull to ensure missing history fails.

## State And Persistence
State is a local repo with refs, commit objects, and partial markers, plus the fake HTTP remote whose commit objects are deliberately removed in the final negative test.

## Dependencies And Integration Points
It covers remote history traversal, commit-parent fetching, partial commit markers, and error handling for incomplete remotes.

## Risks And Test Signals
Expected counts are tied to fixture history length. Passing signals include correct full commit counts for each depth and failure when remote history is unavailable for unlimited depth.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-depth.sh -->
