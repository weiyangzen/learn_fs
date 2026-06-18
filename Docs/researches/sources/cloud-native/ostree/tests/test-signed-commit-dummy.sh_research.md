# sources/cloud-native/ostree/tests/test-signed-commit-dummy.sh

## Purpose
This TAP shell test validates the opt-in dummy signing backend for commit signing and verification.

## Important APIs, Types, And Functions
It sets `OSTREE_DUMMY_SIGN_ENABLED=1` and uses `ostree commit`, `ostree sign --sign-type=dummy`, `ostree sign --verify`, `ostree show --print-detached-metadata-key=ostree.sign.dummy`, `hexdump`, and TAP helpers.

## Control Flow
The script creates an archive repo, commits an unsigned commit, signs it with dummy key `dummysign`, checks detached metadata contains the expected encoded string, verifies the signature, creates a new commit signed during commit creation, verifies it, then unsets the dummy opt-in environment and confirms verification fails with no valid signatures.

## State And Persistence
Detached commit metadata stores `ostree.sign.dummy` signatures. The repo and commits live in `test_tmpdir`.

## Dependencies And Integration Points
This integrates sign CLI commands, commit-time signing, detached metadata, the dummy backend, and environment-gated availability for test-only signing.

## Risks
Dummy signing must remain disabled by default. Detached metadata must be correctly written and read. Error text is noted as imperfect, so the test checks the stable "No valid signatures found" portion.

## Test Signals
TAP helpers report detached signature added, dummy signature verified, commit with dummy signing, and dummy signature requiring the environment variable.
