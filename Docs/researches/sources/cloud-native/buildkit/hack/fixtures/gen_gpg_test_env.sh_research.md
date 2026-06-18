<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/hack/fixtures/gen_gpg_test_env.sh -->
# sources/cloud-native/buildkit/hack/fixtures/gen_gpg_test_env.sh

Purpose: generates GPG signing test fixtures under `BUILDKIT_TEST_SIGN_FIXTURES` for a requested username.

Important APIs, types, and functions: shell script validates `BUILDKIT_TEST_SIGN_FIXTURES` and username argument, sets shared `GNUPGHOME`, writes a no-protection RSA cert key config, substitutes username/email placeholders, runs `gpg --generate-key`, extracts the fingerprint, adds an RSA signing subkey, writes `git_gpg_sign.sh`, writes `<user>.gpg.gitconfig`, exports `<user>.gpg.pub`, and creates a detached signature fixture over `<user>.http.artifact`.

Control flow and state: persists generated GPG home, config, and key material in the fixture directory. It changes into the fixture root and runs with `set -e` plus `set -x` after validation.

Dependencies and integration: depends on `gpg`, shell utilities, and the signing test environment. Used to prepare test data for provenance/signing workflows.

Risks and test signals: generated keys are unprotected and must remain test-only. Existing fixture files may be overwritten depending on username. Test signal is successful key generation and later signing/verifier tests using the generated fixtures.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/hack/fixtures/gen_gpg_test_env.sh -->
