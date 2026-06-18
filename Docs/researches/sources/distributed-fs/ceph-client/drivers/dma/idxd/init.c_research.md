# sources/distributed-fs/ceph-client/drivers/dma/idxd/init.c

## Purpose
`init.c` implements PCI and module lifecycle for Intel DSA/IAA IDXD accelerators: enumeration, capability discovery, object allocation, SVA/PASID setup, interrupts, sysfs/debugfs/perf registration, FLR recovery, shutdown, and removal.

## Important APIs, Types, And Functions
Key routines include `idxd_setup_interrupts`, `idxd_setup_wqs`, `idxd_setup_engines`, `idxd_setup_groups`, `idxd_setup_internals`, `idxd_read_caps`, `idxd_alloc`, `idxd_enable_system_pasid`, `idxd_probe`, config save/restore, `idxd_reset_prepare/done`, `idxd_pci_probe_alloc`, `idxd_wqs_quiesce`, `idxd_shutdown`, `idxd_remove`, and `idxd_init_module`.

## Control Flow
Module init checks CPU MOVDIR64B/ENQCMD, registers IDXD subdrivers, allocates cdev majors, initializes debugfs, and registers PCI. PCI probe enables the function, allocates `idxd_device`, maps MMIO, resets hardware, optionally enables system PASID, reads caps/table offsets, allocates WQs/engines/groups/EVL, sets up MSI-X, initializes perfmon, loads IAA defaults, registers dsa-bus devices, and creates debugfs.

## State And Persistence Behavior
State includes the `idxd_device`, config devices, capability shadows, SVA/PASID flags, MSI-X entries, EVL cache, IDA IDs, and saved FLR state. FLR prepare snapshots config and PCI state; reset-done restores PCI state, re-probes hardware without reallocating, restores config, and rebinds supported WQs.

## Dependencies And Integration Points
It depends on PCI, MSI-X, IOMMU PASID, CPU feature flags, workqueues, dmaengine, IDXD bus/subdrivers, sysfs, debugfs, perfmon, cdev, and IAA defaults.

## Risks And Test Signals
No MOVDIR64B blocks load; ENQCMD absence disables shared WQ support. SVA may be disabled by module parameter. FLR recovery only re-enables user WQs. Test DSA/IAA probe, SVA on/off, MSI-X setup, sysfs tree, IAA defaults, debugfs/perf setup, shutdown/remove, and FLR recovery.
