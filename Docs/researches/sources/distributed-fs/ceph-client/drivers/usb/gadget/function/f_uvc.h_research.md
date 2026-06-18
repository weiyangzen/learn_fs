# sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_uvc.h

## Purpose
This header exposes the small cross-module control surface for the UVC gadget function. It forward-declares `struct uvc_device` and declares helpers used by the UVC V4L2/video implementation to resume delayed USB control handling and to publish userspace-driven connect/disconnect state to the USB composite function.

## Important APIs, types, and functions
The declared functions are `uvc_function_setup_continue(struct uvc_device *uvc, int disable_ep)`, `uvc_function_connect(struct uvc_device *uvc)`, and `uvc_function_disconnect(struct uvc_device *uvc)`. The first continues a delayed EP0 setup transaction and can disable the video endpoint first. The connect/disconnect helpers call into `usb_function_activate()` and `usb_function_deactivate()` in the implementation.

## Control flow
The header is included by UVC support files that do not need the full function implementation. Userspace-facing V4L2 code can receive a UVC event, prepare a response, and call back into `uvc_function_setup_continue()` after queuing the EP0 response. V4L2 open/close or stream lifecycle code can call connect/disconnect to let the host see the function become active or inactive.

## State and persistence
No state is defined here. All state is opaque behind `struct uvc_device` and owned by `f_uvc.c` plus the local UVC video/V4L2 modules.

## Dependencies and integration points
This is an internal header for the USB gadget function directory. It intentionally avoids including USB or V4L2 headers, reducing dependency spread and preserving encapsulation around `struct uvc_device`.

## Risks and edge cases
Because the functions operate on an opaque pointer, callers must only pass live `struct uvc_device` objects. Calling these helpers after unbind or without respecting the UVC locking/connection protocol can race teardown, though `f_uvc.c` includes guards for the disconnect path.

## Test signals
Compile coverage is the main signal. Runtime tests should verify that V4L2 response paths continue delayed EP0 setup successfully and that connect/disconnect helpers handle normal and unbind-adjacent paths without use-after-free.
