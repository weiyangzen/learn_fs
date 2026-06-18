# sources/distributed-fs/ceph-client/drivers/vhost/vdpa.c

## Purpose

`vdpa.c` implements the vhost character-device frontend for vDPA devices. It registers a `vdpa_driver`, creates one `/dev/vhost-vdpa-*` character device per vDPA device, translates vhost ioctls into `vdpa_config_ops`, manages virtqueue callback wiring, processes userspace IOTLB mappings for device DMA, optionally owns an IOMMU domain, and supports suspend/resume and doorbell mmap for devices that expose notification pages.

## Important APIs, Types, and Functions

`struct vhost_vdpa` is the per-device state: shared `vhost_dev`, optional `iommu_domain`, vq array, `vdpa_device`, per-ASID IOTLB hash buckets, char device, opened flag, config eventfd, batch state, IOVA range, and suspended flag. `struct vhost_vdpa_as` binds an ASID to a `struct vhost_iotlb`.

Device registration and file lifecycle are handled by `vhost_vdpa_probe()`, `vhost_vdpa_remove()`, `vhost_vdpa_open()`, `vhost_vdpa_release()`, `vhost_vdpa_cleanup()`, and `vhost_vdpa_release_dev()`. Ioctl handling is split between `vhost_vdpa_unlocked_ioctl()` and `vhost_vdpa_vring_ioctl()`. Config and feature helpers include `vhost_vdpa_get_device_id()`, `vhost_vdpa_get_status()`, `vhost_vdpa_set_status()`, `vhost_vdpa_get_config()`, `vhost_vdpa_set_config()`, `vhost_vdpa_get_features()`, `vhost_vdpa_set_features()`, `vhost_vdpa_get_backend_features()`, `vhost_vdpa_suspend()`, and `vhost_vdpa_resume()`. IOTLB mapping is handled by `vhost_vdpa_process_iotlb_msg()`, `vhost_vdpa_process_iotlb_update()`, `vhost_vdpa_pa_map()`, `vhost_vdpa_va_map()`, `vhost_vdpa_map()`, and `vhost_vdpa_unmap()`.

## Control Flow

Module init allocates a char-device major and registers the vDPA driver. Probe rejects unsupported multi-group/multi-AS platform-IOMMU cases, allocates a `vhost_vdpa`, assigns a minor, initializes the device and cdev, stores the vDPA device pointer, allocates vq state, and initializes ASID hash buckets. Open is exclusive via `atomic_cmpxchg()`: it resets the vDPA device, allocates the vhost vq pointer array, installs kick handlers, initializes the shared vhost device with no worker thread and a custom IOTLB message handler, allocates an IOMMU domain if the backend does not provide map callbacks, computes the IOVA range, and stores private data.

The main ioctl path handles backend feature negotiation outside the device mutex, then serializes most device operations under `vhost_dev.mutex`. It forwards generic vhost ioctls to the shared core and vq ioctls to `vhost_vdpa_vring_ioctl()`. Status writes enforce monotonic status bits except reset-to-zero, call vDPA reset for zero status, and set up or tear down irq-bypass producers when `DRIVER_OK` changes. Vring ioctls validate queue index, handle vDPA-specific queue enable/group/ASID/size operations, call the shared vring ioctl for common fields, and then push ring address, ring base, callback, and queue size changes into `vdpa_config_ops`.

IOTLB writes arrive through `vhost_vdpa_chr_write_iter()` and the shared vhost write parser, then enter `vhost_vdpa_process_iotlb_msg()`. UPDATE and BATCH_BEGIN allocate or find an ASID table. UPDATE validates the requested range and overlap, then maps either virtual addresses (`vdpa->use_va`) by walking shared file-backed VMAs or physical pages by pinning user pages under `RLIMIT_MEMLOCK`. Mapping records are added to vhost IOTLB first and then applied through backend `dma_map`, backend `set_map`, or the local IOMMU domain. INVALIDATE unmaps ranges, unpins pages or drops file references, and updates backend maps outside a batch. Release resets the device, stops vhost state, unbinds mm, drops config eventfd, unmaps all ASIDs, frees the domain, and marks the device reopenable.

## State and Persistence Behavior

State persists for the lifetime of the probed vDPA device and, separately, for the lifetime of an open file. Device lifetime state includes minor number, cdev/device registration, vq array allocation, vDPA pointer, and ASID hash heads. Open lifetime state includes vhost ownership, mm binding, IOTLB maps, IOMMU domain attachment, config eventfd, irq bypass registrations, backend features, and suspended flag. IOTLB mappings pin pages or hold file references until invalidated, reset, release, or device removal. There is no filesystem persistence.

## Dependencies and Integration Points

The file depends on the vDPA bus and `vdpa_config_ops`, the shared vhost core for UAPI parsing and virtqueue metadata, eventfd callbacks, irq-bypass producer registration, IOMMU APIs, mm and page pinning APIs, VMA/file mapping APIs for VA mode, char-device registration, IDA minor allocation, and optional MMU mmap operations. Userspace VMMs configure vDPA devices through `/dev/vhost-vdpa-*`.

## Risks and Edge Cases

The most sensitive logic is IOTLB mapping and unmapping: PA mode must account pinned pages in `mm->pinned_vm`, obey memlock limits, coalesce contiguous PFNs correctly, dirty writable pages on unmap, and unwind partially mapped chunks. VA mode only maps shared file-backed VMAs that are not IO/PFNMAP and must balance every `get_file()` with `fput()`. Batch mapping must not mix ASIDs and must call `set_map()` at batch end. Queue address and base changes are rejected after `DRIVER_OK` unless suspended, so migration code must use suspend where supported. IRQ bypass setup depends on both callback eventfd and backend IRQ availability. Probe intentionally rejects some multi-AS/group configurations when only a platform IOMMU path exists.

## Test Signals

Useful signals include vDPA simulator tests, QEMU boot with `/dev/vhost-vdpa-*`, backend feature negotiation tests for ASID, batching, persistent IOTLB, suspend, resume, and descriptor ASID, IOTLB map/unmap fault injection, memlock-limit tests, VA-mode shared-file mapping tests, migration tests around suspend/resume and ring-base restore, irq-bypass registration checks, mmap doorbell tests, and repeated open/release/remove races under lockdep and KASAN.
