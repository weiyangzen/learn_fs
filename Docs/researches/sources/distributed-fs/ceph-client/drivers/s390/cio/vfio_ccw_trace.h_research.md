## sources/distributed-fs/ceph-client/drivers/s390/cio/vfio_ccw_trace.h

Purpose: declares trace events for vfio-ccw channel-path and FSM diagnostics. It gives maintainers structured observability for device state transitions, async commands, I/O request failures, and channel path changes.

Important APIs/types/functions: `TRACE_EVENT()` definitions cover `vfio_ccw_chp_event`, `vfio_ccw_fsm_async_request`, `vfio_ccw_fsm_event`, and `vfio_ccw_fsm_io_request`. Each records subchannel id components plus event-specific fields such as path mask, command, state, event, fctl, errno, and error string.

Control flow: call sites pass raw state/action data to tracepoints; the header defines assignment and printk formatting. The bottom `TRACE_INCLUDE_PATH`, `TRACE_INCLUDE_FILE`, and `trace/define_trace.h` block follows kernel tracepoint conventions.

State and persistence: no mutable driver state is owned here. Trace records are transient unless tracing infrastructure buffers them.

Dependencies and integration: includes local `cio.h` and Linux tracepoint APIs. `vfio_ccw_private.h`, `vfio_ccw_drv.c`, and `vfio_ccw_fsm.c` use these tracepoints.

Risks and test signals: risks include format mismatch, pointer lifetime for `errstr`, and missing include-path correctness when moved. Test by enabling events, triggering start/halt/clear/errors/channel-path events, and verifying formatted output has correct subchannel ids and errno values.
