<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/vdpa_sim/vdpa_sim.h -->
# sources/distributed-fs/ceph-client/drivers/vdpa/vdpa_sim/vdpa_sim.h

Purpose: Defines shared simulator structures, feature constants, frontend attribute contract, exported creation/scheduling APIs, and virtio endian helpers.

Important APIs/types: `VDPASIM_FEATURES` includes any-layout, version 1, and access-platform. `struct vdpasim_virtqueue` wraps `vringh`, in/out kiovs, head, readiness, ring addresses, size, callback, and private data. `struct vdpasim_dev_attr` describes frontend-provided identity, sizes, callbacks, groups, and address spaces. `struct vdpasim` is the full simulator runtime state. Inline conversion helpers map virtio endian to CPU based on legacy/version-1 negotiation.

Control flow: Net/block modules fill `vdpasim_dev_attr`, call `vdpasim_create()`, then rely on common ops invoking their `work_fn`, `get_config`, `set_config`, `get_stats`, and `free`.

State and persistence: Header declares runtime-only fields; no persistent storage.

Dependencies and integration points: Includes IOVA, vringh, vDPA, virtio byteorder, vhost IOTLB, and virtio config headers. It is the contract between simulator core and frontends.

Risks: Frontends must set `alloc_size`, `config_size`, `nvqs`, `ngroups`, and `nas` correctly or core allocation/ops will misbehave. Endian helpers assume no cross-endian support beyond legacy/version-1 choice.

Test signals: Compile net/block against this header; runtime tests verify frontend callbacks and endian conversions in config structures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/vdpa_sim/vdpa_sim.h -->
