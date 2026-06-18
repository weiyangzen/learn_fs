<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/task_kfunc_common.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/task_kfunc_common.h

Purpose: Shared header for task kfunc tests that defines a map storing referenced task kptrs and helper insertion logic.

Important APIs/types/functions: Defines `struct __tasks_kfunc_map_value`, `__tasks_kfunc_map`, weak task kfunc declarations, `tasks_kfunc_map_value_lookup`, and `tasks_kfunc_map_insert`.

Control flow: Insertion reads task pid, creates a map value, acquires a task reference, and stores it with `bpf_kptr_xchg`; lookup returns the value for later tests.

State and persistence: Persistent state is the hash map keyed by pid containing `struct task_struct __kptr *` references.

Dependencies and integration: Depends on task kfuncs, map kptr support, and BTF task_struct access.

Risks: Reference leaks, wrong pid keys, and stale kptr replacement are key risks.

Test signals: Included success/failure tests validate acquire/release and map ownership behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/task_kfunc_common.h -->
