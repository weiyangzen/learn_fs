# sources/distributed-fs/ceph-client/include/trace/stages/stage7_class_define.h

Purpose: Stage 7 supplies minimal macro definitions while defining final `trace_event_class` objects.

Important APIs/types/functions: Defines neutral `__entry`, IRQ-context helpers, namespace time printers, and `TP_printk` as a string wrapper so class definitions can reference print formats without generating print code again.

Control flow: `trace_events.h` expands event declarations under these macros to build event class metadata and associate print format strings/functions produced by earlier stages.

State/persistence: Produces static event class metadata; no mutable state is owned.

Dependencies/integration: Final stage in the trace event macro pipeline, feeding `trace_event_class` and `trace_event_call` definitions.

Risks: Macro defaults must be compatible with all event `TP_printk` bodies. Missing helper definitions can break otherwise valid trace headers.

Test signals: Full kernel build across diverse trace event headers; class registration succeeds and format strings are available.
