<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/script/setup/install-imgcrypt -->
# sources/cloud-native/containerd/script/setup/install-imgcrypt

- Purpose: Builds and installs imgcrypt/containerd encryption support artifacts for test environments.
- Important variables: `IMGCRYPT_REPO`, `IMGCRYPT_VERSION`, `DESTDIR`, and temporary clone root.
- Control flow: Clone imgcrypt, checkout pinned version, run `make containerd-release -e DESTDIR=...`, and clean the temporary clone.
- State and persistence: Installs generated release artifacts under `DESTDIR/usr/local`.
- Dependencies and integration: Requires git, make, Go tooling, and imgcrypt release targets. Integrates with encrypted image tests.
- Risks: External repository build can be slow/flaky; host install location is global; cleanup only runs after successful command flow unless trap exists.
- Test signals: Tests that exercise encrypted image pull/unpack and presence of installed imgcrypt tooling.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/script/setup/install-imgcrypt -->
