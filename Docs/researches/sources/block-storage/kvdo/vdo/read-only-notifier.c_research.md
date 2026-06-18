# File Research: sources/block-storage/kvdo/vdo/read-only-notifier.c

Read completely: 563 lines.

This file implements VDO-wide read-only mode notification across base threads. The notifier records the first unrecoverable error, propagates per-thread `is_read_only` state, calls registered thread-local listeners, and supports admin-thread barriers that temporarily disallow read-only entry while shutdown or superblock updates need to avoid races.

The core state machine uses atomics with states `MAY_NOTIFY`, `NOTIFYING`, `MAY_NOT_NOTIFY`, and `NOTIFIED`, plus `read_only_error`. `vdo_enter_read_only_mode()` marks the calling thread read-only, records the first error with compare-exchange, and starts notification if notifications are allowed. `make_thread_read_only()` walks all configured threads, skips the dedupe thread, marks each thread read-only, and invokes registered listeners sequentially on the target thread. Completion returns to the admin thread through `finish_entering_read_only_mode()`.

`vdo_wait_until_not_entering_read_only_mode()` is an admin-thread barrier that waits for in-progress notifications and switches the state to disallow new ones. `vdo_allow_read_only_mode_entry()` re-enables notification and starts a pending notification if an error arrived while notification was disallowed. `vdo_register_read_only_listener()` registers listener callbacks per thread and rejects dedupe-thread listeners.

Dependencies: VDO completion framework, thread configuration, callback thread IDs, atomic operations and memory barriers, logger, allocation wrappers, and `struct vdo`.

Security/reliability notes: correctness depends on admin-thread-only calls for wait/allow paths and on per-thread access discipline for `thread_data`. The code deliberately has non-simultaneous read-only visibility across threads. Listener registration is singly linked and not synchronized; it is intended for setup-time use.
