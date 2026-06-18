# sources/distributed-fs/ceph-client/drivers/staging/greybus/gb-camera.h

## Purpose
Host-facing Greybus camera module API. It describes camera streams and CSI parameters and defines the operation callbacks used by the Greybus camera protocol driver to expose camera capabilities to another host camera component.

## Important APIs, Types, And Functions
Defines input/output flags `GB_CAMERA_IN_FLAG_TEST` and `GB_CAMERA_OUT_FLAG_ADJUSTED`. `struct gb_camera_stream` stores width, height, V4L2 media-bus pixel code, CSI virtual channel, data types, and frame size. `struct gb_camera_csi_params` stores lane count and clock frequency. `struct gb_camera_ops` declares capabilities, configure_streams, capture, and flush callbacks. `struct gb_camera_module` wraps private data, ops, interface ID, kref, release hook, and global list node. `gb_camera_call()` safely invokes callbacks.

## Control Flow
The header has no implementation flow. The expected lifecycle is that `camera.c` fills a `gb_camera_module`, registers it with `gb_camera_register()`, services callbacks through `gb_cam_ops`, and unregisters on disconnect.

## State And Persistence
No direct state. The struct layout defines in-memory registration and refcounting state for camera modules.

## Dependencies And Integration Points
Depends on `<linux/v4l2-mediabus.h>` for pixel codes and on Linux kref/list types through included kernel context. It bridges Greybus camera management to a host camera stack that consumes `gb_camera_module`.

## Risks
`gb_camera_call()` returns `-ENODEV` for a missing module and `-ENOIOCTLCMD` for a missing operation; callers must distinguish those. The API assumes callback implementers honor stream array bounds and update `nstreams`/flags consistently.

## Test Signals
Build users against callback signature changes. Exercise register/unregister lifetime, missing operation dispatch through `gb_camera_call()`, test-only stream configuration, adjusted stream outputs, and kref release behavior.
