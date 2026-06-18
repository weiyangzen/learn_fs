# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/isys_irq_global.h

Purpose: defines ISYS IRQ controller register indices and broad mask/clear/enable values.

Important APIs/types/functions: register indices are edge, mask, status, clear, enable, and level/no-pulse. Values `ISYS_IRQ_MASK_REG_VALUE`, `ISYS_IRQ_CLEAR_REG_VALUE`, and `ISYS_IRQ_ENABLE_REG_VALUE` are all `0xFFFF`.

Control flow: no direct flow. `isys_irqc_status_enable()` and private helpers use these constants for MMIO.

State and persistence: constants only; applied values persist in IRQ controller registers.

Dependencies and integration: included by ISYS IRQ public/private code.

Risks and test signals: using `0xFFFF` assumes all active IRQ bits fit and should be enabled/cleared. Tests should validate hardware bit width, masked/unmasked behavior, and status clear semantics.
