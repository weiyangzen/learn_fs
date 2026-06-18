<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/task_local_storage_exit_creds.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/task_local_storage_exit_creds.c

Purpose: Tests task storage access from the `exit_creds` fentry hook.

Important APIs/types/functions: Defines `task_storage` map and `fentry/exit_creds` program.

Control flow: The hook accesses task storage while credentials are exiting to validate lifetime/deadlock behavior.

State and persistence: Persistent state is task storage associated with tasks.

Dependencies and integration: Depends on fentry attachment and task storage helpers.

Risks: Credential teardown is a sensitive lifetime point for task storage lookup/update.

Test signals: Pass signal is successful hook execution without verifier/runtime deadlock issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/task_local_storage_exit_creds.c -->
