# sources/distributed-fs/ceph-client/include/media/v4l2-device.h

Purpose: declares the parent `v4l2_device` object that groups video nodes and subdevices, owns device-level control/priority state, and provides subdevice registration, notification, request capability checks, and bulk subdevice operation fanout macros.

Important APIs/types: `struct v4l2_device` contains parent `struct device`, optional `media_device`, `subdevs` list, spinlock, unique name, driver notification callback, device-level control handler, priority state, kref, and release callback. Lifecycle APIs include `v4l2_device_register()`, `v4l2_device_set_name()`, `v4l2_device_disconnect()`, `v4l2_device_unregister()`, `v4l2_device_get()`, and `v4l2_device_put()`. Subdevice APIs include `v4l2_device_register_subdev()`, `__v4l2_device_register_subdev()`, `v4l2_device_unregister_subdev()`, and subdev-node registration helpers for full or read-only userspace access.

Control flow: a bridge driver registers the `v4l2_device`, then registers subdevices so the core links them into `subdevs` and pins their modules. Drivers can expose subdev device nodes when `CONFIG_VIDEO_V4L2_SUBDEV_API` is enabled. Notifications go from a subdevice to the bridge through `v4l2_subdev_notify()`. Bridge-wide operations use macros such as `v4l2_device_call_all()`, `v4l2_device_call_until_err()`, mask variants, and `v4l2_device_has_op()` to iterate the subdevice list and dispatch a selected ops group member.

State and persistence: the parent object keeps the authoritative subdevice list and refcount. `v4l2_device_disconnect()` sets `dev` to NULL for hot-unplug safety. Fanout macros assume subdevices cannot be added or removed during iteration. `v4l2_device_supports_requests()` is derived from an attached media device with `mdev->ops->req_queue`.

Dependencies and integration: includes `media-device.h`, `v4l2-subdev.h`, and `v4l2-dev.h`. It binds the media controller, V4L2 subdevice API, video-device nodes, control handlers, priority handling, and media requests.

Risks: concurrent subdevice list mutation during macro iteration; ignoring `-ENOIOCTLCMD` behavior in until-error macros; stale parent pointers after USB disconnect if `v4l2_device_disconnect()` is missed; module lifetime bugs when subdev registration fails; and request support being advertised only when the media device ops are fully initialized.

Test signals: parent registration with and without a real parent `struct device`, name instance generation, subdev register/unregister idempotence, full and read-only subdev-node registration under config gates, notification callback delivery, group-id and mask fanout filtering, error propagation for until-error macros, and request support detection.
