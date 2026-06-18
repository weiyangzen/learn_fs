<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_task_vmas.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_task_vmas.c

## Purpose

BPF iterator selftest program that attaches to an iterator target and validates seq output, typed iterator context access, map/object traversal, or socket/task state handling.

## Important APIs, Types, and Functions

- BPF sections: `license`, `iter/task_vma`
- BPF helpers/kfunc-like calls: `bpf_d_path`
- Mutable globals/test result fields: `d_path_buf[D_PATH_BUF_SIZE]`, `pid`, `one_task`, `one_task_error`

## Control Flow and Data Flow

The iterator framework calls the program once per object and once with a NULL element at end-of-iteration. Programs either write seq data, sum keys/values, mutate/delete map entries, or validate typed context pointers while respecting sleepable versus non-sleepable section rules.

## State and Persistence Behavior

Globals are used as userspace-visible configuration/results: `d_path_buf[D_PATH_BUF_SIZE]`, `pid`, `one_task`, `one_task_error`

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf/bpf_helpers.h`. Depends on kernel BPF iterator targets, typed BTF context definitions from `vmlinux.h`, and seq-file output helpers where used.

## Risks and Edge Cases

Iterator contexts may pass NULL end markers and expose mutable kernel/map state; programs must handle NULLs, sleepability, and deletion while iterating. Helper availability and license restrictions matter for `bpf_d_path`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Userspace should read globals such as `d_path_buf[D_PATH_BUF_SIZE]`, `pid`, `one_task`, `one_task_error` to confirm the exercised path ran. Iterator file output, accumulated sums, deletion side effects, and NULL terminal calls should match the userspace expected data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_task_vmas.c -->
