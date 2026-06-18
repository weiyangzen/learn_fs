## sources/cloud-native/composefs-rs/crates/composefs-ioctls/Cargo.toml

Purpose: this manifest defines the small `composefs-ioctls` crate, whose job is to isolate Linux ioctl bindings used by composefs. The package description and keywords identify two covered domains: fs-verity and loop devices.

Important configuration: the crate inherits edition, license, readme, repository, Rust version, version, and lints from the workspace. It has no default features and exposes an optional `loop-device` feature, allowing downstream crates to avoid compiling loop-device support unless needed. Runtime dependencies are deliberately minimal: `rustix` with the `fs` feature for fd, filesystem, and ioctl bindings, plus `thiserror` for typed error enums.

Control flow and integration: the manifest maps to `src/lib.rs`, which always exports `fsverity` and conditionally exports `loop_device`. The crate is meant to be a safe wrapper boundary around `unsafe` ioctl calls so consumers can forbid unsafe code while depending on these operations.

State and persistence behavior: the manifest itself has no persistent runtime state. Its feature gate controls whether loop-device ioctl code and its `/dev/loop-control` interaction become part of builds.

Dependencies and test signals: dev-dependencies are `tempfile` for filesystem-backed ioctl tests and `test-with` for path-gated tests such as `/dev/shm` behavior. The dependency set indicates tests interact with real filesystems and kernel ioctl responses rather than pure mocks.

Risks: this crate is highly platform-specific despite not declaring target gating in the manifest. Linux-only assumptions live in source modules and tests; non-Linux builds or environments without fs-verity/loop support may require cfg handling at higher layers. The optional loop feature prevents some exposure but does not make fs-verity portable.
