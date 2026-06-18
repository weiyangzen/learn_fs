# sources/distributed-fs/ceph-client/drivers/dma/idxd/cdev.c

## Purpose
`cdev.c` implements IDXD user work-queue character devices, including user portal mapping, SVA/PASID binding, user descriptor submission, poll, and completion-record fault support.

## Important APIs, Types, And Functions
Core types are `idxd_cdev_context` and `idxd_user_context`. File operations are open, release, mmap, write, and poll. WQ integration uses `idxd_user_drv_probe/remove`, `idxd_wq_add_cdev`, `idxd_wq_del_cdev`, and `idxd_copy_cr()`.

## Control Flow
The user driver binds matching user WQs only when the device has user PASID/SVA. Open allocates a context, binds the current mm through IOMMU SVA, records PASID in the WQ xarray, optionally writes PASID into a dedicated WQ, creates a file device, and increments WQ clients. Mmap maps the limited portal page after security checks. Write validates descriptors and submits through direct portal writes or ENQCMDS.

## State And Persistence Behavior
State includes global major/minor IDAs, cdev objects, per-open PASID/mm/task/file devices, xarray entries, and fault counters. Release unregisters the file device; final release drains work/PASID, unbinds SVA, removes xarray state, and decrements WQ users.

## Dependencies And Integration Points
It depends on char devices, sysfs attributes, IOMMU SVA, xarray, user copy, polling, capabilities, event-log fault work, and IDXD portal submission.

## Risks And Test Signals
User submission is security-sensitive: unsafe devices require `CAP_SYS_RAWIO` for mmap, DSA v1 batch may be rejected, completion addresses must be aligned, and operations are tied to the opener mm. Test cdev creation, open/mmap/write, SVA rejection, close cleanup, poll, and fault counter updates.
