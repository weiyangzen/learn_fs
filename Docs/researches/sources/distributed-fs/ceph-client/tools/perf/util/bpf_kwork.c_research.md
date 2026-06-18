# sources/distributed-fs/ceph-client/tools/perf/util/bpf_kwork.c

## sources/distributed-fs/ceph-client/tools/perf/util/bpf_kwork.c

Purpose: this file is the user-space loader/reader for BPF-backed `perf kwork report` tracing. It selects tracepoint programs for IRQ, softirq, and workqueue classes, applies CPU/name filters, and converts BPF report-map rows into perf `kwork_work` objects.

Important APIs and functions: `perf_kwork__trace_prepare_bpf()` opens `kwork_trace`, disables all autoload programs, re-enables programs matching selected classes and report mode, sets rodata filter flags, loads, filters, and attaches. `perf_kwork__trace_start()` and `perf_kwork__trace_finish()` record wall-clock monotonic bounds and toggle `enabled`. `perf_kwork__report_read_bpf()` iterates `perf_kwork_report`, uses `add_work()` to populate runtime or latency totals, and `perf_kwork__report_cleanup_bpf()` destroys the skeleton.

Control flow: each `kwork_class_bpf` entry owns a class pointer, a load-preparation hook, and a work-name lookup hook. Runtime report mode enables entry/exit programs; latency mode enables raise/activate to execute/entry programs where applicable. During read, each map key is decoded as type/cpu/id, optional names are fetched from `perf_kwork_names`, class pointers are restored from the supported-list table, and aggregate timing fields are copied into the kwork model.

State and persistence: `skel`, `ts_start`, and `ts_end` are static. BPF maps retain timestamp, name, and report rows until cleanup. `kwork->timestart` and `kwork->timeend` are set from user-space monotonic timestamps, not from the BPF event timestamps.

Dependencies and integration: it relies on `util/kwork.h` class/report enums staying synchronized with the BPF enum and map structs in `kwork_trace.bpf.c`, libbpf map operations, perf CPU map parsing, and the `kwork->add_work` callback.

Risks: BPF map capacity `KWORK_COUNT` is fixed in the skeleton and may drop distinct work items in busy systems. Name filters reject names at or above `MAX_KWORKNAME`. Static class pointers in `kwork_class_bpf_supported_list` are session state. The read loop returns on first lookup/add error and can leak a duplicated name if downstream ownership assumptions change.

Test signals: run runtime and latency reports for IRQ, softirq, and workqueue classes; exercise CPU and name filters; compare BPF totals with tracepoint/raw perf outputs; and stress high-cardinality workqueues to observe map-capacity behavior.
