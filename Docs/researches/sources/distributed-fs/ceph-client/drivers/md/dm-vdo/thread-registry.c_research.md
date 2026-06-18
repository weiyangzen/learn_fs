# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/thread-registry.c

## Purpose
`thread-registry.c` implements a small RCU-protected registry that associates the current `task_struct` with an arbitrary pointer.

## Important APIs, Types, And Functions
`vdo_initialize_thread_registry()` initializes list and spinlock. `vdo_register_thread()` adds the current task and pointer, replacing and warning on an existing current-task entry. `vdo_unregister_thread()` removes the current task and warns if not found. `vdo_lookup_thread()` performs an RCU read-side search and returns the associated pointer or `NULL`.

## Control Flow
Mutations take `registry->lock`, walk the list, delete existing entries with `list_del_rcu()`, add new entries with `list_add_tail_rcu()`, and call `synchronize_rcu()` before reinitializing removed links. Lookup runs under `rcu_read_lock()` and uses `list_for_each_entry_rcu()`.

## State And Persistence
All state is runtime-only: a list of `registered_thread` nodes keyed by `current`. The registry does not allocate nodes; callers own node and pointer lifetime.

## Dependencies And Integration Points
The implementation uses Linux RCU lists, spinlocks, `current`, and VDO assertion logging. It underpins higher-level registries such as thread-device and allocation-thread tracking.

## Risks
Calling logging or complex code while holding the spinlock is intentionally avoided. Caller-owned storage makes lifetime discipline critical. Duplicate registration is tolerated by replacement but logged as an assertion failure, which can hide a lifecycle bug if ignored.

## Test Signals
Tests should cover concurrent lookup during register/unregister, duplicate registration, unregister missing entry, pointer retrieval, and RCU grace-period behavior before node reuse.
