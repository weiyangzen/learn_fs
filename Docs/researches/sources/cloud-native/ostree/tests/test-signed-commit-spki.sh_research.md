# sources/cloud-native/ostree/tests/test-signed-commit-spki.sh

## Purpose
This shell test mirrors the ed25519 signing tests for the SPKI signing backend, including PEM file handling, multi-backend signing, key files, key directories, and revocation.

## Important APIs, Types, And Functions
It uses `gen_spki_keys`, `gen_spki_random_public`, `gen_spki_random_public_pem`, `ostree commit --sign-type=spki`, `ostree sign --verify --sign-type=spki`, `--keys-file`, `--keys-dir`, dummy signing, and `trusted.spki.d`/`revoked.spki.d`.

## Control Flow
The script generates SPKI key material, signs a commit, checks detached metadata, verifies failure with wrong public key and success with correct key in several argument positions, signs another commit with dummy and SPKI signatures, validates empty and invalid keys-file behavior, tests a PEM public key file, a 100-key invalid PEM list, adding the valid PEM key, signing with a PEM secret key file, verifying trusted directory discovery, and rejecting after adding the key to the revoked directory.

## State And Persistence
State includes SPKI detached metadata, PEM public/secret temp files, random key lists, trusted and revoked SPKI directories, and the test repository.

## Dependencies And Integration Points
This integrates the SPKI signing backend, PEM parsing, sign CLI, detached metadata, multi-signature coexistence, and directory-based trust/revocation.

## Risks
PEM parsing and binary/string key formats can diverge from ed25519 behavior. The verification path must count attempted keys correctly, reject wrong keys, and make revoked keys invalid even when trusted.

## Test Signals
TAP results match the ed25519 structure: detached SPKI signature, verification, multiple signing, keys-file verification, secret-file signing, trusted directory verification, and revocation.
