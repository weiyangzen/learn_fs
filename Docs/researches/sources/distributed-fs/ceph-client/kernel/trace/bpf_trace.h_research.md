<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/bpf_trace.h -->
# sources/distributed-fs/ceph-client/kernel/trace/bpf_trace.h

Purpose: declares the `bpf_trace` tracepoint system and the `bpf_trace_printk` trace event consumed by the BPF tracing helper implementation. It is intentionally small: it defines the trace event schema used to route formatted BPF trace-print messages through the kernel trace event machinery.

Important APIs and types: `TRACE_EVENT(bpf_trace_printk, TP_PROTO(const char *bpf_string), ...)` records a single dynamic string field named `bpf_string` and prints it with `TP_printk("%s", __get_str(bpf_string))`. `TRACE_SYSTEM`, `TRACE_INCLUDE_PATH`, and `TRACE_INCLUDE_FILE` connect this header to `<trace/define_trace.h>` when `CREATE_TRACE_POINTS` is defined by `bpf_trace.c`.

Control flow: when `bpf_trace.c` defines `CREATE_TRACE_POINTS` and includes this header, the tracepoint objects and trace event metadata are instantiated. At runtime, `bpf_trace_printk()` and `bpf_trace_vprintk()` format into a temporary buffer and call `trace_bpf_trace_printk(data.buf)`, which emits this event. The helper lookup path also schedules work to enable the event so users loading programs that call the helper can see output even if the event was disabled.

State and persistence: the header declares trace metadata only. Runtime event enablement state, ring-buffer records, and formatted message storage are owned by ftrace/tracefs infrastructure and by `bpf_trace.c` helper buffers; no durable state is held here.

Dependencies and integration points: depends on `<linux/tracepoint.h>` and the trace event macro system. It integrates directly with tracefs event naming as `bpf_trace/bpf_trace_printk`, and with the generated `trace_bpf_trace_printk()` callsite used in `kernel/trace/bpf_trace.c`.

Risks and test signals: risk is primarily ABI/schema drift: changing the event name, field name, or include path would break helper output visibility and tracefs consumers. Test signals are successful kernel trace event generation, `available_events` containing `bpf_trace:bpf_trace_printk`, BPF selftests or manual programs using `bpf_trace_printk`, and build coverage for trace header multi-read handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/bpf_trace.h -->
