# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/regs/xe_irq_regs.h

## Purpose

`xe_irq_regs.h` names the Xe interrupt control/status register block: master interrupt registers, GT interrupt dwords, per-engine interrupt enables/masks, identity registers, and special interrupt bits for GuC, GSC, display, I2C, SoC, and PXP/KCR events.

## Important APIs, Types, and Definitions

- Master interrupt registers: `DG1_MSTR_TILE_INTR`, `GFX_MSTR_IRQ`, and bits such as `MASTER_IRQ`, `GU_MISC_IRQ`, `DISPLAY_IRQ`, `SOC_H2DMEMINT_IRQ`, `I2C_IRQ`, and `GT_DW_IRQ(x)`.
- GT interrupt dwords: `GT_INTR_DW(x)` with engine and GuC/GSC bit helpers.
- Enable/mask registers: `RENDER_COPY_INTR_ENABLE`, `VCS_VECS_INTR_ENABLE`, `GUC_SG_INTR_ENABLE`, `GUNIT_GSC_INTR_ENABLE`, and engine mask registers.
- Identity decoding: `INTR_IDENTITY_REG(x)`, `INTR_DATA_VALID`, `INTR_ENGINE_INSTANCE()`, `INTR_ENGINE_CLASS()`, and `INTR_ENGINE_INTR()`.
- PXP/KCR interrupt bits: `KCR_PXP_STATE_TERMINATED_INTERRUPT`, `KCR_APP_TERMINATED_PER_FW_REQ_INTERRUPT`, and `KCR_PXP_STATE_RESET_COMPLETE_INTERRUPT`.

## Control Flow

This header only defines register contracts. Interrupt setup code writes enable/mask registers, top-half handlers read master/GT/identity registers, decode pending sources, and dispatch to GuC, engine, display, GSC, I2C, error, or PXP handlers.

## State and Persistence Behavior

Interrupt mask/enable bits persist in hardware until reprogrammed or reset. Identity registers expose transient pending interrupt records and include a valid bit plus class/instance/source fields. VF-tagged registers are accessible to virtual functions only on supported interface versions; comments note newer VF paths can move to memory-based interrupts.

## Dependencies and Integration Points

It depends on `regs/xe_reg_defs.h`. It integrates with Xe IRQ install/uninstall, engine interrupt routing, GuC/GSC communication, SR-IOV VF interrupt handling, display and I2C event routing, and PXP state handling.

## Risks and Edge Cases

- VF-accessibility comments encode version-dependent behavior; preserving `XE_REG_OPTION_VF` may be correct for legacy VFs but consumers must gate newer memory-based interrupt paths separately.
- Bit helper macros such as `INTR_BCS(x)` and `INTR_VECS(x)` assume valid engine indices.
- Incorrect masks can lose interrupts, leave sources storming, or route PXP/GSC events to the wrong handler.

## Test Signals

Signals include interrupt smoke tests, GuC event delivery, engine user/context-switch interrupts, PXP reset/termination events, SR-IOV VF interrupt paths, and no spurious interrupt storms during suspend/resume and reset.
