# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/trace.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/trace.h` declares Linux trace events for USB gadget UDC operations. It captures snapshots of `struct usb_gadget`, `struct usb_ep`, and `struct usb_request` state for common gadget, endpoint, and request APIs so failures and state transitions can be observed through kernel tracing. The source was read as a complete 299-line file for this report.

## Important APIs, Types, and Functions

The header sets `TRACE_SYSTEM gadget`, includes Linux tracepoint and USB gadget definitions, and declares three event classes. `udc_log_gadget` records gadget speed, max speed, state, power draw, OTG/HNP flags, quirks, self-powered/deactivated/connected flags, and a return code. It is reused by events such as `usb_gadget_set_state`, `usb_gadget_frame_number`, `usb_gadget_wakeup`, `usb_gadget_set_remote_wakeup`, `usb_gadget_set_selfpowered`, `usb_gadget_clear_selfpowered`, `usb_gadget_vbus_connect`, `usb_gadget_vbus_draw`, `usb_gadget_vbus_disconnect`, `usb_gadget_connect`, `usb_gadget_disconnect`, `usb_gadget_deactivate`, and `usb_gadget_activate`.

`udc_log_ep` records endpoint name, packet limits, streams, mult/burst, address, claimed/enabled flags, and return code. It backs endpoint events such as `usb_ep_set_maxpacket_limit`, `usb_ep_enable`, `usb_ep_disable`, `usb_ep_set_halt`, `usb_ep_clear_halt`, `usb_ep_set_wedge`, `usb_ep_fifo_status`, and `usb_ep_fifo_flush`. `udc_log_req` records endpoint name, request pointer, length/actual, scatter-gather counts, stream id, ZLP/short/no-interrupt flags, request status, and return code for allocation, free, queue, dequeue, and giveback events.

## Control Flow

The header has no ordinary runtime flow. When included normally, it declares tracepoint prototypes and event metadata. When included from `trace.c` with `CREATE_TRACE_POINTS`, the `DECLARE_EVENT_CLASS` and `DEFINE_EVENT` macros instantiate the actual tracepoints. Each event's `TP_fast_assign` copies fields from live gadget/endpoint/request objects into a trace entry, and `TP_printk` formats the stable trace output.

## State and Persistence Behavior

The file defines trace event schemas, not driver state. Trace records are transient and controlled by kernel tracing buffers. The copied fields make each event robust against later mutation of the underlying gadget, endpoint, or request except for the request pointer value intentionally logged for correlation.

## Dependencies and Integration Points

Dependencies include `<linux/types.h>`, `<linux/tracepoint.h>`, `<asm/byteorder.h>`, `<linux/usb/gadget.h>`, and `<trace/define_trace.h>`. `TRACE_INCLUDE_PATH .` and `TRACE_INCLUDE_FILE trace` bind the generated include machinery to this directory and file. The integration point is USB gadget core instrumentation rather than a single UDC driver.

## Risks and Edge Cases

Tracepoint field selection must track `struct usb_gadget`, `struct usb_ep`, and `struct usb_request` layout changes. Format strings need to match field types to avoid misleading trace output. Because events dereference live pointers in `TP_fast_assign`, callers must pass valid gadget, endpoint, and request objects. Include guard and `TRACE_HEADER_MULTI_READ` behavior must remain compatible with Linux trace event generation.

## Test Signals

Build coverage with tracing enabled is the primary signal. Runtime validation can enable `gadget:*` events in tracefs, run gadget bind/connect/endpoint/request operations, and confirm formatted output contains expected speed, state, endpoint, stream, request length, status, and return-code values.
