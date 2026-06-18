# sources/distributed-fs/ceph-client/drivers/iommu/iommufd/main.c

## Purpose
`main.c` is the iommufd module core. It registers `/dev/iommu` and, when enabled, `/dev/vfio/vfio`, owns per-file context creation/destruction, dispatches ioctls, implements object allocation/finalization/removal, supports mmap of driver-provided MMIO windows, and exports context reference helpers.

## Important APIs, Types, And Functions
Core object APIs are `_iommufd_object_alloc()`, `_iommufd_object_alloc_ucmd()`, `iommufd_object_finalize()`, `iommufd_object_abort()`, `iommufd_object_abort_and_destroy()`, `iommufd_get_object()`, and `iommufd_object_remove()`. File operations are `iommufd_fops_open()`, `iommufd_fops_release()`, `iommufd_fops_ioctl()`, and `iommufd_fops_mmap()`. Exported helpers are `iommufd_ctx_get()`, `iommufd_ctx_from_file()`, `iommufd_ctx_from_fd()`, `iommufd_ctx_put()`, and `iommufd_global_device()`.

## Control Flow
Open allocates an `iommufd_ctx`, initializes xarrays, locks, maple tree, waitqueue, MSI state, and optional VFIO accounting mode. Ioctl dispatch reads the user size, validates command number and minimum size, copies the extensible structure, calls the command handler, then finalizes or aborts any object allocated through `ucmd->new_obj`. Unknown iommufd command numbers fall through to VFIO compatibility. Release repeatedly removes leaf objects whose `users` refcount reaches one until the object graph is gone.

## State And Persistence
Persistent state is per file descriptor in `iommufd_ctx`. Objects start as reserved xarray slots and become visible only after finalization. `wait_cnt` allows destroy paths to wait for transient users before freeing. Mmap state is stored in `ictx->mt_mmap`, keyed by page-shifted offsets handed to userspace.

## Dependencies And Integration Points
The dispatch table wires the uapi command set to IOAS, HWPT, dirty tracking, fault queue, vIOMMU, vdevice, vevent queue, hardware queue, VFIO IOAS, and selftest handlers. Module init/exit register misc devices and selftest support.

## Risks And Test Signals
Important risks are refcount ordering, destroy wait timeouts, ucmd auto-finalization mismatch, object ops missing destroy/abort callbacks, mmap offset validation, and VFIO misc-device compatibility. Tests should cover short and extended ioctl sizes, abort after partial object creation, concurrent destroy/get, file release with interior object graphs, mmap exact-offset/length checks, and module init error unwinding.
