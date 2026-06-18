# sources/distributed-fs/ceph-client/drivers/usb/typec/tipd/trace.c

Purpose: Instantiates the TPS6598x tracepoints declared in `trace.h` by defining `CREATE_TRACE_POINTS` before including the trace header.

Important APIs/types/functions: No functions are defined directly. The important interface is the tracepoint generation side effect from `<trace/define_trace.h>` included by `trace.h`.

Control flow and state: no runtime control flow beyond module/object initialization of generated tracepoint metadata. It contributes trace events such as TPS6598x IRQ, CD321x IRQ, TPS25750 IRQ, status, power status, and data status.

Persistence behavior: none. Trace enablement and buffers are handled by the kernel tracing subsystem.

Dependencies/integration points: must be built exactly once in the driver object so tracepoint symbols are emitted. It depends on `trace.h` and the Linux tracepoint build convention.

Risks: if this file is omitted from the build when tracing is enabled, call sites in `core.c` may fail to link or tracepoints may not be available. If included more than once with `CREATE_TRACE_POINTS`, duplicate symbol errors are possible.

Test signals: build/link with tracing enabled, and verify tracefs exposes the `tps6598x` events. Runtime hotplug, power-status updates, and data-status updates should produce events when enabled.
