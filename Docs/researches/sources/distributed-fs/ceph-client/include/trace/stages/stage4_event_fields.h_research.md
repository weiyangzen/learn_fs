# sources/distributed-fs/ceph-client/include/trace/stages/stage4_event_fields.h

Purpose: Stage 4 emits trace event field metadata used by tracefs `format` files and event parsers.

Important APIs/types/functions: Defines `ALIGN_STRUCTFIELD` and field macros that call `trace_event_define_field()` for scalar, struct, array, dynamic, string, bitmask, cpumask, sockaddr, and relative fields.

Control flow: The trace generator expands `TP_STRUCT__entry` under these macros inside event-class field registration functions. Each macro registers field type, name, offset, size, signedness, and filtering behavior.

State/persistence: Registers metadata with trace event infrastructure; no event payload is stored here.

Dependencies/integration: Depends on `trace_event_define_field`, raw event structs, and trace filtering/format consumers.

Risks: Field names, offsets, and signedness are trace ABI. Mistakes break filters, perf/BPF decoders, and trace parsers.

Test signals: Compare generated `/sys/kernel/tracing/events/.../format` fields against expected struct layout and filtering behavior.
