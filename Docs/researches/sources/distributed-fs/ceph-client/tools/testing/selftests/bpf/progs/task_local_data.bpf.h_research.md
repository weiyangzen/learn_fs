<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/task_local_data.bpf.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/task_local_data.bpf.h

Purpose: Reusable task-local data implementation for tests that need metadata, key lookup, and per-task storage values.

Important APIs/types/functions: Defines metadata/data/key unions and structs, `tld_data_map`, `tld_key_map`, `tld_object_init`, and `__tld_fetch_key`, plus a struct_ops hook section.

Control flow: Initialization stores object metadata and fetch helpers derive keys for task-local storage scenarios.

State and persistence: Persistent state lives in the task-local data maps and any task-local storage values created by including tests.

Dependencies and integration: Depends on BPF map definitions, struct_ops support, and task-local storage APIs used by consumers.

Risks: Key/value BTF layout and object lifetime must match consumers; stale keys can hide storage bugs.

Test signals: Compile/include tests and consumers validate map layout and helper behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/task_local_data.bpf.h -->
