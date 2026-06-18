# sources/cloud-native/ostree/rust-bindings/src/tests/repo.rs

## sources/cloud-native/ostree/rust-bindings/src/tests/repo.rs

Unit tests for `Repo::mode_from_string`. They verify a valid mode string (`"bare"`) converts to `RepoMode::Bare` and an invalid string returns an error.

Control flow is direct invocation of the generated static wrapper; there is no repository creation or disk persistence. Dependencies are `Repo` and `RepoMode`.

The test signal is narrow but useful because repo mode parsing crosses the FFI error boundary and is used when creating/opening repositories. Broader repo transaction and object IO behavior is not covered by this test file.
