# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/bench_local_storage_create.c

Purpose: benchmarks creation of BPF local storage owners, either socket storage by creating IPv6 UDP sockets or task storage by creating short-lived pthreads.

Important APIs and functions: argp options `--batch-size` and `--storage-type` select batch count and `BPF_MAP_TYPE_SK_STORAGE` versus `BPF_MAP_TYPE_TASK_STORAGE`. `setup()` loads `bench_local_storage_create.skel.h`, writes `bench_pid`, attaches either `socket_post_create` or `sched_process_fork`, and allocates per-producer fd/thread arrays. `sk_producer()` creates and closes socket batches; `task_producer()` creates and joins thread batches; `measure()` reads `create_cnts`; reporting computes create throughput and error totals.

Control flow: validation only rejects consumers. Setup attaches the BPF hook matching the chosen owner type. Each producer loops over creation batches, records owner-creation syscall failures separately, then destroys owners so the next batch can run.

State and persistence: global `skel`, `threads`, `create_owner_errs`, `storage_type`, and `batch_sz` hold process state. BPF BSS fields track successful storage creations and BPF-side errors; `create_cnts` is atomically reset at each sample.

Dependencies and integration points: uses pthreads, sockets, libbpf skeleton APIs, `bench.h`, and kernel hooks exposed by the BPF object. The BPF program filters using `bench_pid`, so process identity is part of correctness.

Risks: large batch sizes can exhaust file descriptors, memory, or thread limits; task mode creates many real pthreads and can stress scheduler limits; producer arrays are never freed during the benchmark; storage-type string validation is strict.

Test signals: progress lines report `creates k/s`, final summary reports standard deviation and total creates, and any socket/pthread or BPF create errors are printed explicitly.
