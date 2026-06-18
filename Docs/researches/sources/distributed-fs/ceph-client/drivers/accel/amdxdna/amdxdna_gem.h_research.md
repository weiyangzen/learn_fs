# sources/distributed-fs/ceph-client/drivers/accel/amdxdna/amdxdna_gem.h

Purpose: declares AMD XDNA GEM object layout, memory tracking structures, user mmap notifier state, address helpers, pin/get APIs, BO ioctl entry points, and prime-import integration.

Important APIs/types: `struct amdxdna_gem_obj` extends DRM shmem with client ownership, BO type, pin state, lock, `amdxdna_mem`, DRM-MM heap/node data, assigned hardware context, dma-buf attachment, and internal flag. `struct amdxdna_mem` tracks CPU mapping, DMA address, size, HMM mapping list, invalidation flag, and cached first user VA. `struct amdxdna_umap` ties a VMA to an mmu interval notifier and HMM range. Helpers convert to GEM objects, detect imported BOs, compute device heap offsets, choose DMA/user addresses under PASID, and manage references.

Control flow: GEM implementation, context submission, AIE2 command code, and IOMMU paths include this header to look up, pin, map, and address BOs.

State and persistence: declared fields are in-memory per BO or mapping; the only user-visible persistence is through GEM handles and mmap offsets while a DRM file is open.

Dependencies: DRM shmem helper, Linux HMM/IOMMU, AMD XDNA PCI driver definitions, and UAPI BO type constants.

Risks: `amdxdna_obj_dma_addr()` switches address source based on PASID, so callers must know whether firmware expects VA or DMA/IOVA. Lock comments identify protected fields; new users must respect them.

Test signals: compile users across PASID/IOVA modes, object reference lifecycle, address helper outputs for heap/device/share/imported BOs, and notifier invalidation behavior.
