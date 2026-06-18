# sources/distributed-fs/ceph-client/arch/s390/mm/cmm.c

## Purpose
Implements s390 Collaborative Memory Management, allowing the guest to voluntarily allocate and donate pages to the hypervisor and later release them, with sysctl and optional IUCV SMSG control.

## Important APIs, Types, And Functions
`struct cmm_page_array` stores donated page addresses in linked page arrays. Global counters/targets track permanent and timed pages plus timeout settings. Core helpers are `cmm_alloc_pages()`, `cmm_free_pages()`, `cmm_oom_notify()`, `cmm_thread()`, `cmm_set_timer()`, `cmm_timer_fn()`, sysctl handlers for `cmm_pages`, `cmm_timed_pages`, and `cmm_timeout`, optional `cmm_smsg_target()`, `cmm_init()`, and `cmm_exit()`.

## Control Flow And State
Initialization registers `/proc/sys/vm` controls, optional SMSG callback, OOM notifier, and the `cmmthread`. The thread sleeps until target counters differ from actual counters, then allocates or frees one page per wake cycle for each class. Allocated pages are passed to the hypervisor with `diag10_range()` and retained in linked arrays under `cmm_lock`. Timed pages are decremented periodically by `cmm_timer_fn()` according to timeout settings. OOM notification frees up to 256 timed pages first, then regular CMM pages, and resets targets to actual counts.

## Dependencies And Integration
Depends on s390 DIAG 10, sysctl, module parameters, kthreads, timers, OOM notifier, page allocator, optional IUCV SMSG, string helpers, and usercopy-like sysctl buffers.

## Risks And Test Signals
Risks include target counters declared `volatile` rather than fully synchronized, sysctl buffer parsing edge cases, timer/thread races during exit, OOM notifier freeing under pressure, page-array metadata allocation failure, and sender authorization for SMSG control. Signals include CMM module load/unload, sysctl read/write behavior, SMSG SHRINK/RELEASE/REUSE commands, OOM stress, timer expiry, and hypervisor memory balloon accounting.
