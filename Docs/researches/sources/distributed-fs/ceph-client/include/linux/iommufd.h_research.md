# sources/distributed-fs/ceph-client/include/linux/iommufd.h

Purpose: This header defines the in-kernel interface to iommufd, the user-facing IOMMU file descriptor subsystem used by VFIO, virtual IOMMUs, nested translation, access objects, and driver-managed hardware queues.

Important APIs, types, and functions: Core objects include `iommufd_object`, `iommufd_viommu`, `iommufd_vdevice`, and `iommufd_hw_queue`. APIs bind/unbind devices, attach/replace/detach page tables, create/destroy/attach access objects, pin/unpin pages, read/write IOAS memory, get contexts from files/fds, and report vIOMMU events. `iommufd_viommu_ops` defines driver callbacks for nested domains, cache invalidation, vdevice init, and hardware queue init.

Control flow: Kernel users obtain or create an `iommufd_ctx`, bind devices into it, attach devices or access objects to IO address spaces, and manage object dependencies. vIOMMU drivers allocate sanitized embedded structures via size macros, initialize virtual devices/queues, optionally allocate mmap offsets, and report events back to userspace.

State and persistence: Every userspace-visible object carries an ID, type, user refs, and wait count. vIOMMU state owns xarrays of virtual devices, event queues, hardware page table links, and driver ops. Access objects may pin pages or perform IOAS reads/writes until detached/destroyed.

Dependencies and integration points: Depends on IOMMU core, xarray, refcounting, UAPI iommufd definitions, VFIO compatibility, device model, and optional `CONFIG_IOMMUFD_DRIVER_CORE`.

Risks: Object dependency and wait-count rules are critical to avoid UAF during concurrent destroy. Driver structures must embed the core member at the checked offset/type. Disabled configs return `-EOPNOTSUPP` or NULL-like stubs. Access pinning can leak pins if detach/destroy is mishandled.

Test signals: Test object lifetime under concurrent destroy, device bind/attach/replace/detach, access pin/RW, VFIO compat IOAS creation, vIOMMU vdevice/queue init, mmap allocation teardown, event reporting, dependency helpers, and disabled-config stubs.
