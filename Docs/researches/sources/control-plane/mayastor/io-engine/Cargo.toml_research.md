<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/Cargo.toml -->
# sources/control-plane/mayastor/io-engine/Cargo.toml

Purpose: Manifest for the main `io-engine` crate, including binaries, examples, feature flags, local API dependencies, and SPDK-adjacent dependencies.

Important configuration: default feature is `spdk-async-qpair-connect`; optional features include `io-engine-testing`, `extended-tests`, `fault-injection`, `nexus-io-tracing`, and `nvme-pci-tests`. Binaries include `io-engine`, `spdk`, `initiator`, `uring-support`, `io-engine-client`, `jsonrpc`, and `casperf`; example `lvs-eval` points to `examples/lvs-eval/main.rs`.

Dependencies: combines crates for async runtime, CLI, logging/tracing, serialization, NVMe/io_uring/system calls, tonic/prost, and local path crates such as `spdk-rs`, `io-engine-api`, event publisher, secret provider, version info, sysfs, and jsonrpc.

Integration points: dev-depends on `io-engine-tests`, `libnvme-rs`, `run_script`, and `prettytable-rs` for tests/examples.

State and risks: feature combinations gate fault injection, testing hooks, tracing, and async NVMe behavior. Build/test signals should include default build, feature-specific test builds, and example compilation when touching dependencies.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/Cargo.toml -->
