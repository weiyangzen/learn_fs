# sources/distributed-fs/ceph-client/kernel/printk/nbcon.c

## Purpose

`nbcon.c` implements non-blocking console printing for consoles that do not rely on the legacy `console_lock` as their primary serialization mechanism. It provides atomic ownership transfer, per-console sequence tracking, emergency and panic priority handling, threaded printing, legacy-loop compatibility, and driver-facing helpers for marking unsafe hardware regions.

## Important state and APIs

Each nbcon console stores an atomic `nbcon_state` with owner priority, owner CPU, requested handover priority, unsafe state, and permanent unsafe-takeover state. Per-console sequence fields track the next ringbuffer record to print and the previous sequence used to detect replay. Global state includes `nbcon_cpu_emergency_cnt`, per-CPU emergency nesting, `panic_nbcon_pbufs`, and `panic_nbcon_allow_unsafe_takeover`.

Key functions include `nbcon_seq_read()`, `nbcon_seq_force()`, `nbcon_can_proceed()`, `nbcon_enter_unsafe()`, `nbcon_exit_unsafe()`, `nbcon_reacquire_nobuf()`, `nbcon_legacy_emit_next_record()`, `nbcon_atomic_flush_pending()`, `nbcon_atomic_flush_unsafe()`, `nbcon_cpu_emergency_enter()`, `nbcon_cpu_emergency_exit()`, `nbcon_alloc()`, `nbcon_free()`, `nbcon_device_try_acquire()`, `nbcon_device_release()`, `nbcon_kdb_try_acquire()`, and `nbcon_kdb_release()`.

## Ownership control flow

Acquisition tries three paths. Direct acquire succeeds if the console is unlocked or owned by a lower priority context while safe. Friendly handover sets `req_prio`, waits for the lower priority owner to leave its unsafe region, then takes ownership. Hostile takeover is panic-only and marks `unsafe_takeover` when the panic CPU must print despite unsafe state. Release clears owner priority but preserves permanent unsafe status after hostile takeover. `nbcon_context_can_proceed()` is the central checkpoint and releases ownership at safe points when a higher priority waiter exists.

## Printing flow

`nbcon_emit_one()` optionally takes the console's driver lock for thread context, acquires nbcon ownership, and calls `nbcon_emit_next_record()`. That function enters unsafe state to read and format the next printk record, accounts dropped messages, prepends replay notices when a takeover reprints a sequence, leaves unsafe state for the actual driver callback, calls `write_atomic()` or `write_thread()`, then re-enters unsafe state to update dropped count and sequence. If ownership is lost at any point, the higher priority owner becomes responsible for pending records.

## Threading, panic, and emergency behavior

`nbcon_kthread_func()` waits on `con->rcuwait`, suppresses normal threaded output while any CPU is in emergency or panic, holds SRCU across console usability checks and output, and loops while backlog remains. `nbcon_kthreads_wake()` queues per-console irq_work only when threads are actually waiting. Emergency nesting disables preemption and increments global and per-CPU counters; exiting wakes kthreads when the last emergency context leaves and offload is available. Panic priority suppresses non-panic CPUs and can enable unsafe takeover for final flushing.

## Dependencies and integration

The file depends on `printk_ringbuffer` helpers, `printk_get_next_message()`, console SRCU list access, console driver callbacks (`write_thread`, optional `write_atomic`, `device_lock`, `device_unlock`), irq_work, rcuwait, kthreads, panic/KDB helpers, and policy state from `internal.h`. `printk.c` calls nbcon allocation during registration, freeing during unregister, atomic flushes during printk and panic, and kthread wakeups during deferred output.

## Risks and test signals

Atomic state transitions are subtle. Incorrect owner CPU, priority, or unsafe-bit handling can allow duplicate hardware access or missed panic output. Hostile takeover must remain panic-only. Threaded writes require driver locking and migration constraints. Tests should cover registration callback validation, threaded printing, atomic flushing, dropped-message accounting, replay after takeover, emergency nesting, panic flush with unsafe takeover, KDB acquire/release, device acquire/release, mixed boot and nbcon consoles, and PREEMPT_RT interactions.
