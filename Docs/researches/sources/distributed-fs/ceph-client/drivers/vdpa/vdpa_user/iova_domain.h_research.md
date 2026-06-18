<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/vdpa_user/iova_domain.h -->
# sources/distributed-fs/ceph-client/drivers/vdpa/vdpa_user/iova_domain.h

Purpose: Declares VDUSE IOVA-domain data structures, constants, and public mapping/sync/domain lifecycle APIs.

Important APIs/types: Constants define IOVA start PFN and 4 KiB bounce-map granularity. `struct vduse_bounce_map` stores kernel/user bounce pages and original physical address. `struct vduse_iova_domain` stores stream/consistent IOVA allocators, bounce map array, size/limit, bounce-map state, vhost IOTLB, locks, anon file, and user-bounce flag. Public prototypes cover map set/clear, DMA sync, map/unmap page, coherent alloc/free, bounce map reset, user bounce page add/remove, destroy/create, and global init/exit.

Control flow: VDUSE device code includes this header to create a domain, expose mmap through the domain's anon file, perform DMA operations, and tear the domain down.

State and persistence: Header describes runtime-only memory translation state. There is no disk persistence.

Dependencies and integration points: Includes IOVA, DMA mapping, and vhost IOTLB headers. The implementation uses `vdpa_map_file` contexts through vhost IOTLB opaque pointers.

Risks: Callers must respect IOVA limits, bounce-size alignment, and sync directions. User bounce pages must cover the entire bounce window. The domain object is ultimately released by `fput(domain->file)`, so external references must not outlive destroy/release.

Test signals: Compile integration with VDUSE device code; runtime tests should cover all public APIs declared here and validate resource release through `vduse_domain_destroy()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/vdpa_user/iova_domain.h -->
