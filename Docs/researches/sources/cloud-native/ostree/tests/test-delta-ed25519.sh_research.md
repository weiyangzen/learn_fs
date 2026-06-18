# sources/cloud-native/ostree/tests/test-delta-ed25519.sh

Purpose: exhaustive static delta signing and verification tests for the ed25519 signature module.

Important APIs/functions: `skip_without_ostree_feature sign-ed25519`, `static-delta generate --sign-type=ed25519`, `--sign`, `--keys-file`, `--inline`, `static-delta verify`, `static-delta apply-offline`, `--keys-dir`, and helper functions for file permutation and delta directory lookup.

Control flow: creates two revisions, signs deltas with inline keys and key files, verifies with correct, wrong, and multiple public keys, validates failure with bad key files, tests public-key files and multiple keys, applies offline with key files/directories, and checks revocation behavior.

State/persistence: writes `repo/deltas`, key files under the temp dir, `repo2` apply targets, and signature material. Dependencies include user xattrs and ed25519 support.

Integration/risk/test signals: protects modern signature verification for delta transport. Risks include hard-coded key material and large matrix maintenance. TAP ok lines segment each key mode and apply-offline scenario.
