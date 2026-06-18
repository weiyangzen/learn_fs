<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-parent.sh -->
# sources/cloud-native/ostree/tests/test-parent.sh

## Purpose
`test-parent.sh` verifies parent commit relationships and pulling signed parent history.

## Important APIs, Types, And Functions
The script requires user xattrs and GPGME, uses `setup_test_repository "archive"`, `ostree gpg-sign`, `ostree commit`, `ostree_repo_init`, `remote add`, `pull`, and assertions over failure/success.

## Control Flow
It signs commits in the main repo, creates additional repos, pulls refs and parent history, and checks that a repo lacking required signed parent state fails where expected while correctly configured pulls succeed.

## State And Persistence
Temporary repos hold refs, signed commits, parent links, and trusted GPG state. State changes are limited to the test working directory.

## Dependencies And Integration Points
The test covers commit parent metadata, GPG verification during pull, remote configuration, and archive repo fixture content.

## Risks And Test Signals
The test is sensitive to GPG availability and parent traversal rules. Passing signals include expected pull failures for missing/untrusted parent cases and successful pulls when parent/signature requirements are satisfied.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-parent.sh -->
