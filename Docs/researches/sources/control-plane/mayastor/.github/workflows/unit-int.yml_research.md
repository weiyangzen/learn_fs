# sources/control-plane/mayastor/.github/workflows/unit-int.yml

## Purpose
Reusable integration/unit workflow for Rust and JS gRPC tests.

## Important Jobs and Steps
`int-tests` runs on `cncf-ubuntu-16-64-x86`, checks out submodules, installs/configures Nix, warms nix-shell, uses Rust cache with save only on release/develop, builds binaries with `io-engine-testing`, configures hugepages/modules/NVMe, sets Docker journald logging, runs Rust tests via `cargo-test.sh`, checks coredumps and cleans, then runs JS gRPC tests via `grpc-test.sh`, wraps xunit XML in `<testsuites>`, publishes report, collects artifacts on failure, checks coredumps again, and cleans again.

## Control Flow
Rust tests and cleanup/coredump checks run before JS tests. Several diagnostic steps use `if: always()`, while artifact upload occurs on failure/cancellation.

## State and Persistence
Creates build outputs, test processes, Docker state, kernel module/hugepage settings, xunit reports, and optional artifacts. Does not commit changes.

## Dependencies and Integration Points
Depends on custom runner with kernel support, Nix shell, SPDK/submodules, Docker, gdb, and scripts `nvme-conf.sh`, `cargo-test.sh`, `grpc-test.sh`, `ci-report.sh`, `check-coredumps.sh`, and `clean-cargo-tests.sh`. Called by `pr-ci.yml`.

## Risks
The workflow has two `Check Coredumps` and `Cleanup` step names, which can make logs less clear. Kernel/hardware assumptions make it runner-specific. If Rust tests fail, JS tests may be skipped because there is no `if: always()` on `Run JS Grpc Tests`.

## Test Signals
Successful Rust cargo tests, JS gRPC xunit report, no coredumps since `TEST_START_DATE`, and absence of failure artifacts.
