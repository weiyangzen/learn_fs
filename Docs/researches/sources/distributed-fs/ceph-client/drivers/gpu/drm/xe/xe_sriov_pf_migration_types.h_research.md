<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_migration_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_migration_types.h

Purpose: defines PF migration state structures.

Important types: `struct xe_sriov_pf_migration` contains the device-level `disabled` flag. `struct xe_sriov_migration_state` contains per-VF waitqueue, mutex, currently processed pending packet, stream trailer packet, and descriptor packet.

State and risks: packet pointers are cleaned up by migration managed cleanup. Tests should verify cleanup frees partially consumed pending, descriptor, and trailer packets without double-free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_migration_types.h -->
