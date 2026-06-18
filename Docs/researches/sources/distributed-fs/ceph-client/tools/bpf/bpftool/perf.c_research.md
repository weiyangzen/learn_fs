# sources/distributed-fs/ceph-client/tools/bpf/bpftool/perf.c

`perf.c` implements `bpftool perf show|list`, which scans process file descriptors and reports perf-event fds that have BPF programs attached. Its entry point is `do_perf()`.

Before scanning, `has_perf_query_support()` probes `bpf_task_fd_query()` on an arbitrary directory fd. The code treats errno 524 (`ENOTSUPP`) from a query with no attachment as evidence that the syscall feature exists, caches support in `perf_query_supported`, and emits a hint for non-root or unsupported kernels otherwise. `do_show()` then starts a JSON array if requested and calls `show_proc()`.

`show_proc()` opens `/proc`, filters numeric PID directories, opens each `/proc/<pid>/fd`, filters numeric fd entries, and calls `bpf_task_fd_query(pid, fd, ...)`. Successful queries are rendered by `print_perf_json()` or `print_perf_plain()`. The output distinguishes raw tracepoint, tracepoint, kprobe/kretprobe, uprobe/uretprobe, and includes function/file names, offsets, addresses, and program IDs according to fd type.

State is process-local cache plus transient directory scans; no persistent kernel state is changed. Dependencies include procfs visibility, `bpf_task_fd_query()`, JSON writer, pid/fd parsing via ctype, and bpftool globals. Risks include permission-sensitive visibility, processes/fds disappearing during scan, the hard-coded errno 524 portability assumption, silent skipping of query errors after the initial probe, and incomplete output for unknown fd types. Test signals include root and non-root runs, kernels with and without task fd query support, live kprobe/uprobe/tracepoint attachments, disappearing processes during scan, JSON/plain output, and fd names with large numeric values.
