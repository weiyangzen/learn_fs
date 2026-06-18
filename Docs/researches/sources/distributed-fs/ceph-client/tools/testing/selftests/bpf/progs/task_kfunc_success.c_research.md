<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/task_kfunc_success.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/task_kfunc_success.c

Purpose: Positive suite for task kfunc acquisition, release, flavored kfunc relocation, map kptr exchange, pid/vpid lookup, and trusted walked fields.

Important APIs/types/functions: Defines success programs on `tp_btf/task_newtask` and `syscall`, globals `err`/`pid`, weak/flavored kfunc declarations, and helpers for lookup/compare.

Control flow: Programs gate on `pid`, acquire/release task refs from arguments/current task/map kptrs, test kfunc flavor resolution, exchange refs through local/map kptrs, and validate pid/vpid lookup results.

State and persistence: State includes error globals and the shared task kfunc map containing task kptrs.

Dependencies and integration: Depends on task kfuncs, kptr maps, RCU read locks, CO-RE ksym flavor resolution, and pid namespace semantics.

Risks: Reference count deltas, missing kfuncs, incompatible flavored symbols, and namespace assumptions are the main risks.

Test signals: Tests trigger task creation/syscall paths and expect `err==0` with valid map/ref cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/task_kfunc_success.c -->
