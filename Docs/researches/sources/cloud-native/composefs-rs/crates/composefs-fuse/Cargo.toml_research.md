# sources/cloud-native/composefs-rs/crates/composefs-fuse/Cargo.toml

Purpose: declares the `composefs-fuse` library crate, a FUSE backend for exposing composefs trees from a repository.

Important APIs/types/functions: package metadata is workspace-inherited. Dependencies are `anyhow`, workspace `composefs`, `fuser` with ABI 7.31, `log`, and `rustix` with `fs` and `mount` features.

Control flow: Cargo builds the library from `src/lib.rs`; there are no binary targets in this manifest. The crate intentionally uses low-level mount APIs, so its dependency list is small but system-facing.

State and persistence: the manifest configures a runtime library that opens `/dev/fuse`, creates a FUSE mount object, and serves read-only file content from composefs repository objects.

Dependencies and integration points: integrates with Linux FUSE, rustix fsopen/fsconfig/fsmount APIs, and the core `composefs` tree/repository model. Consumers are expected to open `/dev/fuse`, call `mount_fuse`, then call `serve_tree_fuse`.

Risks: platform support is Linux-specific. The `fuser` ABI feature pins kernel protocol expectations. Mount behavior requires appropriate privileges or userns/fuse configuration, and changes in `rustix` mount wrappers can affect this crate.

Test signals: privileged mount integration tests exercise the higher-level `cfsctl mount` path, which depends on composefs mount behavior. Direct unit coverage for this FUSE crate is not present in this subset.
