# sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmb_dev_int.c

Purpose: IPMB slave device interface that queues incoming IPMB requests to userspace and sends responses over I2C/SMBus.

Important APIs, types, and functions: `struct ipmb_msg`, `struct ipmb_dev`, `ipmb_read()`, `ipmb_write()`, `ipmb_slave_cb()`, checksum/header validation, `ipmb_probe()`, and `ipmb_remove()`.

Control flow: probe allocates state, registers a per-adapter misc device, records `i2c-protocol` mode, and registers an I2C slave callback. The slave callback reconstructs messages byte-by-byte, prepending responder address, validates minimum length and checksum on STOP, and queues requests under a spinlock. Reads block until a queued request exists, pop one, and copy it to userspace. Writes copy a userspace response and send via raw `i2c_transfer()` or SMBus block write with a temporary client address.

State and persistence: request assembly buffer, queue list, atomic queue length, message index, spinlock, wait queue, file mutex, protocol mode, and misc device. Queue is in memory only and capped at 256.

Dependencies and integration: I2C slave framework, miscdevice, poll, wait queues, spinlocks, SMBus/I2C transfer APIs.

Risks and test signals: queue elements are not explicitly drained on remove, and checksum validation only covers checksum1. Tests should cover malformed/truncated/overlong messages, queue saturation, blocking/nonblocking reads, poll, I2C vs SMBus writes, copy faults, and remove cleanup.
