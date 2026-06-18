# sources/distributed-fs/ceph-client/include/trace/trace_custom_events.h

Purpose: Implements the multi-stage generator for custom trace events built with `TRACE_CUSTOM_EVENT`, `DECLARE_CUSTOM_EVENT_CLASS`, and `DEFINE_CUSTOM_EVENT`.

Important APIs/types/functions: Redefines custom-event macros across stages 1-7 to generate raw structs, offset structs, print functions, field metadata, callbacks, event classes, and event calls under a `custom` trace system.

Control flow: The file repeatedly includes `TRACE_INCLUDE(TRACE_INCLUDE_FILE)` under different macro definitions, mirroring `trace_events.h` but for custom events. Each pass produces a different piece of generated code.

State/persistence: Produces static metadata and generated callbacks; runtime state is limited to emitted trace records.

Dependencies/integration: Depends on `linux/trace_events.h`, all trace generation stages, and trace include-file conventions.

Risks: Macro ordering is fragile. Custom event class/call names must not collide, and generated callbacks must stay ABI-compatible with normal trace events.

Test signals: Build a custom trace event provider and verify format files, enable/disable behavior, and trace/perf record emission.
