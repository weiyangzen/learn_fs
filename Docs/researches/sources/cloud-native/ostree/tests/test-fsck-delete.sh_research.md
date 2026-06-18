<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-fsck-delete.sh -->
# sources/cloud-native/ostree/tests/test-fsck-delete.sh

## Purpose
`test-fsck-delete.sh` verifies `ostree fsck --delete` behavior when repository objects are missing or corrupt enough to leave commits invalid. It checks both detection and cleanup.

## Important APIs, Types, And Functions
The script uses `ostree_repo_init`, `ostree commit`, `ostree pull-local`, direct object-file removal, `ostree fsck`, `ostree fsck --delete`, and assertions over stdout and stderr.

## Control Flow
It creates a source repo and a target repo, pulls a commit locally, removes one object from the target, and confirms plain fsck fails. It then runs fsck with `--delete`, expects diagnostics about deleting invalid commits, runs fsck again to confirm only the expected object error remains, restores or re-pulls state, and verifies final clean fsck output.

## State And Persistence
Temporary repos `f1`, `f2`, and working directories hold commits and object files. The core state transition is direct deletion of an object followed by fsck deleting invalid commit references or objects.

## Dependencies And Integration Points
This test integrates object storage layout, commit reachability, pull-local replication, fsck validation, and repair/delete semantics.

## Risks And Test Signals
Direct object deletion makes the test sensitive to object layout and selected file globbing. Passing signals include a failing fsck before repair, `--delete` returning failure while deleting invalid data, subsequent reduced error output, and eventually a clean fsck with empty stderr.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-fsck-delete.sh -->
