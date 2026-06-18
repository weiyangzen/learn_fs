# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/decoder.c

## Purpose
Provides common decoder-core support for HabanaLabs devices. It initializes per-decoder bookkeeping, handles abnormal decoder interrupts in workqueue context, converts decoder interrupt status bits into driver notifier events and reset decisions, and stops enabled decoder cores when a user context is finalized.

## Important APIs, Types, And Functions
Public APIs are `hl_dec_init()`, `hl_dec_fini()`, and `hl_dec_ctx_fini()`. Internal helpers are `dec_abnrm_intr_work()` and `dec_print_abnrm_intr_source()`. The file defines VCMD register offsets for control and IRQ status plus bit masks for ENDCMD, BUSERR, TIMEOUT, CMDERR, ABORT, and RESET abnormal interrupt sources.

## Control Flow
`hl_dec_init()` checks `hdev->asic_prop.max_dec`; if no decoder cores exist, it is a no-op. Otherwise it allocates `hdev->dec`, initializes each `struct hl_dec` with the device pointer, core id, abnormal interrupt work item, and ASIC-provided decoder base address. Missing base addresses fail initialization and free the decoder array.

When hardware schedules `dec_abnrm_intr_work()`, the worker reads the decoder VCMD IRQ status register, logs the core and decoded source bits, writes the status back to clear the interrupt, and reads it again to flush the clear. TIMEOUT marks a general hardware error and requires device reset. CMDERR maps to undefined opcode. ENDCMD, BUSERR, and ABORT map to user engine error. If reset is required, the worker adds a device reset notifier bit and calls `hl_device_cond_reset()`; otherwise it sends notifier events directly.

`hl_dec_ctx_fini()` iterates enabled decoders from `decoder_enabled_mask` and writes zero to each VCMD control register to stop decoder activity during context teardown.

## State And Persistence
Persistent state is the `hdev->dec` array. Each element stores the owning device, decoder core id, VCMD base address, and abnormal interrupt work item. No per-context decoder state is allocated in this file; context finalization performs direct register writes based on enabled-core mask.

## Dependencies And Integration Points
The file depends on `hdev->asic_prop.max_dec`, `decoder_enabled_mask`, ASIC `get_dec_base_addr()`, MMIO `RREG32/WREG32`, notifier event masks, and reset/event helpers from `device.c`. It is initialized from `hl_device_init()`, finalized from `hl_device_fini()`, and called from context teardown in `context.c`.

## Risks
The abnormal interrupt worker reads and writes device registers asynchronously, so reset/fini ordering must ensure work cannot access freed `hdev->dec` or inaccessible MMIO. Event classification is simple bitmask mapping; missing a status bit can under-report errors. TIMEOUT triggers reset, while other errors only notify userspace, so hardware behavior must match that policy. `hl_dec_ctx_fini()` assumes decoder base addresses remain valid and that stopping enabled decoders is safe during context release.

## Test Signals
Coverage should include devices with zero decoders, valid multi-decoder init, invalid base-address failure unwind, synthetic abnormal interrupt statuses for each bit, timeout-triggered conditional reset, non-timeout notifier delivery, and context finalization stopping only enabled decoder cores. Runtime signals are decoder abnormal interrupt logs, decoded source strings, notifier masks, and reset scheduling after TIMEOUT.
