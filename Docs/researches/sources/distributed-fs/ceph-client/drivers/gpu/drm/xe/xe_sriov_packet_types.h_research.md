<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_packet_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_packet_types.h

Purpose: defines the SR-IOV VF migration packet protocol structures.

Important types: `enum xe_sriov_packet_type` reserves zero and defines descriptor, trailer, GGTT, MMIO, GuC, and VRAM packet types. `struct xe_sriov_packet_hdr` is a packed protocol header with version, type, tile/GT IDs, flags, offset, and size. `struct xe_sriov_packet` stores runtime streaming state, CPU payload pointer, BO or heap buffer, and header.

Risks and test signals: packed header layout is ABI-like for debugfs migration streams. Tests should assert header size/layout, zero type rejection in restore, and correct allocation choice for VRAM versus non-VRAM packets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_packet_types.h -->
