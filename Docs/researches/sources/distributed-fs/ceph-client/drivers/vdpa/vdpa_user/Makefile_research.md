<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/vdpa_user/Makefile -->
# sources/distributed-fs/ceph-client/drivers/vdpa/vdpa_user/Makefile

Purpose: Builds the VDUSE userspace vDPA module and includes the IOVA-domain implementation.

Important APIs/types/functions: `vduse-y := vduse_dev.o iova_domain.o` and `obj-$(CONFIG_VDPA_USER) += vduse.o`.

Control flow: Kernel build links the userspace-device frontend and MMU/software-IOTLB domain into the `vduse` module when `CONFIG_VDPA_USER` is enabled.

State and persistence: Build-only file; no runtime state.

Dependencies and integration points: `vduse_dev.o` depends on functions exported within `iova_domain.o` for DMA/IOTLB behavior.

Risks: Removing `iova_domain.o` would break VDUSE DMA mapping and mmap support.

Test signals: Build `CONFIG_VDPA_USER=m/y` and ensure the final `vduse` module contains IOVA-domain symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/vdpa_user/Makefile -->
