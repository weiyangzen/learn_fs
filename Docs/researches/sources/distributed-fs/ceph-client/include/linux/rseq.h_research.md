# sources/distributed-fs/ceph-client/include/linux/rseq.h

## Purpose
`rseq.h` provides the scheduler, signal, exec/fork, and virtualization hooks for restartable sequences.

## Important APIs, types, and functions
Important APIs are `rseq_v2()`, `rseq_handle_slowpath()`, `rseq_signal_deliver()`, `rseq_raise_notify_resume()`, `rseq_sched_switch_event()`, `rseq_sched_set_ids_changed()`, `rseq_force_update()`, `rseq_virt_userspace_exit()`, `rseq_reset()`, `rseq_execve()`, `rseq_fork()`, `rseq_alloc_align()`, `rseq_syscall()`, `rseq_syscall_enter_work()`, and `rseq_slice_extension_prctl()`. It declares slow-path implementations such as `__rseq_handle_slowpath()` and `__rseq_signal_deliver()`.

## Control flow, state, and persistence
On context switch or CPU/MM CID change, scheduler code marks `task_struct::rseq.event` and raises `TIF_RSEQ`/notify-resume so exit-to-user updates the user TLS rseq area or aborts an active critical section. Signal delivery invokes rseq fixup before switching register context. `rseq_reset()` clears per-task rseq state under IRQ protection; exec always resets, while fork inherits for separate address spaces and resets for `CLONE_VM`. State persists per task in `task_struct::rseq` until unregister, exec, or clone rules clear it.

## Dependencies and integration points
It depends on `CONFIG_RSEQ`, scheduler task state, UAPI `struct rseq`, generic entry/TIF bits, signal delivery, KVM guest-mode exits, debug RSEQ, and optional slice-extension prctl/syscall hooks.

## Risks and test signals
Risks include lost notify-resume bits on architectures without generic TIF bits, incorrect ABI V1/V2 distinctions, inherited rseq state across clone modes, user TLS faults on exit paths, and virtualization paths clearing notify work too early. Test signals include rseq selftests for registration, fork/clone/exec, signal aborts, CPU migration ID updates, KVM guest-mode return, debug syscall tracing, and disabled-config stubs.
