# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/i40iw_hw.c

## Purpose
`i40iw_hw.c` provides the Gen1/i40e hardware register map, interrupt operations, statistics layout, masks/shifts, and capability defaults for the common IRDMA core.

## Important APIs, types, and functions
The exported API is `i40iw_init_hw`. Local helpers `i40iw_config_ceq`, `i40iw_ena_irq`, and `i40iw_disable_irq` implement Gen1 interrupt programming. Static tables map `IRDMA_MAX_REGS`, hardware statistics offsets, CQP masks, and shifts to i40e register definitions.

## Control flow, state, and persistence
`i40iw_init_hw` fills `dev->hw_regs` from `i40iw_regs`, treating the doorbell offset as a special non-MMIO base, installs stat offsets and hardware masks/shifts, assigns doorbell pointers, installs `i40iw_irq_ops`, and sets Gen1 capability limits. Hardware state changes happen through interrupt configuration writes, while software state persists in `struct irdma_sc_dev` attribute and register pointer fields.

## Dependencies and integration points
This file depends on `i40iw_hw.h` register definitions and common register enum ordering from `irdma.h`. It integrates with `irdma_sc_dev_init`, generic queue setup in `hw.c`, and Gen1 auxiliary setup in `i40iw_if.c`.

## Risks and test signals
Risks are incorrect register offsets, vector index off-by-one behavior, mismatched CQP field masks, and stale Gen1 capability limits. Tests should verify CEQ interrupt enable/disable register writes, stat collection offsets, CQP create/destroy status bit handling, and that Gen1 uses the expected lower capability limits.
