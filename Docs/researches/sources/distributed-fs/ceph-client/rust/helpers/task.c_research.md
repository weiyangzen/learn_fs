# sources/distributed-fs/ceph-client/rust/helpers/task.c

## Purpose
Exposes current task, task reference, UID, namespace, and rescheduling helpers to Rust.

## APIs, Types, and Functions
APIs include `might_resched`, `get_current`, `get_task_struct`, `put_task_struct`, task uid/euid, optional `from_kuid`, `uid_eq`, `current_euid`, `current_user_ns`, and `task_tgid_nr_ns`.

## Control Flow, State, and Persistence
State is task refcounts and task credential/namespace data; helpers read or adjust references and keep no local state.

## Dependencies and Integration
Depends on `linux/kernel.h`, `linux/sched/task.h`, credentials, user namespaces, PID namespaces, and Rust task abstractions.

## Risks and Test Signals
Risks include task lifetime leaks, user namespace config differences, stale credential reads, and calling `might_resched` in invalid contexts. Test signals are Rust task wrapper tests, namespace config builds, and scheduler debug coverage.
