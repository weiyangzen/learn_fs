# sources/distributed-fs/ceph-client/drivers/media/mc/mc-devnode.c

Purpose: generic `/dev/mediaX` character-device registration layer for media devices, including dynamic major allocation, minor bitmap management, open/unregister race protection, file-operation dispatch, and media bus registration.

Important APIs/types/functions: exported functions are `media_devnode_register()`, `media_devnode_unregister_prepare()`, and `media_devnode_unregister()`. Internal file ops wrap `read`, `write`, `poll`, `ioctl`, compat ioctl, `open`, and `release` by checking registration state and dispatching to `devnode->fops`.

Control flow: subsystem init allocates a character-device range and registers the media bus. Register finds a free minor under `media_devnode_lock`, initializes `struct device` and `cdev`, sets the registered flag, and calls `cdev_device_add()`. Open takes the same lock, verifies the registered bit, gets a device ref, and then calls driver open. Unregister prepare clears the registered bit to stop new opens, and unregister removes the cdev/device, clears minor allocation, and drops the final device ref.

State/persistence: global `media_dev_t`, `media_devnode_nums` bitmap, `media_devnode_lock`, and `media_debugfs_root` live for the module lifetime. Individual devnodes are refcounted by the device core.

Dependencies/integration: used by `mc-device.c` and depends on Linux cdev/device/bus APIs, media devnode/device headers, compat ioctl support, and debugfs cleanup.

Risks/test signals: race safety depends on clearing the registered flag before cdev deletion and pairing get/put device refs around open/release. Tests should cover minor exhaustion, open while unregistering, missing fops returning `-EINVAL`/`-ENOTTY`, poll after unregister returning error/hup, cdev add failure cleanup, and module init/exit cleanup.
