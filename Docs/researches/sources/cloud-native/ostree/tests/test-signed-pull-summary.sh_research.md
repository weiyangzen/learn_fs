# sources/cloud-native/ostree/tests/test-signed-pull-summary.sh

## Purpose
This shell test validates summary signing and signed-summary pulls through non-GPG signing backends, currently dummy and ed25519, including cache behavior and race recovery.

## Important APIs, Types, And Functions
It uses `OSTREE_DUMMY_SIGN_ENABLED`, `gen_ed25519_keys`, `setup_fake_remote_repo1`, `ostree commit --sign-type`, `ostree summary -u --sign-type --sign`, remote config keys `sign-verify-summary`, `verification-<engine>-key`, `ostree pull --mirror`, `--cache-dir`, `ostree prune`, `ostree static-delta generate`, `ostree remote summary`, and `OSTREE_REPO_TEST_ERROR=invalid-cache`.

## Control Flow
For each engine, the script creates a signed multi-branch remote, confirms mirror pull works with signature verification disabled, then enables summary sign verification with the public key and tests normal pulls, cache refill, prune of stale cache entries, external cache directories, invalid signature rejection, and static-delta pull. If ed25519 support exists, it additionally checks `remote summary` metadata output and models cache races using old/new summary-signature pairs, ensuring mismatched pairs do not replace the last good cache and a later valid pair recovers.

## State And Persistence
State includes signed commit metadata, signed `summary.sig`, client summary caches, external cache directories, static delta metadata, and copied `summary.1`/`summary.2` race fixtures.

## Dependencies And Integration Points
This integrates signapi summary verification, non-GPG signature storage in `summary.sig`, pull caching, static delta metadata, remote summary rendering, and invalid-cache test injection. Ed25519 portions depend on the `sign-ed25519` feature.

## Risks
Non-GPG summary verification must not be confused with GPG verification flags. Cache update ordering must avoid persisting mismatched summary/signature pairs. The script has a subtle dependency on the `engine` variable after the loop for ed25519-only scenarios.

## Test Signals
The TAP plan is fourteen, with skips for missing ed25519 support. Expected failures include `No signatures found`, ed25519 verification errors, and `OSTREE_REPO_TEST_ERROR_INVALID_CACHE`.
