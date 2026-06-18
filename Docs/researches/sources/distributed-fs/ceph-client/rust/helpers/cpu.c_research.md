# sources/distributed-fs/ceph-client/rust/helpers/cpu.c

## Purpose
Exposes raw CPU id lookup to Rust.

## APIs, Types, and Functions
`rust_helper_raw_smp_processor_id()` wraps `raw_smp_processor_id()`.

## Control Flow, State, and Persistence
No local state; result depends on current execution CPU and preemption context.

## Dependencies and Integration
Depends on `linux/smp.h` and Rust per-CPU or scheduler-sensitive code.

## Risks and Test Signals
Risks are use in preemptible contexts where raw CPU id is unstable. Test signals include lockdep/preemption debug coverage and Rust per-CPU tests.
