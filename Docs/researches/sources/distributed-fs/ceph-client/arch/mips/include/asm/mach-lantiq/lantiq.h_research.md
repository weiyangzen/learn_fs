<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-lantiq/lantiq.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-lantiq/lantiq.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-lantiq/lantiq.h` declares board, firmware, memory, and platform-data contracts for `mach-lantiq`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 13 macros including `_LANTIQ_H__`, `ltq_r32`, `ltq_w32`, `ltq_w32_mask`, `ltq_r8`, `ltq_w8`, `ltq_ebu_w32`, `ltq_ebu_r32`, `ltq_ebu_w32_mask`, `IOPORT_RESOURCE_START`, `IOPORT_RESOURCE_END`, `IOMEM_RESOURCE_START`, `IOMEM_RESOURCE_END`; 0 structs: none; 0 enums: none; 12 callable helpers/prototypes: `ltq_disable_irq`, `ltq_mask_and_ack_irq`, `ltq_enable_irq`, `ltq_eiu_get_irq`, `clk_activate`, `clk_deactivate`, `clk_get_cpu`, `clk_get_fpi`, `clk_get_io`, `clk_get_ppe`, `ltq_boot_select`, `ltq_soc_type`; 2 extern variables: `ltq_ebu_membase`, `ebu_lock`. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
Control flow is concentrated in inline/prototype helpers such as `ltq_disable_irq`, `ltq_mask_and_ack_irq`, `ltq_enable_irq`, `ltq_eiu_get_irq`, `clk_activate`, `clk_deactivate`, `clk_get_cpu`, `clk_get_fpi`, `clk_get_io`, `clk_get_ppe`, and 2 more. Callers include this header and execute the inline range checks, MMIO accessor wrappers, reset/timer calls, DMA start/stop helpers, or board accessors directly in their platform setup path.

## State and Persistence Behavior
The header itself persists no data, but its helpers touch hardware-visible state: MMIO mappings, I/O port byte order, DMA engine registers, timer/reset controls, RTC cells, IRQ enables, or allocation alignment. Any persistent effects are in hardware registers, firmware-provided memory, or kernel subsystem state owned by callers.

## Dependencies and Integration Points
Direct includes are `linux/irq.h`, `linux/device.h`, `linux/clk.h`. Major macro families are `ltq_ebu (3)`, `IOMEM_RESOURCE (2)`, `IOPORT_RESOURCE (2)`, `ltq_w32 (2)`, `_LANTIQ (1)`, `ltq_r32 (1)`, `ltq_r8 (1)`, `ltq_w8 (1)`. Typed contracts include no structs. Callable helpers or declarations include `ltq_disable_irq`, `ltq_mask_and_ack_irq`, `ltq_enable_irq`, `ltq_eiu_get_irq`, `clk_activate`, `clk_deactivate`, `clk_get_cpu`, `clk_get_fpi`, `clk_get_io`, `clk_get_ppe`, `ltq_boot_select`, `ltq_soc_type`. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is machine setup code, boot parameter parsing, platform device registration, board identification, and firmware handoff.

## Risks
layout drift between firmware, board files, and consumers can cause wrong memory maps, device registration, or machine identity.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-lantiq/lantiq.h -->
