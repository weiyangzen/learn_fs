# sources/distributed-fs/ceph-client/include/linux/virtio_anchor.h

## Purpose
This header provides an optional callback anchor for deciding whether a virtio device requires restricted memory access.

## Important APIs, types, and functions
With `CONFIG_VIRTIO_ANCHOR`, it declares `virtio_require_restricted_mem_acc()`, the function pointer `virtio_check_mem_acc_cb`, and `virtio_set_mem_acc_cb()`. Disabled builds make the setter a no-op.

## Control flow, state, and persistence
Platform/security code installs a callback; virtio code queries it to decide restricted memory access policy. State is a global callback pointer, not persistent storage.

## Dependencies and integration points
It integrates virtio with platform-specific memory-access policy such as confidential computing or restricted DMA environments.

## Risks and test signals
Risks include global callback lifetime/order, missing policy when disabled, and inconsistent decisions across devices. Tests should cover callback installation, policy query, module unload ordering, and disabled-config builds.
