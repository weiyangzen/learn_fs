<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_packet.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_packet.c

Purpose: implements PF-side SR-IOV migration packet allocation, streaming read/write, descriptor/trailer creation, and descriptor compatibility validation.

Important APIs and control flow: `xe_sriov_packet_alloc()` creates an uninitialized packet with header bytes remaining. `xe_sriov_packet_init()` fills a header and allocates payload storage; VRAM packets allocate a pinned mapped BO, other packet types allocate `kvzalloc()` memory. `xe_sriov_packet_read_single()` selects descriptor, pending save data, or trailer and streams header then payload to userspace, freeing packets when complete. `xe_sriov_packet_write_single()` streams userspace header/payload into a pending packet and calls `xe_sriov_pf_migration_restore_produce()` when complete. `xe_sriov_packet_save_init()` prepares descriptor and zero-size trailer packets under the per-VF migration mutex.

State and dependencies: packet state tracks remaining header/payload bytes, typed header fields, and either BO or heap buffer storage. Descriptor KLVs include device ID and revision and are validated by `xe_sriov_packet_process_descriptor()`. Integration depends on PF migration state, GuC KLV helpers, per-VF locks, GT lookup, BO allocation, and userspace copy helpers.

Risks and test signals: partial reads/writes must preserve offsets correctly. Tests should cover short header writes, unsupported protocol version, invalid GT/tile, VRAM BO allocation failure, descriptor mismatches, truncated KLVs, unknown KLV skipping, trailer end-of-stream, and read ordering descriptor before data before trailer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_packet.c -->
