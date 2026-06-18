<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/config.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/config.rs

Purpose: defines the complete user-facing configuration surface for the BeeGFS Rust management daemon, covering initialization/import switches, database path, logging, BeeMsg/gRPC networking, TLS, authentication, registration policy, node/client timeout behavior, licensing, blocking thread limits, quota collection/enforcement, capacity-pool thresholds, and hidden daemonization options.

Important APIs/types/functions: the `generate_structs!` macro emits `Config`, its `Default`, private `OptionalConfig` for clap/TOML input, and merge logic. `Config::check_validity()` enforces UUID v4, quota dependency, and capacity-pool consistency. `load_and_parse()` implements default/config-file/CLI precedence and port shifting. `LogTarget` and `LogLevel` are clap/serde enums, with `LogLevel` mapped to `log::LevelFilter`.

Control flow: startup parses CLI first to discover the config file, loads TOML if present or explicitly requested, overlays CLI values, validates the merged result, then applies `port_shift` to BeeMsg and gRPC ports with overflow warnings. TOML uses `deny_unknown_fields`, while some options are CLI-only via `serde(skip)`.

State and persistence: this file does not persist state directly. It determines persistent file locations for SQLite, auth secret, TLS cert/key, license cert/library, quota ID files, and daemon PID. Its defaults shape on-disk deployment behavior.

Dependencies and integration points: used by `main.rs` for binary startup and by `lib.rs`, `grpc.rs`, `quota.rs`, `timer.rs`, and capacity-pool calculations at runtime. It depends on clap, serde/TOML, shared NIC filtering, duration/range parsers, UUID, and capacity-pool validation.

Risks: config precedence comments contain a misleading line saying config file settings overwrite command-line settings, while implementation overlays command line last. Hidden import/init/fs UUID options bypass TOML. `port_shift` intentionally allows overflow. Quota ID ranges can create large query sets if configured too broadly. TLS disable and auth disable are high-impact operational settings.

Test signals: no direct tests in this file. Useful coverage would exercise TOML/CLI precedence, unknown fields, duration/range parsing, invalid quota/enforcement combinations, dynamic capacity limits, UUID version checks, and port-shift overflow messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/config.rs -->
