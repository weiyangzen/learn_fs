# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-is-regs.h

## Purpose
`fimc-is-regs.h` defines FIMC-IS watchdog, MCUCTL, interrupt, ISSR mailbox, and PMU ISP register offsets and bitfield macros, plus prototypes for the register command helpers.

## Important APIs, Types, and Functions
Key register constants include `REG_WDT_ISP`, `MCUCTL_BASE`, `MCUCTL_REG_MCUCTRL`, `MCUCTL_REG_BBOAR`, interrupt generation/clear/mask/status registers 0/1/2, `MCUCTL_REG_ISSR(n)`, and PMU offsets such as `REG_PMU_ISP_ARM_CONFIGURATION`, `REG_PMU_ISP_ARM_STATUS`, and `REG_PMU_ISP_ARM_OPTION`. Bit helpers include `INTGR0_INTGD()`, `INTMSR0_GET_INTMSD()`, and related interrupt field macros. Prototypes expose IRQ clear, mailbox, stream, sensor, setfile, parameter, mode, and sub-IP power helpers.

## Control Flow
There is no executable flow. These macros are composed by `fimc-is-regs.c` and `fimc-is.c` before MMIO accesses.

## State and Persistence
No software state is stored here. The constants describe volatile hardware registers and host/firmware mailbox slots.

## Dependencies and Integration Points
The header is included by FIMC-IS core, register, and parameter code. It depends on `struct fimc_is` being declared by included core headers and on the hardware/firmware register ABI.

## Risks and Edge Cases
Register offsets are absolute within the mapped resource layout used by this driver. Any DT resource that maps a different base window will break accesses. Several bitfield macros accept unchecked indexes. The comment naming for some interrupt clear bits is easy to confuse because host-to-VIC and ISP-to-host register groups use different bit ranges.

## Test Signals
Validate firmware boot using `BBOAR` and PMU registers, host-to-IS interrupt generation, IS-to-host interrupt clear, ISSR command/reply layout, stream/setfile/sensor command register traces, and PMU power-off status polling.
