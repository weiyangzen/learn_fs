# sources/cloud-native/ostree/tests/test-commit-sign.sh

Purpose: end-to-end tests for GPG-signed commits, signature verification during pull/show, corrupted signatures, and signature addition/deletion after content is already present.

Important APIs/functions: `skip_without_ostree_feature gpgme`, `setup_fake_remote_repo1`, `ostree commit --gpg-sign`, `ostree pull`, `show --gpg-verify-remote`, `gpg-sign --delete`, and optional `test-commit-sign-sh-ext`.

Control flow: creates multiple signed remote commits, verifies pull fails without trusted keys, succeeds with the fixture key, optionally runs C API tests, corrupts detached signature metadata and expects verified pulls to fail, disables GPG to repull corrupted content, then tests pulling an unsigned commit that is later signed and later signature-deleted.

State/persistence: mutates remote commitmeta files, local repo signatures, HTTP serving state, and gpghome trust. Dependencies include gpgme and test keys.

Integration/risk/test signals: protects signature lifecycle and detached metadata synchronization. Risks are GPG environment fragility and exact signature count output. TAP plan covers pull/verify/corruption/update cases.
