# sources/cloud-native/ostree/rust-bindings/.ci/gitlab-ci-base.yml

Purpose: This GitLab CI base file defines reusable Rust binding test environments with sccache. It provides one Fedora Rawhide/libostree-devel lane and one generic Rust image lane with Debian `libostree-dev`.

Important jobs and variables: `.sccache` sets `SCCACHE_URL`, `CARGO_TARGET_DIR`, `CARGO_HOME`, `SCCACHE_DIR`, `RUSTC_WRAPPER`, and cache paths. `.fedora-ostree-devel` uses `registry.fedoraproject.org/fedora:rawhide`, installs `cargo rust ostree-devel`, installs sccache, and creates a pkg-config symlink workaround. `.rust-ostree-devel` uses `rust`, installs `libostree-dev`, and installs sccache.

Control flow and state: CI job state is confined to GitLab workspaces and caches for cargo artifacts and sccache. The before-script prepares system dependencies before generated jobs run `cargo test`.

Dependencies and integration points: Integrates GitLab CI, Fedora/Debian package managers, libostree development packages, Rust toolchain, pkg-config, curl, tar, and sccache. The generated test jobs extend `.fedora-ostree-devel`.

Risks: Rawhide is intentionally moving and can break bindings when libostree or packaging changes. Downloading sccache from GitHub during CI adds network dependency and supply-chain surface. The pkg-config symlink workaround is fragile and may become wrong as Fedora changes.

Test signals: Successful generated feature jobs are the main signal. CI logs should show package install success, sccache available as `RUSTC_WRAPPER`, and `pkg-config` locating ostree development metadata.
