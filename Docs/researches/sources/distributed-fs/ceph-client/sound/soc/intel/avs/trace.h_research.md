# sources/distributed-fs/ceph-client/sound/soc/intel/avs/trace.h

Purpose: Declares AVS trace events for DSP core operations, IPC headers/payloads, and D0ix decisions, plus convenience macros for tracing requests, replies, and notifications.

Important APIs/types: `TRACE_EVENT(avs_dsp_core_op)`, event class `avs_ipc_msg_hdr`, derived events for request/reply/notify headers, conditional payload event `avs_ipc_msg_payload`, `TRACE_EVENT(avs_d0ix)`, helper declaration `trace_avs_msg_payload()`, and macros `trace_avs_request/reply/notify`.

Control flow role: IPC and platform code call these macros around message send/receive and power operations. Header events log primary/extension/status/error; payload events dump hex chunks; D0ix traces note ignored/proceeded transitions.

State and persistence: Events write to ftrace buffers only and do not mutate driver state.

Dependencies and integration: Uses Linux tracepoint macros and must keep `TRACE_INCLUDE_PATH`/`TRACE_INCLUDE_FILE` aligned with the file location for `define_trace`.

Risks: Trace macro arguments must be valid pointers and sizes. Payload dumps can leak sensitive firmware/control data to privileged trace consumers. Any field layout changes require trace format compatibility awareness.

Test signals: Kernel build with tracepoints, ftrace/perf visibility of `intel_avs:*`, payload chunk formatting, and D0ix/core-op event emissions during runtime PM and firmware IPC.
