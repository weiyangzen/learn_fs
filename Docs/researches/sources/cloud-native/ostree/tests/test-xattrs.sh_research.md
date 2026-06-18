# sources/cloud-native/ostree/tests/test-xattrs.sh

## Purpose
This shell test is currently skipped. The dead code below the skip would validate committing and checking out `user.*` extended attributes.

## Important APIs, Types, And Functions
The active API is `skip` from `libtest.sh`, with the message that there is no current use case for committing user xattrs. Dead code uses `skip_without_user_xattrs`, `ostree checkout`, `setfattr`, `ostree commit --tree=dir=...`, `getfattr`, and assertion helpers.

## Control Flow
Execution stops immediately at `skip`. If re-enabled, it would set two user xattrs on `firstfile` in a checkout, commit the checkout to `test2`, check it out again, and verify both xattr names and values are preserved.

## State And Persistence
Active execution creates no repo state beyond any pre-skip harness setup. Dead code would persist user xattrs in file metadata and object commits.

## Dependencies And Integration Points
The skipped path would integrate user xattr support, checkout, commit, and metadata round-tripping. It requires filesystem support and `attr` tools.

## Risks
Because the test is skipped, regressions in user xattr commit/checkout behavior are not caught here. The skip references ostreedev issue 758 as rationale.

## Test Signals
The only active signal is a skip. Re-enabled dead code would produce two TAP results for commit and checkout with xattrs.
