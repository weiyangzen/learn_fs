<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-sizes.sh -->
# sources/cloud-native/ostree/tests/test-pull-sizes.sh

## Purpose
`test-pull-sizes.sh` verifies pull progress/output size accounting when summaries include generated object sizes.

## Important APIs, Types, And Functions
It sets `OSTREE_NO_XATTRS=1`, uses `setup_fake_remote_repo1 "archive" "--generate-sizes"`, initializes a repo, runs pulls/show operations, and asserts output for compressed size, unpacked size, and object counts.

## Control Flow
The script performs an initial pull and checks needed/total sizes equal the full summary totals. It then performs subsequent pulls where some or all objects are already present and checks that needed sizes decrease to partial and then zero while totals remain stable.

## State And Persistence
State is the local repo's object cache and output files such as `show.txt`. Remote summary metadata contains generated size information.

## Dependencies And Integration Points
It covers summary size metadata generation, pull progress accounting, no-xattr archive fixtures, and CLI display formatting.

## Risks And Test Signals
The test is exact-output sensitive and accounts for regular/non-breaking spaces in size strings. Passing signals include expected compressed/unpacked byte totals and object needed/total counts for cold, partial, and no-op pulls.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-sizes.sh -->
