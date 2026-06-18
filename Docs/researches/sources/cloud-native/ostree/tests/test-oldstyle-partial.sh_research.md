<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-oldstyle-partial.sh -->
# sources/cloud-native/ostree/tests/test-oldstyle-partial.sh

## Purpose
`test-oldstyle-partial.sh` checks fsck behavior for legacy partial commit markers.

## Important APIs, Types, And Functions
It uses `setup_fake_remote_repo1 "archive"`, initializes a repo, creates an old-style partial marker/ref state, runs `ostree fsck`, and asserts output about verified commit objects and partial commits not verified.

## Control Flow
The script creates an empty local repo, arranges a partial commit marker in the format older OSTree versions used, runs fsck, and verifies fsck reports zero commit objects verified and one partial commit skipped.

## State And Persistence
State is a temporary repo with partial-commit metadata but no complete commit content.

## Dependencies And Integration Points
It targets backward compatibility in fsck's partial-commit discovery and reporting logic.

## Risks And Test Signals
The test guards against treating old partial markers as corrupt complete commits. Passing signals are the expected fsck output lines and no unexpected verification of incomplete commits.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-oldstyle-partial.sh -->
