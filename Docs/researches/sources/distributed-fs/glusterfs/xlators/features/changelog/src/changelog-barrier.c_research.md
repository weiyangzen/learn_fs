# sources/distributed-fs/glusterfs/xlators/features/changelog/src/changelog-barrier.c

## Purpose
Implements the changelog barrier queue used during snapshot-related explicit rollover. It temporarily queues FOP call stubs, disables the barrier on timeout or cleanup, and resumes queued calls.

## APIs, Types, and Functions
Exports `__chlog_barrier_enqueue()`, `__chlog_barrier_dequeue()`, `chlog_barrier_dequeue_all()`, `chlog_barrier_timeout()`, `__chlog_barrier_disable()`, and `__chlog_barrier_enable()`. It operates on `changelog_priv_t::queue`, `queue_size`, `barrier_enabled`, and `timer`.

## Control Flow, State, and Persistence
When barriering is enabled, FOP stubs are appended to `priv->queue`. Disabling cancels the timer, splices the queue into a caller-provided list, resets queue size, clears the enabled flag, and resumes every stub outside the lock. Enabling installs a Gluster timer with `priv->timeout`; timeout callback logs an error, disables the barrier under `priv->lock`, and drains the queue. No on-disk state is written.

## Dependencies and Integration
Depends on `call-stub.h`, Gluster timers, `changelog-helpers.h`, and message IDs. It is called from barrier/reconfigure paths in the main changelog translator and from `changelog_barrier_cleanup()` in `changelog-helpers.c`.

## Risks and Test Signals
Risks include timer cancellation races, queue resume ordering under failure, queue-size consistency, and ensuring stubs are never resumed while still protected by `priv->lock`. Test signals should cover enable failure, timeout disable, explicit cleanup, empty queue disable, and all queued FOPs resuming once.
