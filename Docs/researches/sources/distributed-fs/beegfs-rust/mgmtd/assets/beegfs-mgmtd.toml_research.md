<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/assets/beegfs-mgmtd.toml -->
## sources/distributed-fs/beegfs-rust/mgmtd/assets/beegfs-mgmtd.toml

**Purpose:** Packaged sample/default configuration file for BeeGFS management.

**Important APIs/types/functions:** Documents database/log settings, BeeMsg and gRPC ports, TLS certificate/key, interface filters, IPv6 disable, connection limit, auth disable/file, registration disable, node/client offline timeouts, license cert/library paths, blocking thread count, quota collection/enforcement/user/group selectors, and static/dynamic capacity pool limits for meta and storage targets.

**Control flow:** The binary reads config values from this TOML file, with command-line arguments overriding file values and file values overriding internal defaults. Most entries are commented examples.

**State and persistence behavior:** The config controls persistent database location, authentication file, license paths, and quota/capacity behavior. Package metadata marks it as a config file/noreplace so local edits should survive upgrades.

**Dependencies and integration points:** Parsed by the management service configuration layer using serde/TOML and shared parsers for duration/integer units/interface filters. Installed to `/etc/beegfs/beegfs-mgmtd.toml`.

**Risks:** Because all settings are commented by default, operational behavior depends heavily on internal defaults. Incorrect offline timeouts must also be coordinated with meta/storage/client configuration. Enabling quota can increase load and requires at least one ID source for enforcement to matter. Dynamic cap-pool thresholds must be consistent with static lower bounds.

**Test signals:** Start `beegfs-mgmtd --help`, parse this file as installed, run with representative uncommented TLS/auth/quota/cap-pool settings, and verify command-line overrides.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/assets/beegfs-mgmtd.toml -->
