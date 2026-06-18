# sources/cloud-native/ostree/rust-bindings/src/auto/sysroot_upgrader.rs

## sources/cloud-native/ostree/rust-bindings/src/auto/sysroot_upgrader.rs

Generated binding for `OstreeSysrootUpgrader`, a helper object that pulls and deploys upgrades for a sysroot. Constructors include `new`, `new_for_os`, and version-gated `new_for_os_with_flags`; methods expose `check_timestamps`, `deploy`, `dup_origin`, `pull`, `pull_one_dir`, `pull_only`, `repo`, and `sysroot`.

Control flow delegates upgrade sequencing to libostree, with Rust handling GLib pointer conversion and GError results. State is held in the sysroot, repo, origin config, and upgrade object; persistent effects include pulling commits and writing new deployments when deploy methods run.

Dependencies include `Sysroot`, `Repo`, `AsyncProgress`, `RepoPullFlags`, `SysrootUpgraderFlags`, and pull flags. Risks include network/pull failure, origin mismatch, deployment side effects, and cancellation handling. Local tests are absent.
