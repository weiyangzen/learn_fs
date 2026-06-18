# sources/control-plane/mayastor/scripts/cargo-test.sh

Purpose: CI/developer wrapper for Rust cargo tests and io-engine integration tests.

Important APIs/types/functions: defines `cleanup_handler`, invokes `clean-cargo-tests.sh`, prints `rustc --version`, extends `PATH`, checks `rdma_rxe`/`nvme_rdma` modules, validates NVMe config via `nvme-conf.sh --check`, runs `cargo test` in `jsonrpc`, builds bins with `io-engine-testing`, and runs `io-engine` tests single-threaded.

Control flow: cleanup runs before and after via trap. With `set -euo pipefail`, missing NVMe config exits early after warning.

State/persistence: cleans stale test devices/containers before and after; builds target artifacts and may leave cargo cache.

Dependencies/integration: integrates Rust toolchain, kernel modules, NVMe host config, cleanup script, and test feature flags.

Risks: cleanup at script start can remove active test resources if run concurrently. It exits on invalid NVMe config even though warning text says "may not be valid".

Test signals: successful completion is the main Rust CI gate for jsonrpc and io-engine integration tests.
