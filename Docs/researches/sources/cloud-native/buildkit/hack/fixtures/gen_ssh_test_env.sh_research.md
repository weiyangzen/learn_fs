<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/hack/fixtures/gen_ssh_test_env.sh -->
# sources/cloud-native/buildkit/hack/fixtures/gen_ssh_test_env.sh

Purpose: generates SSH signing test fixtures for BuildKit signing-related tests.

Important APIs, types, and functions: shell script validates `BUILDKIT_TEST_SIGN_FIXTURES` and username argument, creates `.ssh/<user>.id_ed25519` when missing, reads the public key, writes a per-user `git_ssh_sign.sh` wrapper that runs `ssh-keygen -Y sign -n git`, substitutes the username into the wrapper, writes `<user>.ssh.gitconfig` with `gpg.format = ssh` and the public signing key, and exports `<user>.ssh.pub`.

Control flow and state: persists keys, wrapper, gitconfig, and public key under the fixture root. It is fail-fast and command-traced after validation. The wrapper unsets `SSH_AUTH_SOCK` so signing uses the fixture key directly.

Dependencies and integration: depends on OpenSSH `ssh-keygen` and fixture environment variables consumed by signing tests.

Risks and test signals: key material is test-only and should not escape fixture directories. The generated wrapper parses Git signing arguments narrowly and may need updates if Git changes its invocation shape. Test signal is successful fixture generation followed by Git SSH signing verification tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/hack/fixtures/gen_ssh_test_env.sh -->
