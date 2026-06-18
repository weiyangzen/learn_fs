# sources/distributed-fs/ceph-client/drivers/iommu/iommufd/device.c

## Purpose
This file binds physical devices to an IOMMUFD context, manages per-IOMMU-group IOMMUFD state, attaches/replaces/detaches devices and PASIDs to hardware page tables, handles reserved IOVA/MSI setup, exposes in-kernel IOAS access objects, and reports device hardware information to userspace.

## Important APIs, Types, And Functions
`allow_unsafe_interrupts` is a module parameter allowing device binding without isolated MSI support; it is explicitly a security-weakening override.

`struct iommufd_attach` stores the hwpt for a PASID plus a device xarray. `struct iommufd_group` is defined in private headers and is managed here as per-context state indexed by `iommu_group_id()`.

Group helpers include `iommufd_get_group()`, `iommufd_put_group()`, and `iommufd_group_release()`. They keep a per-context xarray of IOMMU groups, refcount entries, and prevent duplicate state for the same core group.

Device lifecycle exports include `iommufd_device_bind()`, `iommufd_device_unbind()`, `iommufd_ctx_has_group()`, `iommufd_device_to_ictx()`, `iommufd_device_to_id()`, `iommufd_device_attach()`, `iommufd_device_replace()`, and `iommufd_device_detach()`.

Attachment internals include `iommufd_hw_pagetable_attach()`, `iommufd_hw_pagetable_detach()`, `iommufd_device_auto_get_domain()`, `iommufd_device_change_pt()`, `iommufd_hwpt_attach_device()`, `iommufd_hwpt_replace_device()`, and `iommufd_hwpt_detach_device()`.

Access-object exports include `iommufd_access_create()`, `iommufd_access_destroy()`, `iommufd_access_attach()`, `iommufd_access_detach()`, `iommufd_access_replace()`, `iommufd_access_pin_pages()`, `iommufd_access_unpin_pages()`, and `iommufd_access_rw()`.

`iommufd_get_hw_info()` implements the userspace hardware-info ioctl for device-specific IOMMU data, dirty tracking capability, ATS/PASID capability signals, and driver-specific data buffers.

## Control Flow
Binding first checks cache coherency, obtains per-context group state, rejects unsafe MSI unless overridden, claims DMA ownership from the IOMMU core, allocates an IOMMUFD device object, references the context, stores coherency capability, and finalizes the object. Unbind destroys the user object, releasing DMA ownership, group refs, vdevice state, and context refs.

Attachment uses `iommufd_device_change_pt()` to accept an existing HWPT, nested HWPT, or IOAS. For IOAS inputs it searches reusable auto-created paging domains, trying compatible domains and treating `-EINVAL` as a soft incompatibility, otherwise creates an auto domain. Immediate attach supports IOMMU drivers that cannot allocate a complete domain before attach.

`iommufd_hw_pagetable_attach()` serializes on `igroup->lock`, reserves the PASID slot with an xarray zero entry, creates `iommufd_attach` if needed, inserts the device, enforces reserved IOVAs and software MSI pages for no-PASID paging domains, attaches the group/PASID only on the first device for that PASID, stores the hwpt, and refcounts the hwpt per device.

Replacement verifies the device is currently attached, optionally enforces reserved regions for a new paging IOAS, calls IOMMU core replace operations, removes old reserved regions if IOAS changed, swaps the attached hwpt, and moves device-array references from the old hwpt to the new hwpt.

Detach removes the device from the PASID attach array; if it was the last device for that PASID, it detaches from IOMMU core, auto-responds outstanding faults as invalid, removes the PASID attach record, and drops reserved IOVA state. It then puts the hwpt reference outside the group lock.

Access-object control flow uses `access->ioas_lock` to block pin/read operations during attach/detach/replace. On IOAS change it sets `access->ioas` to NULL, optionally registers with the new IO page table, notifies external access users to unmap all old ranges, removes old access registration, updates refcounts, and then publishes the new IOAS. Pin and read/write paths walk contiguous `iopt_area` ranges under `iova_rwsem`, enforce permissions and alignment, and unwind partial pins on failure.

Hardware info flow validates flags/reserved fields, obtains the IOMMUFD device object, calls optional `ops->hw_info()`, copies as much as userspace requested, clears trailing buffer bytes, returns the kernel-supported length and capability bits, and reports enabled PASID properties for PCI devices.

## State And Persistence
State is in the IOMMUFD context: object xarrays, per-group xarrays, `pasid_attach` records, `device_array` entries, hwpt object refs, reserved IOVA entries in IO page tables, software MSI bitmaps, vdevice pointers, access-object IOAS references, and lock-protected page pin/access intervals. No state persists across process or kernel lifetime except hardware/domain state until detached.

## Dependencies And Integration Points
The file depends on IOMMU core ownership, group attach handles, PASID attach APIs, reserved-region APIs, dirty/PASID/ATS capabilities, PCI PRI/PASID helpers, MSI isolation, IOMMUFD object lifecycle, IOAS/page-table code, event queue fault cleanup, vIOMMU/vdevice objects, and pages access helpers.

## Risks
This is a security-sensitive boundary. Binding requires cache coherency and isolated MSI because userspace cannot safely repair cache or interrupt isolation after binding. The override parameter should be tested but avoided in production.

Attach/replace/detach lock ordering across `igroup->lock`, IOAS mutexes, IOMMU core group mutexes, and object refs must remain stable. Fault auto-response relies on attach handles being valid until detach/replace frees them.

Reserved IOVA enforcement must unwind exactly; otherwise userspace could map device-reserved ranges or software MSI windows. Replacement across IOASs is particularly sensitive because old and new reserved regions overlap with group devices.

Access objects require external drivers to honor unmap callbacks and unpin exactly matching ranges. The unmap path in `io_pagetable.c` can return `-EDEADLOCK` if access users fail to respond after repeated notifications.

Hardware-info copy paths must handle short buffers, larger kernel data, and zeroing correctly to avoid leaking kernel memory.

## Test Signals
Exercise bind/unbind with and without MSI isolation, cache-coherent and non-coherent devices, group sharing, repeated bind failures, IOAS auto-domain attach, manual HWPT attach, PASID attach, replace across same and different IOASs, detach of multi-device groups, vdevice destruction races, software MSI reservation/install, page fault auto-response on detach/replace, access pin/unpin/rw permissions, access replacement callbacks, and hardware-info short/long buffer behavior.
