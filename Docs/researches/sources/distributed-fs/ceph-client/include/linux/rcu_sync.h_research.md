# sources/distributed-fs/ceph-client/include/linux/rcu_sync.h

Purpose: declares lightweight infrastructure that lets readers use a fast path while updaters temporarily force a grace-period-synchronized slow path.

Important APIs and types: `struct rcu_sync` stores `gp_state`, nested updater `gp_count`, a wait queue, and an RCU callback head. `rcu_sync_is_idle()` tells RCU read-side callers whether fast paths are permitted. Lifecycle APIs are `rcu_sync_init()`, `rcu_sync_enter()`, `rcu_sync_exit()`, and `rcu_sync_dtor()`. `DEFINE_RCU_SYNC()` provides static initialization.

Control flow: readers check `rcu_sync_is_idle()` inside an RCU read-side critical section. Updaters call `rcu_sync_enter()` to transition state and wait for prior fast-path readers to drain, perform update-sensitive work, and call `rcu_sync_exit()` to eventually return to idle after grace-period handling.

State and persistence: state is runtime synchronization state in `struct rcu_sync`. No persistence exists.

Dependencies and integration points: depends on wait queues and RCU primitives. It integrates subsystems needing temporary writer exclusion from reader fast paths without permanently forcing heavy locking.

Risks and test signals: risks include calling `rcu_sync_is_idle()` outside RCU read-side protection, unbalanced enter/exit, teardown while callbacks are pending, and state races around nested updaters. Test lockdep warnings, nested enter/exit, concurrent readers/updaters, destructor after active use, and stress with expedited/normal grace periods.
