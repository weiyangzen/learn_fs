# `sources/distributed-fs/ceph-client/include/linux/usb/onboard_dev.h`

## Purpose

`onboard_dev.h` declares helpers for creating and destroying platform devices that represent onboard USB devices attached below a USB parent device.

## Important APIs, Types, and Constants

- `onboard_dev_create_pdevs(struct usb_device *parent_dev, struct list_head *pdev_list)` creates platform devices for onboard children.
- `onboard_dev_destroy_pdevs(struct list_head *pdev_list)` tears them down.
- Stubs are no-ops when `CONFIG_USB_ONBOARD_DEV` is disabled.

## Control Flow and Lifetimes

Hub or USB core code calls create when a parent USB device appears and destroy during disconnect/removal. The caller supplies a list to track created platform devices for later cleanup.

## State and Persistence Behavior

Runtime state is the list of created platform devices. The header has no persistent state and compiles to no-op behavior without onboard-device support.

## Dependencies and Integration Points

It integrates USB device enumeration with platform drivers for fixed onboard components, often described by firmware. It uses `struct usb_device` and `struct list_head`.

## Risks and Edge Cases

Create/destroy calls must be paired to avoid leaked platform devices. Callers must handle disabled-config stubs. Disconnect ordering matters because child platform devices may still hold references to resources under the USB parent.

## Test Signals

Build with and without `CONFIG_USB_ONBOARD_DEV`, enumerate boards with onboard USB child devices, verify platform child creation/removal, hot unplug parent hubs, and check leak/refcount diagnostics.
