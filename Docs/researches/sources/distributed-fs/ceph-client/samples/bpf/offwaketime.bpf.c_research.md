# sources/distributed-fs/ceph-client/samples/bpf/offwaketime.bpf.c

Purpose: BPF tracing program that attributes off-CPU wait time to waker and target stack traces.

Important APIs/types/functions: `struct key_t`, `struct wokeby_t`, maps for start times, waker info, stack traces, and counts; `waker` kprobe on `try_to_wake_up`; `update_counts`; and `oncpu` handlers for sched switch or finish_task_switch depending on kernel version.

Control flow: when a task wakes another, records waker PID/name and stack. When a task is scheduled back on CPU, computes blocked delta, gathers target stack, combines waker/target identity into a key, and increments aggregate blocked time if above threshold.

State and persistence: BPF maps track last wake info, start timestamps, stack traces, and aggregate counts.

Dependencies and integration: paired with `offwaketime_user.c`; depends on scheduler tracepoints/kprobes, stack trace map support, BTF/CO-RE helpers, and kernel-version attach variants.

Risks: stack capture can fail or collide depending on `BPF_F_FAST_STACK_CMP`. Scheduler internals and probe signatures vary across kernels. High event rates can stress maps.

Test signals: run under blocking workloads, observe nonzero folded stacks and counts, and verify missing stack warnings are limited.
