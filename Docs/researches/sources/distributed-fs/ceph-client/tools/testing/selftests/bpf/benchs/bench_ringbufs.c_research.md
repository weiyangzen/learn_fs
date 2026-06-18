# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/bench_ringbufs.c

Purpose: compares BPF ring buffer and perf buffer throughput across libbpf consumers, custom mmap/epoll consumers, back-to-back notification mode, sampling, reserve/commit versus output, overwrite mode, and producer-only ringbuf stress.

Important APIs and functions: argp flags configure back-to-back, batch count, sampling, sample rate, overwrite, output API, and producer-only mode. `bufs_validate()` enforces compatible producer/consumer counts. `ringbuf_setup_skeleton()` and `perfbuf_setup_skeleton()` load generated skeletons with rodata settings. `ringbuf_libbpf_setup()`, `ringbuf_custom_setup()`, and `perfbuf_libbpf_setup()` prepare consumers and attach BPF programs. Custom processing uses mmaped ringbuf pages, memory barriers, and epoll; perf custom processing reads perf mmap pages directly.

Control flow: producers trigger BPF via `getpgid`; consumers poll ring/perf buffers and count samples. In back-to-back mode, the consumer triggers the next batch after processing data. Measurements collect user-observed hits and BPF drop counters, or producer BSS hits in producer-only mode.

State and persistence: static contexts hold skeletons, libbpf buffers, custom ring mappings, epoll fds, and counters. Ring/perf buffer contents persist in kernel maps until consumed or overwritten.

Dependencies and integration points: depends on `ringbuf_bench.skel.h`, `perfbuf_bench.skel.h`, libbpf ring/perf buffer APIs, Linux perf mmap ABI, epoll, `asm/barrier.h`, and common hits/drops reporting.

Risks: custom consumers duplicate internal ABI assumptions and can break if layouts change; `args.ringbuf_sz` is assumed power-of-two for masking but not validated here; overwrite mode only supports producer benchmark; sampling config rejects sample rates larger than batch count for perfbuf. Back-to-back mode only makes sense with one producer.

Test signals: progress/final reports hits and drops. Regressions appear as poll failures, mmap failures, increased drops, incompatible argument exits, or divergent libbpf versus custom consumer throughput.
