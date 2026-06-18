# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_interrupts.h

## Purpose
Declares DPU interrupt register-group IDs, IRQ index encoding helpers, interrupt table storage, and the hardware interrupt init API.

## Important APIs, Types, and Functions
`enum dpu_hw_intr_reg` defines top, INTF, tear, and AD4 interrupt register groups and must stay synchronized with implementation tables. `MDP_INTFn_INTR`, `DPU_IRQ_IDX`, `DPU_IRQ_REG`, and `DPU_IRQ_BIT` encode and decode 1-based global IRQ indexes. `DPU_NUM_IRQS` is `MDP_INTR_MAX * 32`. `struct dpu_hw_intr_entry` stores one callback, argument, and atomic count. `struct dpu_hw_intr` stores register map, cached masks, optional status storage, lock, active register mask, selected register table, and callback table. `dpu_hw_intr_init` constructs the object.

## Control Flow and State
The header establishes that IRQ callbacks are indexed by a synthetic 1-based ID rather than Linux IRQ numbers. `cache_irq_mask` mirrors hardware enable registers and is protected by `irq_lock`.

## Dependencies and Integration Points
Includes DPU hardware IO, catalog, util, and MDSS definitions. Encoders obtain interrupt IDs from catalog caps and pass them to `dpu_core_irq_*` implementation APIs.

## Risks and Test Signals
Changing enum order breaks every encoded interrupt index and table lookup. Tests should verify `DPU_IRQ_IDX/REG/BIT` round trips, catalog interrupt IDs point at nonzero table entries, and new register groups are added to both enum and implementation tables.
