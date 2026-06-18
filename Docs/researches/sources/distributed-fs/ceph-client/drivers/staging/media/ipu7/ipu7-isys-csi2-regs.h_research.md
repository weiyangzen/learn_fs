# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-isys-csi2-regs.h

## Purpose
Defines the IPU7/IPU7P5 CSI-2 input-system register map used by the CSI receiver, adapter layer, legacy interrupt controller, GP registers, PHY control, MIPI generator, and selected IS main blocks. It is a hardware contract header: no code executes here, but CSI2 enable/disable, IRQ handling, PHY programming, and test-pattern paths depend on these offsets and masks being exact.

## Important APIs, Types, and Constants
Important register base macros include `IS_MAIN_BASE`, `IS_IO_BASE`, `IS_IO_CDPHY_BASE(i)`, `IS_IO_CSI2_HOST_BASE(i)`, `IS_IO_CSI2_ADPL_PORT_BASE(i)`, `IS_IO_CSI2_ERR_LEGACY_IRQ_CTL_BASE(i)`, `IS_IO_CSI2_SYNC_LEGACY_IRQ_CTL_BASE(i)`, `IS_IO_CSI2_LEGACY_IRQ_CTRL_BASE`, `IS_IO_GPREGS_BASE`, `IS_IO_CSI2_GPREGS_BASE`, `PORT_ARB_BASE`, and `IS_IO_MGC_BASE`. Generic IRQ register offsets are `IRQ_CTL_*` plus IPU7P5-specific `IRQ1_CTL_*` for frame-end status. Masks such as `IPU7_CSI_IS_IO_IRQ_MASK`, `IPU7_CSI_ADPL_IRQ_MASK`, `IPU7_CSI_RX_LEGACY_IRQ_MASK`, `IPU7_CSI_RX_ERROR_IRQ_MASK`, `IPU7_CSI_RX_SYNC_IRQ_MASK`, and `IPU7P5_CSI_RX_SYNC_FE_IRQ_MASK` drive top-level and per-port ISR filtering. Enums `CSI_FE_MODE_TYPE`, `CSI_FE_INPUT_MODE`, `MGC_CSI_ADPL_TYPE`, and `CSI2HOST_SELECTION` describe PHY/input-generator mode values.

## Control Flow and State
This header participates in control flow through MMIO sites in `ipu7-isys-csi2.c` and `ipu7-isys.c`: stream enable writes adapter input mode, APB divider, aggregation, PHY/IRQ registers; stream disable clears IRQs and powers down PHY; ISYS setup enables firmware and CSI legacy interrupts; ISRs read and clear per-port legacy error/sync status. State is persisted only in device registers; the header itself has no runtime storage.

## Dependencies and Integration Points
The constants integrate with Linux `readl()`/`writel()` users, CSI PHY helpers, firmware response handling, and platform register definitions. Hardware-version conditionals in the driver interpret IPU7 versus IPU7P5 sync/FE masks differently, so tests and reviews must validate both register layouts.

## Risks and Test Signals
Offset mistakes can silently break stream bring-up, interrupt clearing, or PHY readiness. Notable review risks are duplicated macro names (`SCRAMBLING`, `SPARE_RW`, `SPARE_RO`) and several sync masks currently set to zero, which disables direct FS/FE legacy sync handling unless firmware SOF/EOF responses cover the path. Test signals are successful CSI stream-on/off on each port, correct receiver error logging, no interrupt storms after streamoff, and hardware trace showing expected writes to adapter, legacy IRQ, and PHY registers.
