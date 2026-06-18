# sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/bpf_prog_profiler.bpf.c

## sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/bpf_prog_profiler.bpf.c

Purpose: this BPF skeleton profiles a target BPF program by attaching fentry/fexit programs and measuring perf-event deltas during the target program's execution.

Important maps and programs: `events` is a perf-event array keyed by CPU; `fentry_readings` stores readings captured at entry; `accum_readings` stores accumulated deltas. `fentry_XXX()` reads the event value at entry, and `fexit_XXX()` reads after return and calls `fexit_update_maps()`.

Control flow: user space retargets both programs to a target BPF function name. Entry reads the current CPU's perf event into per-CPU storage. Exit reads the after value, subtracts the entry value if it looks valid, and atomically accumulates counter/enabled/running deltas.

State and persistence: all readings are per-CPU arrays. `num_cpu` rodata is set by user space but this program uses the current CPU as the event key. Accumulated readings persist until user-space reads/destroys the skeleton.

Dependencies and integration: `bpf_counter.c` opens the target BPF prog fd by id, discovers BTF function name, attaches this skeleton, installs event fds into `events`, and folds `accum_readings` into perf counts.

Risks: target BPF program must have BTF and attachable fentry/fexit points. Nested calls on the same CPU can overwrite `fentry_readings`. The "before counter nonzero" guard can skip valid measurements if a counter legitimately reads zero at entry.

Test signals: profile a known BPF program under load, verify BTF-missing failure, compare event deltas with manual instrumentation, and exercise nested/reentrant target behavior.
