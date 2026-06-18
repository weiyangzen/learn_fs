# sources/distributed-fs/ceph-client/rust/helpers/pid_namespace.c

## Purpose
Exposes PID namespace reference helpers and safe task-to-PID-namespace acquisition to Rust.

## APIs, Types, and Functions
APIs are `get_pid_ns`, `put_pid_ns`, and `task_get_pid_ns()`, the latter using an RCU guard around `task_active_pid_ns()` and taking a reference before returning.

## Control Flow, State, and Persistence
Persistent state is PID namespace refcounts. The helper itself has transient RCU read-side state only.

## Dependencies and Integration
Depends on `linux/pid_namespace.h`, `linux/cleanup.h`, RCU, and Rust task/namespace wrappers.

## Risks and Test Signals
Risks include refcount leaks, null namespace handling, and task lifetime assumptions. Test signals are namespace creation/destruction tests, task exit races, and RCU debug coverage.
