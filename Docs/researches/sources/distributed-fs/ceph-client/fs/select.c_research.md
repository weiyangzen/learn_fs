<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/select.c -->
## sources/distributed-fs/ceph-client/fs/select.c

Purpose: provides the Linux `select(2)`, `pselect(2)`, `poll(2)`, and `ppoll(2)` implementations, including timeout accounting, restart behavior, wait-queue registration, busy-poll support, and compat syscall variants.

Important APIs and types: exported helpers include `poll_initwait()`, `poll_freewait()`, `poll_select_set_timeout()`, `select_estimate_accuracy()`, and `core_sys_select()`. Internal structures include `poll_table_page`, `fd_set_bits`, `poll_list`, `sigset_argpack`, and compat equivalents. Syscall entry points are declared with `SYSCALL_DEFINE*` and `COMPAT_SYSCALL_DEFINE*`.

Control flow: `poll_initwait()` prepares a `poll_wqueues` object whose `_qproc` is `__pollwait()`. `do_select()` validates requested fd sets with `max_select_fd()`, then loops over fd bits, calls `vfs_poll()`, records ready bits, optionally busy loops for network sockets, and sleeps through `poll_schedule_timeout()` until events, timeout, signal, or allocation error. `core_sys_select()` copies user fd sets into six bitmaps, invokes `do_select()`, and copies result sets back. `do_sys_poll()` copies `pollfd` arrays into a stack/page linked list, calls `do_poll()`, and writes `revents` back.

State and persistence: state is per syscall. Wait-queue entries hold file references and are freed by `poll_freewait()`. Timeout state is absolute `timespec64` plus syscall restart metadata in `current->restart_block` for `poll`. Signal-mask changes for `pselect` and `ppoll` are restored in `poll_select_finish()`.

Dependencies and integration: integrates with file descriptor tables under RCU, `vfs_poll()` implementations, wait queues, hrtimers, scheduler/freezer state, signal mask helpers, compat bitmap conversion, `copy_from_user()`/`copy_to_user()`, and `net_busy_loop` hooks.

Risks: concurrency depends on barriers between `pollwake()` and `poll_schedule_timeout()`; changing those paths can reintroduce lost wakeups. Large fd sets can allocate substantial memory, and compat select uses a parallel implementation that can drift. Timeout update behavior is ABI-sensitive, including `STICKY_TIMEOUTS`, read-only timeout pointers, and restart conversion from `-ERESTARTNOHAND`.

Test signals: exercise zero, finite, and infinite timeouts; signal interruptions and restart paths; invalid fd detection; high `nfds` with page-backed `poll_list`; compat 32-bit select/poll; pselect/ppoll mask restore; busy-poll sockets; writable timeout faults; and driver poll callbacks that return event masks before or after wait registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/select.c -->
