# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_kfunc_prog_types.c

## Purpose

`verifier_kfunc_prog_types.c` verifies that selected kfunc families are available across supported program types. It covers task, cgroup, and cpumask kfunc load paths in raw tracepoint, syscall, tracepoint, and perf_event programs.

## Important APIs, Types, and Functions

The file includes common headers for cgroup, cpumask, and task kfunc tests. It defines three reusable test bodies: task kfunc load, cgroup kfunc load, and cpumask kfunc load. APIs include `bpf_get_current_task_btf`, `bpf_task_acquire`, `bpf_task_from_pid`, `bpf_task_release`, `bpf_cgroup_from_id`, `bpf_cgroup_acquire`, `bpf_cgroup_release`, `bpf_cpumask_create`, `bpf_cpumask_acquire`, `bpf_cpumask_set_cpu`, `bpf_cpumask_test_cpu`, and `bpf_cpumask_release`.

## Control Flow

Each program type invokes the same family-specific sequence: acquire or create an object, perform a simple operation, and release it. There are 12 success programs, three kfunc families multiplied by four program types.

## State and Persistence Behavior

No maps are declared. Runtime state is temporary refcounted task, cgroup, or cpumask objects. Correct behavior requires release on all paths and no persistent references after program exit.

## Dependencies and Integration Points

The file integrates with BTF kfunc registration, per-program-type kfunc allowlists, reference tracking, task/cgroup/cpumask kernel subsystems, and selftest common helper headers.

## Risks and Test Signals

Risks are missing kfunc allowlist entries for a supported program type, incorrect reference tracking, or cpumask allocation/release mismatch. Test signals are successful load of all raw_tp, syscall, tracepoint, and perf_event variants.
