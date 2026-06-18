# sources/cloud-native/composefs-rs/crates/composefs-ctl/Cargo.toml

## Purpose
This manifest defines the `composefs-ctl` crate, its library, and the `cfsctl` binary. The crate is the command-line control surface for composefs repositories and images and also hosts compatibility implementations of `mkcomposefs` and `composefs-info`.

## Important APIs, types, and functions
The manifest declares `src/lib.rs` as the library and `src/main.rs` as the `cfsctl` binary. Features gate optional functionality: `http` enables `composefs-http`; `oci` enables `composefs-oci` and its varlink integration; `containers-storage` adds native storage support through `composefs-storage`; `rhel9` and `pre-6.15` forward compatibility flags to `composefs`.

## Control flow
Cargo feature resolution controls which command variants and dependencies are compiled. The default feature set includes `pre-6.15`, `oci`, and `containers-storage`, so a normal build includes OCI workflows and compatibility behavior for older kernels unless the user disables defaults.

## State and persistence behavior
The manifest itself has no runtime state, but it selects dependencies that own persistent repository state, OCI storage, varlink service behavior, and boot integration. Optional dependencies keep non-default transports out of builds that do not request them.

## Dependencies and integration points
Core dependencies include `anyhow`, `clap`, `composefs`, `composefs-boot`, `env_logger`, `libsystemd`, `rustix`, `serde`, `serde_json`, `tokio`, and `zlink`. Optional dependencies connect to OCI, HTTP, and containers-storage paths. Workspace lints are applied through `[lints] workspace = true`.

## Risks
Defaulting to OCI and containers-storage increases build surface and platform assumptions. The `pre-6.15` default changes lower-level composefs behavior and should stay aligned with kernel support expectations. Feature combinations can hide code paths from CI if not tested explicitly, especially `http` without `oci`, no-default-feature builds, and RHEL-specific behavior.

## Test signals
The manifest has no direct tests. Build matrix coverage across default features, no default features, `http`, `oci`, `containers-storage`, `rhel9`, and `pre-6.15` is the relevant signal.
