# sources/distributed-fs/ceph-client/drivers/vfio/pci/hisilicon/hisi_acc_vfio_pci.c

## Purpose

`hisi_acc_vfio_pci.c` is a VFIO PCI variant driver for HiSilicon SEC/HPRE/ZIP accelerator VFs. It reuses VFIO PCI core for normal access and, when the VF has a suitable PF/QM backend, adds VFIO live migration support by saving/restoring queue-manager register state, queue context DMA addresses, and match metadata through VFIO migration files.

## Important APIs, Types, and Functions

Hardware helpers read/write QM registers and mailboxes: `qm_get_vft()`, `qm_get_sqc()`, `qm_get_cqc()`, `qm_get_regs()`, `qm_set_regs()`, `pf_qm_get_qp_num()`, `vf_qm_cache_wb()`, `vf_qm_func_stop()`, and `hisi_acc_check_int_state()`. Migration data helpers are `vf_qm_get_match_data()`, `vf_qm_check_match()`, `vf_qm_read_data()`, `vf_qm_state_save()`, and `vf_qm_load_data()`.

Migration file operations include resume write, save read, and precopy ioctl helpers. State-machine entry points are `hisi_acc_vfio_pci_set_device_state()`, `hisi_acc_vfio_pci_get_device_state()`, and `hisi_acc_vfio_pci_get_data_size()`. VFIO ops are split into migration-capable `hisi_acc_vfio_pci_migrn_ops` and generic `hisi_acc_vfio_pci_ops`. Probe selects migration ops only for supported VFs with an accessible PF QM version at least `QM_HW_V3`.

## Control Flow

Probe identifies PF QM data by VF device id and PF driver, chooses migration ops when possible, allocates a `hisi_acc_vf_core_device`, registers it with VFIO PCI core, and creates vendor debugfs. Open enables the PCI core and, for migration ops, initializes VF QM access. Old hardware maps the full VF BAR2 and hides the migration half from userspace; newer hardware uses a PF BAR2 migration region offset by VF id. Close disables migration files, clears `dev_opened`, unmaps old-mode BAR2, and closes VFIO PCI core.

Migration follows VFIO's state graph. RUNNING to PRE_COPY opens a read migration file containing match data. PRE_COPY to STOP_COPY stops the VF, checks interrupt/RAS state, writes back cache, and fills the save file with full state. RUNNING to STOP stops without opening a file. STOP to STOP_COPY opens a stop-copy save file. STOP to RESUMING opens a write migration file; RESUMING to STOP loads received state and closes files. STOP to RUNNING restarts the device if restored state was ready. Reset handlers serialize with PF reset state and reset VF migration state after AER reset.

## State and Persistence Behavior

Persistent runtime state lives in `struct hisi_acc_vf_core_device`: VFIO PCI core device, migration state, VF/PF pci devices, PF/VF QM handles, hardware mode, VF id, VF QM state, migration file pointers, debug migration copy, reset flag, and open/state mutexes. Migration payload state is `struct acc_vf_data`, including magic/version, qp count/base, device id, isolation config, QM register snapshots, interrupt masks, EQ/AEQ registers, reserved registers, and DMA base addresses. No data is file-backed beyond anonymous migration file descriptors returned to userspace.

## Dependencies and Integration Points

The driver depends on VFIO PCI core, VFIO migration core, IOMMUFD physical helpers, HiSilicon QM/SEC/HPRE/ZIP PF driver helpers, PCI SR-IOV VF identification, PCI AER reset callbacks, debugfs, anon inodes, eventfd headers, and hardware register definitions in its header. It supports Huawei SEC, HPRE, and ZIP VFs through `PCI_DRIVER_OVERRIDE_DEVICE_VFIO`.

## Risks and Edge Cases

Migration correctness depends on exact hardware state sequencing. Stop must pause QM, verify PF/VF interrupt state is idle, and write back cache before reading registers. Resume validates magic/version, device id, qp count, and isolation state before accepting the stream; if only match data is present, it can complete without loading queue state. BAR2 filtering is critical in old VF-control mode so userspace cannot access the migration control half. Migration files can be disabled asynchronously by state transitions and close; file operations must return `-ENODEV` after disable.

The code returns `-EFAULT` to userspace when `vf_qm_check_match()` fails during resume write, even though the cause may be semantic mismatch. Reset prepare spins up to `QM_RESET_WAIT_TIMEOUT` milliseconds waiting for PF reset ownership. Debugfs reads require the device to be open because `io_base` is otherwise unavailable.

## Test Signals

Test probe with and without PF driver data, hardware mode selection, BAR2 region-size filtering, read/write/mmap denial of migration BAR space, open/close migration setup, every VFIO migration state transition, precopy ioctl byte counts, save file read bounds, resume write bounds and match failures, V1 and V2 migration magic handling, stop-device interrupt busy cases, cache writeback timeout, resume with missing DMA addresses, AER reset prepare/done, debugfs output, and remove cleanup after active migration files.
