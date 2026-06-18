<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rust/test_probe_samples.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rust/test_probe_samples.sh

## Purpose

Rust selftest shell probe that verifies Rust sample kernel modules can be inserted and removed when the kernel was built with Rust sample support.

## Important APIs, Types, and Functions

Uses modprobe/rmmod for sample modules, kselftest shell exit conventions, and skip behavior for unavailable modules or missing privileges.

## Control Flow and Integration

The script attempts to load the Rust sample modules, checks command success, unloads them, and emits kselftest-style pass/skip/fail results. It is intentionally small because module loadability is the tested contract.

## State and Persistence Behavior

Temporarily changes the loaded-module set. It should leave sample modules unloaded after a successful run but can leave state behind if interrupted.

## Dependencies and Integration Points

Requires CONFIG_RUST, CONFIG_SAMPLES_RUST and sample modules such as rust_minimal and rust_print to be built as modules, plus root or CAP_SYS_MODULE access.

## Risks and Edge Cases

Fails or skips on kernels without Rust, module signing restrictions, lockdown mode, missing modules, or insufficient privilege. Module insertion can execute sample init/exit code on the host.

## Test Signals

Pass signal is successful module insertion and removal. Skip/fail output separates unsupported build configuration from actual module-loading regression.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rust/test_probe_samples.sh -->
