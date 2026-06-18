# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/bench_rename.c

Purpose: benchmarks overhead of different BPF attachment types on the task rename path by repeatedly writing to `/proc/self/comm`.

Important APIs and functions: `validate()` enforces one producer and no consumers. `setup_ctx()` loads `test_overhead.skel.h` and opens `/proc/self/comm`. Attachment setup variants attach `prog1` through `prog5` for kprobe, kretprobe, raw tracepoint, fentry, and fexit. `producer()` writes a fixed string and increments a user-space hit counter; `measure()` swaps the counter.

Control flow: each benchmark entry shares the same producer, setup context, and report functions. The base benchmark attaches no BPF program; other setups attach one specific BPF program before the producer loop starts.

State and persistence: process-local `ctx.fd` persists for repeated writes, and `ctx.hits` is reset every measurement interval. BPF links are owned by libbpf skeleton/link lifetime.

Dependencies and integration points: integrates with `bench.h`, `test_overhead` BPF skeleton, `/proc/self/comm`, and libbpf attach APIs.

Risks: requires permission and kernel support for the selected attach kinds; `/proc/self/comm` writes can fail in unusual procfs or namespace configurations; base hit counter measures user writes rather than BPF hits.

Test signals: `run_bench_rename.sh` expects summary throughput per attach type. Attach failure or write failure aborts the benchmark.
