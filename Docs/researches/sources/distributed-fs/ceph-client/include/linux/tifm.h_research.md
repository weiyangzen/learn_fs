<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/tifm.h -->
# sources/distributed-fs/ceph-client/include/linux/tifm.h

## Purpose
declares the Texas Instruments FlashMedia adapter bus API, socket/device structures, register bits, DMA/FIFO constants, and MemoryStick/xD/SD socket helpers.

## Important APIs, Types, and Functions
The file is 161 lines and exports these visible symbol families: types/enums `tifm_device_id`, `tifm_driver`, `tifm_dev`, `tifm_adapter`; macros/constants `TIFM_CTRL_LED`, `TIFM_CTRL_FAST_CLK`, `TIFM_CTRL_POWER_MASK`, `TIFM_SOCK_STATE_OCCUPIED`, `TIFM_SOCK_STATE_POWERED`, `TIFM_FIFO_ENABLE`, `TIFM_FIFO_READY`, `TIFM_FIFO_MORE`, `TIFM_FIFO_INT_SETALL`, `TIFM_FIFO_INTMASK`, `TIFM_DMA_RESET`, `TIFM_DMA_TX`, `TIFM_DMA_EN`, `TIFM_DMA_TSIZE`, and 3 more; function-like macros none; inline helpers `tifm_set_drvdata`; external prototypes `void`, `tifm_add_adapter`, `tifm_remove_adapter`, `tifm_free_adapter`, `tifm_free_device`, `tifm_register_driver`, `tifm_unregister_driver`, `tifm_eject`, `tifm_has_ms_pif`, `tifm_map_sg`, `tifm_unmap_sg`, `tifm_queue_work`, `dev_get_drvdata`.

## Control Flow
Host drivers allocate and add a `tifm_adapter`, allocate per-socket `tifm_dev` children, and card-function drivers bind through `tifm_driver` match tables. Data paths use FIFO/DMA register bits and map/unmap scatterlists for socket transfers.

## State and Persistence Behavior
`tifm_adapter` owns sockets, resources, clock, IRQ, eject work, and lock; `tifm_dev` tracks socket address, type, media ID, IRQ status, resources, and callback hooks.

## Dependencies and Integration Points
It depends on device model, PCI, workqueue, clocks, spinlocks, resources, and scatterlists; it integrates with flash-media card drivers. Direct includes are `linux/spinlock.h`, `linux/interrupt.h`, `linux/delay.h`, `linux/pci.h`, `linux/workqueue.h`.

## Risks and Edge Cases
Socket hotplug/eject races, DMA mapping lifetime, and FIFO interrupt masks can lose media events or corrupt transfers. Resource arrays are fixed per socket.

## Test Signals
Probe/remove adapters, hotplug/eject media, run scatter-gather DMA and FIFO transfer tests, validate driver match tables for XD/MS/SD types, and exercise suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/tifm.h -->
