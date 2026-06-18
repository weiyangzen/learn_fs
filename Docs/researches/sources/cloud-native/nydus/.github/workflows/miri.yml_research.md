# sources/cloud-native/nydus/.github/workflows/miri.yml

## Purpose
This workflow runs Rust unit tests under Miri to detect undefined behavior in interpreter-supported code paths.

## Important APIs, Types, and Functions
It triggers on push, PR, daily schedule, and manual dispatch. The single job `nydus-unit-test-with-miri` checks out code, uses the Rust cache, installs cargo-nextest, sets up fscache, installs nightly Miri, installs protoc, and runs `sudo -E RUSTUP=<path> make miri-ut-nextest`.

## Control Flow
After setup, the Makefile target runs `cargo miri nextest` on workspace tests excluding integration and two known unsupported/heavy tests. Output is tee'd to `miri-ut.log`, and the workflow greps for `Undefined Behavior`.

## State and Persistence
State includes the Rust toolchain override to nightly in the workspace, cargo cache, fscache setup, and `miri-ut.log` in the Actions workspace. No artifacts are uploaded.

## Dependencies and Integration Points
This depends on the Makefile `miri-ut-nextest` target, `misc/fscache/setup.sh`, `misc/install-protoc.sh`, nightly Rust/Miri, and the workspace test suite.

## Risks and Edge Cases
The final `grep -C 2 'Undefined Behavior' miri-ut.log` returns nonzero when no match is found, which can make an otherwise clean run fail unless shell behavior or preceding pipeline masks it. Running with `sudo -E` and Miri isolation disabled changes environment assumptions. Nightly toolchain changes may introduce flakiness.

## Test Signals
The primary signal is Miri execution of unit tests and absence of UB reports. The workflow currently also treats grep behavior as a signal, so its exit semantics should be watched.
