# sources/distributed-fs/ceph-client/drivers/usb/core/endpoint.c

## Purpose

`endpoint.c` creates and removes per-endpoint sysfs child devices for USB host endpoints. These devices expose descriptor-derived read-only attributes such as endpoint address, attributes, max packet size, polling interval, transfer type, and direction.

## Important APIs, Types, and Functions

- `struct ep_device` stores a pointer to the endpoint descriptor, the parent `struct usb_device`, and an embedded `struct device`.
- `usb_ep_attr()` creates simple descriptor field show functions for `bLength`, `bEndpointAddress`, `bmAttributes`, and `bInterval`.
- Custom sysfs attributes `wMaxPacketSize_show()`, `type_show()`, `interval_show()`, and `direction_show()` format decoded endpoint properties.
- `ep_dev_attrs`, `ep_dev_attr_grp`, and `ep_dev_groups` define the endpoint sysfs group.
- `usb_ep_device_type` identifies endpoint devices as `usb_endpoint` and uses `ep_device_release()` to free the allocation.
- `usb_create_ep_devs()` allocates/registers the endpoint device and stores it in `endpoint->ep_dev`.
- `usb_remove_ep_devs()` unregisters the device and clears `endpoint->ep_dev`.

## Control Flow

Endpoint device creation allocates `struct ep_device`, points `desc` at `endpoint->desc`, stores `udev`, sets the sysfs groups and device type, parents the device under the supplied parent, names it `ep_%02x` using `bEndpointAddress`, and calls `device_register()`. On success it enables async suspend on the endpoint device and records the created object in `endpoint->ep_dev`; on registration failure it calls `put_device()` so the release function frees memory.

Removal is intentionally small: if `endpoint->ep_dev` exists, `device_unregister()` drops it from the device model and `endpoint->ep_dev` is cleared. Memory is released later by the driver core through `ep_device_release()`.

## State and Persistence Behavior

The only persistent state is live kernel/device-model state: the `endpoint->ep_dev` backpointer and the allocated `ep_device`. Attribute values are not cached beyond the endpoint descriptor pointer; reads decode current descriptor values. There is no disk persistence.

## Dependencies and Integration Points

This file depends on the Linux device model, sysfs attribute groups, USB endpoint descriptor helpers (`usb_endpoint_type`, `usb_endpoint_maxp`, `usb_decode_interval`, `usb_endpoint_dir_in`, `usb_endpoint_xfer_control`), and endpoint lifecycle calls from configuration/interface setup and teardown code elsewhere in USB core.

## Risks and Edge Cases

- `ep_device::desc` points into the owning endpoint object, so teardown ordering must unregister endpoint devices before endpoint descriptor storage is freed.
- Attribute output is descriptor-derived and assumes valid descriptors; malformed descriptors may yield unusual but bounded strings.
- Registration failure relies on `put_device()` to release the allocation; double-removal is avoided by clearing `endpoint->ep_dev`.
- The endpoint child device must not outlive its parent interface/device hierarchy.

## Test Signals

Signals include sysfs endpoint directory creation after setting a configuration, correct read-only values for control/bulk/interrupt/isoc endpoints, interval formatting in microseconds vs milliseconds, endpoint directories disappearing on configuration reset or disconnect, and leak checks on `device_register()` failure injection.
