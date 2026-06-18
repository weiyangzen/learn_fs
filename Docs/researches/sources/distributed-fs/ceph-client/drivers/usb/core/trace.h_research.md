# sources/distributed-fs/ceph-client/drivers/usb/core/trace.h

## Purpose
Declares usbcore trace events for logging key `struct usb_device` state snapshots during device allocation and state transitions.

## Important APIs, Types, And Functions
Defines trace system `usbcore`, event class `usb_core_log_usb_device`, and events `usb_set_device_state` and `usb_alloc_dev`. The event captures device name, `enum usb_device_speed`, `enum usb_device_state`, `bus_mA`, and authorization state, and prints speed/state strings using usbcore formatting helpers.

## Control Flow
Call sites pass a `struct usb_device *` to the trace event. `TP_fast_assign` copies fields from the live device into the ring buffer, and `TP_printk` formats them for trace readers. The include tail sets `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE` before including `<trace/define_trace.h>`.

## State And Persistence
The header does not store state itself. Captured event records live in tracing buffers according to ftrace/perf configuration.

## Dependencies And Integration Points
Depends on Linux tracepoint macros, USB type definitions, `dev_name()`, `usb_speed_string()`, and `usb_state_string()`. `trace.c` instantiates the declarations; usbcore state-management code can include and call the generated trace hooks.

## Risks And Test Signals
Risks include trace header include-path mistakes, stale field types if `struct usb_device` changes, dereferencing devices outside valid lifetime at call sites, and trace format changes affecting tools. Test signals include compiling with `TRACE_HEADER_MULTI_READ`, enabling both events, and confirming output during device allocation and state changes.
