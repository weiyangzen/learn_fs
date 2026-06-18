# sources/distributed-fs/ceph-client/drivers/usb/typec/ucsi/trace.c

Purpose: Instantiates UCSI tracepoints and supplies string decoders for UCSI command and altmode recipient IDs.

Important APIs/types/functions: `ucsi_cmd_str` maps raw command opcodes to names for core trace output. `ucsi_recipient_str` maps UCSI altmode recipients to port/partner/plug strings. `CREATE_TRACE_POINTS` causes trace events declared in `trace.h` to be generated.

Control flow and state: no driver state. Runtime trace formatting indexes static string tables from command/recipient values. The command helper clamps unknown command IDs to index 0; recipient helper directly indexes its table.

Persistence behavior: none; trace state is owned by ftrace/tracefs.

Dependencies/integration points: includes `ucsi.h` for command constants and `trace.h` for tracepoint declarations. Built conditionally by the Makefile for `CONFIG_TRACING`.

Risks: `ucsi_recipient_str` does not bounds-check recipient values, so malformed trace calls could index outside the table. Command table coverage stops at `GET_ERROR_STATUS`; newer commands trace as unknown unless extended.

Test signals: build with tracing enabled, enable UCSI events, run core commands and altmode registration, and verify readable command/recipient names in trace output including unknown command fallback.
