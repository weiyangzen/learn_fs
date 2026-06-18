# sources/control-plane/mayastor/scripts/grpc-test.sh

Purpose: CI wrapper for JavaScript gRPC integration tests.

Important APIs/types/functions: cleanup handler invokes `clean-cargo-tests.sh`; builds Rust bins with `io-engine-testing`; enters `test/grpc`, runs `npm install --legacy-peer-deps`, kills existing `io-engine`, validates NVMe config, and runs mocha suites `cli`, `replica`, `nexus`, and `rebuild` with `multi_reporter.js`.

Control flow: cleanup runs before and after via traps. Each suite emits both xunit and spec output with per-suite XML reports.

State/persistence: installs node dependencies, builds cargo artifacts, kills processes, cleans host resources, and writes xunit XML reports.

Dependencies/integration: integrates Rust binaries, Node/mocha tests, custom reporter, NVMe config, and cleanup script.

Risks: `sudo pkill io-engine` and cleanup are broad. `npm install` during test runs can be slow/flaky and network-dependent if cache is cold.

Test signals: passing script means legacy JS gRPC suites pass and xunit reports were generated.
