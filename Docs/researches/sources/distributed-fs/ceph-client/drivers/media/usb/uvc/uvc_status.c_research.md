# sources/distributed-fs/ceph-client/drivers/media/usb/uvc/uvc_status.c

## Purpose
`uvc_status.c` implements the UVC driver's interrupt status endpoint handling. It receives asynchronous device notifications, dispatches streaming button/error events and control value-change events, and owns the lifetime of the status URB. When `CONFIG_USB_VIDEO_CLASS_INPUT_EVDEV` is enabled it also exposes compatible camera trigger buttons as a Linux input device reporting `KEY_CAMERA`.

## Important APIs, types, and functions
The public entry points are `uvc_status_init()`, `uvc_status_unregister()`, `uvc_status_cleanup()`, `uvc_status_resume()`, `uvc_status_suspend()`, `uvc_status_get()`, and `uvc_status_put()`. They operate on status fields in `struct uvc_device`: `int_ep`, `int_urb`, `status`, `status_lock`, `status_users`, `flush_status`, `input`, `input_phys`, and `async_ctrl`. `uvc_status_complete()` is the USB completion callback. `uvc_event_streaming()` handles streaming status packets. `uvc_event_control()` validates control status packets and calls `uvc_ctrl_status_event_async()` for value changes. The helper pair `uvc_event_find_ctrl()` and `uvc_event_entity_find_ctrl()` resolve the originator and selector in a status packet to a `struct uvc_control` inside a `struct uvc_video_chain`.

## Control flow
Initialization allocates `dev->status`, allocates `dev->int_urb`, computes the receive interrupt pipe, applies the high-speed interval quirk when requested, fills the URB, and optionally registers an input device. The status endpoint is demand-started: `uvc_status_get()` submits the URB when the first user arrives, increments `status_users`, and `uvc_status_put()` stops it when the last user leaves. Completion accepts only success and benign shutdown/unlink errors. On successful packets it switches on `bStatusType & 0x0f`; control events may transfer URB resubmission to the asynchronous control worker, while streaming events are handled inline and the URB is normally resubmitted in atomic context.

## State and persistence behavior
All persistent state is in memory and tied to the USB device lifetime. `status_users` is a reference count guarded by `status_lock`; it controls whether the interrupt URB is active across open/close and suspend/resume. `flush_status` is a cross-CPU stop flag coordinated with release stores to prevent the asynchronous control work item from requeuing the URB during stop. Input device registration persists from init until unregister; there is no disk persistence.

## Dependencies and integration points
This file integrates with USB core URBs, Linux input, the UVC control subsystem, and V4L2 device chains. It relies on `uvcvideo.h` structures, `uvc_ctrl_status_event_async()`, `uvc_ctrl_status_event()`, and the entity/control graph populated by UVC descriptor parsing. Runtime PM users in `uvc_v4l2.c` call `uvc_status_get()` and `uvc_status_put()` through `uvc_pm_get()`/`uvc_pm_put()`.

## Risks and edge cases
The highest-risk area is stop/resume ordering: `uvc_status_stop()` must cancel pending work, kill the URB, then cancel work again because completion can queue work during teardown. Incorrect memory ordering around `flush_status` can cause URB requeue races. Status packet validation is intentionally conservative; malformed control events are ignored. Input support depends on trigger descriptor bits, so devices with nonstandard button reporting may not expose an input device. URB resubmission failures are logged but leave the status path inactive.

## Test signals
Useful tests include open/close cycles that exercise `status_users`, suspend/resume with active users, unplug while status URB is active, cameras that emit control-change interrupts, and devices with physical shutter/snapshot buttons. Debug categories `STATUS` and input event traces should show valid button/control event flow. Race testing should focus on simultaneous status events and stream or file-handle teardown.
