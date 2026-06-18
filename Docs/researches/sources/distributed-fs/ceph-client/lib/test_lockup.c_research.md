
# sources/distributed-fs/ceph-client/lib/test_lockup.c

## Purpose

This module intentionally generates lockups, stalls, sleeps, and lock contention patterns for watchdog and scheduler testing. It is controlled entirely by module parameters and returns `-EAGAIN` after a normal run so it does not remain loaded.

## Important APIs, Types, And Functions

Parameters control active wait time, cooldown, iterations, CPU fan-out, sleep state, hrtimer use, iowait accounting, lock mode, watchdog touching, `cond_resched()`, IRQ/BH/preempt/RCU locking, arbitrary lock pointers, page allocation under locks, and file-derived locks. `test_lock()` acquires configured locks or disables contexts. `test_unlock()` reverses them. `test_wait()` busy-waits for `TASK_RUNNING` or schedules in the selected sleep state. `test_lockup()` performs the configured iterations and optional page allocation/reallocation.

## Control Flow And State

Init records `main_task`, parses the `state` parameter, validates unsafe lock pointers with `get_kernel_nofault()` and optional debug magic checks, rejects combinations that would sleep in atomic context, optionally opens `file_path` to derive inode/mapping/superblock semaphores, then either runs on the current CPU or queues per-CPU work on `system_highpri_wq` for all online CPUs. It reports timing, maximum lock wait, page allocation failures, and final duration before returning `-EAGAIN` or `-EINTR`.

## State And Persistence

Persistent state is limited to module parameter globals, atomic counters, `main_task`, optional `test_file`, and per-CPU work structs during init. Any allocated pages are held only across test iterations and freed before exit from `test_lockup()`.

## Dependencies And Integration Points

It depends on scheduler, delay, CPU hotplug read locking, workqueues, watchdog APIs, MM locks, uaccess nofault helpers, files/inodes/superblocks, and module parameters. It integrates with watchdog and lockup selftests through controlled module insertion.

## Risks And Test Signals

This module can deliberately hang CPUs, disable interrupts/preemption, take arbitrary kernel locks by address, and allocate memory under locks. It has guards against invalid pointers and sleeping in atomic context, but it should only be run in controlled test environments. Signals include `START`/`FINISH` logs, per-CPU start/finish logs, max lock wait, allocation failure count, watchdog reports, RCU stall reports, and `-EAGAIN` for a completed test.
