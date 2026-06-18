# sources/distributed-fs/ceph-client/drivers/vfio/container.c

## Purpose

`container.c` implements the legacy VFIO container device `/dev/vfio/vfio`. Containers collect one or more VFIO groups and attach them to a selected VFIO IOMMU backend, enabling userspace DMA mappings, page pinning, and DMA read/write for traditional group-based VFIO.

## Important APIs, Types, and Functions

`struct vfio_container` tracks a kref, attached group list, group rwsem, selected `vfio_iommu_driver`, backend data, and no-IOMMU mode. IOMMU backend registration is done by `vfio_register_iommu_driver()` and `vfio_unregister_iommu_driver()`. File operations expose `VFIO_GET_API_VERSION`, `VFIO_CHECK_EXTENSION`, `VFIO_SET_IOMMU`, and backend ioctl passthrough. Group entry points include `vfio_container_attach_group()`, `vfio_group_detach_container()`, `vfio_group_use_container()`, and `vfio_group_unuse_container()`. Device helpers call backend `register_device`, `unregister_device`, `pin_pages`, `unpin_pages`, and `dma_rw`.

## Control Flow

Opening `/dev/vfio/vfio` allocates an empty container. `VFIO_CHECK_EXTENSION` either asks the selected backend or probes all registered backends that are allowed for the container's current no-IOMMU mode. `VFIO_SET_IOMMU` requires at least one attached group and no existing backend, finds a backend whose `CHECK_EXTENSION` matches the arg, opens it, attaches every group in the container, then records the backend/data. Attaching a group claims DMA ownership for real IOMMU groups, rejects mixing real and no-IOMMU groups, optionally attaches the group to an already selected backend, marks the group as using the container, adds it to the list, and takes a container reference.

Detach removes the group from the backend, releases DMA ownership, removes it from the container list, and if it was the last group releases the backend and module reference, returning the container to an unprivileged unset state. Group use increments `container_users` and gets the group file only after an IOMMU backend is selected.

## State and Persistence Behavior

Container state persists across file references and group/device fds through kref references. The backend is intentionally released when the last group detaches. No-IOMMU containers can only use the built-in no-IOMMU backend, and real containers cannot mix with no-IOMMU groups. There is no file-backed persistence; DMA ownership and mappings live in the IOMMU backend.

## Dependencies and Integration Points

This file integrates with `group.c`, IOMMU group DMA ownership, legacy VFIO IOMMU backends, `vfio_noiommu`, CAP_SYS_RAWIO checks, misc device registration, and VFIO device-driver helper APIs. `vfio_container_init()` registers `/dev/vfio/vfio` and optionally registers no-IOMMU ops.

## Risks and Edge Cases

The container/group locking contract is critical: callers must hold `group->group_lock` around attach/detach/use/unuse, while container state is protected by `group_lock` rwsem. Backend selection iterates modules under `iommu_drivers_lock` and uses `try_module_get()`; failure unwinds must detach already attached groups in reverse. No-IOMMU support intentionally taints security expectations and must never mix with real IOMMU groups. Page pin/unpin helpers assume a valid backend and enforce `VFIO_PIN_PAGES_MAX_ENTRIES`.

## Test Signals

Test open/release, extension probing before and after backend selection, set-IOMMU without groups, duplicate set-IOMMU, attach/detach with and without existing backend, mixed no-IOMMU/real rejection, CAP_SYS_RAWIO enforcement, backend open/attach failure unwind, last-group backend release, group use before set-IOMMU rejection, device register/unregister callbacks, pin/unpin limit checks, DMA read/write passthrough, and init/cleanup with no-IOMMU enabled.
