<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/.github/workflows/rust-test.yaml -->
# sources/cloud-native/fuse-overlayfs/.github/workflows/rust-test.yaml

Purpose: CI workflow for the Rust fuse-overlayfs implementation.

Important jobs: `build` installs stable Rust with clippy/rustfmt, caches Cargo state, checks formatting, runs clippy with warnings as errors, builds and tests release mode, and uploads the x86_64 binary. `integration-test` installs the binary and dependencies, builds containers/storage tests, runs project test scripts, unionmount tests, containers/storage tests, and unprivileged tests with and without overlay whiteouts. `cross-build` uses `cross` for multiple Linux architectures. `release` packages downloaded artifacts, writes `SOURCE_DATE_EPOCH`, creates SHA256 sums, and creates draft releases on version tags.

State and integration: extensive GitHub Actions automation using FUSE, root privileges, Podman/storage tests, and external repositories. Risks include external dependency drift, privileged kernel settings, long integration runtime, and tag-only release behavior. Test signal is strong across unit, integration, compatibility, and cross-arch builds.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/.github/workflows/rust-test.yaml -->
