<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-local-pull.sh -->
# sources/cloud-native/ostree/tests/test-local-pull.sh

## Purpose
`test-local-pull.sh` tests local repository-to-repository pulls across archive, bare-user, GPG, and object-copy scenarios.

## Important APIs, Types, And Functions
The script uses `skip_without_user_xattrs`, `setup_test_repository`, `ostree_repo_init --mode=bare-user/archive`, `pull-local`, `fsck`, `refs`, optional GPG signing/verification, and direct object inspection.

## Control Flow
It creates several repos, pulls commits locally between modes, verifies pulled refs and content, exercises GPG-related paths when available, checks that pulling from a bare/user repo to archive works, and includes a final loop over source `.filez` objects to validate copied payload availability in another repo.

## State And Persistence
Temporary repos `repo2`, `repo3`, and later numbered repos hold copied objects and refs. Xattrs and user-mode object metadata are persisted in the repo object stores.

## Dependencies And Integration Points
Coverage spans repository mode conversion, local object copying, user xattr support, optional GPG metadata, checkout validation, and fsck.

## Risks And Test Signals
The test is environment-sensitive because user xattrs are required and GPG coverage is optional. Passing signals include clean fsck after each local pull, correct refs, readable checkouts, and no missing file content after object-store copying.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-local-pull.sh -->
