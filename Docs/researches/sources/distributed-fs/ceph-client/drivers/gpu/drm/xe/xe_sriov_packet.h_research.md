<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_packet.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_packet.h

Purpose: declares SR-IOV migration packet helpers.

Important APIs: allocation/free, header-backed initialization, read/write streaming, save initialization, and descriptor processing. These functions are used by PF migration read/write paths and migration control setup.

Risks and test signals: callers must hold the per-VF migration mutex where packet selection requires it. Tests should assert free handles NULL/ERR pointers and that descriptor processing rejects incompatible devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_packet.h -->
