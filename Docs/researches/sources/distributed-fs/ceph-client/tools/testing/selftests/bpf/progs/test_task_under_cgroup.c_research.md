<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_task_under_cgroup.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_task_under_cgroup.c

## Purpose

Exercises `bpf_task_under_cgroup` and acquire/release kfuncs from tracing and sleepable LSM contexts. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 77 source lines. BPF sections: `tp_btf/task_newtask`, `lsm.s/bpf`, `license`. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_attr`, `bpf_cgroup_from_id`, `bpf_cgroup_release`, `bpf_get_current_pid_tgid`, `bpf_get_current_task_btf`, `bpf_helpers`, `bpf_misc`, `bpf_task_acquire`, `bpf_task_release`, `bpf_task_under_cgroup`, `bpf_tracing`. Important C functions and entry points include `bpf_task_under_cgroup`, `bpf_cgroup_release`, `bpf_task_release`, `BPF_PROG`, `BPF_PROG`. Notable globals or configuration/result fields include `long bpf_task_under_cgroup(struct task_struct *task, struct cgroup *ancestor) __ksym`; `const volatile int local_pid`; `const volatile __u64 cgid`; `int remote_pid`; `int BPF_PROG(tp_btf_run, struct task_struct *task, u64 clone_flags)`; `int BPF_PROG(lsm_run, int cmd, union bpf_attr *attr, unsigned int size, bool kernel)`.

## Control Flow

The task_newtask tracepoint checks local/remote pids and cgroup id; the sleepable LSM hook acquires current task and cgroup objects, calls the kfunc, and releases both.

## State And Persistence Behavior

Input globals include `local_pid`, `remote_pid`, and `cgid`; result is implicit through selftest assertions. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Reference release must happen on all paths, and sleepable LSM semantics differ from raw tracepoint constraints. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

The harness should create tasks inside/outside the target cgroup and verify true/false kfunc outcomes. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_task_under_cgroup.c -->
