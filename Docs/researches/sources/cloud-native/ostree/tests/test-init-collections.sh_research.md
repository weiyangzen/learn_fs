<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-init-collections.sh -->
# sources/cloud-native/ostree/tests/test-init-collections.sh

## Purpose
`test-init-collections.sh` verifies repository initialization with a collection ID.

## Important APIs, Types, And Functions
It uses `ostree_repo_init repo --collection-id org.example.Collection` and `assert_file_has_content` against `repo/config`.

## Control Flow
The script creates a temporary repo, initializes it with a collection ID, and checks that the generated config contains the expected `collection-id` entry.

## State And Persistence
State is the temporary `repo` directory and its config file. No commits or objects are created.

## Dependencies And Integration Points
It covers the repository init helper in `libtest.sh` and the underlying `ostree init` collection configuration path consumed by collection-aware refs, fsck, pull, and find-remotes.

## Risks And Test Signals
The test is narrow and config-format-sensitive. Passing confirms collection IDs are persisted during init and available to later collection-aware operations.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-init-collections.sh -->
