# sources/distributed-fs/coda/coda-src/volutil/vol-tracerpc.cc

## Purpose

`vol-tracerpc.cc` implements `S_TraceRpc`, a diagnostics RPC that toggles RPC2 tracing and returns trace-buffer/state output to the client. The complete 103-line file was read.

## Important APIs, Types, and Functions

The entry point is `S_TraceRpc(RPC2_Handle, SE_Descriptor *)`. It uses global `RPCTraceBufInited`, `RPC2_Trace`, `RPC2_InitTraceBuffer()`, `RPC2_DumpTrace()`, `RPC2_DumpState()`, and SMARTFTP transfer by file descriptor.

## Control Flow

On first call it initializes a 500-entry trace buffer and enables tracing. If initialized but disabled, it enables tracing. If already enabled, it dumps trace buffers and RPC2 state to a temporary file and disables tracing. Every call transfers a short status or dump file to the client.

## State and Persistence Behavior

The handler mutates in-memory RPC2 tracing globals only. No persistent files are kept after the temporary file closes.

## Dependencies and Integration Points

Dependencies include RPC2 tracing APIs, SMARTFTP side effects, and `volutil.h`. The client command is `volutil tracerpc [outfile]`.

## Risks and Test Signals

Risks include process-global trace toggling from an admin command, fixed buffer size, and potential large dumps. Tests should cover first-call initialization, enable-after-disable, dump-and-disable path, side-effect failures, and trace state after each call.
