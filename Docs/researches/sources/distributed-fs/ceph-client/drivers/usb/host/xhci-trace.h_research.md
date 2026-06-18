# sources/distributed-fs/ceph-client/drivers/usb/host/xhci-trace.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/usb/host/xhci-trace.h` declares the xHCI host controller tracepoint set. The source was read as a complete 652-line file. It defines reusable event classes and concrete events for formatted debug messages, context structures, TRBs, virtual devices, URBs, stream contexts, endpoint contexts, slot contexts, input-control contexts, rings, port status/control, doorbells, and xHCI debug capability requests. These tracepoints give maintainers low-overhead observability into xHCI scheduling, command handling, device setup, hub state, and DbC gadget activity.

## Important APIs, Types, and Functions

Trace systems are declared as `TRACE_SYSTEM xhci-hcd` and `TRACE_SYSTEM_VAR xhci_hcd`. Event classes include `xhci_log_msg`, `xhci_log_ctx`, `xhci_log_trb`, `xhci_log_free_virt_dev`, `xhci_log_virt_dev`, `xhci_log_urb`, `xhci_log_stream_ctx`, `xhci_log_ep_ctx`, `xhci_log_slot_ctx`, `xhci_log_ctrl_ctx`, `xhci_log_ring`, `xhci_log_portsc`, `xhci_log_doorbell`, and `xhci_dbc_log_request`.

Concrete tracepoints include `xhci_dbg_address`, `xhci_dbg_context_change`, `xhci_dbg_quirks`, `xhci_dbg_reset_ep`, `xhci_dbg_cancel_urb`, `xhci_dbg_init`, `xhci_dbg_ring_expansion`, `xhci_address_ctx`, `xhci_handle_event`, `xhci_handle_command`, `xhci_handle_transfer`, `xhci_queue_trb`, DbC TRB events, virtual-device allocation/setup/stop/free events, URB enqueue/giveback/dequeue events, stream context events, endpoint/slot/control context command events, ring allocation/free/expansion/enqueue/dequeue events, port status events, host/endpoint doorbells, and DbC request allocation/free/queue/giveback events.

The event payloads snapshot xHCI and USB types including `struct va_format`, `struct xhci_hcd`, `struct xhci_container_ctx`, `struct xhci_ring`, `struct xhci_generic_trb`, `struct xhci_virt_device`, `struct urb`, `struct xhci_stream_info`, `struct xhci_ep_ctx`, `struct xhci_slot_ctx`, `struct xhci_input_control_ctx`, `struct xhci_port`, and `struct dbc_request`.

## Control Flow

The header has compile-time trace declaration flow rather than normal function flow. It sets up a multi-read-safe include guard, includes tracepoint and xHCI/DbC definitions, declares event classes with `TP_PROTO`, `TP_ARGS`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`, then maps many concrete `DEFINE_EVENT` tracepoints onto those classes. The final block intentionally sits outside the guard, sets `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE`, and includes `<trace/define_trace.h>` so the trace generator can produce definitions when included by `xhci-trace.c` with `CREATE_TRACE_POINTS`.

At runtime, callers elsewhere in the xHCI driver invoke generated `trace_xhci_*` functions. The tracepoint snapshots raw fields into trace entries and formats them through xHCI decoding helpers such as `xhci_decode_trb`, `xhci_decode_ep_context`, `xhci_decode_slot_context`, `xhci_decode_ctrl_ctx`, `xhci_decode_portsc`, `xhci_decode_doorbell`, and `xhci_ring_type_string`.

## State and Persistence Behavior

This header defines trace event schemas, not driver-owned persistent state. Runtime state is transient: each enabled event copies selected fields into kernel tracing buffers. The events deliberately record DMA addresses, virtual pointers, TRB words, port status words, URB lengths/status, ring enqueue/dequeue positions, context flags, and DbC request status at the moment of tracing, making later state changes irrelevant to the recorded entry.

## Dependencies and Integration Points

Direct dependencies are `<linux/tracepoint.h>`, `"xhci.h"`, and `"xhci-dbgcap.h"`. The file integrates with the Linux tracepoint/ftrace infrastructure, xHCI core decode helpers, USB core URB and endpoint helpers, and debug capability request structures. It is consumed by many xHCI implementation files through generated trace helpers, and by `xhci-trace.c` as the one definition unit.

## Risks and Edge Cases

Tracepoint payloads must avoid dereferencing invalid objects when callers pass partially initialized or teardown-path objects. Several events capture virtual pointers and DMA addresses; that is useful for debugging but sensitive in logs and only meaningful within the running kernel context. Formatting depends on decode helpers and buffer sizes such as `XHCI_MSG_MAX`; mismatches can reduce trace usefulness. The `TRACE_INCLUDE_PATH`/`TRACE_INCLUDE_FILE` placement is fragile and must remain outside the guard for trace generation. Schema changes affect user-space tracing scripts that parse xHCI trace events.

## Test Signals

Useful signals include successful xHCI build with tracing enabled, generated trace event files under tracefs for the `xhci-hcd` system, enabling TRB/URB/ring/port events during enumeration and transfer tests, DbC event coverage when debug capability support is active, and validation that decoded port/TRB/context strings match expected hardware state during command, transfer, suspend, and reset paths.
