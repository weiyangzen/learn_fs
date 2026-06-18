# sources/cloud-native/composefs-rs/crates/composefs-integration-tests/src/main.rs

Purpose: custom integration-test runner using `libtest_mimic`, plus host-safe helpers shared by test modules.

Important APIs/types/functions: `cfsctl()` resolves the binary path from `CFSCTL_PATH`, workspace target release/debug, or `/usr/bin/cfsctl`. `create_test_rootfs(parent)` creates a simple rootfs fixture with `/usr/bin/hello`, `/usr/lib/readme.txt`, and `/etc/hostname`. `main` initializes containers-storage helper mode, converts registered `IntegrationTest`s to `libtest_mimic::Trial`s, and runs them.

Control flow: `main` first calls `composefs_oci::cstor::init_if_helper()` because this binary may be re-executed under `podman unshare` as a containers-storage helper. It parses libtest-style arguments, maps each distributed test to a trial closure returning formatted errors, and exits with libtest status.

State and persistence: `create_test_rootfs` writes a temporary fixture tree. The runner itself only executes tests; persistent state is produced by individual tests.

Dependencies and integration points: bridges the library registration slice to the test executable. It is both a Cargo test target and standalone binary, matching the manifest. The rootfs deliberately includes a 128 KiB file to force external object storage for `image-objects`/dump tests.

Risks: path discovery assumes the crate is two parents below workspace root. Re-exec helper initialization must run before argument handling. Tests are plain functions, so filtering and exact matching depend on libtest-mimic names from `IntegrationTest::new`.

Test signals: all integration tests flow through this file. Failures in `cfsctl()` or registration show up as immediate harness failures rather than domain-specific errors.
