# sources/distributed-fs/ceph-client/rust/helpers/mm.c

## Purpose
Exposes memory-management reference and mmap-lock helpers to Rust.

## APIs, Types, and Functions
APIs include `mmgrab`, `mmdrop`, `mmget`, `mmget_not_zero`, `mmap_read_lock`, `mmap_read_trylock`, `mmap_read_unlock`, `vma_lookup`, and `vma_end_read`.

## Control Flow, State, and Persistence
State is in `mm_struct` reference counts and mmap/VMA lock/read-side state. Helpers keep no local state.

## Dependencies and Integration
Depends on `linux/mm.h`, `linux/sched/mm.h`, and Rust process/mm abstractions.

## Risks and Test Signals
Risks include refcount leaks, locking imbalance, VMA pointer lifetime after unlock, and task-exit races. Test signals are Rust mm wrapper tests, lockdep, and process exit/mmap stress.
