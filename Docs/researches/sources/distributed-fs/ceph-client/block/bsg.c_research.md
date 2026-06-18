# sources/distributed-fs/ceph-client/block/bsg.c

Purpose: implements the userspace-facing BSG character device layer for SG v4 passthrough. It registers the `bsg` class/major, creates character devices, handles legacy sg ioctls, and forwards SG_IO or io_uring commands to queue-specific callbacks.

Important APIs and functions: `struct bsg_device` stores the backing request queue, device and cdev, queue limits visible to userspace, timeout/reserved-size settings, and SG_IO/io_uring callbacks. Public functions are `bsg_register_queue()` and `bsg_unregister_queue()`. Core routines include `bsg_timeout()`, `bsg_sg_io()`, `bsg_open()`, `bsg_release()`, `bsg_ioctl()`, `bsg_check_uring_features()`, `bsg_uring_cmd()`, `bsg_device_release()`, `bsg_devnode()`, and init `bsg_init()`.

Control flow: `bsg_init()` registers the class and char-device range. A caller registers a queue, gets a minor from an IDA, initializes a cdev/device, and optionally links `/sys/block/<disk>/queue/bsg` to the device. Open pins the request queue with `blk_get_queue()`. Ioctl handles SG queue depth, version, timeout, reserved size, `SG_IO`, and rejects unsupported `SCSI_IOCTL_SEND_COMMAND`. SG_IO copies `sg_io_v4`, checks guard byte `Q`, calls the queue callback, and copies the modified header back. io_uring passthrough requires big SQE/CQE support and a queue callback.

State and persistence: state is per registered BSG device and includes minor allocation, queue reference lifetime, timeout, max queue, and reserved size. It is removed by `bsg_unregister_queue()` and freed by device release.

Dependencies and integration points: integrates with `bsg-lib.c`, block request queues, Linux cdev/device model, sysfs, io_uring command infrastructure, SCSI sg ioctl compatibility, and queue maximum bytes.

Risks and test signals: queue lifetime during open/unregister, IDA minor cleanup, sysfs link cleanup, userspace copy failures, timeout conversions, and io_uring feature validation are important. Test SG_IO with valid/invalid guard, reserved-size bounds, timeout set/get, concurrent unregister/open, io_uring without required features, queues without uring callback, and sysfs bsg link creation/removal.
