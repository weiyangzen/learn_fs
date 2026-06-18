# sources/distributed-fs/ceph-client/drivers/staging/vme_user/vme_bridge.h

## Purpose
Defines the private provider-side contract for VME bridge drivers. It describes bridge-owned resource structs, IRQ callback tables, error handlers, DMA list state, and the function-pointer table that concrete bridges must fill before registering with `vme.c`.

## Important APIs, Types, and Constants
Important structs are `vme_master_resource`, `vme_slave_resource`, `vme_dma_resource`, `vme_dma_list`, `vme_dma_pattern`, `vme_dma_pci`, `vme_dma_vme`, `vme_lm_resource`, `vme_error_handler`, `vme_callback`, `vme_irq`, and `vme_bridge`. `VME_CRCSR_BUF_SIZE` defines the 508 KiB CR/CSR backing image size. `struct vme_bridge` carries lists for every resource class, `driver_priv`, parent `device`, per-level IRQ callbacks, and callback pointers for slave, master, DMA, IRQ, location-monitor, slot, and coherent-allocation operations.

## Control Flow and State
Bridge drivers allocate and initialize resource structs, attach them to the lists in `struct vme_bridge`, set callback pointers, and then call `vme_register_bridge()`. Client-facing operations in `vme.c` recover the concrete resource with `list_entry()` from `struct vme_resource.entry` and invoke the relevant callback. Locks are per-resource: master windows use spinlocks to support interrupt-context access; slave/DMA/LM resources use mutexes.

## Dependencies and Integration Points
Includes `vme.h` and is consumed by both provider implementations (`vme_fake.c`, `vme_tsi148.c`) plus framework internals. The callback table is the integration seam between generic resource management and hardware-specific MMIO/software emulation.

## Risks and Test Signals
The framework assumes list entries remain valid while resources are checked out; bridge removal must unregister devices before freeing resources. Callback pointers are optional, so client APIs must handle unsupported operations. Test bridge registration/unregistration under client driver load, lockdep on mixed master spinlock and DMA/location-monitor mutex paths, and teardown with IRQ callbacks still registered.
