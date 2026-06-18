<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-bench/Cargo.toml -->
# sources/control-plane/mayastor/io-engine-bench/Cargo.toml

Purpose: Defines the `io-engine-bench` crate, a Criterion benchmark package for io-engine workflows.

Important APIs/types/functions: no Rust API is declared here, but the manifest maps the `nexus` benchmark to `src/nexus.rs` with `harness = false`, allowing Criterion to own the benchmark main.

Dependencies: development dependencies include workspace `tokio` with `full`, workspace `uuid` with v4 generation, local `io-engine`, local `io-engine-tests`, and Criterion `0.5.1` with `async_tokio`. This positions the crate as a benchmark-only consumer of the runtime, gRPC compose test harness, and direct io-engine APIs.

Integration points: uses local path crates from the mayastor tree and expects the bench runner/build script to provide SPDK link/runtime setup.

State and persistence: Cargo metadata only; runtime state is created by bench code and Criterion outputs.

Risks and test signals: dependency drift is mostly tied to workspace versions plus Criterion. Because the benchmark uses test infrastructure, failures can come from docker/composer, SPDK privileges, or gRPC setup rather than benchmark logic. A healthy signal is `cargo bench -p io-engine-bench --bench nexus` reaching Criterion measurement rather than failing during setup.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-bench/Cargo.toml -->
