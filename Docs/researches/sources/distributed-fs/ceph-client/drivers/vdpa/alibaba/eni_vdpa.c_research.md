# sources/distributed-fs/ceph-client/drivers/vdpa/alibaba/eni_vdpa.c

Purpose: vDPA bridge for Alibaba ENI devices implemented as legacy virtio-pci network devices. It exposes a legacy virtio PCI function as a `vdpa_device`.

Important APIs/types/functions: `struct eni_vdpa` embeds `vdpa_device`, `virtio_pci_legacy_device`, vring callback/IRQ state, and config callback. `eni_vdpa_ops` implements feature negotiation, status/reset, virtqueue size/address/ready/callback/kick, config access, and IRQ lookup. `eni_vdpa_request_irq()` allocates one MSI-X vector per queue plus config. `eni_vdpa_probe()` enables PCI, probes legacy virtio, allocates vring state, and registers with the vDPA bus.

Control flow: probe initializes legacy virtio-pci state, discovers queue count from features/config, prepares notify addresses, and registers the vDPA device. When status gains `DRIVER_OK`, IRQ vectors are requested and programmed with `vp_legacy_queue_vector()`/`vp_legacy_config_vector()`. Reset or clearing `DRIVER_OK` disables vectors. Queue kicks write queue id to the legacy notify register.

State and persistence: state is in `eni_vdpa`: queue count, vector count, per-vring IRQ/callback/notify pointer, config IRQ/callback, and legacy device state. No persistence beyond PCI device lifetime.

Dependencies and integration: uses Linux PCI, vDPA core, `virtio_pci_legacy` accessors, virtio-net config layout, MSI-X, and Red Hat/Qumranet virtio PCI IDs with Alibaba subsystem matching.

Risks: legacy virtio-pci cannot set/get full migration queue state; `get_vq_state()` is unsupported and `set_vq_state()` only accepts initial zero state. Feature negotiation requires `VIRTIO_NET_F_MRG_RXBUF` if any features are negotiated. IRQ allocation result from `eni_vdpa_request_irq()` in `set_status()` is not propagated to the vDPA caller.

Test signals: PCI probe/remove, feature negotiation with/without MRG_RXBUF, DRIVER_OK IRQ setup/free, queue notify writes, config read/write offsets after vector count changes, reset paths, and queue-state migration rejection.
