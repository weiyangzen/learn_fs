# sources/cloud-native/composefs-rs/crates/composefs-integration-tests/Cargo.toml

Purpose: declares the unpublished integration-test harness crate for composefs-rs.

Important APIs/types/functions: `autobins = false` and `autotests = false` prevent Cargo defaults. `src/main.rs` is declared both as a `[[bin]]` named `cfsctl-integration-tests` and a `[[test]]` with `harness = false`, allowing container image execution and nextest/libtest-mimic discovery. `src/cleanup.rs` is a separate `test-cleanup` binary.

Control flow: tests are registered through code, not Cargo test discovery. Dependencies include CLI/test helpers (`xshell`, `libtest-mimic`, `linkme`, `paste`, `tempfile`), serialization (`serde`, `serde_json`), archive/layout tools (`tar`, `ocidir`), repository crates (`composefs`, `composefs-oci`, `composefs-ctl` with `oci`), `tokio`, `rustix`, and `zlink`.

State and persistence: tests create temporary repositories, containers-storage images, loop-mounted filesystems, podman containers/images, and OCI layouts. The cleanup binary removes labeled podman resources.

Dependencies and integration points: this crate intentionally verifies behavior through the `cfsctl` CLI for most checks, while using library helpers for fixture setup and typed varlink tests. It is excluded from workspace default members per comments and is expected to run through `just test-integration` or VM workflows.

Risks: tests are highly environment-sensitive: podman, skopeo, bcvk, user namespaces, root privileges, fs-verity-capable ext4, XFS reflinks, network access, and old binary paths can all affect execution. Because `src/main.rs` is both bin and test, warnings around shared source are expected.

Test signals: the manifest itself shows broad coverage intent: host-safe CLI tests, privileged mount/verity tests, containers-storage import tests, network digest stability tests, old-format migration tests, and varlink protocol tests.
