<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/catpt/trace.h -->
# sources/distributed-fs/ceph-client/sound/soc/intel/catpt/trace.h

## Purpose
Tracepoint definitions for CATPT IRQ and IPC diagnostics, including request/reply/notification headers and optional payload hex dumps.

## APIs, Types, and Functions
Defines trace system `intel_catpt`, event class `catpt_ipc_msg`, events `catpt_irq`, `catpt_ipc_request`, `catpt_ipc_reply`, `catpt_ipc_notify`, and conditional event `catpt_ipc_payload`. The payload event stores a dynamic byte array and prints a hex dump when data and size are non-zero.

## Control Flow, State, and Persistence
The header has no driver state. `device.c` defines `CREATE_TRACE_POINTS` before including it, while IPC paths call tracepoints around MMIO header reads/writes and payload copies. Trace data is transient through ftrace/perf rather than persisted by the driver.

## Dependencies and Integration
Depends on Linux tracepoint infrastructure and must keep `TRACE_INCLUDE_PATH`/`TRACE_INCLUDE_FILE` aligned with the local header. Used primarily by `ipc.c` and included once with tracepoint creation by `device.c`.

## Risks and Test Signals
Risks include trace header include-path breakage if files move, payload trace overhead when enabled, and accidental mismatch between traced headers and actual mailbox direction. Test signals are successful build of trace events, visible events under `/sys/kernel/tracing/events/intel_catpt`, and correlated request/reply/payload traces during firmware boot and stream operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/catpt/trace.h -->
