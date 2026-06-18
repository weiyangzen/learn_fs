<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-large-metadata.sh -->
# sources/cloud-native/ostree/tests/test-pull-large-metadata.sh

## Purpose
`test-pull-large-metadata.sh` verifies that pulls reject metadata objects exceeding the configured maximum size.

## Important APIs, Types, And Functions
The script uses `setup_fake_remote_repo1 "archive"`, `rev-parse`, `dd if=/dev/zero bs=1M count=130` to overwrite a commit object, `ostree_repo_init`, `ostree pull`, and assertion for "exceeded maximum".

## Control Flow
It locates the remote commit object for `main`, replaces it with a 130 MiB zero-filled file, initializes a fresh local repo, attempts to pull, and expects failure with a maximum-size diagnostic.

## State And Persistence
State is the deliberately oversized remote commit object and the local repo that should remain without a successful pull.

## Dependencies And Integration Points
It covers pull metadata fetch limits, object validation before storage, HTTP/local file serving behavior, and error reporting.

## Risks And Test Signals
The test uses a large temporary file and is sensitive to size thresholds. Passing signals include pull failure and an error containing "exceeded maximum".
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-large-metadata.sh -->
