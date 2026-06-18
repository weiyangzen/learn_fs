# sources/distributed-fs/ceph-client/drivers/usb/serial/usb-wwan.h

## Purpose
`usb-wwan.h` declares the shared helper API and private data structures used by USB wireless WAN modem subdrivers. It centralizes multi-URB buffering, modem control, and PM-related state for drivers that include `usb_wwan.c`.

## Important APIs, Types, and Functions
The header declares exported helpers for DTR/RTS, open/close, port probe/remove, write/write-room/chars-in-buffer, TIOCM get/set, and optional suspend/resume. Constants define four IN URBs, four OUT URBs, and 4096-byte input/output buffers. `struct usb_wwan_intf_private` tracks interface suspend state, feature flags `use_send_setup` and `use_zlp`, in-flight writes, open-port count, and an opaque private pointer. `struct usb_wwan_port_private` owns input/output URBs and buffers, an output busy bitset, delayed anchor, signal-state booleans, and tx start timestamps.

## Control Flow, State, and Persistence
The header itself has no execution path, but it defines the state contract that subdrivers must allocate and initialize before calling the helper functions. Interface-private flags control whether CDC `SET_CONTROL_LINE_STATE` requests are sent and whether outbound URBs use zero-length packets. Port-private state supports concurrent write URBs, delayed write queuing while suspended, and modem signal reporting.

All state is volatile per device/interface/port and is freed by the companion implementation during port remove or disconnect.

## Dependencies and Integration Points
It depends on USB serial core type definitions and PM types. Subdrivers must include this header, allocate `usb_wwan_intf_private` as serial data, and use the declared callbacks in their `usb_serial_driver` structures.

## Risks and Test Signals
Risks are contract mismatches: a subdriver can forget to initialize `susp_lock`, feature flags, or serial/port data before using helpers. The header exposes fields directly, so locking discipline is partly caller-dependent. Test signals include compile coverage for CONFIG_PM and non-PM builds, helper consumers allocating both private structures, and runtime tests for send-setup and zero-length-packet feature flags.
