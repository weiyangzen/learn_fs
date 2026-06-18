<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_pmem.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/virtio_pmem.h

Purpose: defines the virtio persistent memory ABI for exposing a persistent memory range and issuing flush requests.

Important APIs and types: `VIRTIO_PMEM_F_SHMEM_REGION` indicates that the pmem guest physical range is exposed as shared memory region 0, with `VIRTIO_PMEM_SHMEM_REGION_ID`. `struct virtio_pmem_config` carries start and size. `VIRTIO_PMEM_REQ_TYPE_FLUSH`, `struct virtio_pmem_req`, and `struct virtio_pmem_resp` define flush commands and host return status.

Control flow, state, and persistence: the guest maps the advertised range and submits flush requests to ensure persistence. Actual durable state is in the backing storage, while the header only defines command/config format.

Dependencies and integration points: depends on virtio IDs/config and integrates with Linux pmem, DAX, nvdimm-like persistence, and shared-memory virtio capability handling.

Risks and test signals: risks include incorrect flush completion semantics, range/config mismatch, and shared-memory region ID drift. Test fsync/msync durability paths, DAX mappings, shared-memory feature negotiation, and backend flush failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_pmem.h -->
