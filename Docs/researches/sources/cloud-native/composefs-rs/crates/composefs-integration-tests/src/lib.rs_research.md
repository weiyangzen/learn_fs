# sources/cloud-native/composefs-rs/crates/composefs-integration-tests/src/lib.rs

Purpose: shared integration-test infrastructure: registration metadata, test macro, cfsctl path discovery, test image settings, repository setup, and podman fixture helpers.

Important APIs/types/functions: `TestFn`, `IntegrationTest`, distributed slice `INTEGRATION_TESTS`, and macro `integration_test!` implement registration. Constants/functions include `INTEGRATION_TEST_LABEL`, `get_cfsctl_path`, `get_primary_image`, `get_all_images`, `create_test_repository`, `build_test_image`, and `cleanup_test_image`.

Control flow: modules call `integration_test!(function)` to insert metadata into the linkme slice. The runner later reads `INTEGRATION_TESTS`. `get_cfsctl_path` checks `CFSCTL_PATH`, target release/debug binaries, then `/usr/bin/cfsctl`. `create_test_repository` opens a tempdir fd and initializes an insecure SHA-256 repository. `build_test_image` writes a temporary Containerfile, builds a CentOS-based image with small/large files, symlink, `/boot`, and `/sysroot`, then reads the image ID from an iid file.

State and persistence: creates temporary repositories and podman images. Podman images may outlive tests unless explicitly cleaned. The repository helper returns `Arc<Repository<Sha256HashValue>>` for async/library tests.

Dependencies and integration points: uses `linkme`/`paste` for distributed registration, `tempfile`, `rustix`, `composefs_oci` re-exported composefs types, and podman. It supports both CLI subprocess tests and library-level setup for containers-storage imports.

Risks: distributed slices require unsafe allowance. `build_test_image` depends on network/base image availability and podman behavior. The test label constant is not embedded in the sample Containerfile shown here, so cleanup only applies where tests label podman resources elsewhere. Path discovery can accidentally pick stale target binaries if multiple builds exist.

Test signals: this file is foundational; if registration or cfsctl path resolution breaks, all integration modules fail. It also standardizes the minimal image used by cstor/bootable tests.
