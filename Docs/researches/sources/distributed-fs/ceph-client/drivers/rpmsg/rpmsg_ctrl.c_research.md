# sources/distributed-fs/ceph-client/drivers/rpmsg/rpmsg_ctrl.c

Purpose: rpmsg control character device. It exposes `/dev/rpmsg_ctrlN` for userspace to create endpoint char devices, request backend-created rpmsg channels, and release channels via ioctls.

Important APIs, types, and functions: `struct rpmsg_ctrldev` holds the backing `rpmsg_device`, cdev, device, and `ctrl_lock`. File ops are `rpmsg_ctrldev_open()`, `release()`, and `rpmsg_ctrldev_ioctl()`. The ioctl path accepts `struct rpmsg_endpoint_info` and handles `RPMSG_CREATE_EPT_IOCTL`, `RPMSG_CREATE_DEV_IOCTL`, and `RPMSG_RELEASE_DEV_IOCTL`. Probe/remove manage one control cdev per rpmsg control device.

Control flow: backend transports register a control rpmsg device, commonly through `rpmsg_ctrldev_register_device()`. Probe allocates a minor and control ID, initializes cdev, adds `rpmsg_ctrl%d`, and stores the control device in parent driver data. Open pins the device. Each ioctl copies endpoint info, builds `rpmsg_channel_info`, takes `ctrl_lock`, and either creates an endpoint char device below the control device, asks the backend to create a channel, or releases a channel. Remove serializes against ioctls, destroys all child endpoint devices, removes the cdev, and drops the reference.

State and persistence: state is runtime-only: IDA allocations, cdev lifetime, parent rpmsg pointer, and child endpoint devices. `ctrl_lock` serializes ioctl operations and removal.

Dependencies and integration points: depends on rpmsg core channel ops, `rpmsg_char.h` endpoint helpers, uapi `linux/rpmsg.h`, and `rpmsg_class`. Virtio and Qualcomm SMD create control rpmsg devices so userspace can instantiate endpoints.

Risks: the ioctl copies `struct rpmsg_endpoint_info` before switching on `cmd`, so even release/create-dev commands require a valid user pointer. If `CONFIG_RPMSG_CHAR` is disabled, endpoint creation returns `-ENXIO`. Backend create/release support is optional and can return `-ENXIO`. Removal relies on child endpoint destruction to wake blocked readers.

Test signals: open/close control devices, issue all three ioctls with valid and invalid user memory, create endpoint devices and communicate through them, create duplicate channels, release nonexistent channels, race removal with ioctl, and build with `CONFIG_RPMSG_CHAR` disabled.
