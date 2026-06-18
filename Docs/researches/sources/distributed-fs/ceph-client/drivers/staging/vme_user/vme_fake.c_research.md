# sources/distributed-fs/ceph-client/drivers/staging/vme_user/vme_fake.c

## Purpose
Provides a fake VME bridge module for exercising the VME framework without VME hardware. It models eight master windows, eight slave windows, one four-address location monitor block, CR/CSR storage, and software-generated VME interrupts using heap memory and a tasklet.

## Important APIs, Types, and Functions
The bridge private state is `struct fake_driver`, with arrays of `fake_slave_window` and `fake_master_window`, location monitor callbacks, interrupt-generation fields, CR/CSR buffer, and a mutex for generated interrupts. Main callbacks are `fake_slave_set/get()`, `fake_master_set/get/read/write/rmw()`, `fake_irq_set()`, `fake_irq_generate()`, `fake_lm_set/get/attach/detach()`, `fake_slot_get()`, `fake_alloc_consistent()`, and `fake_free_consistent()`. Module entry/exit are `fake_init()` and `fake_exit()`.

## Control Flow
`fake_init()` validates `geoid`, creates a root `vme` device, allocates bridge/private state, initializes resources, fills callback pointers, initializes CR/CSR memory, and registers the bridge. Master reads/writes compute the VME address from the configured master window and scan matching fake slave windows by address space and cycle. Access helpers perform 8/16/32-bit operations and run location-monitor checks. `fake_irq_generate()` stores level/vector and schedules `fake_VIRQ_tasklet()`, which calls the generic `vme_irq_handler()`.

## State and Persistence Behavior
All bridge state is volatile kernel memory. Slave buffers are host pointers encoded as fake DMA addresses. Master/slave configuration persists in private arrays until changed or module exit. Location-monitor callbacks persist in arrays and are invoked during fake VME accesses.

## Dependencies and Integration Points
Depends on the VME framework, root device registration, module parameters, tasklets, locks, and heap allocation. It provides the same bridge callback table as hardware bridges, letting `vme_user` and other VME clients test framework paths.

## Risks and Test Signals
It intentionally lacks true hardware timing, posted-write, DMA, and PCI resource behavior. `fake_master_rmw()` appears to use logical `&&` rather than bitwise `&` in its compare expression, making RMW semantics suspect. Monitor indices are not range-checked in attach/detach. Test signals include fake bridge load/unload, `vme_user` reads/writes between configured master and slave windows, location monitor callback firing, IRQ generation to registered callbacks, and no leaks on failed allocation paths.
