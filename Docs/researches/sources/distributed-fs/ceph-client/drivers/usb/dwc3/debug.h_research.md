# sources/distributed-fs/ceph-client/drivers/usb/dwc3/debug.h

## Purpose
`debug.h` provides inline formatting helpers for DWC3 modes, commands, link states, endpoint/device events, TRB types, EP0 state, and command status values. It also declares debugfs lifecycle hooks when `CONFIG_DEBUG_FS` is enabled and provides no-op stubs otherwise.

## Important APIs, Types, and Functions
Important helpers include `dwc3_mode_string()`, `dwc3_gadget_ep_cmd_string()`, `dwc3_gadget_generic_cmd_string()`, `dwc3_gadget_link_string()`, `dwc3_gadget_hs_link_string()`, `dwc3_trb_type_string()`, `dwc3_ep0_state_string()`, `dwc3_gadget_event_string()`, `dwc3_ep_event_string()`, `dwc3_gadget_event_type_string()`, `dwc3_decode_event()`, `dwc3_ep_cmd_status_string()`, and `dwc3_gadget_generic_cmd_status_string()`. Debugfs APIs are `dwc3_debugfs_create_endpoint_dir()`, `dwc3_debugfs_remove_endpoint_dir()`, `dwc3_debugfs_init()`, and `dwc3_debugfs_exit()`.

## Control Flow
Most helpers are switch statements mapping register or event constants from `core.h` to stable human-readable strings. `dwc3_decode_event()` copies a raw 32-bit event into `union dwc3_event`, then dispatches to device-event or endpoint-event decoding based on `evt.type.is_devspec`. Endpoint event formatting includes EP number/direction, transfer status bits, control endpoint phase, stream status, and EP0 state where relevant.

## State and Persistence Behavior
The file has no persistent state. It formats caller-provided event/status values into caller-provided buffers. The debugfs declarations are compile-time integration points and become no-ops without debugfs support.

## Dependencies and Integration Points
It depends directly on `core.h` constants and event structures. It is consumed by trace/debug logging, `debugfs.c`, gadget command/event paths, and core role/debug paths. The header deliberately centralizes string conversion so diagnostic output stays consistent across tracepoints and debugfs.

## Risks
String helpers can drift from hardware constants, especially when new DWC3/DWC31/DWC32 event or TRB types are added. `dwc3_decode_event()` assumes the raw event layout in `union dwc3_event` matches hardware and compiler packing. Formatting truncation is bounded by `snprintf()`/`scnprintf()`, but callers must provide adequate buffers for diagnostic clarity.

## Test Signals
Useful checks include trace/debugfs output for device events, endpoint transfer events, stream events, EP0 phases, command status returns, TRB ring dumps, and link-state displays at high speed and SuperSpeed. Kconfig builds with and without debugfs should confirm the debugfs hooks compile to working functions or no-op stubs.
