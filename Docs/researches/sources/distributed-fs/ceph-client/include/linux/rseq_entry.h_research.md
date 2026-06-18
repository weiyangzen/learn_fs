# sources/distributed-fs/ceph-client/include/linux/rseq_entry.h

## Purpose
`rseq_entry.h` implements the fast and slow exit-to-user mechanics for restartable sequences, including statistics, tracepoints, critical-section validation/fixup, CPU/node/MM-CID updates, and optional time-slice extensions.

## Important APIs, types, and functions
Key elements include `struct rseq_stats`, `rseq_stat_inc()`, `rseq_trace_update()`, `rseq_trace_ip_fixup()`, `rseq_slice_extension_enabled()`, `rseq_arm_slice_extension_timer()`, `rseq_slice_clear_grant()`, `rseq_slice_clear_user()`, `rseq_grant_slice_extension()`, `rseq_note_user_irq_entry()`, `rseq_debug_update_user_cs()`, `rseq_update_user_cs()`, `rseq_set_ids_get_csaddr()`, `rseq_update_usr()`, `rseq_exit_user_update()`, `rseq_exit_to_user_mode_restart()`, `rseq_syscall_exit_to_user_mode()`, `rseq_irqentry_exit_to_user_mode()`, and `rseq_debug_syscall_return()`.

## Control flow, state, and persistence
Exit-to-user checks rseq event bits, writes CPU ID, node ID, and MM CID into the registered user `struct rseq`, reads `rseq_cs`, and either clears it or redirects the user instruction pointer to the abort IP if the interrupted IP is inside the critical section. Debug mode validates descriptor range, overflow, header fields, abort signature, and user-interrupt origin more strictly. Slice-extension code can grant a brief delay by updating user `slice_ctrl`, clearing resched state under IRQ protection, and arming a timer. Per-CPU stats and tracepoints record paths; per-task state is in `current->rseq`.

## Dependencies and integration points
It depends on generic entry, hrtimer rearm, jump labels, scheduler signal state, uaccess unsafe access regions, tracepoints, pagefault disabling, TIF bits, `task_cpu()`, `task_mm_cid()`, NUMA node lookup, and optional `CONFIG_RSEQ_STATS`, `CONFIG_RSEQ_SLICE_EXTENSION`, and `CONFIG_TRACEPOINTS`.

## Risks and test signals
Risks are high because this code runs in exit paths with interrupts/page faults constrained. Hazards include user pointer faults, bad abort IP signatures enabling control-flow attacks, memory-order bugs against GUP or reschedule IPIs, stale `user_irq` state, missed timer arming, and ABI V2 slice fields overwriting legacy users. Test signals include rseq selftests for signal/preemption aborts, debug-mode invalid descriptor death, forced user faults, tracepoint firing, stats increments, generic-entry fast-path loops, slice-extension grant/revoke/yield behavior, and lockdep/pagefault assertions.
