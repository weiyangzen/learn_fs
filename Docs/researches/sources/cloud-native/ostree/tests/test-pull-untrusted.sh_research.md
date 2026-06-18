# sources/cloud-native/ostree/tests/test-pull-untrusted.sh

## Purpose
This security regression test ensures `ostree pull-local --untrusted` rejects repository content with path traversal filenames.

## Important APIs, Types, And Functions
The test uses `setup_test_repository`, `tar xf ostree-path-traverse.tar.gz`, `ostree_repo_init`, and `ostree pull-local --untrusted`. It asserts the literal error `Invalid / in filename ../afile`.

## Control Flow
The script sets up a bare repository fixture, extracts a crafted archive containing a malicious OSTree repository, initializes a new archive repo, and attempts to pull `pathtraverse-test` from that untrusted local repo. Success is considered a failure; the expected path validation error is checked from stderr.

## State And Persistence
The crafted repository and target `repo2` live in `test_tmpdir`. No successful refs or objects should be persisted in `repo2` from the rejected pull.

## Dependencies And Integration Points
This integrates untrusted local pull validation, archive object import, filename sanitization, and the test fixture archive `ostree-path-traverse.tar.gz`.

## Risks
If validation regresses, malicious object names could escape repository object paths during untrusted imports. The test only covers one traversal payload but anchors the expected rejection path.

## Test Signals
The single TAP result is `ok untrusted pull-local path traversal`. Any successful pull or missing literal error indicates a security-sensitive failure.
