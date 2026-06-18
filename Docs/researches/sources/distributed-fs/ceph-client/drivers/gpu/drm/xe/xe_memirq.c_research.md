# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_memirq.c

## Purpose
`xe_memirq.c` implements memory-based interrupt reporting for Xe, a scalable alternative to MMIO interrupt status registers used especially by SR-IOV and MSI-X flows.

## Important APIs, Types, And Functions
- `xe_memirq_init()` allocates and initializes the memory IRQ BO and enables the mask.
- Pointer helpers return GGTT addresses for source, status, and enable-mask pages: `xe_memirq_source_ptr()`, `xe_memirq_status_ptr()`, and `xe_memirq_enable_ptr()`.
- `xe_memirq_init_guc()` programs GuC self-config keys with memory IRQ source/status addresses.
- Reset/postinstall toggle interrupt processing through `xe_memirq_reset()` and `xe_memirq_postinstall()`.
- Dispatch helpers check source/status bytes and call HWE or GuC handlers.
- Public handlers are `xe_memirq_hwe_handler()` and `xe_memirq_handler()`.
- `xe_memirq_guc_sw_int_0_irq_pending()` peeks at GuC software interrupt state without clearing it.

## Control Flow
Initialization exits when the device does not use memory IRQs. Otherwise it allocates a system, GGTT-pinned, uncached BO sized either one page or one page per engine instance for MSI-X, clears it, maps source/status/mask iosys offsets, and enables all mask bits. Handlers check source bytes, then corresponding status vectors, clear consumed bytes, and invoke engine or GuC handlers. MSI-X per-HWE flow can call `xe_memirq_hwe_handler()` directly for each engine.

## State And Persistence
`struct xe_memirq` stores the BO, iosys maps, and enabled flag. Hardware writes 0xff bytes into source/status memory; software clears them after dispatch. The mask page persists in the BO and is toggled on reset/postinstall. For MSI-X, page layout is duplicated per engine instance to distinguish engines reporting to instance zero.

## Dependencies And Integration Points
Depends on Xe BO creation, GGTT addresses, GT/HWE iteration, GuC self-config, GuC IRQ handling, tile/device helpers, memory IRQ capability checks, and register bit definitions. LRC code programs these GGTT pointers into context images.

## Risks
Unexpected status byte values are rate-limited errors but still treated as received. Correct source/status offsets are crucial; MSI-X instance remapping changes pointer semantics. `GUC_INTR_SW_INT_0` has special no-clear-then-clear ordering to avoid VF recovery races. BO must be UC and system memory to match hardware requirements.

## Test Signals
Test BO size/layout for MSI-X and non-MSI-X, GuC self-config values, source/status dispatch and clearing, SW_INT_0 pending behavior, reset/postinstall mask changes, and VF memory IRQ interrupt delivery.
