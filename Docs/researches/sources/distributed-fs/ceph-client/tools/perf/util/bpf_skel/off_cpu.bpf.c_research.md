# sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/off_cpu.bpf.c

## sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/off_cpu.bpf.c

Purpose: this BPF program measures how long user tasks stay off-CPU after scheduler switch-out, keyed by pid/tgid/state/callchain/cgroup, and either aggregates short waits in a map or emits thresholded raw samples directly.

Important maps and globals: `stacks` stores user stack traces; `offcpu_output` is a perf-event array; `offcpu_payload` is per-CPU scratch; task-local `tstamp` stores timestamp/state/stack data; `off_cpu` stores aggregated durations; CPU/task/cgroup filter maps gate collection. Ro/BSS globals configure filters, tgid mode, sched_switch signature, cgroup mode, and threshold.

Control flow: `on_switch` extracts previous and next tasks and previous state from either ctx or task struct, then calls `off_cpu_stat()`. The helper records a timestamp and user stack for eligible previous tasks in interruptible/uninterruptible sleep, then when a next task has a stored timestamp it computes delta, emits direct output if over threshold, otherwise aggregates into `off_cpu`, and clears the timestamp. `on_newtask` expands tgid filters for forked processes when tracking process targets.

State and persistence: task-local storage associates off-CPU start data with task structs. Aggregated map rows persist until user space writes them. Thresholded direct output is emitted immediately to perf ring buffers.

Dependencies and integration: user space in `bpf_off_cpu.c` fills filters, detects `prev_state` ABI, populates `offcpu_output`, and converts map rows to perf samples. The program uses CO-RE for task state/cgroup fields and stack helpers for user callchains.

Risks: kernel threads are skipped because user stacks are unavailable. Stack helper failures can create ambiguous stack ids. The code stores full stack data only when `stack_id > 0`, so stack id zero is treated as not copied. Task-local storage requires kernel support. Direct output and aggregate paths differ based on threshold, so parsers must handle both.

Test signals: test sleeping user workloads, cgroup recording/filtering, pid/tgid filters with forks, threshold zero and nonzero paths, kernels with old/new `task_struct` state field, and stack collection failure cases.
