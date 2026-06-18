# sources/distributed-fs/ceph-client/drivers/i2c/i2c-dev.c

Purpose: character-device frontend exposing adapters as `/dev/i2c-*` for userspace. It registers major `I2C_MAJOR`, creates class devices for adapters, implements read/write and ioctl APIs, and tracks adapter hotplug through bus notifiers.

Important APIs/types: `struct i2c_dev` ties an adapter to a `cdev` and device node. File operations are `i2cdev_read()`, `i2cdev_write()`, `i2cdev_ioctl()`, compat ioctl handling, open, and release. Ioctls cover `I2C_SLAVE`, `I2C_SLAVE_FORCE`, `I2C_TENBIT`, `I2C_PEC`, `I2C_FUNCS`, `I2C_RDWR`, `I2C_SMBUS`, `I2C_RETRIES`, and `I2C_TIMEOUT`.

Control flow: module init reserves device numbers, registers the class and bus notifier, then attaches existing adapters. Opening gets the adapter module reference and allocates an anonymous, unregistered `i2c_client`. Raw read/write require `I2C_FUNC_I2C` and use the current client address. `I2C_RDWR` copies an array of messages and user buffers, enforces count and 8192-byte length limits, handles `I2C_M_RECV_LEN`, marks DMA-safe buffers, transfers, and copies reads back.

State and persistence: `i2c_dev_list` maps minors to adapters under a spinlock. Per-open state is the anonymous client with address, 10-bit, and PEC flags. Ioctls can mutate adapter timeout and retries globally for all users of that adapter.

Dependencies and integration: depends on I2C core adapter lookup, bus notifications, cdev/class APIs, compat ABI translation, uaccess, and SMBus helpers.

Risks: userspace can talk to arbitrary addresses, and `I2C_SLAVE_FORCE` bypasses busy checks. Busy checks deliberately allow unbound registered devices. Adapter timeout/retry mutation is shared state. Message length and receive-length validation are critical for user-copy safety.

Test signals: device-node creation/removal on adapter hotplug, ioctl ABI and compat tests, forced and non-forced address selection, 8192-byte caps, `I2C_M_RECV_LEN` validation, adapter removal while FDs are open, and timeout/retry side effects.
