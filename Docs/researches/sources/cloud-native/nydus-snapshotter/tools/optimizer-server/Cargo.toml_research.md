<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/tools/optimizer-server/Cargo.toml -->
## sources/cloud-native/nydus-snapshotter/tools/optimizer-server/Cargo.toml

Purpose: Rust package manifest for the `optimizer-server` utility, described as generating accessed-file information in a target mount namespace.

Important metadata/dependencies: package name `optimizer-server`, version `0.1.0`, edition 2021, Apache-2.0 OR BSD-3-Clause license, and Nydus authors. Dependencies include `clap` for CLI parsing, `lazy_static`, `libc`, `nix` for Unix/mount namespace/syscall work, `serde`/`serde_json` for data structures, and `signal-hook` for signal handling.

Control flow and state: Cargo manifest only; implementation is elsewhere. It declares runtime capabilities implied by dependencies rather than direct logic.

Dependencies/integration: built by the adjacent Makefile into `bin/optimizer-server`, likely packaged with snapshotter tooling.

Risks and test signals: dependency versions are pinned with older minor versions; security/compatibility updates should be reviewed periodically. No tests are declared in this manifest.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/tools/optimizer-server/Cargo.toml -->
