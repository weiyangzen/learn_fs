# sources/distributed-fs/ceph-client/drivers/bus/fsl-mc/fsl-mc-allocator.c

## Purpose
Implements fsl-mc resource pools for allocatable DPAA2 objects and IRQ resources. It binds to DPBP, DPMCP, and DPCON devices, inserts them into per-bus pools, allocates/free objects for functional devices, and manages MSI IRQ pools shared by devices in a DPRC.

## Important APIs, Types, And Functions
Core exports are `fsl_mc_resource_allocate()`, `fsl_mc_resource_free()`, `fsl_mc_object_allocate()`, `fsl_mc_object_free()`, `fsl_mc_populate_irq_pool()`, `fsl_mc_cleanup_irq_pool()`, `fsl_mc_allocate_irqs()`, `fsl_mc_free_irqs()`, and `fsl_mc_init_all_resource_pools()`. Static helpers validate allocatable devices, add/remove devices from pools, map object type strings to pool types, and implement `fsl_mc_allocator_probe()`/`remove()`.

## Control Flow
`fsl_mc_init_all_resource_pools()` initializes each pool on DPRC scan. The allocator driver probes DPBP/DPMCP/DPCON devices and adds them as free resources in the parent bus pool. Functional drivers call `fsl_mc_object_allocate()` to remove a free resource from the pool and create an autoremove consumer device link; freeing returns the resource to the list. IRQ pool population allocates a block of MSI interrupts, wraps each vector in `struct fsl_mc_device_irq`, and inserts those resources into the IRQ pool. Device IRQ allocation removes enough IRQ resources for a device and records back-pointers/indexes; free returns them.

## State And Persistence
State is held in each `struct fsl_mc_bus`: resource pools, free lists, max/free counts, mutexes, and `irq_resources`. Individual allocatable MC devices point at their `struct fsl_mc_resource`. IRQ resources track virtual IRQ numbers and owning MC devices. There is no persistent storage; MC object inventory remains authoritative.

## Dependencies And Integration Points
The allocator depends on fsl-mc bus type helpers, fsl-mc MSI domain functions, Linux device links, devm allocation tied to the bus/device, and pool type constants shared with private headers. It is deliberately ordered by DPRC scanning before functional devices so resource consumers can allocate DPBP/DPCON objects during probe.

## Risks And Test Signals
Risks include free/max count corruption, removing an allocated resource, DPMCP misuse, leaked device links, insufficient IRQ pool sizing, freeing IRQ pools while vectors are still allocated, and silent returns on invariant violations. Test signals include resource exhaustion paths, add/remove of allocatable devices, allocation/free under driver bind/unbind, IRQ allocation for DPRCs and child devices, and cleanup only when free counts equal max counts.
