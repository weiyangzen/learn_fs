# sources/distributed-fs/ceph-client/drivers/media/common/videobuf2/vb2-trace.c

Purpose: Instantiates and exports Videobuf2 tracepoints when kernel tracepoint support is enabled. The file has no queue logic itself; it creates the tracepoint definitions declared in `include/trace/events/vb2.h` so other vb2 code can emit and modules can observe buffer lifecycle events.

Important APIs, types, and functions: defines `CREATE_TRACE_POINTS` before including `<trace/events/vb2.h>`, then exports `vb2_buf_done`, `vb2_buf_queue`, `vb2_dqbuf`, and `vb2_qbuf` with `EXPORT_TRACEPOINT_SYMBOL_GPL()`. It includes `<media/videobuf2-core.h>` for vb2 type context required by the trace event header.

Control flow: build-time control from the Makefile includes this object only when `CONFIG_TRACEPOINTS=y`. At compile time, `CREATE_TRACE_POINTS` turns trace event declarations into definitions. At runtime, vb2 core paths invoke tracepoint callsites elsewhere; this file only provides the symbols those callsites and external modules reference.

State and persistence behavior: no persistent data or per-device state is managed here. Tracepoint state is handled by the kernel tracing subsystem, including enablement, probes, and ring buffers.

Dependencies and integration points: depends on the trace event declarations in `include/trace/events/vb2.h`, the vb2 core API header, and GPL tracepoint export infrastructure. Integrated through `videobuf2-common-objs` so tracepoints ship with vb2 core support when tracing is configured.

Risks and invariants: exactly one translation unit should define `CREATE_TRACE_POINTS` for `trace/events/vb2.h`; duplicating it would cause duplicate symbol definitions, while omitting it would leave tracepoints unavailable. Export names must match the trace event header and callsites. Conditional build rules must keep this file out when tracepoints are unavailable.

Test signals: build with tracepoints enabled and disabled. With tracing enabled, verify the four vb2 events appear under tracefs and fire during `VIDIOC_QBUF`, queue-to-driver, buffer completion, and `VIDIOC_DQBUF` paths. Module link tests should confirm GPL modules can attach to the exported tracepoints without unresolved symbols.
