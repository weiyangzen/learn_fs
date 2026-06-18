# sources/distributed-fs/ceph-client/drivers/scsi/snic/vnic_cq_fw.h

Purpose: this header defines the firmware-completion CQ service loop for SNIC-specific `struct snic_fw_req` entries.

Important APIs, types, and functions: `vnic_cq_fw_service()` reads a firmware completion descriptor at `cq->to_clean`, extracts its color with `snic_color_dec()`, invokes a callback with `vdev`, CQ index, and descriptor pointer, advances the consumer index, toggles `last_color` on wrap, and enforces a work budget.

Control flow: `snic_fwcq_cmpl_handler()` calls this for firmware-to-host CQs. The callback is `snic_io_cmpl_handler()`, which dispatches by firmware response type.

State and persistence: state is CQ ring memory, `to_clean`, and `last_color`. No persistent state exists.

Dependencies and integration: includes `snic_fwint.h` for `snic_fw_req` and color decode. It assumes `struct vnic_cq` is visible through including context.

Risks: same unsigned work-budget behavior as generic CQ service applies. The loop trusts firmware completion descriptors once color changes; malformed type/status is handled later with assertions in `snic_scsi.c`.

Test signals: firmware CQ wraparound, malformed completion types, high completion rates, and limited work budget behavior.
