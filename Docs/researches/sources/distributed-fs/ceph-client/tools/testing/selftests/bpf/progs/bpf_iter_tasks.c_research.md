<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_tasks.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_tasks.c

## Purpose

BPF iterator selftest program that attaches to an iterator target and validates seq output, typed iterator context access, map/object traversal, or socket/task state handling.

## Important APIs, Types, and Functions

- BPF sections: `license`, `iter/task`, `iter.s/task`
- Important functions/callbacks: `dump_task`, `dump_task_sleepable`
- BPF helpers/kfunc-like calls: `bpf_copy_from_user_task`, `bpf_copy_from_user_task_str`, `bpf_strncmp`, `bpf_task_pt_regs`
- Mutable globals/test result fields: `num_unknown_tid`, `num_known_tid`, `num_expected_failure_copy_from_user_task`, `num_expected_failure_copy_from_user_task_str`, `num_success_copy_from_user_task`, `num_success_copy_from_user_task_str`

## Control Flow and Data Flow

The iterator framework calls the program once per object and once with a NULL element at end-of-iteration. Programs either write seq data, sum keys/values, mutate/delete map entries, or validate typed context pointers while respecting sleepable versus non-sleepable section rules.

## State and Persistence Behavior

Globals are used as userspace-visible configuration/results: `num_unknown_tid`, `num_known_tid`, `num_expected_failure_copy_from_user_task`, `num_expected_failure_copy_from_user_task_str`, `num_success_copy_from_user_task`, `num_success_copy_from_user_task_str`

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`. Depends on kernel BPF iterator targets, typed BTF context definitions from `vmlinux.h`, and seq-file output helpers where used.

## Risks and Edge Cases

Iterator contexts may pass NULL end markers and expose mutable kernel/map state; programs must handle NULLs, sleepability, and deletion while iterating. Helper availability and license restrictions matter for `bpf_copy_from_user_task`, `bpf_copy_from_user_task_str`, `bpf_strncmp`, `bpf_task_pt_regs`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Userspace should read globals such as `num_unknown_tid`, `num_known_tid`, `num_expected_failure_copy_from_user_task`, `num_expected_failure_copy_from_user_task_str`, `num_success_copy_from_user_task`, `num_success_copy_from_user_task_str` to confirm the exercised path ran. Iterator file output, accumulated sums, deletion side effects, and NULL terminal calls should match the userspace expected data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_tasks.c -->
