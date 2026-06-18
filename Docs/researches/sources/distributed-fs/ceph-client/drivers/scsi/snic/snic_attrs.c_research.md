# sources/distributed-fs/ceph-client/drivers/scsi/snic/snic_attrs.c

Purpose: this file exposes SNIC host attributes through SCSI host sysfs groups.

Important APIs, types, and functions: show callbacks return the adapter symbolic name, driver state string, driver version, and link state. `snic_show_link_state()` refreshes link status from `svnic_dev_link_status()` for direct-attached SNIC_DAS configurations. `snic_host_groups` exports the attribute group to the `scsi_host_template`.

Control flow: sysfs reads resolve the `Scsi_Host` through `class_to_shost(dev)`, then read `struct snic` via `shost_priv()`. Values are emitted with `sysfs_emit()`. There are no store callbacks; all attributes are read-only.

State and persistence: the file only observes runtime fields: `snic->name`, `snic->state`, `snic->config.xpt_type`, and `snic->link_status`. No persistent configuration is accepted.

Dependencies and integration: depends on `snic_state_str`, `snic_get_state()`, `SNIC_DRV_VERSION`, and the vNIC notify path. The attribute group is referenced by `snic_host_template.shost_groups` in `snic_main.c`.

Risks: the state string is indexed by `snic_get_state()` without a local bounds check, relying on state enum integrity. Link state reads may touch the notify buffer and cached checksum path, so sysfs reads can reflect stale or unavailable firmware notify data.

Test signals: verify `/sys/class/scsi_host/host*/snic_sym_name`, `snic_state`, `drv_version`, and `link_state` during online, offline, and removal windows. KASAN/lockdep testing should cover concurrent sysfs reads and PCI unbind.
