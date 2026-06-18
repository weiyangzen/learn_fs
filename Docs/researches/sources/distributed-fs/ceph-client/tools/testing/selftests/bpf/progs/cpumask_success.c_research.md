<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cpumask_success.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cpumask_success.c

## Purpose
`cpumask_success.c` is a positive cpumask kfunc suite for allocation, mutation, map storage, kptr exchange, and RCU-safe use. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 18458 bytes across 890 lines.

## Important APIs, Types, and Functions
- Dependencies: `<vmlinux.h>`, `<bpf/bpf_tracing.h>`, `<bpf/bpf_helpers.h>`, `"bpf_misc.h"`, `"cpumask_common.h"`.
- Important macros/constants: `CPUMASK_TEST_MASKLEN`.
- BPF API surface: task/cgroup/time/function metadata helpers; cpumask ownership/query/mutation kfuncs.
- Helper/kfunc calls: `bpf_cpumask_and`, `bpf_cpumask_any_and_distribute`, `bpf_cpumask_any_distribute`, `bpf_cpumask_clear`, `bpf_cpumask_clear_cpu`, `bpf_cpumask_copy`, `bpf_cpumask_create`, `bpf_cpumask_empty`, `bpf_cpumask_equal`, `bpf_cpumask_first`, `bpf_cpumask_first_and`, `bpf_cpumask_first_zero`, `bpf_cpumask_full`, `bpf_cpumask_intersects`, `bpf_cpumask_or`, `bpf_cpumask_populate`, `bpf_cpumask_release`, `bpf_cpumask_set_cpu`, plus 13 more.
Attach sections and exported entry points:
- line 11 `SEC("license")` -> int pid, nr_cpus;
- line 138 `SEC("tp_btf/task_newtask")` -> int BPF_PROG(test_alloc_free_cpumask, struct task_struct *task, u64 clone_flags)
- line 154 `SEC("tp_btf/task_newtask")` -> int BPF_PROG(test_set_clear_cpu, struct task_struct *task, u64 clone_flags)
- line 183 `SEC("tp_btf/task_newtask")` -> int BPF_PROG(test_setall_clear_cpu, struct task_struct *task, u64 clone_flags)
- line 212 `SEC("tp_btf/task_newtask")` -> int BPF_PROG(test_first_firstzero_cpu, struct task_struct *task, u64 clone_flags)
- line 251 `SEC("tp_btf/task_newtask")` -> int BPF_PROG(test_firstand_nocpu, struct task_struct *task, u64 clone_flags)
- line 283 `SEC("tp_btf/task_newtask")` -> int BPF_PROG(test_test_and_set_clear, struct task_struct *task, u64 clone_flags)
- line 315 `SEC("tp_btf/task_newtask")` -> int BPF_PROG(test_and_or_xor, struct task_struct *task, u64 clone_flags)
- line 362 `SEC("tp_btf/task_newtask")` -> int BPF_PROG(test_intersects_subset, struct task_struct *task, u64 clone_flags)
- line 404 `SEC("tp_btf/task_newtask")` -> int BPF_PROG(test_copy_any_anyand, struct task_struct *task, u64 clone_flags)
- line 458 `SEC("tp_btf/task_newtask")` -> int BPF_PROG(test_insert_leave, struct task_struct *task, u64 clone_flags)
- line 473 `SEC("tp_btf/task_newtask")` -> int BPF_PROG(test_insert_remove_release, struct task_struct *task, u64 clone_flags)
- plus 12 more entries of the same pattern.
Key functions/subprograms:
- line 88 `is_test_task`: `static bool is_test_task(void)`
- line 95 `create_cpumask_set`: `static bool create_cpumask_set(struct bpf_cpumask **out1,`
- line 139 `BPF_PROG`: `int BPF_PROG(test_alloc_free_cpumask, struct task_struct *task, u64 clone_flags)`
- line 155 `BPF_PROG`: `int BPF_PROG(test_set_clear_cpu, struct task_struct *task, u64 clone_flags)`
- line 184 `BPF_PROG`: `int BPF_PROG(test_setall_clear_cpu, struct task_struct *task, u64 clone_flags)`
- line 213 `BPF_PROG`: `int BPF_PROG(test_first_firstzero_cpu, struct task_struct *task, u64 clone_flags)`
- line 252 `BPF_PROG`: `int BPF_PROG(test_firstand_nocpu, struct task_struct *task, u64 clone_flags)`
- line 284 `BPF_PROG`: `int BPF_PROG(test_test_and_set_clear, struct task_struct *task, u64 clone_flags)`
- line 316 `BPF_PROG`: `int BPF_PROG(test_and_or_xor, struct task_struct *task, u64 clone_flags)`
- line 363 `BPF_PROG`: `int BPF_PROG(test_intersects_subset, struct task_struct *task, u64 clone_flags)`
- line 405 `BPF_PROG`: `int BPF_PROG(test_copy_any_anyand, struct task_struct *task, u64 clone_flags)`
- line 459 `BPF_PROG`: `int BPF_PROG(test_insert_leave, struct task_struct *task, u64 clone_flags)`
- plus 14 more entries of the same pattern.

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `license`, `tp_btf/task_newtask`, `tp_btf/task_newtask`, `tp_btf/task_newtask`, `tp_btf/task_newtask`, `tp_btf/task_newtask`, `tp_btf/task_newtask`, `tp_btf/task_newtask` and additional sections. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `is_test_task`, `create_cpumask_set`, `BPF_PROG`, `BPF_PROG`, `BPF_PROG`, `BPF_PROG`, `BPF_PROG`, `BPF_PROG` and related helper subprograms. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 13 `int pid, nr_cpus;`
- line 25 `int dummy;`
- line 35 `int dummy;`
- line 40 `int dummy;`
- line 45 `long dummy;`
- line 50 `long dummy[2];`
- line 55 `int dummy;`
- line 60 `long dummy;`
- line 65 `long dummy[2];`
- line 70 `int dummy;`
- plus 13 more entries of the same pattern.
The file exercises explicit reference/lifetime behavior; accepted paths must release or transfer ownership, while failure variants intentionally leave or misuse references.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.

## Risks and Edge Cases
- Cpumask cases depend on trusted pointer tracking, nullability, and exact ownership/release rules.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cpumask_success.c -->
