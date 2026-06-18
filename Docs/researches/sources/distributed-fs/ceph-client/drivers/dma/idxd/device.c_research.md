# sources/distributed-fs/ceph-client/drivers/dma/idxd/device.c

## Purpose
`device.c` is the IDXD control-plane core. It handles device commands, WQ enable/disable, resource allocation, portals, PASID programming, group/WQ/engine config, EVL setup, interrupt handles, and the internal `idxd` driver.

## Important APIs, Types, And Functions
Key functions include `idxd_wq_alloc_resources`, `idxd_wq_enable`, `idxd_wq_disable`, `idxd_wq_drain`, `idxd_wq_map_portal`, `idxd_wq_set_pasid`, `idxd_device_init_reset`, `idxd_device_enable`, `idxd_device_disable`, `idxd_device_config`, `idxd_wq_request_irq`, `idxd_drv_enable_wq`, and `idxd_device_drv_probe/remove`. `idxd_cmd_exec()` serializes commands with `cmd_lock`, wait queues, and interrupt completion.

## Control Flow
Device probe writes config, sets up EVL, enables the device, and registers a dmaengine device. WQ enable validates device/WQ state, configures PASID, writes hardware tables, enables the WQ, maps portal, requests IRQ/int handle, allocates descriptors/completions, and initializes a percpu ref. Disable reverses the sequence with drain/reset/cleanup.

## State And Persistence Behavior
State includes WQ/group/engine shadow config, `wq_enable_map`, coherent completion records, software descriptors, sbitmap queues, EVL memory/bitmap, IRQ permission entries, int handles, PASID fields, command status, and device state.

## Dependencies And Integration Points
It depends on IDXD registers/uapi, PCI IRQs, dmaengine completion, IOMMU PASID, devm MMIO mapping, percpu refs, and subdrivers in `dma.c` and `cdev.c`.

## Risks And Test Signals
Command completion depends on misc IRQs. WQ disable must drain translations before config changes. Shared WQs require ENQCMD/PASID. Test sysfs enable/disable, WQ binding, portal mapping, IRQ setup, EVL debugfs, PASID changes, drain/reset, and unwind paths.
