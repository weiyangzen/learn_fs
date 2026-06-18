<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/vio.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/vio.c

Purpose: implements the pSeries virtual I/O bus. It registers VIO and platform-facilities devices from the device tree, provides driver matching/probe/remove/shutdown, builds VIO IOMMU tables, supports PFO `H_COP` operations, manages VIO interrupt signaling, and optionally enforces cooperative memory overcommitment (CMO) DMA entitlement accounting.

Important APIs/types/functions: exported `__vio_register_driver()`, `vio_unregister_driver()`, `vio_register_device_node()`, `vio_unregister_device()`, `vio_get_attribute()`, `vio_find_node()`, `vio_enable_interrupts()`, `vio_disable_interrupts()`, `vio_h_cop_sync()`, `vio_cmo_entitlement_update()`, and `vio_cmo_set_dev_desired()`. Key internal paths are `vio_cmo_alloc/dealloc/balance/bus_probe/bus_remove/bus_init`, VIO DMA ops, `vio_build_iommu_table()`, `vio_bus_probe/remove/shutdown/match`, `vio_bus_init()`, and `vio_device_init()`.

Control flow: postcore init registers the VIO bus and fake parent device, initializes CMO if firmware advertises it, then device init scans `/vdevice` and `/ibm,platform-facilities`. `vio_register_device_node()` classifies nodes as VDEVICE or PFO, derives names/type/resource IDs/IRQs, installs DMA ops and IOMMU tables when `ibm,my-dma-window` exists, and registers the device. Driver probe matches by VIO type and OF compatible, runs CMO entitlement setup first when enabled, then calls the driver. DMA mappings under CMO reserve entitlement before calling IOMMU mapping and release entitlement on unmap. PFO synchronous operations loop on busy/resource hypervisor returns until success, error, or timeout.

State and persistence: persistent runtime state includes the bus type, fake parent device, registered `vio_dev` objects, OF node references, IOMMU table refs, CMO global pools (`entitled`, `reserve`, `excess`, `spare`, `min`, `desired`, `curr`, `high`), per-device CMO desired/entitled/allocated counters, and delayed balancing work. Sysfs exposes device identity and CMO counters when `CONFIG_PPC_SMLPAR` is enabled.

Dependencies and integration points: depends on pSeries machine initcall ordering, OF nodes/properties, hypervisor calls `h_get_mpp`, `h_vio_signal`, and `H_COP`, pSeries/LAPR IOMMU table ops, `asm/vio.h` driver contracts, DMA mapping infrastructure, kexec state, and sysfs bus/device attribute groups.

Risks: CMO accounting has many invariants; underflow/overcommit bugs can panic or deny DMA. Probe failure must unwind CMO list entries. Kexec shutdown can call remove when drivers lack shutdown hooks. `vio_find_node()` relies on the exact kobject naming rules used during registration. `vio_h_cop_sync()` timeout handling uses jiffies and may exceed the nominal timeout while an operation is in progress.

Test signals: VIO devices appearing under `/sys/bus/vio`, module autoload modalias values, successful driver probe/remove cycles, VIO DMA map/unmap under CMO with correct sysfs counters, entitlement updates via `vio_cmo_entitlement_update()`, successful PFO operations and timeout/error mapping, and interrupt enable/disable HCALL results are the main validation points.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/vio.c -->
