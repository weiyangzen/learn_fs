# sources/distributed-fs/ceph-client/drivers/usb/core/offload.c

## Purpose
Tracks active USB transfer offload users on a device tree so runtime power-management paths can detect when another entity is handling USB traffic and avoid unstable PM transitions.

## Important APIs, Types, And Functions
Exports `usb_offload_get()`, `usb_offload_put()`, `usb_offload_check()`, and `usb_offload_set_pm_locked()`. The relevant `struct usb_device` fields are `offload_usage`, `offload_pm_locked`, `offload_lock`, child topology, and the embedded `struct device` runtime PM state.

## Control Flow
`usb_offload_get()` takes a USB device reference, requires the runtime PM device to be active via `pm_runtime_get_if_active()`, checks `offload_pm_locked` under `offload_lock`, increments `offload_usage`, then drops runtime PM and USB references. `usb_offload_put()` follows the same active-device and lock checks, decrementing only if usage is nonzero. `usb_offload_check()` must be called with the device lock held; it returns true for local usage or recursively locks and checks child devices. `usb_offload_set_pm_locked()` flips the lock flag under the spinlock.

## State And Persistence
State is volatile per-device memory. `offload_usage` is a reference-style activity count, while `offload_pm_locked` freezes modifications during PM critical sections. There is no persistent storage or sysfs surface in this file.

## Dependencies And Integration Points
Depends on usbcore device references, hub child iteration, runtime PM, and spinlock/device-lock ordering. It integrates with PM code that must first mark a subtree locked, then call `usb_offload_check()` for a stable view of offload activity.

## Risks And Test Signals
Risks include usage leaks if get/put users are imbalanced, false negatives if callers fail to lock the full subtree before recursive checks, `-EBUSY` behavior for suspended devices, and deadlocks from inconsistent parent/child lock ordering. Test signals include get/put on active vs suspended devices, PM-locked rejection returning `-EAGAIN`, recursive child activity detection, concurrent offload toggling during suspend, and lockdep/KCSAN coverage.
