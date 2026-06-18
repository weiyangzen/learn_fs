<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/Cargo.toml -->
# sources/control-plane/mayastor/io-engine-tests/Cargo.toml

Purpose: Defines `io-engine-tests`, the shared support library for io-engine integration tests, benchmarks, and examples.

Important dependency surface: async helpers use `tokio`, `async-trait`, and `tonic`; command/test utilities use `run_script`, `regex`, `nix`, `chrono`, and `colored_json`; storage-facing helpers depend on local `io-engine`, `io-engine-api`, `spdk-rs`, `libnvme-rs`, `composer`, and the local proc-macro crate `io-engine-tests-macros`.

Integration points: this crate exposes builders and wrappers for bdevs, pools, replicas, nexus, snapshots, NVMf/NVMe devices, file I/O, FIO, compose clusters, and SPDK single-thread test execution. It is consumed by io-engine tests and by `io-engine-bench`.

State and persistence: no manifest-level state, but dependencies imply runtime access to SPDK, system block devices, docker/compose networking, and host binaries.

Risks and test signals: path dependencies mean this crate tracks local API changes tightly. Because many modules panic on setup failures, a Cargo build only proves API compatibility; meaningful tests require privileged host tools, SPDK environment variables, and available NVMe/fio/loopback resources.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/Cargo.toml -->
