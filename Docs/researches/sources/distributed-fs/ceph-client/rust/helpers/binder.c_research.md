# sources/distributed-fs/ceph-client/rust/helpers/binder.c

## Purpose
Exposes list-LRU and task-work helpers used by Rust Android Binder support.

## APIs, Types, and Functions
APIs are `rust_helper_list_lru_count()`, `rust_helper_list_lru_walk()`, and `rust_helper_init_task_work()`.

## Control Flow, State, and Persistence
State lives in caller-provided `list_lru` and `callback_head` objects; the helpers count, walk, or initialize them through the C APIs.

## Dependencies and Integration
Depends on `linux/list_lru.h`, `linux/task_work.h`, and Binder Rust integration gated elsewhere by configuration.

## Risks and Test Signals
Risks include callback ABI mismatch for LRU isolation, walking under wrong locks, and task-work lifetime errors. Test signals are Binder Rust tests, list_lru shrinker exercise, and task-work cancellation/exit races.
