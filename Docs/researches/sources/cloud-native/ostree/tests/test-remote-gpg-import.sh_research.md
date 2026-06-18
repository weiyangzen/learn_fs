# sources/cloud-native/ostree/tests/test-remote-gpg-import.sh

## Purpose
This comprehensive shell test validates remote GPG key import, per-remote trust isolation, `gpgkeypath` option parsing, signed commit pull verification, static-delta upgrade verification, and expired/revoked key handling.

## Important APIs, Types, And Functions
It uses `ostree remote add`, `remote gpg-import --keyring`, `--stdin`, `--gpg-import`, `ostree pull`, `ostree prune --refs-only`, remote config `gpgkeypath`, `ostree static-delta generate`, `ostree summary -u --gpg-sign`, `which_gpg`, and GPG commands such as `--quick-set-expire`, `--armor --export`, and revocation import.

## Control Flow
The test first ensures deleting a remote removes its `R1.trustedkeys.gpg` keyring. It imports selected keys, all keys, and stdin keys, checking import counts. It then creates three remotes pointing at the same URL but with distinct trusted keys, signs successive commits with key1, key2, and key3, and verifies only the matching remote can pull each commit. A large matrix validates `gpgkeypath` with files, directories, multiple comma or semicolon-separated paths, missing paths, empty path elements, and mixed separators. Static delta pulls are tested to ensure commit signatures are checked even when the summary signature is trusted. If GPG is available, expired and revoked key material is imported and pulls must fail with `Key expired` or `Key revoked`.

## State And Persistence
Per-remote keyrings such as `repo/R1.trustedkeys.gpg`, repo config `gpgkeypath` values, remote commits and deltas, summary signatures, refs/remotes cleanup, and generated key files under `test_tmpdir` are central persistent states.

## Dependencies And Integration Points
This integrates GPGME verification, external GPG for key mutation, remote config parsing, static delta pull path, commit metadata signatures, and keyring lifecycle during remote delete. It depends on fixture keys from `gpghome`.

## Risks
Key trust must remain per remote. `gpgkeypath` parser bugs can either reject valid deployments or silently ignore missing/untrusted keys. Delta upgrades must not bypass commit signature verification. External GPG version differences can affect expired/revoked handling.

## Test Signals
The non-GPG test plan covers import and pull trust behavior; extra tests cover expired and revoked keys. Expected failures include `public key not found`, missing path errors, mixed-separator parser errors, `Key expired`, and `Key revoked`.
