# sources/distributed-fs/ceph-client/drivers/media/cec/platform/s5p/regs-cec.h

## Purpose
This private header defines Samsung S5P CEC register offsets, interrupt bits, TX/RX control bits, logical address mask, and the PMU HDMI PHY control offset.

## Important APIs, Types, and Functions
There are no functions. Important definitions include `S5P_CEC_STATUS_0..3`, `S5P_CEC_IRQ_MASK/CLEAR`, TX and RX buffer base offsets, `S5P_CEC_TX_CTRL_START/BCAST/RESET`, `S5P_CEC_RX_CTRL_ENABLE/RESET`, and `EXYNOS_HDMI_PHY_CONTROL`.

## Control Flow
`exynos_hdmi_cecctrl.c` uses these constants to program the hardware in reset, enable, transmit, receive, and IRQ-clear flows. Buffer offsets are spaced by four bytes and are used by loops that add `i * 4`.

## State and Persistence
The file documents hardware state layout only. Runtime values are held in MMIO registers.

## Dependencies and Integration Points
It is consumed by the Samsung S5P CEC driver files and must match the SoC register map. No external subsystem directly includes it.

## Risks and Test Signals
Wrong offsets or bit values would cause silent hardware misbehavior. Tests require hardware or register-level emulation checking TX start, RX enable, interrupt mask/clear, buffer byte placement, and logical address programming.
