<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/misc/ocxl.h -->
# sources/distributed-fs/ceph-client/include/uapi/misc/ocxl.h

Purpose: defines the OpenCAPI Accelerator Function Unit userspace ABI for attach, metadata, interrupt allocation, eventfd binding, P9 wait, features, and kernel events.

Important APIs and types: event structures report XSL fault errors with address, DSISR, and count. `ocxl_ioctl_attach` carries AMR and reserved fields. `ocxl_ioctl_metadata` reports version, AFU version, PASID, per-PASID/global MMIO sizes, and reserved space. `ocxl_ioctl_p9_wait`, `ocxl_ioctl_features`, and `ocxl_ioctl_irq_fd` support waiting and interrupt setup. Ioctls allocate/free IRQs, set IRQ fd, get metadata/features, attach, and enable P9 wait.

Control flow, state, and persistence: userspace opens an AFU, attaches a context, maps MMIO, allocates IRQs, binds eventfds, reads events, and may enable P9 wait. Context and IRQ state persist until fd close or ioctl teardown.

Dependencies and integration points: integrates OpenCAPI/Power platform AFU drivers, PASID/IOMMU, eventfd, MMIO mapping, and userspace accelerator runtimes.

Risks and test signals: risks include reserved-field ABI growth, PASID lifetime, IRQ/eventfd leaks, event ordering, and fault event sizing. Test attach/detach, metadata versions, IRQ allocation/free, eventfd delivery, P9 wait, and XSL fault reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/misc/ocxl.h -->
