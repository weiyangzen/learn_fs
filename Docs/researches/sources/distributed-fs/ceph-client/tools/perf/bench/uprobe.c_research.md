# sources/distributed-fs/ceph-client/tools/perf/bench/uprobe.c

Purpose: implements `perf bench uprobe` variants that time repeated `usleep(1000)` calls with no probe, empty uprobe/uretprobe BPF programs, or trace_printk uprobe/uretprobe programs attached system-wide to libc `usleep`.

Important APIs, types, and functions: `enum bench_uprobe` identifies the benchmark variant. When `HAVE_BPF_SKEL` is enabled, `bench_uprobe__setup_bpf_skel()` opens, loads, and attaches the generated `bench_uprobe` BPF skeleton using `bpf_program__attach_uprobe_opts()`. `bench_uprobe__teardown_bpf_skel()` destroys it. Stub versions make non-BPF builds compile. `bench_uprobe_format__default_fprintf()` tracks static baseline and previous timings and prints deltas. `bench_uprobe()` performs option parsing, setup, timing, output, and teardown. The exported wrappers map each bench name to an enum value.

Control flow: each wrapper calls `bench_uprobe()`. Non-baseline modes attempt BPF setup; on setup failure they return 0 without measured output. Timing uses `clock_gettime(CLOCK_REALTIME)` around `loops` calls to `usleep(USEC_PER_MSEC)`, converts nanoseconds to microseconds, and prints either detailed default output or a simple integer.

State and persistence: process-local static state includes `loops`, `skel`, and the default formatter's `baseline`/`previous` values. Kernel state includes temporary uprobe links when BPF skeleton support is compiled in. No persistent files are written.

Dependencies and integration points: depends on perf bench, libbpf skeleton generation, libc path resolution for `libc.so.6`, `usleep`, and global `bench_format`. `builtin-bench.c` exposes the variants under the `uprobe` collection.

Risks: baseline and previous are static across calls in the same process, so running collection `all` intentionally compares variants but repeated independent invocations do not share the same baseline. Setup failure returning success can hide missing BPF capability in automation. `CLOCK_REALTIME` can jump; monotonic time would be less sensitive. Hard-coded `"libc.so.6"` and function name `usleep` depend on loader/libc behavior.

Test signals: run baseline and each BPF variant with `-l 1`, with and without BPF skeleton support. Verify teardown removes links, simple output is numeric, default output reports baseline and previous deltas, and unsupported BPF environments do not crash.
