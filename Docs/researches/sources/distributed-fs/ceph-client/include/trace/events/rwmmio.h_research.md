# sources/distributed-fs/ceph-client/include/trace/events/rwmmio.h

Purpose: Defines tracepoints for raw MMIO read/write operations and post-read/post-write instrumentation. It helps debug register access ordering and values.

Important APIs/types/functions: `DECLARE_EVENT_CLASS(rwmmio_rw_template)` backs `rwmmio_write` and `rwmmio_post_write`. Standalone events `rwmmio_read` and `rwmmio_post_read` capture caller, MMIO address, width, and value or return value.

Control flow: Instrumented MMIO accessors emit write/read events before or after accessing registers. Post events can confirm ordering or values after barriers/relaxed operations depending on caller usage.

State and persistence: No state is owned. It observes transient register addresses, values, access widths, and call sites. Hardware registers hold the actual state.

Dependencies and integration points: Depends on tracepoints and symbol printing. It integrates with architecture MMIO access instrumentation, driver register debugging, and ftrace/perf.

Risks and test signals: Risks include leaking MMIO addresses/values, perturbing timing-sensitive register access, recursion from tracing backend MMIO, and width/value mismatch. Test read/write instrumentation on platform devices, relaxed vs ordered accessors, 8/16/32/64-bit widths, early boot constraints, and tracing during driver probe/remove.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/rwmmio.h` completely for this pass (108 lines, 2731 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/rwmmio.h_research.md`.
