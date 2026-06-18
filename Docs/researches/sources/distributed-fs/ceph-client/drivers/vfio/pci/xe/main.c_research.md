<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/xe/main.c -->
# sources/distributed-fs/ceph-client/drivers/vfio/pci/xe/main.c

## Purpose
This file implements `xe-vfio-pci`, a VFIO PCI driver variant for Intel Xe graphics devices with SR-IOV VF migration support. It wraps `vfio_pci_core_device`, delegates standard PCI BAR/config/IRQ handling to VFIO PCI core, and adds Intel Xe PF/VF hooks for live migration state transitions, FLR coordination, and migration data streams.

## Important APIs, types, and functions
Key local types are `struct xe_vfio_pci_core_device`, which embeds the VFIO PCI core device plus Xe PF pointer, VF id, migration state, reset deferral state, and locks, and `struct xe_vfio_pci_migration_file`, which represents an anonymous save or resume data file. The driver exports `xe_vfio_pci_ops` to VFIO core, `xe_vfio_pci_migration_ops` to the VFIO migration feature path, and a `pci_driver` matching Intel PTL, WCL, and BMG IDs through `PCI_DRIVER_OVERRIDE_DEVICE_VFIO`. Important functions include `xe_vfio_pci_open_device`, `xe_vfio_pci_close_device`, `xe_vfio_pci_set_device_state`, `xe_vfio_set_state`, `xe_vfio_pci_reset_prepare`, and `xe_vfio_pci_reset_done`.

## Control flow
Probe allocates the extended VFIO PCI object with `vfio_alloc_device`, stores driver data, and registers with `vfio_pci_core_register_device`. VF initialization detects VFs, obtains the PF `xe_device` through `xe_sriov_vfio_get_pf`, derives the PF-facing VF id as `pci_iov_vf_id() + 1`, and enables migration if `xe_sriov_vfio_migration_supported()` is true. Open enables the VFIO PCI core and starts in `VFIO_DEVICE_STATE_RUNNING`. Migration SET state requests are decomposed by `vfio_mig_get_next_state()` and applied through Xe SR-IOV helper calls: suspend/resume for running-p2p, stop-copy enter/exit with a read-only save file, and resume-data enter/exit with a write-only resume file. Reset prepare/done calls let the PF prepare and wait for VF FLR, then schedule migration cleanup through the state lock path.

## State and persistence behavior
State is in memory only: `mig_state`, `migf`, `deferred_reset`, `xe`, and `vfid` are stored per device instance. Migration data is exposed through anonymous inode files and is not persisted by this driver. `xe_vfio_pci_put_file()` disables a migration file before `fput()`, making later reads/writes fail with `-ENODEV`. The `state_mutex` serializes migration state and migration data access setup, while `reset_lock` protects `deferred_reset`; reset cleanup may be deferred if the migration state mutex is already held to avoid ABBA deadlocks with higher VFIO locks.

## Dependencies and integration points
The file depends on VFIO PCI core, generic VFIO migration feature handling, PCI AER/reset callbacks, Intel Xe SR-IOV VFIO DRM helpers, and Intel PCI ID macros. It integrates with userspace through VFIO device feature ioctls that consume `core_vdev->mig_ops`, and with the PF driver through `xe_sriov_vfio_*` calls.

## Risks and test signals
Migration correctness depends on the PF helper functions being ordered exactly with VFIO state changes and file lifetimes. Reset races are the main concurrency risk: test FLR during active stop-copy/resume streams, repeated state transitions, and close while a migration fd remains open. Test signals include successful bind/probe only for VFIO-overridden Intel IDs, VF open/close, migration state matrix coverage, read/write returning `-ESPIPE` for positioned I/O, `-ENODEV` after reset-disabling migration fds, and PF FLR wait failure logging without use-after-free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/xe/main.c -->
