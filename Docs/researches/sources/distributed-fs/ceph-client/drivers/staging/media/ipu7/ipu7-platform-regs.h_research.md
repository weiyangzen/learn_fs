# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-platform-regs.h

## Purpose
Provides common IPU7 platform register offsets for ISYS/PSYS microcontroller control, firmware code/data bases, printf/logging registers, software interrupt controls, local DMEM/SPC offsets, CSI port count, PSYS IRQ controls, and PSYS buttress subdomain power masks.

## Important APIs, Types, and Constants
Key bases are `IS_BASE`, `IS_UC_CTRL_BASE`, `PS_BASE`, and `PS_UC_CTRL_BASE`. Interrupt definitions include `TO_SW_IRQ_MASK`, `TO_SW_IRQ_FW`, `IS_UC_TO_SW_IRQ_MASK`, `IPU_REG_PSYS_TO_SW_IRQ_CNTL_*`, and `IRQ_FROM_LOCAL_FW`. Firmware/debug offsets include `FW_CODE_BASE`, `FW_DATA_BASE`, `PRINTF_*`, and `LOCAL_DMEM_BASE_ADDR`. `IPU_ISYS_SPC_OFFSET`, `IPU7_PSYS_SPC_OFFSET`, `IPU_ISYS_DMEM_OFFSET`, and `IPU_PSYS_DMEM_OFFSET` describe local memory windows. `enum ipu7_device_buttress_psys_domain_pos` and power masks define PSYS subdomain control bits.

## Control Flow and State
The header contains no runtime code. `ipu7-isys.c` uses IS UC interrupt and printf offsets to set up hardware and service firmware IRQs. Firmware-loading and PSYS code elsewhere use the same base offsets and power masks.

## Dependencies and Integration Points
Depends on `BIT()` from Linux bit macros in including C files. It is included by ISYS queue/video/top-level code and MMU/platform code that needs shared IPU address layout.

## Risks and Test Signals
Wrong offsets can break firmware IRQ delivery, debug logging, or subdomain power sequencing. Test signals include firmware-to-host IRQs being observed and cleared, printf AXI control being programmed, PSYS power masks matching hardware generation, and no spurious IRQ after runtime suspend.
