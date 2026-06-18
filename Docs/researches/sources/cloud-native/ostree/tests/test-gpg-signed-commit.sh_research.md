<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-gpg-signed-commit.sh -->
# sources/cloud-native/ostree/tests/test-gpg-signed-commit.sh

## Purpose
`test-gpg-signed-commit.sh` is broad CLI coverage for GPG-signed commits. It validates adding, displaying, duplicating, deleting, and verifying commit signatures across normal, missing-key, expired-key, expired-subkey, missing-subkey, and revoked-key cases.

## Important APIs, Types, And Functions
The script uses `skip_without_ostree_feature gpgme`, `which_gpg`, `ostree gpg-sign`, `ostree show`, `ostree commit --gpg-sign --gpg-homedir`, `ostree show --gpg-homedir`, `gpg --quick-generate-key`, `--quick-add-key`, `--quick-set-expire`, `--export`, and test key IDs from `libtest.sh`.

## Control Flow
The first phase signs an existing commit, verifies show output, rejects duplicate signatures, signs with multiple keys, and deletes signatures one at a time and all at once. The second phase creates an isolated GPG home, generates primary keys and subkeys, exports a trusted keyring, signs a commit with combinations of keys, and changes key state to force missing public key, expired primary key, expired subkey, missing subkey, and revocation diagnostics.

## State And Persistence
State lives in temporary GPG homes, trusted keyring directories, generated revocation certificates, exported keyrings, and commit signature metadata in the test repo. Cleanup removes the temporary GPG home unless skipped by the harness.

## Dependencies And Integration Points
It integrates OSTree commit signing and signature display with GPGME/GnuPG trust and key status behavior. It also depends on version-specific GnuPG support for subkey expiration.

## Risks And Test Signals
The test is sensitive to installed GnuPG features, exact diagnostic wording, and local clock/key-expiration handling. Passing signals include correct signature counts, duplicate rejection, deletion counts, good/bad signature classification, primary key ID reporting, and correct skip behavior when subkey expiration is unsupported.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-gpg-signed-commit.sh -->
