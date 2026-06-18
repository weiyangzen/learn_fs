<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-corruption.sh -->
# sources/cloud-native/ostree/tests/test-pull-corruption.sh

## Purpose
`test-pull-corruption.sh` validates pull-time detection of corrupted remote objects.

## Important APIs, Types, And Functions
It requires `gjs`, uses `setup_fake_remote_repo1`, defines `do_corrupt_pull_test`, mutates remote object bytes, runs `ostree pull`, checks `corrupted-status.txt`, and gates some cases on user xattrs.

## Control Flow
The helper corrupts selected remote objects, attempts pulls into fresh repos, and expects pull failures with checksum/corruption diagnostics. It runs variants for different repo modes or object types, skipping where environment support is missing.

## State And Persistence
State includes corrupted copies of remote objects, temporary client repos, status/error files, and restored or recreated remote state between cases.

## Dependencies And Integration Points
It covers HTTP pull integrity verification, object checksum validation, repo mode differences, and test corruption tooling implemented with GJS.

## Risks And Test Signals
The test is sensitive to fixture object selection and GJS availability. Passing signals include explicit "Changed byte" evidence and pull failures that identify corrupted content instead of accepting bad objects.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-corruption.sh -->
