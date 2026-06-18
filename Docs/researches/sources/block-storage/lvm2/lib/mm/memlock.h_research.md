# File Research: sources/block-storage/lvm2/lib/mm/memlock.h

This header declares memory-lock/critical-section APIs.

Key contract:
- Inside a critical section, memory is locked.
- After leaving, memory remains locked until `memlock_unlock()`.
- `memlock_reset()` clears state after forking/polldaemon use.

APIs:
- `critical_section_inc/dec()`, `critical_section()`, `prioritized_section()`.
- `memlock_inc_daemon()`, `memlock_dec_daemon()`, `memlock_count_daemon()`.
- `memlock_init()`, `memlock_reset()`, `memlock_unlock()`.

Role:
- Used by activation and daemon paths to avoid swap-related deadlocks while devices are suspended.
