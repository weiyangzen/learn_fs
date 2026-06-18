<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pre-signed-pull.sh -->
# sources/cloud-native/ostree/tests/test-pre-signed-pull.sh

## Purpose
`test-pre-signed-pull.sh` verifies pulling a pre-generated Ed25519-signed repository and rejecting a repository signed with an untrusted or wrong key.

## Important APIs, Types, And Functions
It checks `has_ostree_feature sign-ed25519`, extracts `pre-signed-pull-data.tar.gz`, initializes a repo, configures remotes/keys from the fixture, runs `ostree pull`, and asserts Ed25519 verification errors.

## Control Flow
If Ed25519 signing support is unavailable, the single TAP test is skipped. Otherwise the fixture archive is unpacked, a local repo is initialized, a good pull path is exercised, and a bad upstream pull is expected to fail with a signature verification message.

## State And Persistence
State consists of unpacked fixture repositories, temporary local repo config, imported keys, and pulled refs/objects.

## Dependencies And Integration Points
It integrates static signed test data, Ed25519 signature verification, pull verification, and remote configuration.

## Risks And Test Signals
The fixture must remain in sync with verification code. Passing signals include successful good pull and an error matching `ed25519: Signature couldn't be verified with: key` for bad pulls.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pre-signed-pull.sh -->
