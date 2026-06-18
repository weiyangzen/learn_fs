<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/pds/vdpa_dev.h -->
# sources/distributed-fs/ceph-client/drivers/vdpa/pds/vdpa_dev.h

Purpose: Declares PDS vDPA queue and device runtime structures plus public helper prototypes.

Important APIs/types: `struct pds_vdpa_vq_info` holds VQ readiness, descriptor/avail/used addresses, queue length, qid, IRQ metadata, notify mapping, doorbell, migration indices, callback, and parent pointer. `struct pds_vdpa_device` embeds `vdpa_device`, links to `pds_vdpa_aux`, stores fixed-size VQ array, feature masks, vDPA index, queue count, MAC, config callback, and notifier block. Constants include `PDS_VDPA_MAX_QUEUES`, `PDS_VDPA_MAX_QLEN`, and `PDS_VDPA_PACKED_INVERT_IDX`.

Control flow: Structures are populated during `dev_add`, updated by vDPA ops, read by adminq command wrappers and debugfs, and cleaned during `dev_del`/remove.

State and persistence: All fields are runtime-only software mirrors of firmware/virtio state. Queue indices survive readiness toggles in memory and are synchronized with firmware on VQ reset/init.

Dependencies and integration points: Includes PCI and vDPA headers. Exports `pds_vdpa_release_irqs()` and `pds_vdpa_get_mgmt_info()` across PDS source files.

Risks: The VQ array is fixed at 65, so management info clamps max VQs to this limit. Packed-ring invert index is a protocol convention that must match firmware and `cmds.c`.

Test signals: Compile-time structure users across PDS files and runtime debugfs VQ fields verify layout assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/pds/vdpa_dev.h -->
