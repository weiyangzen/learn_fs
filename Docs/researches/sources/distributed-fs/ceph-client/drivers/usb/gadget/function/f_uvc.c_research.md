# sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_uvc.c

## Purpose
This file implements the USB Video Class gadget function named `uvc`. It bridges USB UVC control and streaming state to a V4L2 video-output device so userspace can provide video frames and respond to UVC control requests. Most format/frame descriptors come from configfs, while this file builds the standard interface, endpoint, and copied descriptor arrays required by the composite framework.

## Important APIs, types, and functions
`uvc_alloc_inst()` initializes default camera, processing, output terminal, control descriptor arrays, streaming endpoint defaults, and attaches the UVC configfs tree. `uvc_alloc()` creates `struct uvc_device`, resolves configfs streaming headers, snapshots descriptor pointers, and wires the `usb_function` callbacks. `uvc_function_bind()` clamps endpoint options, autoconfigures interrupt and streaming endpoints, assigns strings/interfaces, copies descriptors for each speed using `uvc_copy_descriptors()`, preallocates the EP0 control request, initializes V4L2 and video state, and registers the video node. `uvc_function_setup()`, `uvc_function_set_alt()`, and `uvc_function_disable()` translate USB events to V4L2 events. `uvc_function_setup_continue()`, `uvc_function_connect()`, and `uvc_function_disconnect()` are exported to the UVC userspace/video side.

## Control flow
On bind, the function normalizes streaming interval, max packet, and max burst, computes HS multiplier and SS companion fields, autoconfigures the highest applicable streaming endpoint to reserve UDC resources, assigns endpoint addresses into all speed descriptors, resolves extension-unit string IDs, attaches fallback strings, allocates control and streaming interface IDs, deep-copies descriptors, allocates EP0 request storage, registers V4L2, initializes `uvc_video`, and registers a V4L2 video device. Class-specific setup requests are not answered directly; they are queued as `UVC_EVENT_SETUP`, and OUT data stages later queue `UVC_EVENT_DATA`. Streaming alt 1 enables the video endpoint and queues `UVC_EVENT_STREAMON`; alt 0 queues `UVC_EVENT_STREAMOFF`; both use delayed status so userspace can coordinate completion.

## State and persistence
Configfs `struct f_uvc_opts` owns descriptor templates, extension-unit lists, endpoint knobs, optional string indexes, and refcount state. Runtime `struct uvc_device` tracks connection state, function unbind state, interface IDs, endpoint pointers, EP0 buffers, V4L2 device/video device objects, wait queues, and video streaming state. No durable persistence exists; state is rebuilt from configfs on function allocation and bind.

## Dependencies and integration points
The file depends on Linux USB gadget/composite APIs, V4L2 device and event APIs, UVC class descriptors, and local `uvc_configfs`, `uvc_v4l2`, and `uvc_video` helpers. It integrates with userspace through `/dev/video*`, V4L2 events, and ioctls such as the response path that eventually calls `uvc_function_setup_continue()`. It registers as the `uvc` USB function.

## Risks and edge cases
Descriptor copying assumes configfs control and streaming descriptor graphs are complete and linked; missing descriptors fail allocation. Endpoint options are clamped but still rely on the UDC supporting the requested resources. Unbind is complex: it waits for clean userspace disconnect and video-device release to avoid use-after-free, so regressions can deadlock or delay teardown. Control requests larger than `UVC_MAX_REQUEST_SIZE` are stalled. The delayed-status model requires userspace participation; absent or crashed userspace can stall host-visible control/stream transitions.

## Test signals
Test configfs descriptor graph creation and missing-header failures, enumeration at FS/HS/SS/SSP, interrupt endpoint enabled/disabled modes, extension-unit descriptor copying, UVC control GET/SET event delivery, userspace response completion, stream on/off altsetting with delayed status, disconnect while userspace holds the video node, and endpoint max packet/max burst combinations on different UDCs.
