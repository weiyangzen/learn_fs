# sources/distributed-fs/ceph-client/drivers/hsi/controllers/omap_ssi_regs.h

## Purpose
Defines OMAP SSI hardware register offsets and bit fields for SYS, SST, SSR, and GDD blocks.

## Important APIs, Types, and Functions
This is a register-definition header. It provides macros such as `SSI_MPU_STATUS_REG(port, irq)`, `SSI_MPU_ENABLE_REG(port, irq)`, `SSI_WAKE_REG(port)`, `SSI_SST_BUFFER_CH_REG(channel)`, `SSI_SSR_BUFFER_CH_REG(channel)`, and GDD channel register macros.

## Control Flow
No executable control flow. The macros are consumed by controller and port code for MMIO reads/writes, interrupt masking/acknowledgement, DMA programming, wake manipulation, and context restore.

## State and Persistence
The file itself has no state. It names hardware state held in SSI registers: wake bits, interrupt enable/status, SST/SSR modes and buffers, SSR errors, GDD logical channel descriptors, and GDD global control.

## Dependencies and Integration Points
Integrated with `omap_ssi_core.c`, `omap_ssi_port.c`, and `omap_ssi.h`. The values encode the contract with OMAP SSI hardware and the GDD DMA engine.

## Risks and Test Signals
Risks are incorrect offsets, bit masks, or channel calculations causing silent hardware corruption. Test signals include successful register debugfs dumps, correct interrupt ack/mask behavior, DMA descriptor operation on all logical channels, and wake bit manipulation on each port.
