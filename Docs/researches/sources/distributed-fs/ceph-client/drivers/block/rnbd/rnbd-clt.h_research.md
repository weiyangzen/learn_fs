# sources/distributed-fs/ceph-client/drivers/block/rnbd/rnbd-clt.h

## Purpose
Declares the RNBD client-side shared state, request context, queues, device/session objects, and exported functions used between the client core and sysfs layer.

## Important APIs, types, and functions
- `enum rnbd_clt_dev_state` defines `INIT`, `MAPPED`, `MAPPED_DISCONNECTED`, and `UNMAPPED`.
- `struct rnbd_iu` is the per-request/per-admin-message unit holding an RTRS permit, request or response buffer, sg table, worker, errno, wait completion, refcount, and inline scatterlist storage.
- `struct rnbd_clt_session` holds the RTRS session, wait queue, reconnect readiness, blk-mq tag set, queue-depth/segment limits, per-CPU requeue state, device list, protocol version, and session name.
- `struct rnbd_queue` binds blk-mq hardware contexts to RNBD requeue lists.
- `struct rnbd_clt_dev` holds one mapped disk's kobject, queue, hw queues, server device id, local IDA id, state, path, access mode, disk, sysfs symlink name, and unload work.
- Exports client core calls plus sysfs creation/destruction and symlink removal.

## Control flow
The header establishes the contract: sysfs creates and controls `rnbd_clt_dev` instances through exported functions, while the core embeds per-request `struct rnbd_iu` objects into blk-mq request private data and uses session/device fields to coordinate RTRS and block-layer state.

## State and persistence behavior
The structures are transient kernel state. Refcounts protect sessions and devices across sysfs calls, block-device opens, RTRS callbacks, and workqueue completions. `RNBD_INLINE_SG_CNT` depends on SG chaining support and affects request private data sizing.

## Dependencies and integration points
Includes Linux wait, inet, blk-mq, refcount APIs, `rtrs.h`, `rnbd-proto.h`, and `rnbd-log.h`. Its types are consumed by `rnbd-clt.c`, `rnbd-clt-sysfs.c`, and logging macros.

## Risks and test signals
Changing any field used by blk-mq private data, kobject release, or refcount paths can create lifetime bugs. Build coverage should include architectures with and without `CONFIG_ARCH_NO_SG_CHAIN`. Runtime tests should cover sysfs unmap while block devices are open and while admin message completions are pending.
