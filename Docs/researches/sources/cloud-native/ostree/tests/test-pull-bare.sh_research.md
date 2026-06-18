<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-bare.sh -->
# sources/cloud-native/ostree/tests/test-pull-bare.sh

## Purpose
`test-pull-bare.sh` runs the shared HTTP pull regression suite against a `bare` destination repository.

## Important APIs, Types, And Functions
It sources `libtest.sh`, calls `setup_fake_remote_repo1 "archive"`, sets `repo_mode=bare`, and sources `${test_srcdir}/pull-test.sh`.

## Control Flow
The wrapper prepares a fake archive HTTP remote, selects the destination repo mode, and delegates all test flow to `pull-test.sh`, which covers normal pulls, mirror pulls, fsck, static delta refusal in archive mirror scenarios, invalid remote schemes, bareuseronly safety checks, corruption handling, path traversal rejection, and optional GPG cases.

## State And Persistence
State is created by the shared pull suite under `test_tmpdir`, including a `repo` initialized as bare and several mirror/cache repos.

## Dependencies And Integration Points
This is the bare-mode integration lane for the central pull suite, covering object storage with hardlinks/metadata rather than user-only xattrs.

## Risks And Test Signals
Risks and signals are inherited from `pull-test.sh`; the wrapper specifically ensures those behaviors work for bare repositories.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-bare.sh -->
