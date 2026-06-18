# sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_regs.c

- Purpose: Resource mapping helpers for MGB4 MMIO register windows.
- Important APIs/types/functions: `mgb4_regs_map()` and `mgb4_regs_free()`.
- Control flow: Map requests a memory region, ioremaps it, and records base/size; free unmaps and releases the region.
- State and persistence: State is `struct mgb4_regs` mapbase/mapsize/membase; no persistence.
- Dependencies and integration points: Used by core to map video and CMT windows before all register access.
- Risks: Free assumes a successfully mapped resource. Error handling returns `-EINVAL` for both busy region and ioremap failure.
- Test signals: Probe failure injection for busy BAR subregion and ioremap failure, plus unload map cleanup.
