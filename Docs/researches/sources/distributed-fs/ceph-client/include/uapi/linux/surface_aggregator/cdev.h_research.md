# sources/distributed-fs/ceph-client/include/uapi/linux/surface_aggregator/cdev.h

## Purpose
Defines the `/dev/surface/aggregator` userspace ABI for direct Surface System Aggregator Module EC requests, notifier registration, event enable/disable, and event reads. It is mainly for debugging and development.

## Important APIs, Types, and Constants
`enum ssam_cdev_request_flags` defines `SSAM_CDEV_REQUEST_HAS_RESPONSE` and `SSAM_CDEV_REQUEST_UNSEQUENCED`. `struct ssam_cdev_request` carries target category/id, command id, instance id, flags, output status, user payload pointer/length, and response pointer/length. `struct ssam_cdev_notifier_desc` registers event categories with priority. `struct ssam_cdev_event_desc` describes registry commands and event IDs. `struct ssam_cdev_event` is the variable-length event read format. Ioctls are `SSAM_CDEV_REQUEST`, `SSAM_CDEV_NOTIF_REGISTER`, `SSAM_CDEV_NOTIF_UNREGISTER`, `SSAM_CDEV_EVENT_ENABLE`, and `SSAM_CDEV_EVENT_DISABLE`.

## Control Flow, State, and Persistence
Userspace submits request ioctls and may register notifiers, enable events, then read event records. Kernel state includes notifier registrations, event enablement, EC transaction queues, and response buffers.

## Dependencies and Integration Points
Depends on `<linux/ioctl.h>` and `<linux/types.h>`. Integrates with Surface aggregator core, EC transport, and misc-device userspace tooling.

## Risks and Test Signals
Risks include mutually exclusive response/unsequenced flags, packed pointer fields, invalid user buffers, and privileged EC access. Test invalid flag combinations, short buffers, event lifecycle register-enable-read-disable, and 32-bit compatibility.
