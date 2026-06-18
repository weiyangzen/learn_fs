# sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/kwork_trace.bpf.c

## sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/kwork_trace.bpf.c

Purpose: this BPF program backs `perf kwork report` by measuring IRQ, softirq, and workqueue runtime or latency using tracepoints.

Important maps and helpers: `perf_kwork_names` stores display names, `perf_kwork_time` stores start timestamps, `perf_kwork_report` stores count/total/max rows, `perf_kwork_cpu_filter` and `perf_kwork_name_filter` gate collection. Helpers `trace_event_match()`, `do_update_time()`, `do_update_timestart()`, `do_update_timeend()`, and `do_update_name()` implement shared filtering and aggregation.

Control flow: runtime programs pair entry/exit events for IRQ, softirq, and workqueue execution. Latency programs pair softirq raise to entry and workqueue activate to execute start. Each begin stores a timestamp, each end deletes it and updates report totals, and names are stored when available from tracepoint data or `%ps` formatting.

State and persistence: BPF maps hold up to `KWORK_COUNT` keys for names, timestamps, and reports. `enabled` gates all updates; rodata flags enable CPU/name filters.

Dependencies and integration: user space controls autoload based on class/report mode and reads reports via matching C structs in `bpf_kwork.c`. The file depends on tracepoint struct definitions in `vmlinux.h` and softirq constants.

Risks: the fixed `KWORK_COUNT` of 100 is small for high-cardinality workqueues. Name filtering is exact string comparison and only applied when a name is known. Missing exit events leave timestamp rows. `bpf_snprintf("%ps")` availability and symbol formatting can vary by kernel.

Test signals: exercise runtime and latency modes for each class, CPU/name filters, workqueue functions with many unique work pointers, and tracepoint loss/missing-pair scenarios.
