<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/octeon_ep/octep_vdpa_hw.c -->
# sources/distributed-fs/ceph-client/drivers/vdpa/octeon_ep/octep_vdpa_hw.c

Purpose: Implements low-level Marvell Octeon endpoint vDPA hardware access: emulated virtio PCI capability discovery, feature/status/config MMIO, queue register programming, notify address setup, and firmware mailbox commands for virtqueue state.

Important APIs and functions: `octep_verify_features()` enforces mandatory `VIRTIO_F_VERSION_1`, `VIRTIO_F_NOTIFICATION_DATA`, and `VIRTIO_F_RING_PACKED`; `octep_hw_get_status()`, `octep_hw_set_status()`, and `octep_hw_reset()` wrap virtio common status; `octep_hw_get_dev_features()`, `octep_hw_get_drv_features()`, and `octep_hw_set_drv_features()` select low/high feature words through firmware-acknowledged selectors. Queue APIs include `octep_set_vq_address()`, `octep_set_vq_num()`, `octep_set_vq_ready()`, `octep_get_vq_ready()`, `octep_get_vq_size()`, and `octep_notify_queue()`. `octep_hw_caps_read()` is the main setup entry.

Control flow: `octep_hw_caps_read()` verifies firmware signatures in BAR memory, walks the emulated PCI capability list, maps common/notify/device/ISR regions, processes vendor config records to learn virtio device ID, reads features and queue count, allocates `oct_hw->vqs`, computes per-queue notify and callback-notify addresses, and initializes the mailbox. Mailbox commands serialize through `octep_process_mbox()`: wait for available status, write optional payload and queue id, write request header, poll for response signature/status, then copy response data for reads.

State and persistence: State lives in MMIO registers, `oct_hw` fields, and firmware mailbox memory. There is no disk persistence. Queue state is persisted in device firmware and moved through `vdpa_vq_state` mailbox commands. Config reads use `config_generation` retry loops for consistent snapshots.

Dependencies and integration points: Depends on `octep_vdpa.h`, virtio PCI common structs, `ioread/iowrite`, PCI BAR resources, and firmware-specific signatures/offsets. Upper-layer Octeon vDPA ops call these helpers from `octep_vdpa_main.c`.

Risks: Hardware/firmware protocol assumptions are strict: unaligned mailbox buffers fail, missing ACK-bit clear causes feature or queue select timeouts, and invalid cap lengths/BARs abort setup. `octep_process_mbox()` lacks an explicit mutex, so callers must avoid concurrent mailbox users. Feature verification rejects devices that do not support packed rings and notification data.

Test signals: Probe logs should show mapped common/device/ISR/notify regions, device features, maximum queues, and mailbox mapping. Negative tests include firmware signature mismatch, malformed caps, missing mandatory features, feature selector timeout, queue selector timeout, mailbox timeout/signature failure, and get/set vq state round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/octeon_ep/octep_vdpa_hw.c -->
