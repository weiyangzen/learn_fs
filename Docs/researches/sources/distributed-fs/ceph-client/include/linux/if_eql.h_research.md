# `sources/distributed-fs/ceph-client/include/linux/if_eql.h`

Purpose: internal structures for the legacy EQL serial-line equalizer/load-balancer driver.

Important APIs/types/functions: `slave_t`, `slave_queue_t`, and `equalizer_t` track member devices, priority/byte accounting, a spinlock-protected slave list, min/max slave counts, and a timer.

Control flow and state: no functions are defined here; state is persistent in the equalizer device private structures and updated by the EQL driver.

Dependencies/integration: depends on timers, spinlocks, netdevice trackers, and UAPI `if_eql.h`.

Risks: legacy code with shared mutable lists and timers; netdevice reference tracking must be balanced; priority and byte counters use `long`, so overflow/sign assumptions matter on old platforms.

Test signals: EQL device add/remove, slave attach/detach, timer-driven balancing, device unregister cleanup, and lockdep coverage around queue list operations.
