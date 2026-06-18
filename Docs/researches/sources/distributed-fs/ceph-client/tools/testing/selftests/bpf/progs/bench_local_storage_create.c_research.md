# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bench_local_storage_create.c

## Purpose

Benchmark BPF program for local storage creation on task fork and socket creation paths. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

`BPF_MAP_TYPE_SK_STORAGE`, `BPF_MAP_TYPE_TASK_STORAGE`, `bpf_task_storage_get()`, `bpf_sk_storage_get()`, `BPF_LOCAL_STORAGE_GET_F_CREATE`, tracepoint BTF `sched_process_fork`, sleepable LSM `socket_post_create`, and counters `create_cnts`/`create_errs` gated by `bench_pid`.

## Control Flow

On fork, if parent TGID matches `bench_pid`, create task storage for the child and atomically increment success/error counters. On socket post-create, if current PID matches and `sock->sk` exists, create socket storage and update counters.

## State and Persistence Behavior

Persistent BPF local storage maps attach data to tasks/sockets for the life of those kernel objects. Global counters report benchmark outcomes.

## Dependencies and Integration Points

It depends on BPF CO-RE/libbpf helper headers, section annotations, generated skeleton loading from the selftest harness, and kernel verifier support for the program type, map type, helpers, kfuncs, and BTF metadata declared here. It requires task and socket local storage support, tp_btf, and sleepable LSM attachment.

## Risks and Edge Cases

Benchmark results depend on workload PID filtering and object lifetime. Missing `sock->sk` is handled as a no-op.

## Test Signals

Counters should show storage creation counts/errors corresponding to benchmark-generated forks or sockets.
