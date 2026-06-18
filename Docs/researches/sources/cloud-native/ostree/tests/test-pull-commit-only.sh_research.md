<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-commit-only.sh -->
# sources/cloud-native/ostree/tests/test-pull-commit-only.sh

## Purpose
`test-pull-commit-only.sh` verifies `ostree pull --commit-metadata-only` style behavior, where commit metadata can be fetched without content objects.

## Important APIs, Types, And Functions
It uses `setup_fake_remote_repo1 "archive"`, `ostree_repo_init`, `ostree pull`, commit-object counts, and fsck/prune-style object inspection.

## Control Flow
The script initializes a local repo, pulls only commit metadata from the remote, asserts commit object counts, checks that content object counts remain absent or zero, and verifies subsequent behavior around refs and metadata-only state.

## State And Persistence
State is a temporary repo containing commit objects and refs but intentionally lacking full file content for metadata-only pulls.

## Dependencies And Integration Points
This covers pull options that support metadata-only discovery, partial repository state, and object type filtering.

## Risks And Test Signals
The risk is accidentally fetching content or creating unusable refs without intended partial semantics. Passing signals are exact commit counts and absence of unintended content objects.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-commit-only.sh -->
