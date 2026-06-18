<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/solidrun/snet_main.c -->
# sources/distributed-fs/ceph-client/drivers/vdpa/solidrun/snet_main.c

Purpose: Implements the SolidRun PCI vDPA driver: PF config discovery and SR-IOV enablement, VF vDPA device creation, vDPA config ops, IRQ handling, DPU config handoff, reset, suspend/resume, and removal.

Important APIs/functions: `snet_config_ops` implements queue, config, feature, status, reset, suspend, and resume vDPA operations. PF helpers open BARs, detect the config BAR, read `struct snet_cfg`, allocate PF IRQ vectors, and enable SR-IOV. VF helpers find per-VF config, allocate IRQs, map VF BAR, build VQs, reserve IRQ indexes, and register the vDPA device.

Control flow: PF probe enables PCI, maps all non-empty BARs, polls for `SNET_SIGNATURE`, keeps the BAR containing config, reads global and per-device configuration, optionally allocates all MSI-X vectors on the PF, enables configured VFs, and optionally registers hwmon. VF probe derives DPU VF ID as PCI VF index plus one, finds matching config, optionally allocates VF MSI-X vectors, allocates `struct snet`, maps VF BAR, points virtio config into BAR, clears control registers, builds VQs/kick pointers, reserves IRQ indexes, and registers the vDPA device. On `DRIVER_OK`, `snet_set_status()` requests config/VQ IRQs, writes the full host config to the DPU, and waits for DPU ACK by clearing the signature.

State and persistence: PF state lives in `struct psnet` with BARs, negotiated config version, next IRQ index, config, and hwmon name. VF state lives in `struct snet` and `struct snet_vq`: callbacks, queue addresses, state, readiness, IRQs, negotiated features, status, DPU-ready flag, BAR pointers, and config pointer. No disk persistence.

Dependencies and integration points: Uses PCI, SR-IOV, vDPA bus, MSI-X, SolidRun DPU BAR config protocol, `snet_ctrl.c` for migration/control commands, and optional `snet_hwmon.c`. Device IDs match SolidRun vendor/device/subsystem IDs.

Risks: Config parsing trusts DPU-provided counts after size checks; malformed `devices_num` can drive allocations. `snet_write_conf()` casts `vdpa_vq_state` to a 32-bit word for config v2, so only the encoded first word is sent. Status failure paths set `VIRTIO_CONFIG_S_FAILED` in local state but do not necessarily inform DPU. PF IRQ allocation requires exact vector count. Reset destroys DPU device only if previous status had `DRIVER_OK`.

Test signals: PF probe should log config version and enable requested VFs. VF probe should register one vDPA device per configured VF. Test PF-allocated and VF-allocated IRQ modes, DPU config ACK timeout, DRIVER_OK creation, reset destroy, suspend/resume, kick and kick-with-data, config read/write bounds, VQ state for config v1/v2, and remove paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/solidrun/snet_main.c -->
