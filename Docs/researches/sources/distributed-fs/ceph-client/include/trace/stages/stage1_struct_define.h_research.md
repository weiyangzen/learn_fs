# sources/distributed-fs/ceph-client/include/trace/stages/stage1_struct_define.h

Purpose: Stage 1 of trace generation: converts `TP_STRUCT__entry` field macros into members of the raw trace event structure.

Important APIs/types/functions: Defines `__field`, `__field_ext`, `__field_struct`, `__array`, `__dynamic_array`, `__string`, `__vstring`, `__bitmask`, `__cpumask`, `__sockaddr`, and relative dynamic variants. Dynamic fields become `u32 __data_loc_*` or `__rel_loc_*` descriptors.

Control flow: `trace_events.h` includes this stage while redefining `DECLARE_EVENT_CLASS`; event headers are then expanded to build `struct trace_event_raw_<call>`.

State/persistence: Defines compile-time struct layout; no runtime state is mutated here.

Dependencies/integration: Relies on trace event macro protocol and the raw event structure generated in surrounding headers.

Risks: Field layout is ABI-critical for tracefs/perf/BPF consumers. Incorrect dynamic-data descriptors corrupt event decoding.

Test signals: Compile trace events with scalar, array, string, bitmask, cpumask, sockaddr, and relative fields; inspect generated `format` files.
