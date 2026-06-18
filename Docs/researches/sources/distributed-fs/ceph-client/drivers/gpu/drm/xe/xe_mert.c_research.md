# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_mert.c

## Purpose
`xe_mert.c` manages MERT-specific state, LMTT invalidation, and MERT interrupt handling for SR-IOV-capable devices with a standalone MERT block.

## Important APIs, Types, And Functions
- `xe_mert_init_early()` initializes spinlock and completion state on the root tile.
- `xe_mert_invalidate_lmtt()` triggers MERT LMTT invalidation and waits up to `HZ / 4`.
- `mert_handle_cat_error()` decodes CAT error register state and handles unmapped GGTT or LMTT faults.
- `xe_mert_irq_handler()` processes MERT interrupts, CAT errors, and invalidation completion.

## Control Flow
Early init prepares synchronization. LMTT invalidation takes the lock, triggers the descriptor if not already active, reinitializes completion, writes the valid bit, then waits for completion. The IRQ handler runs on root tile SOC memory interrupt, handles CAT errors, then checks whether the hardware cleared the valid bit and completes waiters.

## State And Persistence
`struct xe_mert` stores a spinlock, `tlb_inv_triggered`, and a completion. Trigger state persists between invalidate request and interrupt completion. CAT errors can wedge the device on severe faults.

## Dependencies And Integration Points
Integrates with Xe MMIO, root tile state, SR-IOV logging, device wedging, MERT registers, IRQ dispatch in `xe_irq.c`, and LMTT invalidation in `xe_lmtt.c`.

## Risks
Invalidation depends on receiving the MERT interrupt before timeout. Severe CAT error handling wedges the device, while LMTT faults are only debug-logged with a TODO for malicious VF tracking. Concurrent invalidation callers share one trigger/completion and rely on lock-protected state.

## Test Signals
Test successful invalidation completion, timeout path, concurrent callers, CAT error decoding, wedging on unmapped GGTT/unexpected codes, and IRQ path integration from master interrupt bits.
