# sources/distributed-fs/ceph-client/drivers/soc/mediatek/mtk-devapc.c

## Purpose
This driver handles MediaTek Device APC access violations. It enables violation interrupts, synchronizes hardware violation debug information through the shift mechanism, logs violation metadata, clears status, and masks/unmasks module interrupts.

## Important APIs, Types, and Functions
Key local types are `struct mtk_devapc_vio_dbgs`, `struct mtk_devapc_regs_ofs`, `struct mtk_devapc_data`, and `struct mtk_devapc_context`. Important functions are `clear_vio_status()`, `mask_module_irq()`, `devapc_sync_vio_dbg()`, `devapc_extract_vio_dbg()`, `devapc_violation_irq()`, `start_devapc()`, `stop_devapc()`, `mtk_devapc_probe()`, and `mtk_devapc_remove()`.

## Control Flow and State
Probe maps registers with `of_iomap()`, parses IRQ, enables the infraclock, registers the IRQ handler, stores context, and unmasks violation interrupts. The IRQ handler loops while shift status reports pending groups, extracts debug registers, clears violation status, and returns handled. Remove masks interrupts and unmaps MMIO.

## Dependencies and Integration Points
The driver integrates with device tree compatibles `mediatek,mt6779-devapc` and `mediatek,mt8186-devapc`, the clock framework, IRQ framework, and MMIO polling. Per-SoC data supplies violation count and register offsets.

## Risks and Test Signals
Risks include off-by-one handling in violation register loops, incomplete IRQ masking for the final partial register, and using `IS_ERR()` on an OF node pointer in probe. Test signals are synthetic access violations, IRQ logs showing bus/domain/address, clock enable failures, poll timeout behavior, and remove/reprobe cleanup.
