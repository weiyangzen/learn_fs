# sources/distributed-fs/ceph-client/drivers/usb/core/hub.h

## Purpose

`hub.h` defines the private USB hub and USB port data structures shared by USB core hub-related source files. It captures the runtime state needed by `hub.c`, port-device code, Type-C integration, power management, status polling, event dispatch, and port-level sysfs state.

## Important APIs, Types, and Functions

`struct usb_hub` stores the hub interface device, hub USB device, reference count, interrupt URB, interrupt/status buffers, status mutex, consecutive error tracking, event/change/removed/wakeup/power/child-usage/warm-reset bitmaps, hub descriptor, transaction translator state, power budget, PM wake descendant count, lifecycle flags, hub quirk flags, indicator LED state/work, initialization and post-resume delayed work, hub event work, interrupt URB retry state, per-port pointer array, and onboard-device list.

`struct usb_port` represents one downstream port as a device. It stores the attached child `usb_device`, generic device, usbfs port owner, peer port, Type-C connector, PM QoS request, firmware/platform connection type, mirrored child device state and kernfs notification node, physical location token, status mutex, over-current count, port number, quirks, early-stop/ignore-event flags, SuperSpeed marker, and per-port USB3 LPM permission bits.

The header declares hub/port helpers implemented elsewhere: port device create/remove, port power control, hub lookup/refcounting, debounce, clear port feature, get port status, and port-power decoding. Inline helpers provide `to_usb_port()`, `hub_is_port_power_switchable()`, `hub_is_superspeed()`, `hub_is_superspeedplus()`, `hub_power_on_good_delay()`, and debounce variants for connected versus stable states.

## Control Flow

The header has no standalone runtime flow, but it fixes the call contract for hub lifecycle and event handling. `hub.c` allocates `struct usb_hub` during probe, fills descriptor and port arrays during configuration, schedules the declared work items during activation/resume/event processing, and releases the object through `hub_put()`. Port-device code allocates and registers `struct usb_port` objects and stores them in `hub->ports`, while `hub.c` updates `child`, `state`, PM references, and event counters as devices appear and disappear.

## State and Persistence Behavior

All state described here is runtime kernel memory. `struct usb_hub` persists for the bound lifetime of a hub interface and is kref-managed because work items can hold references after the interface path queues them. `struct usb_port` persists as a child device for each physical/logical hub port until hub disconnect. Bitmaps use one-based port numbers and assume `USB_MAXCHILDREN` fits in the single `unsigned long` storage, guarded by a preprocessor check. No file-backed persistence is defined; visible state is projected through devices, sysfs attributes, PM state, and connector/ACPI associations.

## Dependencies and Integration Points

The header depends on USB core declarations, Chapter 11 hub definitions, HCD types, Type-C connector types, and local `usb.h`. It is the shared structure boundary between `hub.c`, port-device implementation, USB Type-C attachment, ACPI/firmware port metadata, LED/indicator handling, onboard-device helpers, and runtime PM. The inline speed and power helpers embed descriptor interpretation that callers rely on for USB2 versus USB3 behavior.

## Risks and Test Signals

Risks include layout coupling across USB core files, one-based bitmap indexing mistakes, insufficient bitmap size if `USB_MAXCHILDREN` grows, stale `child` pointers across disconnect and runtime resume, unbalanced krefs around delayed work, and mismatched assumptions about when `descriptor` or `ports` are initialized. Test signals are compile coverage of all hub/port users, probe/disconnect under concurrent queued work, port sysfs state notifications, Type-C attach/detach on port child changes, USB3 LPM policy through per-port permit bits, and hubs with maximum port counts.
