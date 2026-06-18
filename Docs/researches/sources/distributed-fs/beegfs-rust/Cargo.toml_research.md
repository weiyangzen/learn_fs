<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/Cargo.toml -->
## sources/distributed-fs/beegfs-rust/Cargo.toml

**Purpose:** Root Cargo workspace manifest for BeeGFS Rust components.

**Important APIs/types/functions:** Declares workspace resolver 2, members `shared`, `mgmtd`, `sqlite`, `sqlite_check`, and `bee_serde_derive`. Workspace package metadata sets edition 2024, ThinkParQ authorship, BeeGFS docs/homepage, and `publish=false`. Shared dependency versions include `anyhow`, `clap`, `env_logger`, `itertools`, `libc`, `log`, `prost`, a git-pinned ThinkParQ `protobuf` crate, `rusqlite` with bundled/vtab/array/fallible_uint features, `serde`, `thiserror`, `tokio`, `tokio-stream`, `tonic`, and `uuid`.

**Control flow:** Cargo resolves dependency versions and workspace metadata from here for member crates. `mgmtd/Cargo.toml` inherits edition, authors, documentation, homepage, publish flag, and many dependency versions.

**State and persistence behavior:** Source-control state only; dependency resolution is persisted by `Cargo.lock` and constrained in CI by `CARGO_LOCKED`.

**Dependencies and integration points:** Drives all Makefile targets, CI checks, package builds, and procedural macro crate compilation. The git dependency on `thinkparq/protobuf` is allowed by `deny.toml` source policy.

**Risks:** Edition 2024 requires a sufficiently new Rust toolchain, matching the nightly-centric Makefile. The git-pinned protobuf dependency can break if unavailable unless Cargo uses CLI git fetching as configured in CI. Workspace-wide dependency changes affect multiple crates and packaging.

**Test signals:** `cargo metadata`, `make check`, `make test`, and `make deny` validate resolution, linting, tests, and source/license policy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/Cargo.toml -->
