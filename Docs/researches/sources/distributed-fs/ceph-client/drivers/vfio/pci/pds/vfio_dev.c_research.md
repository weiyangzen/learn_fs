# sources/distributed-fs/ceph-client/drivers/vfio/pci/pds/vfio_dev.c

Purpose: implements the PDS VFIO device operations, migration ops, log ops, state storage, and shared helpers.

Important APIs and functions: device pointer helpers, `pds_vfio_reset()`, migration set/get/data-size ops, log ops binding to dirty tracking, init/release/open/close VFIO device ops, and `pds_vfio_ops_info()`.

Control flow: init resolves VF id, initializes VFIO PCI core and mutex, sets migration flags for stop-copy and P2P, and installs migration/log ops. Open enables the PCI device and sets migration state to RUNNING. Set-state loops through VFIO-approved next states and delegates each transition to `lm.c`. Close releases active migration files, disables dirty logging, and closes VFIO core.

State and persistence: top-level state is in `struct pds_vfio_pci_device`: active save/restore files, dirty logging state, state mutex, current migration state, notifier block, VF id, and PDS client id.

Dependencies and integration: integrates VFIO PCI core, iommufd ops, migration file logic, dirty logging, and PCI driver client/notification setup. `pds_vfio_reset()` is shared with recovery and AER paths.

Risks: state ERROR is sticky until VFIO reset; set-state avoids asking VFIO core for transitions out of ERROR. Close and reset must release files and dirty resources under `state_mutex`. Data-size is a fixed PDS device-state constant, not queried dynamically.

Test signals: open/close, state transition errors, ERROR handling, fixed data-size reporting, log op start/report/stop through VFIO, and reset cleanup from both AER and PF recovery.
