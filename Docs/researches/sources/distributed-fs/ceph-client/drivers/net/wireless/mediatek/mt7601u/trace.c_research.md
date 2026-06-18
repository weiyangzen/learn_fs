# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/trace.c

Purpose: Instantiates MT7601U tracepoints by defining `CREATE_TRACE_POINTS` and including `trace.h`. It is the single compilation unit that emits tracepoint storage and metadata for the driver.

Important APIs and functions: There are no callable driver functions. The important behavior is conditional inclusion guarded by `__CHECKER__`, avoiding tracepoint creation for sparse/checker contexts while normal builds instantiate all trace events declared in `trace.h`.

Control flow: Build-time only. When compiled, it expands `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, and `DEFINE_EVENT` definitions into tracepoint code.

State and persistence: Tracepoint definitions create kernel tracing metadata and callsites. They do not store persistent driver state by themselves.

Dependencies and integration points: Includes `linux/module.h` and local `trace.h`. Every `trace_*` call in MT7601U source files depends on this object being linked into the module.

Risks: Multiple files defining `CREATE_TRACE_POINTS` would cause duplicate symbols; this file correctly centralizes creation. If omitted from the build, trace calls would not resolve.

Test signals: Module build/link, ftrace/perf visibility of `mt7601u:*` events, and sparse builds with `__CHECKER__` are the main signals.
