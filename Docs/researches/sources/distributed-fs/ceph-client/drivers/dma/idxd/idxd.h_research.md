# sources/distributed-fs/ceph-client/drivers/dma/idxd/idxd.h

## Purpose
`idxd.h` is the central private interface for Intel DSA/IAA drivers. It defines the device model, WQ/group/engine/device state, event logs, descriptors, portal helpers, registration helpers, and cross-file prototypes.

## Important APIs, Types, And Functions
Major types include `idxd_dev`, `idxd_device_driver`, `idxd_irq_entry`, `idxd_group`, `idxd_wq`, `idxd_engine`, `idxd_hw`, `idxd_device`, `idxd_saved_states`, `idxd_desc`, `idxd_dma_dev`, `idxd_cdev`, `idxd_pmu`, and `idxd_evl`. Helpers classify device/WQ types, compute portal offsets, manage WQ client counts, constrain batch/SGL size, and dispatch descriptor completion.

## Control Flow
It has no standalone flow but coordinates `bus.c`, `init.c`, `device.c`, `dma.c`, `cdev.c`, IRQ, submit, sysfs, debugfs, and perfmon files.

## State And Persistence Behavior
It models volatile state: hardware capability shadows, flags, command status, PASID/SVA state, WQ config, descriptor pools, completion records, EVL state, saved FLR state, debugfs and perf pointers.

## Dependencies And Integration Points
It depends on dmaengine, PCI, IOMMU, cdev, perf, xarray, wait queues, percpu refs, crypto, uapi IDXD structures, and `registers.h`.

## Risks And Test Signals
Shared layout changes affect all IDXD layers. `idxd_wq_portal_addr()` intentionally rotates non-atomically and WQ refcount helpers require caller locking. Validate full build matrix, namespace checks, WQ binding, and FLR recovery.
