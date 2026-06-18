# sources/cloud-native/ostree/tests/test-pull2-bareuseronly.sh

## Purpose
This wrapper runs the shared `pull-test2.sh` suite against a `bare-user-only` target repository mode. It validates the common pull matrix for user-only bare repos.

## Important APIs, Types, And Functions
It uses `setup_fake_remote_repo2 "archive" "--canonical-permissions"`, sets `repo_mode=bare-user-only`, and sources `${test_srcdir}/pull-test2.sh`.

## Control Flow
The script initializes an archive remote with canonical permissions, sets the repo mode consumed by the shared test file, and delegates all actual scenarios to `pull-test2.sh`.

## State And Persistence
State is created by the shared pull-test harness: remote repositories, client repo, refs, objects, checkouts, and any pull cache state. This wrapper's only persistent behavior is selecting `bare-user-only` mode.

## Dependencies And Integration Points
It depends directly on `libtest.sh`, `pull-test2.sh`, and OSTree support for bare-user-only repositories. It integrates the shared pull semantics with canonical permission normalization.

## Risks
Because behavior is delegated, drift in `pull-test2.sh` can change the effective coverage. The main mode-specific risks are UID/GID, mode, xattr, and object layout differences between archive and bare-user-only repos.

## Test Signals
Test output and TAP plan come from `pull-test2.sh`. Failure indicates the shared pull behavior does not hold for `bare-user-only`.
