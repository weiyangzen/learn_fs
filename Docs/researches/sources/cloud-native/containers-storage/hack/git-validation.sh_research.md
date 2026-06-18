<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/hack/git-validation.sh -->
# sources/cloud-native/containers-storage/hack/git-validation.sh

## Purpose
This helper runs DCO and short-subject validation over commits in the current branch.

## Important APIs, Types, And Functions
It expects `tests/tools/build/git-validation` to be executable, determines `EPOCH_TEST_COMMIT` from `CIRRUS_BASE_SHA` or `git merge-base ${DEST_BRANCH:-main} HEAD`, and execs the validator with `-q -run DCO,short-subject`.

## Control Flow
Missing validator prints install guidance and exits 1. Otherwise it computes the range and replaces the shell with the validation tool.

## State And Persistence
No repository state is modified.

## Dependencies And Integration Points
It integrates with CI variables and local tool installation via `make install.tools`.

## Risks And Test Signals
Unquoted branch variable expansion is typical shell risk for unusual values. The correctness of the range depends on CI base SHA or local `DEST_BRANCH`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/hack/git-validation.sh -->
