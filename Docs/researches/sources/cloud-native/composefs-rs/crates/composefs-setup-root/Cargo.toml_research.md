# sources/cloud-native/composefs-rs/crates/composefs-setup-root/Cargo.toml

## Purpose
This manifest defines the `composefs-setup-root` binary crate, an initramfs setup tool for composefs-based boot. It participates in the workspace and inherits edition, license, readme, repository, Rust version, version, and lints.

## Important APIs, Types, and Functions
As a Cargo manifest, its important API surface is feature and dependency selection. Features are `default = ["pre-6.15"]`, `rhel9 = ["composefs/rhel9"]`, and `pre-6.15 = ["composefs/pre-6.15"]`. The default feature selects compatibility behavior for kernels before 6.15.

## Control Flow
Cargo resolves this crate as a binary package. Feature flags flow into the Rust code via `cfg!(feature = "pre-6.15")`, changing whether the new root is mounted early or after submount setup. `rhel9` and `pre-6.15` propagate to the `composefs` workspace crate.

## State and Persistence
The manifest itself has no runtime persistence. It determines which dependencies are built into the setup tool and therefore which mount/repository behavior is available at early boot.

## Dependencies and Integration Points
Runtime dependencies include `anyhow`, `fn-error-context`, `clap`, `composefs`, `composefs-boot`, `env_logger`, `hex`, `rustix`, `serde`, and `toml`. `similar-asserts` is used for tests. The dependency set reflects a low-level boot utility: command-line parsing, TOML config parsing, digest parsing, composefs repository/mount APIs, boot command line parsing, and Linux mount syscalls through `rustix`.

## Risks
Defaulting to `pre-6.15` materially changes mount sequencing and can hide newer floating-tree behavior unless disabled. The crate uses low-level mount APIs, so dependency feature changes can affect initramfs footprint and syscall availability. `env_logger` is present but the current code does not configure much logging.

## Test Signals
The manifest exposes only `similar-asserts` as a dev dependency. The Rust tests in `src/main.rs` focus on command-line digest parsing rather than mount behavior, which is difficult to unit-test without privileged/kernel-specific environments.
