<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rust/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rust/config

## Purpose

Kselftest config fragment declaring kernel options needed for Rust sample-module probing.

## Important APIs, Types, and Functions

Lists CONFIG_RUST, CONFIG_SAMPLES, CONFIG_SAMPLES_RUST, CONFIG_SAMPLE_RUST_MINIMAL=m, and CONFIG_SAMPLE_RUST_PRINT=m.

## Control Flow and Integration

Consumed by kselftest config tooling to tell builders which options are needed before running rust selftests.

## State and Persistence Behavior

Static configuration metadata only.

## Dependencies and Integration Points

Requires kernel Rust support and sample module infrastructure.

## Risks and Edge Cases

If options are unavailable for an architecture, the probe script should skip rather than fail.

## Test Signals

A configured kernel should build rust_minimal and rust_print modules for test_probe_samples.sh.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rust/config -->
