# sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/bench_uprobe.bpf.c

## sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/bench_uprobe.bpf.c

Purpose: this small skeleton provides BPF programs for `perf bench uprobe`, measuring empty uprobes/uretprobes and trace-printing variants.

Important APIs and functions: `BPF_UPROBE(empty)`, `BPF_UPROBE(trace_printk)`, `BPF_URETPROBE(empty_ret)`, and `BPF_URETPROBE(trace_printk_ret)` are attached externally as uprobe/uretprobe programs. Globals `nr_uprobes` and `nr_uretprobes` count trace-print invocations.

Control flow: empty probes immediately return. Trace-print probes increment the relevant counter and call `bpf_trace_printk()` with a fixed format.

State and persistence: only BPF global counters are maintained for the life of the loaded skeleton. No maps are declared.

Dependencies and integration: depends on libbpf tracing macros and the perf bench harness that attaches the sections to user-space symbols.

Risks: `bpf_trace_printk()` is intentionally expensive and suitable only for benchmarking/debug behavior. Counter globals are not atomic and are used for approximate benchmark signaling.

Test signals: run perf bench uprobe modes for entry/return, empty/trace_printk variants, and compare overhead with expected relative cost.
