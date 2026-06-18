<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-bareuseronly.sh -->
# sources/cloud-native/ostree/tests/test-pull-bareuseronly.sh

## Purpose
`test-pull-bareuseronly.sh` runs the shared HTTP pull suite against a `bare-user-only` destination repository with canonical permissions.

## Important APIs, Types, And Functions
It uses `skip_without_user_xattrs`, `setup_fake_remote_repo1 "archive" "--canonical-permissions"`, sets `repo_mode=bare-user-only`, and sources `pull-test.sh`.

## Control Flow
The wrapper prepares an archive remote whose commits use canonical permissions, then delegates to the shared pull suite. The shared suite sets commit and checkout flags appropriate for bare-user-only repositories and includes explicit safe/unsafe `--bareuseronly-files` checks.

## State And Persistence
Temporary state is the bare-user-only repo, user-xattr object metadata, canonical-permission remote objects, and shared test artifacts.

## Dependencies And Integration Points
It validates unprivileged storage constraints, canonical permission handling, and shared pull behavior in the most restrictive repo mode.

## Risks And Test Signals
The suite is skipped without user xattrs. Passing signals include successful normal pulls and rejection of unsafe setuid content for bare-user-only files.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-bareuseronly.sh -->
