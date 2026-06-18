# sources/distributed-fs/ceph-client/include/media/v4l2-async.h

## Purpose
Defines the V4L2 asynchronous subdevice matching and notifier API used to bind sensors/subdevices to bridge drivers when probe order is not fixed.

## Important APIs, Types, and Functions
`enum v4l2_async_match_type` supports I2C and firmware-node matching. `struct v4l2_async_match_desc`, `v4l2_async_connection`, notifier operations, `v4l2_async_notifier`, and `v4l2_async_subdev_endpoint` model waiting/done lists and parent/child notifiers. APIs initialize root/subdev notifiers, add fwnode/remote/I2C connections, add subdev endpoints, find a unique connection, register/unregister/cleanup notifiers, register sensor subdevices, and unregister subdevices.

## Control Flow
Bridge drivers initialize a notifier, add expected async connections, and register it. Subdevices register asynchronously; the framework matches them by fwnode or I2C, calls `bound`, moves entries between waiting/done lists, and calls root `complete` once all dependencies bind. Unregister invokes `unbind`; cleanup releases allocated connection resources.

## State and Persistence Behavior
Notifiers own waiting/done lists and parent relationships for the binding lifetime. Connection structs must embed `v4l2_async_connection` first when driver-specific types are used. Fwnode references acquired during add are released during cleanup.

## Dependencies and Integration Points
Depends on lists/mutexes, firmware nodes, I2C identity, V4L2 devices, and subdevices. It is central to camera sensor, bridge, and firmware graph integration.

## Risks
Forgetting cleanup leaks fwnode refs/connections. Incorrect first-member embedding breaks casts. Duplicate or non-unique subdevice connections cause ambiguous binding. Complete only runs for the root notifier, so child-notifier expectations must be explicit.

## Test Signals
Out-of-order bridge/sensor probe, fwnode remote matching, I2C matching, nested notifiers, endpoint list cleanup via `v4l2_subdev_cleanup()`, unbind on driver remove, and partial-bind failure unwinds.
