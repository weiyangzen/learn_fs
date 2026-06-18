<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/mux.h -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/mux.h

## Purpose

`mux.h` is the private header for registered Type-C switch and mux device wrappers.

## Important APIs, Types, and Functions

It defines `struct typec_switch_dev` with a device and orientation `set` callback, `struct typec_mux_dev` with a device and mode `set` callback, container macros, device type externs, and type-test macros.

## Control Flow

There is no executable control flow. The definitions are consumed by `mux.c` and hardware drivers through the public registration APIs.

## State and Persistence Behavior

The wrappers are runtime device objects allocated in `typec_switch_register()` or `typec_mux_register()` and freed by their release callbacks. Driver-private state is stored through device driver data.

## Dependencies and Integration Points

It includes `linux/usb/typec_mux.h` and integrates the public Type-C mux API with local class/device implementation details.

## Risks and Test Signals

Risks are local API coupling between chip drivers and the core mux implementation. Test signals are compile coverage for all switch/mux drivers and runtime registration/unregistration with drvdata retrieval.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/mux.h -->
