# sources/distributed-fs/ceph-client/kernel/rseq.c

## Purpose
`rseq.c` implements the restartable sequences syscall and kernel slow paths. Rseq lets user space execute short per-CPU critical sections without heavyweight atomics, with the kernel aborting the sequence on migration, preemption, or signal delivery by fixing the user instruction pointer to an abort address. This file also provides debugfs controls/statistics and, when configured, time-slice extension support for rseq v2.

## Important APIs, Types, And Functions
Key exported or externally used entry points are `SYSCALL_DEFINE4(rseq)`, `__rseq_handle_slowpath()`, `__rseq_signal_deliver()`, `__rseq_debug_syscall_return()`, trace helpers `__rseq_trace_update()` and `__rseq_trace_ip_fixup()`, optional `rseq_syscall_enter_work()`, `rseq_slice_extension_prctl()`, and `SYSCALL_DEFINE0(rseq_slice_yield)`. Important internal helpers include `rseq_register()`, `rseq_unregister()`, `rseq_reregister()`, `rseq_length_valid()`, `rseq_handle_cs()`, `rseq_slowpath_update_usr()`, and `rseq_reset_ids()`. Optional statistics use per-CPU `struct rseq_stats` and debugfs files under `rseq/`.

## Control Flow
Registration validates user memory, structure size, and alignment; determines ABI version; initializes user fields such as `rseq_cs`, `flags`, `cpu_id_start`, `cpu_id`, `node_id`, and `mm_cid`; then records the userspace pointer, length, signature, and event version in `current->rseq`. Unregistration verifies pointer, length, flags, and signature, resets user IDs, then clears task rseq state. Re-registration of the same area returns `-EBUSY`; mismatches return `-EINVAL` or `-EPERM`.

On return-to-user slow paths, `rseq_slowpath_update_usr()` reads and clears scheduler event state with interrupts disabled, samples CPU/MMCID IDs, and updates user ABI fields or sends `SIGSEGV` on unrecoverable faults. Signal delivery calls `rseq_handle_cs()` to abort any active critical section before the signal handler IP is used. Debug syscall-return validation detects syscalls issued inside a critical section and kills the task under debug policy.

The optional slice extension path uses per-CPU hrtimers to bound granted extensions, syscall work to revoke grants on kernel entry, prctl controls to enable/disable per task, and debugfs to tune the nanosecond grant window.

## State And Persistence
Per-task state lives in `task_struct::rseq`, including the registered userspace pointer, ABI length, signature, event flags, and optional slice state. User-visible state is written into the registered TLS `struct rseq`. Per-CPU stats are volatile and exposed through debugfs. Static keys control debug and slice-extension availability. Boot parameters `rseq_debug=` and `rseq_slice_ext=` set initial feature behavior.

## Dependencies And Integration Points
The file integrates with scheduler migration/preemption events, signal delivery, syscall entry/exit work, tracepoints, debugfs, hrtimers, prctl, `uaccess` helpers, `task_mm_cid()`, `cpu_to_node()`, and architecture `pt_regs` IP manipulation through rseq API helpers declared in headers. User-space ABI compatibility depends on ELF auxiliary vector feature/align values and libc registration behavior.

## Risks
The highest-risk areas are user memory access fault handling, ABI-size/version compatibility, alignment validation, clearing or preserving event bits correctly, and avoiding stale critical-section state on signal or syscall transitions. Slice extension adds latency-sensitive timer and rescheduling behavior; incorrect revocation can either overrun scheduling latency or falsely abort user sequences. Debug and stats paths must not perturb hot exit-to-user paths excessively.

## Test Signals
Relevant tests include rseq selftests for registration, unregister, migration aborts, signal aborts, mm_cid/node/cpu ID updates, and critical-section IP fixups. Debugfs stats should increment in expected paths when `CONFIG_RSEQ_STATS` is enabled. Slice-extension tests should cover prctl enable/disable, `rseq_slice_yield`, syscall aborts, expiration, and disabled static-key behavior.
