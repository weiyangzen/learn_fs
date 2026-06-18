# sources/distributed-fs/ceph-client/kernel/bpf/task_iter.c

## Purpose

`task_iter.c` implements BPF iterator targets for tasks, task files, and task VMAs, plus kfunc iterator objects for task lists, cgroup tasks, and per-VMA traversal. These APIs let BPF programs walk kernel task-related state through `seq_file`-backed BPF iterators or verifier-recognized kfunc iterator patterns.

## Important APIs, Types, And Functions

- Seq iterator private state: `bpf_iter_seq_task_common`, `bpf_iter_seq_task_info`, `bpf_iter_seq_task_file_info`, and `bpf_iter_seq_task_vma_info`.
- Task traversal: `task_seq_get_next()` handles all tasks, one TID, or one thread group; `task_group_seq_get_next()` walks threads in a TGID.
- Seq targets: `task_seq_ops`, `task_file_seq_ops`, and `task_vma_seq_ops` run BPF iterator programs with contexts `bpf_iter__task`, `bpf_iter__task_file`, and `bpf_iter__task_vma`.
- Attach parsing: `bpf_iter_attach_task()` accepts at most one of `tid`, `pid`, or `pid_fd` and records iterator type/pid in aux info.
- Registration metadata: `task_reg_info`, `task_file_reg_info`, and `task_vma_reg_info` declare target names, BTF context argument IDs, resched support, seq private sizes, fdinfo, and link-info fill behavior.
- VMA helper: `bpf_find_vma()` invokes a BPF callback for a task VMA containing a requested address under a trylocked mmap read lock.
- Kfunc iterators: `bpf_iter_task_vma_new/next/destroy()`, `bpf_iter_css_task_new/next/destroy()`, and `bpf_iter_task_new/next/destroy()` expose verifier-managed iteration objects.
- Init: `task_iter_init()` initializes per-CPU mmap unlock irq work, fills BTF IDs, and registers the three seq iterator targets.

## Control Flow

For seq iterators, `BPF_ITER_CREATE` opens a link-backed iterator FD through the generic iterator layer. The seq start/next callbacks call task/file/VMA find functions, store enough cursor state to resume after user-space reads, and pass the current kernel object to `bpf_iter_run_prog()`. Stop callbacks either emit the final in-stop event or release held task/file/mm/mmap-lock references.

Task-file iteration walks each selected task while skipping threads that share file tables when requested, then uses `fget_task_next()` to acquire each file. Task-VMA iteration obtains an mm with `get_task_mm()`, takes `mmap_read_lock_killable()`, finds VMAs, and drops/reacquires the lock when contended, using previous VMA boundaries to avoid duplicating or skipping ranges after relock.

The VMA kfunc iterator is separate from seq iteration. It allocates opaque kernel data from `bpf_global_ma`, safely grabs a task and mm reference with `spin_trylock(&task->alloc_lock)`, locates VMAs through an RCU maple-tree walk followed by `lock_vma_under_rcu()`, returns a snapshot copy, and releases `vm_file`, task, and mm state in destroy.

## State And Persistence Behavior

Seq iterator state persists per open iterator file in seq private memory. It stores pid namespace references, task type/pid cursors, current task/file/fd, current mm/VMA, and previous VMA range. References are acquired only while needed and released on stop/next/fini. Kfunc iterator state is explicit BPF-side opaque storage backed by kernel allocations or embedded cursor fields and must be destroyed by the BPF program.

`DEFINE_PER_CPU(struct mmap_unlock_irq_work, mmap_unlock_work)` supports deferred mmap unlock mechanics used by `bpf_find_vma()` and initialized once at late init.

## Dependencies And Integration Points

The file integrates with the BPF iterator core, BTF ID infrastructure, pid namespaces, pidfd lookup, task and file reference helpers, mm/VMA locking, maple tree VMA iteration, cgroup task iterators, BPF memory allocator, and `mmap_unlock_work.h`. `syscall.c` reaches these targets through tracing program attach and iterator FD creation.

## Risks And Edge Cases

Reference and lock balance is the main risk. Seq stop paths must drop `task_struct`, `file`, `mm_struct`, and mmap locks exactly once, including final stop callbacks. VMA iteration must tolerate concurrent VMA mutation, lock contention, task exit, kernel threads with no mm, and user-space reads that split output buffers. The kfunc VMA iterator rejects IRQ-disabled contexts to avoid deadlocks and can return `-EBUSY` if it cannot safely lock task/mm state.

Iterator filtering also has correctness edges: only one of `tid`, `pid`, and `pid_fd` is allowed; TGID iteration must avoid duplicate shared files; pid namespace translation is captured at iterator creation.

## Test Signals

High-value tests include BPF iterator selftests for `task`, `task_file`, and `task_vma` over all tasks, one TID, one TGID, and pidfd selection; tests that force small seq read buffers to exercise resume paths; task exit during iteration; threads sharing files; VMA churn and mmap lock contention; `bpf_find_vma()` success, miss, invalid flags, no-mm, and busy paths; and verifier/kfunc tests requiring new/next/destroy pairing for task, css-task, and VMA iterators.
