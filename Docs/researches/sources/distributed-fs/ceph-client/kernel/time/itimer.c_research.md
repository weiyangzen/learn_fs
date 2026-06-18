# sources/distributed-fs/ceph-client/kernel/time/itimer.c

Purpose: implements legacy interval timer syscalls `getitimer`, `setitimer`, optional `alarm`, and compat variants for `ITIMER_REAL`, `ITIMER_VIRTUAL`, and `ITIMER_PROF`.

Important APIs and flow: `do_getitimer()` returns remaining real hrtimer time or process CPU timer state. `do_setitimer()` cancels/rearms the real hrtimer under `sighand->siglock`, or delegates CPU timers to `set_process_cpu_timer()`. `it_real_fn()` sends `SIGALRM` to the thread-group leader and deliberately does not restart; `posixtimer_rearm_itimer()` rearms periodic real timers from signal delivery to avoid tiny-period high-res DoS patterns. User ABI helpers convert old `itimerval`/compat timeval layouts into `itimerspec64`.

State and persistence: uses `current->signal->real_timer`, `it_real_incr`, and `signal->it[]` CPU timer fields. Old timer values can be returned atomically during set. SELinux builds expose `clear_itimer()` to zero all three timers.

Dependencies and integration: hrtimer core, process CPU timers, signal delivery, syscall/compat layers, uaccess, timer tracepoints, and architecture opt-in for `sys_alarm`.

Risks and test signals: races around concurrent real-timer expiry and cancellation are handled with retry and `hrtimer_cancel_wait_running()`. Tests should cover invalid `which`, timeval validation, NULL new-value legacy warning, compat ABI, real timer signal delivery/rearm, CPU virtual/prof accounting, old-value return, and second rounding in `alarm()`.
