<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/Cargo.toml -->
## sources/distributed-fs/beegfs-rust/mgmtd/Cargo.toml

**Purpose:** Manifest and package metadata for the BeeGFS management service binary.

**Important APIs/types/functions:** Defines package `mgmtd`, binary `beegfs-mgmtd` at `src/main.rs`, build dependency on local `sqlite`, local dependencies `shared`, `protobuf`, `sqlite`, `sqlite_check`, and runtime dependencies including `daemonize`, `libloading`, `rusqlite`, `sd-notify`, `tokio`, `toml`, and `tonic`. Denies undocumented unsafe blocks through clippy. RPM and DEB metadata install the binary, third-party license HTML, copyright/config/service assets, and debug-symbol variants.

**Control flow:** Cargo builds `build.rs` first to generate migration artifacts, then builds the `beegfs-mgmtd` binary. Makefile packaging uses this manifest as input for `cargo deb` and `cargo generate-rpm`, and temporarily patches dependency requirements when `GLIBC_VERSION` is set.

**State and persistence behavior:** Package metadata persists install paths: binary under `/opt/beegfs/sbin/`, config under `/etc/beegfs/`, systemd unit under `/usr/lib/systemd/system/`, docs under `/usr/share/doc/beegfs-mgmtd/`, and debug symbols under `/opt/beegfs/sbin/`.

**Dependencies and integration points:** Integrates with assets `beegfs-mgmtd.toml` and `beegfs-mgmtd.service`, the Makefile release/package flow, and external `libbeegfs-license >= 8.3`.

**Risks:** Packaging paths are hard-coded and must match service `ExecStart`. `daemonize = "=0.5.0"` is advisory-ignored in `deny.toml`; changes to daemonization use need security review. Package metadata is mutated by the Makefile during glibc-targeted builds, so restoration must be reliable.

**Test signals:** `cargo build -p mgmtd`, `cargo test -p mgmtd --all-features`, `make package`, and package installation tests verifying config/service/debug artifacts and dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/Cargo.toml -->
