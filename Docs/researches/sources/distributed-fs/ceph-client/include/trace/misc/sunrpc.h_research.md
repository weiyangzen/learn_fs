# sources/distributed-fs/ceph-client/include/trace/misc/sunrpc.h

Purpose: Defines shared SUNRPC trace printf specifiers for stable task/client identifiers.

Important APIs/types/functions: Exports `SUNRPC_TRACE_PID_SPECIFIER`, `SUNRPC_TRACE_CLID_SPECIFIER`, and `SUNRPC_TRACE_TASK_SPECIFIER`.

Control flow: SUNRPC tracepoint headers include this helper and embed the specifier macros in `TP_printk` strings. There is no runtime logic.

State/persistence: No state is stored; the file standardizes formatting.

Dependencies/integration: Depends only on tracepoint headers. Integrated with SUNRPC/NFS trace events that need consistent task and client id formatting.

Risks: Format-string changes affect trace ABI readability and tooling assumptions.

Test signals: Build SUNRPC trace events and inspect formatted task/client ids in trace output.
