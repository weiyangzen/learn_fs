# sources/distributed-fs/ceph-client/drivers/parisc/gsc.c

## Purpose
This file provides common interrupt and setup infrastructure for PA-RISC GSC ASICs such as ASP, LASI, and Wax. It allocates transaction-based interrupt targets, demultiplexes local ASIC interrupt bits into Linux IRQs, implements a shared IRQ chip for local GSC lines, and walks child devices to assign platform IRQs.

## Important APIs, Types, And Functions
Exported APIs are `gsc_alloc_irq()`, `gsc_claim_irq()`, `gsc_asic_intr()`, `gsc_find_local_irq()`, `gsc_assign_irq()`, `gsc_asic_assign_irq()`, `gsc_fixup_irqs()`, and `gsc_common_setup()`. The IRQ chip `gsc_asic_interrupt_type` provides mask/unmask and SMP affinity support. `struct gsc_asic` and `struct gsc_irq` are declared in `gsc.h`.

## Control Flow
ASIC drivers allocate or claim a transaction IRQ with `gsc_alloc_irq()`/`gsc_claim_irq()`, request that IRQ with `gsc_asic_intr()` as the handler, call `gsc_common_setup()` to initialize local IRQ mappings and reserve the ASIC HPA range, then call `gsc_fixup_irqs()` with a chip-specific mapping callback. At runtime, `gsc_asic_intr()` reads `OFFSET_IRR`, finds each set bit, looks up the assigned global IRQ in `global_irq[]`, and calls `generic_handle_irq()`. Mask/unmask callbacks convert a Linux IRQ back to a local bit and update the ASIC interrupt mask register.

## State And Persistence
Each `gsc_asic` stores its HPA, EIM value, transaction interrupt tuple, and a 32-entry local-to-global IRQ map. `gsc_assign_irq()` uses a static monotonically increasing IRQ allocator from `GSC_IRQ_BASE` to `GSC_IRQ_MAX`. Register programming in IMR/IAR persists in hardware until reboot or later mask changes.

## Dependencies And Integration Points
The file depends on PA-RISC transaction IRQ allocation (`txn_*`, `cpu_*` helpers), generic IRQ dispatch, `parisc_device` hierarchy traversal, and GSC MMIO read/write helpers. LASI, ASP, Wax, and related drivers use this file to route child device interrupts.

## Risks
`gsc_find_local_irq()` returns `NO_IRQ` when a mapping is absent; mask/unmask shifts by that value if called on an unmapped IRQ, so callers must only install valid mappings. The debug print in mask/unmask references `imr` before assignment when debugging is enabled. `gsc_assign_irq()` has global static state and no locking, but it runs during early platform initialization. Affinity changes assume the ASIC supports IAR reprogramming except for ASP revision `0x70`.

## Test Signals
Test signals include successful child IRQ assignment, IRR demultiplexing for multiple simultaneous local bits, mask/unmask register updates, SMP affinity migration on supported ASICs, and correct handling of faulty path recursion in `gsc_fixup_irqs()`. Lockdep and IRQ tracing are useful around nested `generic_handle_irq()` dispatch.
