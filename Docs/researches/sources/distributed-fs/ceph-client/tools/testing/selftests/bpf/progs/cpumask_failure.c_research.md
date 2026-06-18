<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cpumask_failure.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cpumask_failure.c

## Purpose
`cpumask_failure.c` is a negative cpumask kfunc verifier suite for trusted pointer, nullable, ownership, and reference rules. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 5774 bytes across 262 lines.

## Important APIs, Types, and Functions
- Dependencies: `<vmlinux.h>`, `<bpf/bpf_tracing.h>`, `<bpf/bpf_helpers.h>`, `"bpf_misc.h"`, `"cpumask_common.h"`.
- BPF API surface: cpumask ownership/query/mutation kfuncs.
- Helper/kfunc calls: `bpf_cpumask_acquire`, `bpf_cpumask_create`, `bpf_cpumask_empty`, `bpf_cpumask_populate`, `bpf_cpumask_release`, `bpf_cpumask_set_cpu`, `bpf_cpumask_test_cpu`, `bpf_kptr_xchg`, `bpf_rcu_read_lock`, `bpf_rcu_read_unlock`.
Attach sections and exported entry points:
- line 11 `SEC("license")` -> struct kptr_nested_array_2 {
- line 34 `SEC("tp_btf/task_newtask")` -> int BPF_PROG(test_alloc_no_release, struct task_struct *task, u64 clone_flags)
- line 47 `SEC("tp_btf/task_newtask")` -> int BPF_PROG(test_alloc_double_release, struct task_struct *task, u64 clone_flags)
- line 62 `SEC("tp_btf/task_newtask")` -> int BPF_PROG(test_acquire_wrong_cpumask, struct task_struct *task, u64 clone_flags)
- line 75 `SEC("tp_btf/task_newtask")` -> int BPF_PROG(test_mutate_cpumask, struct task_struct *task, u64 clone_flags)
- line 85 `SEC("tp_btf/task_newtask")` -> int BPF_PROG(test_insert_remove_no_release, struct task_struct *task, u64 clone_flags)
- line 109 `SEC("tp_btf/task_newtask")` -> int BPF_PROG(test_cpumask_null, struct task_struct *task, u64 clone_flags)
- line 119 `SEC("tp_btf/task_newtask")` -> int BPF_PROG(test_global_mask_out_of_rcu, struct task_struct *task, u64 clone_flags)
- line 153 `SEC("tp_btf/task_newtask")` -> int BPF_PROG(test_global_mask_no_null_check, struct task_struct *task, u64 clone_flags)
- line 181 `SEC("tp_btf/task_newtask")` -> int BPF_PROG(test_global_mask_rcu_no_null_check, struct task_struct *task, u64 clone_flags)
- line 206 `SEC("tp_btf/task_newtask")` -> int BPF_PROG(test_invalid_nested_array, struct task_struct *task, u64 clone_flags)
- line 226 `SEC("tp_btf/task_newtask")` -> int BPF_PROG(test_populate_invalid_destination, struct task_struct *task, u64 clone_flags)
- plus 1 more entries of the same pattern.
Key functions/subprograms:
- line 35 `__msg`: `__failure __msg("Unreleased reference")`
- line 36 `BPF_PROG`: `int BPF_PROG(test_alloc_no_release, struct task_struct *task, u64 clone_flags)`
- line 48 `__msg`: `__failure __msg("NULL pointer passed to trusted arg0")`
- line 49 `BPF_PROG`: `int BPF_PROG(test_alloc_double_release, struct task_struct *task, u64 clone_flags)`
- line 63 `__msg`: `__failure __msg("must be referenced")`
- line 64 `BPF_PROG`: `int BPF_PROG(test_acquire_wrong_cpumask, struct task_struct *task, u64 clone_flags)`
- line 76 `__msg`: `__failure __msg("bpf_cpumask_set_cpu args#1 expected pointer to STRUCT bpf_cpumask")`
- line 77 `BPF_PROG`: `int BPF_PROG(test_mutate_cpumask, struct task_struct *task, u64 clone_flags)`
- line 86 `__msg`: `__failure __msg("Unreleased reference")`
- line 87 `BPF_PROG`: `int BPF_PROG(test_insert_remove_no_release, struct task_struct *task, u64 clone_flags)`
- line 110 `__msg`: `__failure __msg("NULL pointer passed to trusted arg0")`
- line 111 `BPF_PROG`: `int BPF_PROG(test_cpumask_null, struct task_struct *task, u64 clone_flags)`
- plus 12 more entries of the same pattern.

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `license`, `tp_btf/task_newtask`, `tp_btf/task_newtask`, `tp_btf/task_newtask`, `tp_btf/task_newtask`, `tp_btf/task_newtask`, `tp_btf/task_newtask`, `tp_btf/task_newtask` and additional sections. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `__msg`, `BPF_PROG`, `__msg`, `BPF_PROG`, `__msg`, `BPF_PROG`, `__msg`, `BPF_PROG` and related helper subprograms. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 231 `u64 bits;`
- line 232 `int ret;`
- line 247 `int ret;`
The file exercises explicit reference/lifetime behavior; accepted paths must release or transfer ownership, while failure variants intentionally leave or misuse references.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.

## Risks and Edge Cases
- Expected verifier failures/messages are part of the test contract; diagnostic text and annotation drift can break the harness.
- Cpumask cases depend on trusted pointer tracking, nullability, and exact ownership/release rules.

## Test Signals
- Uses `__failure` annotations; a passing test is verifier rejection with expected diagnostics.
- Expected verifier messages include `Unreleased reference`, `NULL pointer passed to trusted arg0`, `must be referenced`, `bpf_cpumask_set_cpu args#1 expected pointer to STRUCT bpf_cpumask`, `Unreleased reference`, plus 7 more.
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cpumask_failure.c -->
