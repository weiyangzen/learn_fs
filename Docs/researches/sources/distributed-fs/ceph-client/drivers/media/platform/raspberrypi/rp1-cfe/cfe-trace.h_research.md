# sources/distributed-fs/ceph-client/drivers/media/platform/raspberrypi/rp1-cfe/cfe-trace.h

Purpose: tracepoint definitions for RP1 CFE, CSI-2, and PiSP FE runtime diagnostics.

Important APIs/types/functions: declares `TRACE_SYSTEM cfe`, events for returned buffers, buffer prepare/queue/schedule/complete, frame start/end, job preparation, CSI-2 IRQs, and FE IRQs. It duplicates CSI-2 status bit definitions needed for trace formatting and ends with `TRACE_INCLUDE_FILE` pointing back to this header.

Control flow: compiled into tracepoint callsites when included with `CREATE_TRACE_POINTS` in `cfe.c`; other files include it for trace event declarations.

State and persistence: tracepoints do not own driver state; emitted records are consumed by ftrace/perf infrastructure.

Dependencies and integration: depends on Linux tracepoint API and vb2 types. Events are called from `cfe.c`, `csi2.c`, and `pisp-fe.c`.

Risks: trace include path is relative and must remain valid under kernel trace generation. Format strings expose assumptions about buffer index, frame counters, and CSI-2 status bit meanings.

Test signals: kernel builds with trace events enabled, `trace-cmd list | grep cfe`, and runtime capture showing schedule, IRQ, and completion events in expected order.
