# sources/distributed-fs/ceph-client/sound/soc/intel/avs/trace.c

Purpose: Defines AVS tracepoints and provides a helper to split IPC payloads into trace-safe chunks.

Important APIs/functions: `CREATE_TRACE_POINTS` instantiates events declared in `trace.h`. `trace_avs_msg_payload()` chunks arbitrary payloads by `MAX_CHUNK_SIZE` and emits `trace_avs_ipc_msg_payload()`.

Control flow: The helper loops over remaining bytes, emits each chunk with offset and total size, then advances until the full payload has been traced. `MAX_CHUNK_SIZE` is calculated to keep formatted hex dumps within a page-sized trace event budget.

State and persistence: No persistent state. Trace data is emitted into the kernel tracing subsystem.

Dependencies and integration: Depends on `trace.h`, kernel tracepoint infrastructure, `PAGE_SIZE`, and the AVS IPC tracing macros used by lower IPC code.

Risks: Payload tracing can be high-volume and may expose firmware/control payload data to trace readers. Chunk-size math depends on trace header overhead assumptions. Null data/zero size is filtered by the trace event condition.

Test signals: Enable tracepoints while sending IPC with no payload, small payload, and multi-page payload; verify offsets and total sizes in trace output.
