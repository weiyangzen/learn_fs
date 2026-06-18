## sources/distributed-fs/ceph-client/include/linux/bsg.h

**Purpose:** This header exposes the higher-level BSG character-device queue registration API for request queues that accept SG_IO v4 and io_uring command paths.

**Important APIs/types/functions:** `bsg_sg_io_fn` handles `struct sg_io_v4` requests with write-open and timeout context. `bsg_uring_cmd_fn` handles `struct io_uring_cmd` with issue flags and write-open state. `bsg_register_queue()` binds a request queue to a parent device/name and callbacks, returning an opaque `struct bsg_device *`. `bsg_unregister_queue()` tears it down.

**Control flow, state, persistence:** The header defines an entry/exit contract only. Runtime state is owned by the BSG core and block queue. Registered callbacks are invoked when userspace submits passthrough commands; unregister must coordinate with in-flight users.

**Dependencies/integration:** Includes UAPI `linux/bsg.h` for `sg_io_v4`. It integrates with block request queues, device model parentage, and io_uring passthrough.

**Risks and test signals:** Risks are callback ABI mismatches, queue lifetime races during unregister, permission mistakes around `open_for_write`, and timeout semantics that differ between SG_IO and io_uring. Test signals include bsg device-node creation/removal, SG_IO passthrough, io_uring passthrough, permission tests, and teardown with open file descriptors.
