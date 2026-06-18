# sources/cloud-native/ostree/tests/run-installed

Purpose: convenience runner for tests that must execute against installed binaries after a development `make install`.

Important APIs/functions: plain Bash with `set -xeuo pipefail`; computes `dn=$(dirname $0)` and runs Cargo in `tests/inst` via `(cd ${dn}/../tests/inst && cargo run --release)`.

Control flow: no branching. It changes to the Rust installed-test directory relative to the script and delegates all test logic to Cargo.

State/persistence: writes only whatever Cargo build/test artifacts are produced under the Rust target tree. It depends on an installed OSTree environment, Rust/Cargo, and the `tests/inst` crate.

Integration/risk/test signals: integrates the shell test tree with Rust installed tests. Risks are path assumptions and accidental testing of build-tree binaries if the environment is not clean. Success is Cargo's release run exit status.
