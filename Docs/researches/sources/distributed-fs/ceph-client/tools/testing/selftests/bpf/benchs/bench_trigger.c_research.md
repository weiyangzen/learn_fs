# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/bench_trigger.c

Purpose: central benchmark collection for BPF trigger overhead across syscall counting, in-kernel batch drivers, kprobe/kretprobe/fentry/fexit/fmodret/tracepoint/raw tracepoint, kprobe-multi all-symbol attachment, uprobes/uretprobes, uprobe-multi, and x86 USDT probes.

Important APIs and functions: `bench_trigger_batch_argp` parses `--trig-batch-iters`. `setup_ctx()` opens `trigger_bench`, enables the driver program, and writes rodata. `trigger_producer()` triggers syscalls; `trigger_producer_batch()` repeatedly calls a BPF driver with `bpf_prog_test_run_opts`. Setup functions selectively autoload and attach programs. `attach_ksyms_all()` gets filtered kallsyms and attaches multi-kprobes. `usetup()` calculates target offsets and attaches uprobe or uprobe-multi. User target functions are carefully marked weak/noinline/nocf for stable probe points.

Control flow: setup selects the BPF path and optional driver fd. Producers either call `getpgid`, run a BPF driver, or call a user-space target function. `trigger_measure()` reads either user-mode sharded counters or BPF BSS hit counters. Macro blocks declare many `struct bench` entries.

State and persistence: `ctx` stores skeleton, selected counter source, and optional driver program fd. User counters are sharded by hashed tid into 256 counters to reduce contention. BPF links persist for the benchmark lifetime.

Dependencies and integration points: depends on `trigger_bench.skel.h`, `trace_helpers.h` for kallsyms/uprobe offsets, libbpf attach APIs, arch-specific x86 probe targets, and `bench.h`.

Risks: all-symbol kprobe-multi is kernel/config sensitive and intentionally skips problematic recursive functions; uprobe instruction choice affects measured overhead; USDT only builds under x86 section; missing feature support causes load/attach failures. Batch iteration values are capped at 1000.

Test signals: `run_bench_trigger.sh` and `run_bench_uprobes.sh` extract per-trigger summary throughput. Attach/load failures, verifier errors, or zero BPF hits indicate regressions.
