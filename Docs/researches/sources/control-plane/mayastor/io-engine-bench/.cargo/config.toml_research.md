# sources/control-plane/mayastor/io-engine-bench/.cargo/config.toml

## Purpose
Cargo target configuration for `io-engine-bench` tests/benchmarks requiring elevated privileges.

## Important Settings
For both `x86_64-unknown-linux-gnu` and `aarch64-unknown-linux-gnu`, Cargo uses `runner = ".cargo/runner.sh"`. Comments state the runner asks for sudo password as needed.

## Control Flow
When Cargo runs binaries/tests for those targets inside `io-engine-bench`, it invokes `.cargo/runner.sh` instead of executing the binary directly.

## State and Persistence
No persistent state in this file. The runner may elevate and mutate system state depending on benchmark behavior.

## Dependencies and Integration Points
Depends on `.cargo/runner.sh`, sudo/elevated privileges, and Linux targets. Integrates with Mayastor benchmarks that need privileged device operations.

## Risks
Cargo test/run behavior changes only in this subcrate, which can surprise developers. Privileged runners are unsuitable for untrusted code. Missing runner script breaks cargo execution.

## Test Signals
Run `cargo test` or benchmark commands in `io-engine-bench` on both supported architectures where possible and verify the runner prompts/elevates correctly.
