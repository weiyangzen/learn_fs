# sources/distributed-fs/ceph-client/include/rv/instrumentation.h

Purpose: Provides small tracepoint attach/detach macros for generated RV monitor instrumentation.

Important APIs/types/functions: `rv_attach_trace_probe(monitor, tp, rv_handler)` type-checks a trace callback and registers it, warning on failure. `rv_detach_trace_probe()` unregisters the callback.

Control flow and state: The macros bind monitor handlers to static tracepoints. Attach uses the tracepoint-generated `check_trace_callback_type_*` and `register_trace_*`; detach uses `unregister_trace_*`.

Dependencies and integration: Depends on Linux ftrace tracepoint APIs and generated trace event symbols. Used by generated DA/LTL monitor code during init/destroy.

Risks and test signals: Risks are handler signature drift, attach failure ignored beyond warning, and missing detach on module unload. Tests should build with tracepoint type checks, enable/disable monitors repeatedly, and inspect warning paths for failed registrations.
