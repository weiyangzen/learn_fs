# sources/distributed-fs/ceph-client/drivers/usb/core/notify.c

## Purpose
Provides the USB core notifier chain used by other kernel components to observe USB bus and device add/remove events. It is a small event fan-out layer around Linux blocking notifier infrastructure.

## Important APIs, Types, And Functions
The public registration APIs are `usb_register_notify()` and `usb_unregister_notify()`, both exported GPL symbols taking a `struct notifier_block`. Internal event emitters are `usb_notify_add_device()`, `usb_notify_remove_device()`, `usb_notify_add_bus()`, and `usb_notify_remove_bus()`. The single persistent object is `usb_notifier_list`, declared with `BLOCKING_NOTIFIER_HEAD`.

## Control Flow
Observers register a notifier block into the blocking chain. USB core callers invoke the add/remove helpers with either `struct usb_device *` or `struct usb_bus *`; the helper calls `blocking_notifier_call_chain()` with event IDs such as `USB_DEVICE_ADD`, `USB_DEVICE_REMOVE`, `USB_BUS_ADD`, and `USB_BUS_REMOVE`.

## State And Persistence
State is limited to the notifier chain list in memory. The blocking notifier implementation owns synchronization for registration and callback dispatch. No event history is persisted, and callbacks receive live object pointers whose lifetime is controlled by the caller's surrounding USB core path.

## Dependencies And Integration Points
Depends on `<linux/notifier.h>`, USB event constants and object types, and the core `usb.h` declarations. It integrates with enumeration/removal paths elsewhere in usbcore and with consumers that need coarse USB topology notifications.

## Risks And Test Signals
Risks are mostly callback context and lifetime assumptions: notifier clients must not sleep or recurse into USB teardown in unsafe ways beyond what a blocking notifier context allows, and unregistering must be paired with prior registration. Test signals include registering multiple callbacks, verifying event order during bus/device add/remove, module unload with notifier unregister, and lockdep checks for callbacks that take USB locks.
