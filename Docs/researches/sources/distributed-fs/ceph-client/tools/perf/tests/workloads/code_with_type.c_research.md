# sources/distributed-fs/ceph-client/tools/perf/tests/workloads/code_with_type.c

## Purpose
This C workload wraps a Rust function to provide a bounded runtime and signal handling for perf data type profiling tests that need mixed C/Rust code and discoverable Rust data types.

## Important APIs, Types, And Functions
The exported dependency is `extern void test_rs(uint count)`, implemented in `code_with_type.rs`. The workload entry is `code_with_type()`, registered with `DEFINE_WORKLOAD(code_with_type)`. It uses `pthread_setname_np()`, `signal()`, `alarm()`, `atoi()`, and a `volatile sig_atomic_t done` flag.

## Control Flow
The workload sets the thread name, parses optional seconds and loop count arguments, installs SIGINT and SIGALRM handlers, arms an alarm, and repeatedly calls `test_rs(num_loops)` until `done` is set. Signal handling remains in C because the Rust standard library path here intentionally avoids external signal-management crates.

## State, Dependencies, And Integration
State is only the `done` flag. Integration requires the Rust object defining `test_rs()` to be linked with the perf workload binary. The named thread and bounded alarm help perf tests identify and constrain samples.

## Risks And Test Signals
Risks include link failures if Rust support or the companion object is unavailable, and optimized Rust code that changes profile shape. Downstream tests should observe Rust function/type information while the process exits cleanly after the requested duration.
