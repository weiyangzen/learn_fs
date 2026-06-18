# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/host/isys_irq_private.h

Purpose: provides private ISYS IRQ controller register access plus state capture and dump helpers.

Important APIs/types/functions: `isys_irqc_state_get()` reads edge, mask, status, enable, and level/no-pulse registers. `isys_irqc_state_dump()` logs the snapshot. `isys_irqc_reg_store()` and `isys_irqc_reg_load()` compute register addresses from `ISYS_IRQ_BASE` and word indexes.

Control flow: state capture calls the load helper for readable register indices. Store/load assert controller and register bounds, calculate address, trace the operation, and access hardware through `ia_css_device_*`.

State and persistence: register stores mutate hardware; snapshots are caller-owned.

Dependencies and integration: depends on global/local IRQ headers, CSS debug tracing, and device access. Used by `isys_irq.c` and diagnostic code.

Risks and test signals: only `reg_idx <= ISYS_IRQ_LEVEL_NO_REG_IDX` is checked; semantic read/write constraints remain caller responsibility. Tests should cover readable state capture, write-only clear behavior, and register address correctness.
