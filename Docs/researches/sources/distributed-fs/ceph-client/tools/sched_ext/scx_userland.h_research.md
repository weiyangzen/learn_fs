# sources/distributed-fs/ceph-client/tools/sched_ext/scx_userland.h

Purpose: shared header for the userland sched_ext example, defining the message payload sent from BPF to userspace.

Important APIs, types, and functions: defines `struct scx_userland_enqueued_task` with `pid`, `sum_exec_runtime`, and `weight`. There are no functions.

Control flow: BPF fills this structure in `enqueue_task_in_user_space()` and pushes it onto the `enqueued` BPF queue map. Userspace reads the same structure in `drain_enqueued_map()` and uses it to update its per-PID vruntime state.

State and persistence: each record is transient queue data. `sum_exec_runtime` and `weight` are snapshots from the kernel at enqueue time; userspace persists derived vruntime in its own task array.

Dependencies and integration points: must compile in both BPF and userspace contexts, so it relies on available integer aliases such as `__s32` and `u64` from included sched_ext/libbpf headers. Layout compatibility with the BPF queue map is critical.

Risks: adding fields or changing types requires updating BPF map value size and userspace consumers together. The record uses PID rather than a stable task reference, so consumers must tolerate exit and reuse races.

Test signals: skeleton generation and queue map operations validate layout. Userspace counters increasing after BPF enqueues confirm producer/consumer agreement.
