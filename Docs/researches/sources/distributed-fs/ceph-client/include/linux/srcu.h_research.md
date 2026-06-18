<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/srcu.h -->
# sources/distributed-fs/ceph-client/include/linux/srcu.h

Purpose: Defines the public Sleepable RCU API for synchronization domains whose readers may sleep. It selects tiny or tree SRCU implementations and exposes read-side, update-side, callback, polling, flavor-checking, dereference, and cleanup guard helpers.

Important APIs/types/functions: `init_srcu_struct*()`, `DEFINE_SRCU*()` from included implementations, `srcu_read_lock/unlock()`, `srcu_read_lock_fast/unlock_fast()`, `srcu_read_lock_fast_updown/unlock_fast_updown()`, `srcu_down_read/up_read()`, NMI-safe and notrace variants, `call_srcu()`, `cleanup_srcu_struct()`, `synchronize_srcu()`, `synchronize_srcu_expedited()`, `srcu_barrier()`, `get_state_synchronize_srcu()`, `start_poll_synchronize_srcu()`, `poll_state_synchronize_srcu()`, `srcu_dereference*()`, and `DEFINE_LOCK_GUARD_1(srcu*)`.

Control flow: Public read locks validate the configured reader flavor, call implementation-specific `__srcu_read_lock*()`, and annotate lockdep. Unlock paths validate cookies/pointers, release lockdep state, and call implementation-specific unlock. Update-side APIs wait for or start grace periods, and polling cookies track grace-period completion state.

State and persistence behavior: SRCU domains maintain reader counters, callback queues, grace-period sequence state, lockdep maps, and implementation-specific work/irq_work state. The read-lock return value or per-CPU counter pointer must be passed to the matching unlock.

Dependencies: Uses mutexes, RCU core APIs, workqueues, segmented callback lists, lockdep, and either `srcutiny.h` or `srcutree.h`.

Integration points: Subsystems that need sleepable read-side critical sections, notifier chains, pointer dereference checking, and callback deferral. Distributed filesystem code can use SRCU for object lifetime and mount/session state protected across blocking paths.

Risks: Mixing reader flavors on one `srcu_struct`, unlocking in the wrong context for `srcu_read_lock()`, waiting for a grace period while inside a read-side section, or using fast readers when RCU is not watching can deadlock or violate ordering.

Test signals: RCU torture tests, lockdep/prove-RCU flavor warnings, NMI-safe reader tests, callback/barrier tests, polling-cookie tests, and cleanup/init lifetime tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/srcu.h -->
