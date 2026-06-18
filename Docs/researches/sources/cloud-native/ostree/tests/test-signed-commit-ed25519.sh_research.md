# sources/cloud-native/ostree/tests/test-signed-commit-ed25519.sh

## Purpose
This shell test validates the ed25519 signing backend for commit-time signing, detached signing, multi-backend signatures, key files, keys directories, and revocation.

## Important APIs, Types, And Functions
It uses `gen_ed25519_keys`, `gen_ed25519_random_public`, `ostree commit --sign --sign-type=ed25519`, `ostree sign --verify`, `--keys-file`, `--keys-dir`, dummy signing for multi-sign tests, and trusted/revoked directory naming `trusted.ed25519.d` and `revoked.ed25519.d`.

## Control Flow
The test generates an ed25519 keypair, signs a commit at commit time, verifies detached metadata exists, and checks verification fails with a wrong key but succeeds with the correct key among many positional keys. It creates an unsigned commit, signs it with both dummy and ed25519 backends, and verifies both outputs. It then tests empty and invalid keys-file behavior, a single-key file, a 100-key invalid file, combining file and positional key, adding the valid key to the file, signing from a secret key file, verifying from a keys file, verifying keys discovered from a trusted directory, and rejecting once the public key is present in the revoked directory.

## State And Persistence
State includes commit metadata signatures, temporary public/secret key files, trusted and revoked ed25519 directories, and random public-key lists.

## Dependencies And Integration Points
This integrates libsodium-backed ed25519 support, the sign CLI, commit metadata, key-file parsing, key-directory discovery, revocation precedence, and dummy backend coexistence.

## Risks
Verification must try multiple keys without accepting wrong keys, report useful counts for large key files, handle file/directory errors, and prioritize revocation over trust. Secret-key file handling must not confuse public and private formats.

## Test Signals
TAP results cover detached signature creation, verification, multiple signing, keys-file verification, signing with a keys file, trusted directory verification, and revocation rejection.
