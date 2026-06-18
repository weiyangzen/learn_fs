# sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-device.c

## Purpose
`v4l2-device.c` implements the core `struct v4l2_device` lifecycle and the registration lifecycle for `struct v4l2_subdev` objects attached to a V4L2 device. It is the central glue between a physical Linux `struct device`, V4L2 priority handling, subdevice lists, optional media-controller entities, and subdevice character nodes.

## Important APIs, Types, and Functions
The exported device APIs are `v4l2_device_register`, `v4l2_device_put`, `v4l2_device_set_name`, `v4l2_device_disconnect`, and `v4l2_device_unregister`. The subdevice APIs are `__v4l2_device_register_subdev`, `__v4l2_device_register_subdev_nodes`, and `v4l2_device_unregister_subdev`. Important state lives in `struct v4l2_device`: `subdevs`, `lock`, `prio`, `ref`, `dev`, `name`, `ctrl_handler`, optional `mdev`, and optional `release`. Important subdevice state includes `sd->v4l2_dev`, `sd->owner`, `sd->owner_v4l2_dev`, `sd->list`, `sd->entity`, `sd->devnode`, and `sd->internal_ops`.

## Control Flow
`v4l2_device_register` initializes the subdevice list, spinlock, priority state, and reference counter, takes a reference on the parent device with `get_device`, stores `dev`, and derives a device name if one was not already supplied. It also installs the V4L2 device as driver data if the parent has no driver data yet. `v4l2_device_disconnect` reverses only the parent-device association: it clears driver data if it points at this V4L2 device, drops the device reference, and nulls `v4l2_dev->dev`. `v4l2_device_unregister` is the full teardown path: it disconnects, iterates the subdevice list safely, unregisters each subdevice, asks I2C/SPI helpers to remove bus-created subdevices when flagged, and clears `name[0]` to make duplicate unregisters no-ops.

`__v4l2_device_register_subdev` validates inputs, handles module ownership, attaches the subdevice to the V4L2 device, merges the subdevice control handler into the device handler, registers a media entity when a media device is present, calls the subdevice `registered` internal op, and appends the subdevice to `v4l2_dev->subdevs` under `v4l2_dev->lock`. Failure unwinds media entity registration, module references, and `sd->v4l2_dev`. `__v4l2_device_register_subdev_nodes` walks registered subdevices with `V4L2_SUBDEV_FL_HAS_DEVNODE`, allocates a `video_device`, wires it to `v4l2_subdev_fops`, registers it as `VFL_TYPE_SUBDEV`, and creates an immutable media interface link when media-controller support is enabled. `v4l2_device_unregister_subdev` removes the subdevice from the list, calls `unregistered`, unregisters media entities and devnodes, or directly releases the subdevice when no node owns the release.

## State and Persistence Behavior
The file manages in-kernel object state only; there is no on-disk persistence. Persistent-looking state is lifetime and ownership state: parent device references, module use counts, media-controller entity registration, video minor allocation, `sd->devnode`, and list membership. The `v4l2_device` reference counter calls an optional driver `release` callback when the last reference is dropped. `name[0] == '\0'` is used as an idempotence marker after unregister.

## Dependencies and Integration Points
This code integrates with the device core (`get_device`, `put_device`, driver data), module reference counting, `v4l2-ctrls`, V4L2 priority helpers, `video_device` registration, subdevice fops, I2C/SPI subdevice unregister helpers, and media-controller entity/interface link APIs under `CONFIG_MEDIA_CONTROLLER`. It is called by bridge drivers and bus helpers when assembling a V4L2 graph.

## Risks
The main risks are lifetime and unwind bugs: missing module puts, double unregisters, stale `sd->v4l2_dev`, leaked media entities, or leaked `video_device` nodes. Subdevice list operations depend on `v4l2_dev->lock`, while callbacks can have driver-specific side effects. Registering subdev nodes partially can fail, and cleanup assumes registered nodes appear first in list order until the first subdevice with no `devnode`. Drivers must not pass unnamed subdevices or subdevices already bound to another V4L2 device.

## Test Signals
Useful tests are bridge-driver probe/remove cycles, subdevice registration failure injection at control merge, media entity registration, internal `registered`, and video node registration. Runtime signals include no leaked module references after remove, correct `/dev/v4l-subdev*` node creation for `HAS_DEVNODE`, idempotent `v4l2_device_unregister`, correct media graph links, and KASAN/KCSAN/lockdep clean teardown under hot-unplug.
