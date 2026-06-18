<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-bareuser.sh -->
# sources/cloud-native/ostree/tests/test-pull-bareuser.sh

## Purpose
`test-pull-bareuser.sh` runs the shared HTTP pull suite against a `bare-user` destination repository.

## Important APIs, Types, And Functions
It uses `skip_without_user_xattrs`, `setup_fake_remote_repo1 "archive"`, sets `repo_mode=bare-user`, and sources `pull-test.sh`.

## Control Flow
After ensuring user xattrs are available, the wrapper creates the fake remote, selects bare-user mode, and executes the shared pull suite. The shared suite adjusts checkout flags for bare-user repos and runs the same pull, mirror, corruption, traversal, and optional GPG checks.

## State And Persistence
Temporary repo state includes bare-user object metadata encoded in user xattrs and the shared suite's remote, mirror, and cache repos.

## Dependencies And Integration Points
This validates that the central pull code works when destination metadata is represented in user xattrs, important for unprivileged use.

## Risks And Test Signals
The wrapper skips without user xattr support. Passing signals mirror `pull-test.sh` plus successful bare-user checkout/fsck behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-bareuser.sh -->
