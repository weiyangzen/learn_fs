<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pds/pds_intr.h -->
# sources/distributed-fs/ceph-client/include/linux/pds/pds_intr.h

## Purpose
Defines PDS interrupt-control register layout, interrupt status layout, masks/credit bits, and inline MMIO helpers for coalescing, masking, rearming, and cleaning interrupts.

## Important APIs, Types, And Functions
- `struct pds_core_intr` is a 32-byte MMIO control record with `coal_init`, `mask`, signed `credits`, `flags`, `mask_on_assert`, and `coalescing_curr`.
- `PDS_CORE_INTR_F_UNMASK` and `PDS_CORE_INTR_F_TIMER_RESET` are control flags; `PDS_CORE_INTR_CTRL_REGS_MAX`, `PDS_CORE_INTR_CTRL_COAL_MAX`, and `PDS_CORE_INTR_INDEX_NOT_ASSIGNED` describe hardware limits/sentinels.
- `struct pds_core_intr_status` contains two status words.
- `enum pds_core_intr_mask_vals` defines mask clear/set values.
- `enum pds_core_intr_credits_bits` defines credit count mask, signed mask, unmask/reset/rearm bits.
- Inline helpers: `pds_core_intr_coal_init()`, `pds_core_intr_mask()`, `pds_core_intr_credits()`, `pds_core_intr_clean_flags()`, `pds_core_intr_clean()`, and `pds_core_intr_mask_assert()`.

## Control Flow
Drivers program coalescing, mask or unmask an interrupt resource, process interrupts, then write consumed credits and optional rearm flags. `pds_core_intr_credits()` protects against over-large credit counts by warning and rereading the signed credit value before writing. Cleaning reads current credits, preserves signed credit bits, ORs requested flags, and writes back to reset coalescing or rearm.

## State And Persistence
State lives in device MMIO registers. `credits` represents interrupt events sent by hardware and decremented atomically by software writes. `mask_on_assert` can cause hardware to mask after assertion, and `coalescing_curr` is hardware-managed transient timing state.

## Dependencies And Integration Points
Depends on Linux MMIO accessors `ioread32()`/`iowrite32()`, `WARN_ON_ONCE()`, and `__iomem` typing. Integrates with PDS queue completion handlers, AdminQ/NotifyQ interrupt setup, PCI interrupt allocation, and identity-provided coalescing scale factors.

## Risks And Edge Cases
Risks include treating the signed credit register as unsigned, writing a credit count above `PDS_CORE_INTR_CRED_COUNT`, failing to preserve signed bits while cleaning, using mask-on-assert in legacy interrupt mode, coalescing unit conversion mistakes, and accessing an unassigned interrupt index.

## Test Signals
Test interrupt delivery under MSI/MSI-X and legacy modes, mask/unmask behavior, coalescing timer values at 0 and max, rearm after high interrupt rates, WARN path for invalid credits, reset recovery, and queue completion progress with interrupts masked and unmasked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pds/pds_intr.h -->
