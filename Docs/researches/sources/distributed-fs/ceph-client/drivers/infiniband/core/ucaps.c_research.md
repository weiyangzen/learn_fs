# sources/distributed-fs/ceph-client/drivers/infiniband/core/ucaps.c

## Purpose
`ucaps.c` manages RDMA user capability character devices under `/dev/infiniband`. Drivers can create reference-counted capability device nodes, and consumers can pass FDs back to the kernel to derive a bitmask of granted capability types.

## Important APIs, types, and functions
- `ib_create_ucap(enum rdma_user_cap type)` creates or references a capability cdev.
- `ib_remove_ucap(enum rdma_user_cap type)` drops a reference and removes the cdev on the final put.
- `ib_get_ucaps(int *fds, int fd_count, uint64_t *idx_mask)` converts user FDs to a capability bitmask.
- `ib_cleanup_ucaps()` validates cleanup and unregisters the class/chrdev range.
- Internal helpers include `ib_ucaps_init()`, `get_devt_from_fd()`, `get_ucap_from_devt()`, and `ib_release_ucap()`.

## Control flow and behavior
The first create registers the `infiniband_ucaps` class and allocates a character-device major range. Creating a capability validates the enum, reuses and kref-increments an existing entry if present, or allocates an `ib_ucap`, initializes its embedded device and cdev, names it from `ucap_names`, adds it with `cdev_device_add()`, initializes the kref, and stores it in `ucaps_list`. Removing a capability kref-puts the entry; final release clears the list slot, removes the cdev/device, and drops the device reference. `ib_get_ucaps()` locks the global mutex, resolves each FD to `i_rdev`, matches that device number against active ucaps, and ORs the matching type bit.

## State, persistence, and dependencies
Global persistent state is guarded by `ucaps_mutex`: `ucaps_list[]`, `ucaps_class_is_registered`, and `ucaps_base_dev`. Each active capability has a `struct cdev`, `struct device`, and `kref`. Device nodes default to mode `0600` and path `infiniband/<name>`.

## Integration points
The file integrates with Linux cdev/device/class APIs, file descriptor lookup, and public `<rdma/ib_ucaps.h>` capability enums. Current names include mlx5 local-control and other-vHCA-control capabilities.

## Risks and test signals
Risks include enum/name mismatches, `ib_remove_ucap()` called for a never-created type, stale FDs after cdev removal, device-number reuse assumptions, missing cleanup while ucaps remain active, and bit shifting beyond 64 bits if capability enums grow too large. Test signals include repeated create/remove reference counts, FD-to-mask success and invalid FD failure, permissions and devnode path checks, cleanup warnings with live caps, and concurrent create/remove/get operations under lockdep.
