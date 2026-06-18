# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_interrupts.c

## Purpose
Implements DPU core interrupt register mapping, IRQ dispatch, callback registration, enable/disable masking, preinstall/uninstall cleanup, status reads, and debugfs reporting.

## Important APIs, Types, and Functions
Public APIs include `dpu_hw_intr_init`, `dpu_core_irq`, `dpu_core_irq_read`, `dpu_core_irq_register_callback`, `dpu_core_irq_unregister_callback`, `dpu_core_irq_preinstall`, `dpu_core_irq_uninstall`, and debugfs `dpu_debugfs_core_irq_init`. Static interrupt register tables cover legacy DPU <=6.x, DPU >=7.x, and DPU >=13.x layouts. Helpers include `dpu_core_irq_is_valid`, `dpu_core_irq_get_entry`, `dpu_core_irq_callback_handler`, `dpu_hw_intr_enable_irq_locked`, `dpu_hw_intr_disable_irq_locked`, `dpu_clear_irqs`, and `dpu_disable_all_irqs`.

## Control Flow and State
`dpu_hw_intr_init` selects the register table by core major version, anchors MMIO at MDP base, and builds `irq_mask` from top interrupts plus catalog INTF and tear interrupts. The top IRQ handler locks `irq_lock`, scans enabled register groups, reads status and enable masks, clears raw status, masks disabled bits, dispatches each set bit to its registered callback, and writes a memory barrier. Registration stores one callback/arg per IRQ index, clears pending status, enables the bit in cached mask and hardware, and rejects busy entries. Unregister disables and clears the bit, then clears callback state. Atomic counts track dispatches.

## Dependencies and Integration Points
Used by DPU KMS IRQ install path and all encoder/PP/INTF/WB users that register callbacks. Relies on catalog interrupt indexes, DPU IRQ index macros, MMIO helpers, runtime PM during preinstall/uninstall, tracepoints, and debugfs.

## Risks and Test Signals
Risks include wrong register table for a core version, catalog IRQ indexes outside supported registers, single-callback conflicts, unregistering while IRQ fires, and callbacks running under `irq_lock`. Tests should exercise each register layout, INTF tear IRQs, register/unregister error paths, spurious IRQs with no callback, status read clearing, debugfs counts, suspend/resume preinstall/uninstall, and concurrent callback registration protection.
